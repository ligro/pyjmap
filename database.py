from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects import postgresql
import sqlalchemy

db = SQLAlchemy()

NoResultFound = sqlalchemy.orm.exc.NoResultFound

def commit():
    try:
        db.session.commit()
    except DatabaseError as e:
        db.session.rollback()
        current_app.logger.warning(e)


class Model():
    def setFromArray(self, data):
        # TODO limit to known column
        for k in data:
            if k in self.__table__.columns.keys():
                setattr(self, k, data[k])

    def save(self):
        db.session.add(self)

    def toDict(self, found=None):
        if found is None:
            found = []
        mapper = class_mapper(self.__class__)
        columns = [column.key for column in mapper.columns]
        get_key_value = lambda c: (c, getattr(self, c).isoformat()) if isinstance(getattr(self, c), datetime.datetime) else (c, getattr(self, c))
        out = dict(list(map(get_key_value, columns)))
        for name, relation in list(mapper.relationships.items()):
            if relation not in found:
                found.append(relation)
                related_obj = getattr(self, name)
                if related_obj is not None:
                    if relation.uselist:
                        out[name] = [child.toDict(found) for child in related_obj]
                    else:
                        out[name] = related_obj.toDict(found)
        return out


class User(db.Model, Model):
    # TODO auto increment
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))
    modseq = db.Column(db.BigInteger)

    class BadPassword(Exception):
        pass

    def __init__(self):
        self.modseq = 0

    def getNextState(self):
        self.modseq += 1
        self.save()
        return self.modseq

    def setPassword(self, password):
        import random

        algo = 'sha1'
        salt = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz', 15))
        hsh = self._enc(algo, salt, password)
        self.password = '%s$%s$%s' % (algo, salt, hsh)

    def checkPwd(self, raw_pwd):
        try:
            algo, salt, hsh = self.password.split('$')
        except:
            raise BadPassword

        if hsh != self._enc(algo, salt, raw_pwd):
            raise BadPassword

    def _enc(self, algo, salt, pwd):
        import hashlib

        hl = hashlib.new(algo)
        hl.update(bytes('{0}{1}'.format(salt, pwd), 'utf-8'))
        return hl.hexdigest()


class Device(db.Model, Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')
    name = db.Column(db.String(80))
    clientName = db.Column(db.String(80))
    clientVersion = db.Column(db.String(80))
    accessToken = db.Column(db.String(80))

    def getByAccessToken(accessToken):
        return Device.query.filter_by(accessToken=accessToken).one()


