import re


def get_qname(label, category='figshare'):
    return "{}_{}".format(category, label)


def wikipedia_url(dbpedia_link):
    """
    Transform the dbpedia_link into its Wikipedia counterpart.
    URLs which do not match DBpedia resource naming scheme are
    returned untouched.
    """
    pattern = '(http://)?([a-zA-Z]{2,3}\\.)?dbpedia.org/resource/(.*)'
    result = re.match(pattern, dbpedia_link, re.I)
    if result:
        schema, lang, concept = result.groups()
        lang = lang or 'en.'
        return 'http://{}wikipedia.org/wiki/{}'.format(lang, concept)
    else:
        return dbpedia_link
