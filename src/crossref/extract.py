from pdfminer.pdfinterp import PDFResourceManager, process_pdf
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from cStringIO import StringIO
from pprint import pprint
import re
import glob

## Regular expressions for matching reference patterns.
## Based on: http://amath.colorado.edu/documentation/LaTeX/reference/faq/bibstyles.html

# springer
_springer = r'\n\d+\.\s'

# plain, abbrv, Nabbrv, acm, amsplain, annotation, is-abbrv, is-plain, 
# is-unsrt, unsrt, nar, nature, Nplain, Nunsrt, phcpc, phiaea, plainyr, sej
# ieeetr, ieeetr, ama, cj, phjcp, siam, jbact, finplain, IEEEannot, 
_ieeetr = r'\n\[\d+\]\s' 

# abstract, agsm, automatica, dcu, kluwer
_abstract = r'\n\[\w+\-\d{4}\w*\]\s'

# alpha, nalpha, amsalpha, annotate, cparalleless, is-alpha
_alpha = r'\n\[\w{2-3}\d{2}\w*\]\s'

# authordate, apalike, cea, cell, jmb, aaai-named, jqt1999
_authordate = r'\n\[\w+,\s\d{4}\w*\]\s'

# jas99, jtb, humanbio
_jas99 = r'\n\[.+?\S\d{4}\w*\]\s'

# apa, apasoft, bbs, cbe, humannat
_apa = r'\n\[\w+\d{4}\w*\]\s'

# named
_named = r'\n\[\w+\s\d{4}\w*\]\s'

# these, (wmaainf)
_these = r'\n\[.+\s\d{2}\w*\]\s'

# wmaainf
#_wmaainf = r'\n\[\w{2-4}\s\d{2}\w*\]\s'

# decsci, jtbnew, neuron, abbrvnat, ametsoc, plainnat, development, unsrtnat
_decsci = r'\n\[.*\(\d{4}\w*\)\]\s'

# alphanum
_alphanum = r'\n\[\w+\d*\]\s'

# last resort
_last_resort = r'\n\n'


# Array of all patterns (NB: order is important!)
patterns = [_ieeetr,_abstract,_alpha,_authordate, _jas99,_apa, _named, _these, _decsci, _alphanum, _springer, _last_resort]


def main(fileGlob):
    """Runs the extraction engine over the files returned by matching the file mask (glob) pattern"""
    
    for fileName in glob.glob(fileGlob) :
        extract_references(fileName)
        
        
def extract_references(fileName):
    """Runs the extraction engine over a single file, specified by its name (full or relative path).
    
    1. Convert the PDF to a plain text document
    2. Extract references from the text
    
    Returns the references
    """
    print "Converting PDF to plain text..."
    document = convert_pdf(fileName)
    print "... done"
    print "Extracting references..."
    references = extract_references_from_text(document)
    print "done"
    return references




def convert_pdf(path):
    """Uses the pdfminer library to get the contents of the PDF as a string, returns the string"""
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)

    fp = file(path, 'rb')
    process_pdf(rsrcmgr, device, fp)
    fp.close()
    device.close()

    pdf_as_string = retstr.getvalue()
    retstr.close()
    return pdf_as_string

def extract_references_from_text(document):
    """Takes a plain text version of a document, finds the reference section, 
    and tries to match regular expression patterns to the text. 
    
    If the pattern returns multiple matches, we have found the type of bibliograpic reference style used.
    Clean each reference (i.e. remove line breaks), and add them to a dictionary
    
    Returns a dictionary of index/text pairs for all references found."""
    
    print "Finding reference section..."
    references_section = re.split('(References|Bibliography)',document)[-1]
    print "... done"
    
    print "References section: \n{}".format(references_section)

    clean_references = None
    for p in patterns :
        print "Checking for pattern {}".format(p)
        references = re.split(p,references_section)
        print "Length of references array: {}".format(len(references))
        if len(references) == 1 :
            continue
        else :
            print "Match found for pattern {}".format(p)
            clean_references = []
            index = 1
            
            for r in references :
                if len(r)>5 :
                    clean_reference_text = re.sub('\n',' ',r)
                    clean_references.append({'id': index, 'text': clean_reference_text})
                    
                    index += 1
            
            print "References:"
            pprint(clean_references)
            break
    
    
    if clean_references:
        return clean_references
    else:
        print "None of the reference patterns matched the text of the PDF"
        return {}

    

    
    
if __name__ == "__main__":
    """Only used for testing purposes."""
#    main('/Users/hoekstra/Downloads/99918.pdf')
#    main('/Users/hoekstra/Downloads/j02-08.pdf')
#    main('/Users/hoekstra/Downloads/Principles of Health Interoperability HL7 and SNOMED.pdf')
    main('/Users/hoekstra/Downloads/1754-9493-6-2.pdf')