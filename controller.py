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
from flask import flash

from ControlPaste import app

from ControlPaste.database import db
from ControlPaste.models import Paste
from ControlPaste.lib.hilite import languages, preferred_languages

app.secret_key = 'cup%oapho7yuaN7IexaiNg8tichi7Hir6igi'

@app.before_request
def before_request():
    session.permanent = True
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
        ## first we check our honeypot
        if 'really' not in request.form:

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
        preferred=preferred_languages,
    )

@app.route('/view/<uri>/')
def view(uri, raw=False):
    session_author = session.get('author', '')
    paste = Paste.get(uri)
    if not paste:
        abort(404)

    if raw:
        ## weed out @h@ lines
        code = paste.code.splitlines()
        for idx, line in enumerate(code):
            if line[0:3] == '@h@':
                code[idx] = line[3:]
        code = '\n'.join(code)
        return Response(code, 200, mimetype='text/plain; charset=utf-8')
    else:
        return render_template(
            'view.html',
            session_author=session_author,
            paste=paste,
            user=session['user'],
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
        user=session['user'],
    )

@app.route('/author/<author>/')
@app.route('/author/<author>/<int:page>/')
def author(author, page=1):
    session_author = session.get('author', '')
    pastes = Paste.get_all(author).limit(10).offset(10 * (page - 1)).all()

    if not pastes and page != 1:
        abort(404)

    ## weed out private pastes if the user
    ## of the paste does not match the session user
    for paste in pastes:
        if not paste.user == session['user'] and paste.private:
            pastes.remove(paste)

    ## TODO handle pagination
    return render_template(
        "all.html",
        author=author,
        session_author=session_author,
        pastes=pastes,
        user=session['user'],
    )

@app.route('/delete/', methods=['POST'])
@app.route('/delete/<uri>')
def delete(uri=None):
    session_author = session.get('author', '')

    uri = request.form.get('uri', uri)
    paste = Paste.get(uri)
    if not paste:
        abort(404)

    if request.method == 'POST':

        if paste.user != session['user']:
            abort(403)

        paste.delete()
        flash("Deleted Paste")

        return redirect(url_for('all'))

    return render_template(
        'delete.html',
        paste=paste,
        user=session['user'],
        session_author=session_author,
    )



## ERROR HANDLERS

@app.errorhandler(403)
def page_not_found(e):
    return render_template('403.html'), 403
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
@app.errorhandler(405)
def page_not_found(e):
    return render_template('405.html'), 405
