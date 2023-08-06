# -*- coding: utf-8 -*-

import re
import tempfile
import requests


def fetch_url(url):
    """Downloads acceptable URL to temporary file
    """
    ext = None
    ALLOWED = ['jpg', 'jpeg', 'png', 'pdf', 'gif',]

    try:
        ext = re.search(r'\.([a-zA-Z]{3,})$', url).group(1)
    except AttributeError:
        raise ValueError('Cannot determine file extension of URL %s' % url)

    ext = ext.lower()

    if ext not in ALLOWED:
        raise ValueError('File extension should be one of %s, not %s' % (', '.join(ALLOWED), ext))

    try:
        resp = requests.get(url)
    except Exception as e:
        raise Exception('Failed to fetch URL: %s' % e)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.' + ext) as fp:
        fp.write(resp.content)
        return fp.name
