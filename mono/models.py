from sqlalchemy.orm import synonym
from werkzeug.security import check_password_hash, generate_password_hash

from mono import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.INTEGER, primary_key=True)
    name = db.Column(db.CHAR, unique=True, nullable=False)
    _password = db.Column('password', db.CHAR, nullable=False)

    item = db.relationship('Item', backref=db.backref('users', lazy=True))

    def _get_password(self):
        return self._password

    def _set_password(self, password):
        if password:
            password = password.strip()
        self._password = generate_password_hash(password)
    password_descriptor = property(_get_password, _set_password)
    password = synonym('_password', descriptor=password_descriptor)

    def check_password(self, password):
        password = password.strip()
        if not password:
            return False
        return check_password_hash(self.password, password)

    @classmethod
    def authenticate(cls, query, name, password):
        user = query(cls).filter(cls.name == name).first()
        if user is None:
            return None, False
        return user, user.check_password(password)

    def __repr__(self):
        return '<Users id={id} name={name!r}>'.format(id=self.id, name=self.name)


class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.INTEGER, db.ForeignKey('users.id'))
    name = db.Column(db.CHAR)
    description = db.Column(db.VARCHAR)
    url = db.Column(db.CHAR)
    category = db.Column(db.CHAR)
    status = db.Column(db.CHAR)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return '<Items id={id} name={name!r}>'.format(id=self.id, name=self.name)


def init():
    db.create_all()