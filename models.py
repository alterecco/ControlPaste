from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relation, backref
from werkzeug import cached_property

from ControlPaste.database import db
from ControlPaste.lib import hilite
from ControlPaste.lib.urigen import encode_uri, decode_uri

class Paste(db.Base):
    __tablename__ = 'pastes'

    id =        Column(Integer, primary_key=True)
    date =      Column(DateTime)
    uri =       Column(String(10), unique=True)

    code =      Column(Text)
    language =  Column(String(30), default='text')
    user =      Column(String(40))

    author =    Column(String(255), nullable=True)
    title =     Column(String(255), nullable=True)
    parent_id = Column(Integer, ForeignKey('pastes.id'), nullable=True)
    private =   Column(Boolean, nullable=True)

    children =  relation('Paste', cascade='all', primaryjoin=parent_id == id,
                         backref=backref('parent', remote_side=[id]))

    def __init__(self, code, language, user, title=None, author=None,
                 parent=None, private=False):

        self.date = datetime.now()

        self.code = u'\n'.join(code.splitlines())
        if hilite.check(language):
            self.language = language
        self.user = user

        self.author = author
        self.title = title
        if isinstance(parent, Paste):
            self.parent = parent
        else:
            self.parent_id = parent
        self.private = private

    @cached_property
    def highlighted(self):
        return hilite.parse(self.code, self.language, True)

    @cached_property
    def preview(self, lines=5):
        code = self.code.strip()
        code = code.split('\n')[:5]
        code = '\n'.join(code)
        return hilite.parse(code, self.language)

    @property
    def human_date(self):
        return self.date.strftime("%a %d %B, %H:%M:%S")

    @cached_property
    def human_language(self):
        return hilite.name(self.language)

    @staticmethod
    def get(uri):
        ## decode the uri
        try:
            id = decode_uri(uri)
        except ValueError:
            return False
        return Paste.query.filter(Paste.id == id).first()

    @staticmethod
    def get_all(author=None):
        if author:
            query = Paste.query.filter(Paste.author == author)
        else:
            query = Paste.query.filter(Paste.private == False)

        return query.order_by(Paste.date.desc())

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def save(self):
        db.session.add(self)
        db.session.flush()

        ## generate the uri from the id
        self.uri = encode_uri(self.id, 5)

        db.session.commit()







#import os
#import sqlite3
#import time
#from contextlib import closing
#from flask import g
#
#from paste import app
#
#DATABASE = os.getcwd() + '/pastes.db'
#print(DATABASE)
#
#def init():
#    with closing(connect()) as db:
#        with app.open_resource('schema.sql') as f:
#            db.cursor().executescript(f.read())
#
#        db.commit()
#
#def connect():
#    conn = sqlite3.connect(DATABASE)
#    conn.row_factory = sqlite3.Row
#    return conn
#
#@app.before_request
#def before_request():
#    g.db = connect()
#    try:
#        g.db.execute("SELECT * FROM pastes LIMIT 1");
#    except sqlite3.OperationalError:
#        init()
#
#@app.after_request
#def after_request(response):
#    g.db.close()
#    return response
#
#class Paste():
#
#    code = u''
#    date = int(time.time())
#    language = 'text'
#
#    title = u''
#    parent = None
#    private = False
#
#    uri = None
#    user = None
#
#    def __init__(self, code, language, title=None, private=False, parent=None,
#                 user=None):
#        self.code = u'\n'.join(code.splitlines())
#
#        if check_lang(language):
#            self.language = language
#
#        if title:
#            self.title = title
#
#        self.private = private
#        self.parent = parent
#        self.user = user
#
#    @staticmethod
#    def get(ident):
#        """Return paste for ident. Private pastes must be fetched
#        with their private id, public with their normal id"""
#        c = g.db.execute("SELECT * FROM pastes WHERE id=:ident", {"ident": ident})
#        res = c.fetchone()
#        if res:
#            paste = Paste(res['code'], res['language'], res['title'],
#                          res['private'], res['parent'], res['user'])
#            paste.uri = res['uri']
#            # paste.date = res['date']
#            return paste
#
#        return False
#
#    @staticmethod
#    def get_all():
#        c = g.db.execute("SELECT * FROM pastes WHERE private = 0 ORDER BY date DESC")
#        res = c.fetchall()
#        if res:
#            pastes = []
#            for r in res:
#                paste = Paste(r['code'], r['language'], r['title'],
#                              r['private'], r['parent'], r['user'])
#                paste.uri = r['uri']
#                paste.date = r['date']
#                pastes.append(paste)
#            return pastes
#
#        return False
#
#    def save(self):
#
#        columns = [u'code', u'date', u'language', u'user']
#        placeholder = [u'?', u'?', u'?', u'?']
#        values = [self.code, self.date, self.language, self.user]
#
#        ## only insert the rows that have values
#        if self.title:
#            columns.append(u'title')
#            placeholder.append(u'?')
#            values.append(self.title)
#
#        if self.parent:
#            columns.append(u'parent')
#            placeholder.append(u'?')
#            values.append(self.parent)
#
#        if self.private:
#            columns.append(u'parent')
#            placeholder.append(u'?')
#            values.append(self.parent)
#
#        values = tuple(values)
#        ## insert the row
#        c = g.db.execute(u'INSERT INTO pastes ({columns}) values ({values})'.format(
#            columns=','.join(columns),
#            values=','.join(placeholder)
#        ), values)
#
#        ## create a nice uri
#        ident = c.lastrowid
#
#        if not ident:
#            return False
#
#        self.uri = encode_url(ident, 5)
#
#        ## update the row with the uri
#        c = g.db.execute(u'UPDATE pastes set uri=? where id=?', (self.uri, ident))
#
#        g.db.commit()
#
#        return self.uri
#
#    def hilited(self):
#        return hilite(self.code, self.language)
#
#    def human_date(self):
#        dt = datetime.fromtimestamp(self.date)
#        return dt.strftime("%a %d %B, %H:%M:%S")
