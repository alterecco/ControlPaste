from pygments import highlight
from pygments.lexers import get_all_lexers
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

## list of languages we want to support
LANGUAGES = [  'ahk'
             , 'common-lisp'
             , 'rb'
             , 'text'
             , 'xml'
            ]

languages = []
for l in get_all_lexers():
    if l[1][0] in LANGUAGES:
        languages.append((l[0], l[1][0]))

languages.sort(key=lambda x: x[1].lower())

## confirm that `lang' is a valid language
def check(lang):
    return lang in LANGUAGES

def name(lang):
    for x in languages:
        if x[1] == lang:
            return x[0]
    return "Unknown"

def parse(code, lang, lines=False):
    lexer = get_lexer_by_name(lang, stripall=True)
    # formatter = HtmlFormatter(linenos=lines, noclasses=True, style='emacs')
    formatter = HtmlFormatter(linenos=lines, cssclass='paste')
    return highlight(code, lexer, formatter)

