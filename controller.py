import time
from random import random
from hashlib import sha1

from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import session
from flask import abort
from flask import Response

from ControlPaste import app

from ControlPaste.database import db
from ControlPaste.models import Paste
from ControlPaste.lib.hilite import languages

app.secret_key = 'cup%oapho7yuaN7IexaiNg8tichi7Hir6igi'

@app.before_request
def before_request():
    session.permanent_session_lifetime = 31556926
    if not 'user' in  session:
        session['user'] = sha1('{0}|{1}'.format(random(), time.time())).hexdigest()

@app.after_request
def shutdown_session(response):
    db.session.remove()
    return response

@app.route('/', methods=['GET', 'POST'])
def new():

    code = title = ''
    author = session.get('author', '')
    ## get the language from the session (if present)
    language = session.get('language', 'text')
    parent = None
    private = False

    if request.method == 'POST':
        code = request.form['code']
        language = request.form['language']
        author = request.form['author']
        title = request.form['title']
        private = 'private' in request.form
        if 'parent' in request.form:
            parent = Paste.get(request.form['parent'])

        if code and language:
            paste = Paste(code, language, session['user'], title, author,
                          parent, private)
            paste.save()

            ## set some defaults for next time around
            session['language'] = language
            session['author'] = author

            ## show the paste
            return redirect(url_for('view', uri=paste.uri))

    return render_template(
        'new.html',
        code=code,
        author=author,
        session_author=author,
        title=title,
        private=private,
        language=language,
        languages=languages,
    )

@app.route('/view/<uri>/')
def view(uri, raw=False):
    session_author = session.get('author', '')
    paste = Paste.get(uri)
    if not paste:
        abort(404)

    if raw:
        return Response(paste.code, 200, mimetype='text/plain; charset=utf-8')
    else:
        return render_template(
            'view.html',
            session_author=session_author,
            paste=paste
        )

@app.route('/raw/<uri>/')
def raw(uri):
    return view(uri, True)

@app.route('/all/')
@app.route('/all/<int:page>/')
def all(page=1):
    session_author = session.get('author', '')
    pastes = Paste.get_all().limit(10).offset(10 * (page - 1)).all()

    if not pastes and page != 1:
        abort(404)

    ## TODO handle pagination
    return render_template(
        "all.html",
        session_author=session_author,
        pastes=pastes,
    )

@app.route('/author/<author>/')
@app.route('/author/<author>/<int:page>/')
def author(author, page=1):
    session_author = session.get('author', '')
    pastes = Paste.get_all(author).limit(10).offset(10 * (page - 1)).all()

    print(pastes)
    if not pastes and page != 1:
        abort(404)

    ## TODO handle pagination
    return render_template(
        "all.html",
        author=author,
        session_author=session_author,
        pastes=pastes,
    )


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
