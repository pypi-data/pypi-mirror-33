import re
import cgi
import bleach


def make_name_simple(markup):
    markup = markup.strip()
    return re.sub('{.*}', '', markup) \
           .replace('<', '') \
           .replace('>', '') \
           .strip()

def make_name_html(markup):
    markup = markup.strip()
    markup = cgi.escape(markup)
    return markup.replace('{', '<span class="auth">') \
                 .replace('}', '</span>') \
                 .replace('&lt;', '<span class="auth">') \
                 .replace('&gt;', '</span>')

def clean_html(html):
    if html is None:
        return
    return bleach.clean(html, tags=['b', 'u', 'i', 'p'])

