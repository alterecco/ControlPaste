from pygments import highlight
from pygments.lexers import get_all_lexers
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

## list of languages we want to support
LANGUAGES = [
          'text'
        , 'xml'
        , 'common-lisp'
        , 'bbcode'
        , 'bash'
        , 'javascript'
        , 'css'
        , 'html'
        , 'c'
        , 'ahk'
        , 'batch'
        , 'cpp'
        , 'd'
        , 'diff'
        , 'go'
        , 'ini'
        , 'irc'
        , 'java'
        , 'lua'
        , 'make'
        , 'mysql'
        , 'perl'
        , 'php'
        , 'postscript'
        , 'python3'
        , 'python'
        , 'rb'
        , 'sql'
        , 'vim'
]
PREFERRED = ['text', 'xml', 'common-lisp']

languages = []
for l in get_all_lexers():
    if l[1][0] in LANGUAGES:
        languages.append((l[0], l[1][0]))

languages.sort(key=lambda x: x[1].lower())

preferred_languages = []
for l in languages:
    if l[1] in PREFERRED:
        preferred_languages.append(l)
        ## delete the preferred languages from languages list
        languages.remove(l)

## confirm that `lang' is a valid language
def check(lang):
    return lang in LANGUAGES

def name(lang):
    for x in languages:
        if x[1] == lang:
            return x[0]
    for x in preferred_languages:
        if x[1] == lang:
            return x[0]
    return "Unknown"

def parse(code, lang, lines=False):
    lexer = get_lexer_by_name(lang, stripall=True)
    if lines:
        hlist = []
        #loop over the lines of code and find the ones to highlight
        code = code.splitlines()
        for idx, line in enumerate(code):
            if line[0:3] == '@h@':
                hlist.append(idx + 1)
                code[idx] = line[3:]
        print(hlist)
        code = '\n'.join(code)
        formatter = HtmlFormatter(linenos='inline', lineanchors="line", anchorlinenos=True, cssclass='paste', hl_lines=hlist)
    else:
        formatter = HtmlFormatter(cssclass='paste')
    return highlight(code, lexer, formatter)

