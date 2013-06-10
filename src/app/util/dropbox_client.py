from dropbox import session as db_session
from dropbox import client
from flask import request, session, render_template, redirect, url_for, g, jsonify
from app import app, db, lm, oid, nanopubs_dir, docxs
import xlrd
import nltk
from docx import *
import os



APP_KEY = 'r2mo1zdpeg0vnw3'
APP_SECRET = 'xgurgou9iosk3c7'
ACCESS_TYPE = 'dropbox' # should be 'dropbox' or 'app_folder' as configured for your app


def get_session():
    return db_session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)

@app.route('/dropbox_authorize')
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
    for f in folder_metadata['contents']:
        print f['path'], f['mime_type']
        if not f['is_dir'] and f['mime_type'] == 'application/vnd.ms-excel' :
            result += extractTextFromExcel(f['path'], db_client)
        if not f['is_dir'] and f['mime_type'] == 'text/plain' :
            result += extractText(f['path'], db_client)
        if not f['is_dir'] and f['mime_type'] == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' :
            result += extractWord(f['path'], db_client)
            
    

    currentRev = None
    for r in revisions:
        if currentRev == None:
            currentRev = r
        else:
            print str(currentRev['revision']) + 'wasRevisionOf' + str(r['revision'])
            currentRev = r
    

    import re
    words = re.split('\W',result)

    
    from nltk.corpus import stopwords
    words2 = [w.lower() for w in words if (not w.lower() in stopwords.words('english')) and not w == u'']
    
    
    # words2 = [w for w in words if not w in nltk.corpus.stopwords.words['english']]
    # print words2
    
    from nltk.probability import FreqDist
    
    fd = FreqDist(words2)
    print "FREQ"
    print fd
    
    
    return render_template('words.html', results=fd)

    
def extractWord(path, client):
    f, metadata = client.get_file_and_metadata(path)
    
    out = open('/tmp/doc.docx', 'w')
    out.write(f.read())
    out.close()
    
    out = open('/tmp/doc.docx', 'rb')
    document = opendocx(out)
    
    
    
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
