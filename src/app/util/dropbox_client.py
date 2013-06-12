from dropbox import session as db_session
from dropbox import client
from flask import request, session, render_template, redirect, url_for, g, jsonify
from flask.ext.login import login_required
from app import app, db, lm, oid, nanopubs_dir, docxs
import xlrd
import nltk
from docx import *
import os
from tempfile import TemporaryFile, NamedTemporaryFile
import subprocess
from nltk.probability import FreqDist
from nltk.corpus import stopwords
import re
import requests
from requests_oauthlib import OAuth1
from glob import glob
import shutil


APP_KEY = 'r2mo1zdpeg0vnw3'
APP_SECRET = 'xgurgou9iosk3c7'
ACCESS_TYPE = 'dropbox' # should be 'dropbox' or 'app_folder' as configured for your app


def get_session():
    return db_session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)

@app.route('/dropbox_authorize')
@login_required
def dropbox_authorize():
    
    # We only land on this page, if the user does not yet have granted access
    
    sess = get_session()
    request_token = sess.obtain_request_token()
    
    session['dropbox_request_token_key'] = request_token.key
    session['dropbox_request_token_secret'] = request_token.secret
    
    print request_token.key, request_token.secret

    callback = "http://localhost:5000" + url_for(dropbox_callback)
    oauth_request_auth_url = sess.build_authorize_url(request_token, oauth_callback=callback)
    
    print oauth_request_auth_url
    session.modified = True
    print "2"
    return redirect(oauth_request_auth_url)
    

@app.route('/dropbox_callback', methods=['GET'])
@login_required
def dropbox_callback():
    request_token_key = request.args.get('oauth_token')
    
    if not request_token_key:
        return "Expected a request token key back!"
    
    print request_token_key
    
    sess = get_session()
    
    if session['dropbox_request_token_key'] != request_token_key :
        return "Request tokens do not match!"
    
    request_token_secret = session['dropbox_request_token_secret']
    
    request_token = db_session.OAuthToken(request_token_key,request_token_secret)
    access_token = sess.obtain_access_token(request_token)
    
    session['dropbox_access_token_key'] = access_token.key
    session['dropbox_access_token_secret'] = access_token.secret
        
    g.user.dropbox_access_token_key = access_token.key
    g.user.dropbox_access_token_secret = access_token.secret
    
    print "Committing DB session"
    db.session.commit()
    print "Good to go!"
    
    return redirect(url_for('dropbox'))





@app.route('/dropbox_files', methods=['GET'])
@login_required
def dropbox_files():
    print "Getting dropbox files ..."
    sess = get_session()
    sess.set_token(g.user.dropbox_access_token_key, g.user.dropbox_access_token_secret)
    
    db_client = client.DropboxClient(sess)
    
    print "linked account:", db_client.account_info()
    
    path = request.args.get('path', '/Data2Semantics')
    
    print "Dropbox path is ", path
    files = db_client.metadata(path)
    
    print "... done"
    return jsonify(files)

@app.route('/dropbox/go', methods=['GET'])
@login_required
def dropbox_go():
    path = request.args.get('path', 'blaat')
    
    sess = get_session()
    sess.set_token(g.user.dropbox_access_token_key, g.user.dropbox_access_token_secret)
    
    db_client = client.DropboxClient(sess)
    
    fileMeta = db_client.metadata(path)
    revisions = db_client.revisions(path)
    print revisions
    
    folder = os.path.dirname(path)
    
    folder_metadata = db_client.metadata(folder)
    print folder_metadata
    
    result = ""
    catreport = None
    odspath = None
    rdfpath = None
    nwa_url = None
    for f in folder_metadata['contents']:
        print f['path'], f['mime_type']
        
        if f['is_dir']:
            continue
        
        if f['mime_type'] =='application/vnd.ms-excel' :
            r = extractTextFromExcel(f['path'], db_client)
            
            if f['path'] == path:
                odspath = convertToODS(f['path'], db_client)
                
                tsvs,ttls,jsons,sheetdep_json = extractDependencies(path, odspath)
                
                # Append all turtle files
                outfile = NamedTemporaryFile(delete=False)
                
                print "Appending {} to {}".format(ttls, outfile.name)
                for fname in ttls:
                    with open(fname) as infile:
                        for line in infile:
                            outfile.write(line)
                
                outfile.close()
                rdfpath = outfile.name
                            
                print "Generating CAT report"
                catreport = cat(f['path'], db_client, _format='TURTLE', _file=outfile)
                
                print "Running Network analysis"
                nwa_url = runNetworkAnalysis(path, tsvs, jsons, sheetdep_json)
                
                
        elif f['mime_type'] == 'text/plain' :
            r = extractText(f['path'], db_client)
        elif f['mime_type'] == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' :
            r = extractWord(f['path'], db_client)
        elif f['mime_type'] == 'application/rdf+xml' :
            # Need to do something fancy here
            r = ""
            if f['path'] == path :
                catreport = cat(f['path'], db_client, _format='RDFXML')
        elif f['mime_type'] == 'application/octet-stream' and f['path'].endswith('.ttl') :
            # Need to do something fancy here
            r = ""
            if f['path'] == path :
                catreport = cat(f['path'], db_client, _format='TURTLE')
        else :
            r = ""
            
        result += r
        # Store results for selected file separately
        if f['path'] == path :
            s_result = r
            
                
            
    
    
    

    currentRev = None
    for r in revisions:
        if currentRev == None:
            currentRev = r
        else:
            print str(currentRev['revision']) + 'wasRevisionOf' + str(r['revision'])
            currentRev = r
    

    words = re.split('\W',result)
    s_words = re.split('\W',s_result)
    

    words2 = [w.lower() for w in words if (not w.lower() in stopwords.words('english')) and not w == u'']
    s_words2 = [w.lower() for w in s_words if (not w.lower() in stopwords.words('english')) and not w == u'']
    
    # words2 = [w for w in words if not w in nltk.corpus.stopwords.words['english']]
    # print words2
    

    
    fd = FreqDist(words2)
    s_fd = FreqDist(s_words2)
    
    
    s_fd_length =  s_fd.N()
    
    print "FREQ"
    print fd
    
    
    return render_template('words.html',
                           name = f['path'].split('/')[-1],
                           s_fd_length = s_fd_length,
                           s_fd = s_fd,
                           fd=fd,
                           revisions = revisions,
                           catreport = catreport,
                           odspath = odspath,
                           rdfpath = rdfpath,
                           nwa_url = nwa_url)


@app.route('/dropbox/publish', methods=['POST'])
@login_required
def dropbox_publish():
    # print request.form
    
    # Dropbox Client
    sess = get_session()
    sess.set_token(g.user.dropbox_access_token_key, g.user.dropbox_access_token_secret)
    
    db_client = client.DropboxClient(sess)
    
    # Figshare Client
    oauth_token = g.user.oauth_token
    oauth_token_secret = g.user.oauth_token_secret

    client_key = app.config['FIGSHARE_CLIENT_KEY']
    client_secret = app.config['FIGSHARE_CLIENT_SECRET']

    oauth = OAuth1(client_key,
                   client_secret=client_secret,
                   resource_owner_key=oauth_token,
                   resource_owner_secret=oauth_token_secret)
    
    if request.method == 'POST':
        print "Method is POST"
        # Data coming in
        try:
            report = request.form['report']
            name = request.form['name']
            tags = request.form['tags[]']
            print description
            print name, tags
            
            return "Success ja"
        except Exception as e:
            print e
            return "Bad request, I guess"
        
    else :
        return "Failed!"

    
    
def runNetworkAnalysis(path, tsvs, jsons, sheetdep_json):
    nwa_path = app.config['NWANALYSIS_PATH']
    nwa_base = app.config['NWANALYSIS_OUTPUT_PATH'] + path
    nwa_output = nwa_base + "/json"
    nwa_url = app.config['NWANALYSIS_BASE_URL'] + path + '/explore.html'
    
    nwa_explore = app.config['NWANALYSIS_EXPLORER_PATH']
    
    # Don't forget to copy the html + json file to that location! 
    
    if not os.path.exists(nwa_output) :
        os.makedirs(nwa_output)
        print "Created "+nwa_output
        
    print "Changing working directory to {}".format(nwa_output)
    os.chdir(nwa_output)
    
    for tsv in tsvs:
        print "Processing {}".format(tsv)
        (tsvpath, tsvfn) = os.path.split(tsv)
        
        # Remove the extension
        tsvfn = tsvfn[:-4]
        
        tsvout = nwa_output + "/" + tsvfn
        
        subprocess.call(['R','-f',nwa_path,'--args',"{}".format(tsv),"{}".format(tsvout)])
        print "Done"
        
    for json in jsons:
        print "Moving {}".format(json)
        (jsonpath, jsonfn) = os.path.split(json)
        
        # Remove the extension
        jsonfn = jsonfn[:-5]
        
        jsonout = nwa_output + "/" + jsonfn + "/graph.json"
        
        print "Copying to {}".format(jsonout)
        shutil.copy(json,jsonout)
    
        
    
    if not os.path.exists(nwa_base+'/js') :
        os.makedirs(nwa_base+'/js')
        print "Created "+nwa_base+'/js'
    if not os.path.exists(nwa_base+'/css') :
        os.makedirs(nwa_base+'/css')
        print "Created "+nwa_base+'/css'
        
    shutil.copy(nwa_explore+'/js/d3.min.js',nwa_base+'/js')
    shutil.copy(nwa_explore+'/css/bootstrap.min.css',nwa_base+'/css')
    shutil.copy(nwa_explore+'/explore.html',nwa_base)
    shutil.copy(sheetdep_json,nwa_output+'/dep.json')
    
    print "Done!"
    
    return nwa_url
    
    
    
    


def extractDependencies(path, ods_filename):
    (ods_path, ods_file) = os.path.split(ods_filename)
    print "Changing working directory to {}".format(ods_path)
    os.chdir(ods_path)
    
    plsheet_path = app.config['PLSHEET_PATH']

    print "Clearing folder of tsv, json and ttl files..."
    
    old = glob("{}/*.tsv".format(ods_path))
    old.extend(glob("{}/*.ttl".format(ods_path)))
    old.extend(glob("{}/*.json".format(ods_path)))
    
    for f in old :
        try:
            if os.path.isfile(f):
                print "Deleting {}".format(f)
                os.unlink(f)
        except Exception as e:
            print e
        
    
    
    print "Calling ", ' '.join([plsheet_path,ods_file])
    subprocess.call([plsheet_path,ods_file])
    
    
    tsvs = glob("{}/*.tsv".format(ods_path))
    print tsvs
    ttls = glob("{}/*.ttl".format(ods_path))
    print ttls
    
    
    sheetdep = glob("{}/tmp*.json".format(ods_path))
    print sheetdep

    sheetdep_json = sheetdep[0]
    print sheetdep_json
    
    jsons = glob("{}/*.json".format(ods_path))
    jsons.remove(sheetdep_json)
    
    return tsvs, ttls, jsons, sheetdep_json



def convertToODS(path, client):
    f, metadata = client.get_file_and_metadata(path)
    
    xls = NamedTemporaryFile(delete=False)
    xls.write(f.read())
    xls.close()
    
    xls_filename = xls.name
    ods_filename = xls.name + ".ods"
    
    print "TempFile: ", xls_filename

    
    python_path = app.config['LIBRE_OFFICE_PYTHON_PATH']
    unoconv_path = app.config['UNOCONV_PATH']
    
    print "Calling ", ' '.join([python_path, unoconv_path, '-f', 'ods', xls_filename])
    subprocess.call([python_path, unoconv_path, '-f', 'ods', xls_filename])
    
    return ods_filename


def cat(path, client, _format='RDFXML', _file = None):
    
    if _file == None :
        f, metadata = client.get_file_and_metadata(path)
        
        rdf = NamedTemporaryFile(delete=False)
        rdf.write(f.read())
        rdf.close()
    else :
        rdf = _file
        
    rdf_filename = rdf.name
    
    print "TempFile: ", rdf_filename
    
    cat_path = app.config['CAT_PATH']
    cat_output = app.config['CAT_OUTPUT_PATH'] + path
    print "Output  : ", cat_output
    cat_url = app.config['CAT_BASE_URL'] + path + '/report/index.html'
    print "URL     : ", cat_url
    
    if not os.path.exists(cat_output) :
        os.makedirs(cat_output)
        print "Created "+cat_output
    
    print "Calling ", cat_path
    print ' '.join(['java','-Xmx1G', '-jar',cat_path,'--data',rdf_filename,'--size','large','--type',_format, '--out', cat_output])
    subprocess.call(['java','-Xmx1G','-jar',cat_path,'--data',rdf_filename,'--size','large','--type',_format, '--out', cat_output])
    print "Done"
    
    return cat_url
    
def extractWord(path, client):
    f, metadata = client.get_file_and_metadata(path)
    
    out = TemporaryFile()
    out.write(f.read())
    document = opendocx(out)
    
    out.close()
    
    text = getdocumenttext(document)
    
    print text
    
    return '\n'.join(text)
    

def extractText(path, client):
    f, metadata = client.get_file_and_metadata(path)
    
    text = f.read()
    
    
    return text
    


#bits of code prov:wasAttributedTo  http://www.youlikeprogramming.com/2012/03/examples-reading-excel-xls-documents-using-pythons-xlrd/
def extractTextFromExcel(path, client):
    print path
    text = ''
    f, metadata = client.get_file_and_metadata(path)
    workbook = xlrd.open_workbook(file_contents=f.read())
    # workbook = xlrd.open_workbook(path);
    worksheets = workbook.sheet_names()
    for worksheet_name in worksheets:
        worksheet = workbook.sheet_by_name(worksheet_name)
        num_rows = worksheet.nrows - 1

        curr_row = -1
        while curr_row < num_rows:
            curr_row += 1
            row = worksheet.row(curr_row)

            curr_cell = -1
            num_cells = len(row) - 1
            while curr_cell < num_cells:
                curr_cell += 1
                #print curr_cell
                # Cell Types: 0=Empty, 1=Text, 2=Number, 3=Date, 4=Boolean, 5=Error, 6=Blank
                cell_type = worksheet.cell_type(curr_row, curr_cell)
                cell_value = worksheet.cell_value(curr_row, curr_cell)
                #print cell_value
                if cell_type == 1:
                    text += ' ' + cell_value
        #f.close();
    return text
