
from flask_login import UserMixin, AnonymousUserMixin,url_for
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from . import db, login_manager
from datetime import datetime
from flask import current_app, request, url_for



class PassProjectContainerInfo(db.Model):
    __tablename__ = 'pass_project_container_info'
    id = db.Column(db.Integer, primary_key=True)
    app_id = db.Column(db.Integer)
    micro_service_id = db.Column(db.Integer)
    container_name = db.Column(db.String(64))
    container_ip = db.Column(db.String(64))
    host_ip = db.Column(db.String(64))
    hostname = db.Column(db.String(64))
    port = db.Column(db.String(64))
    status = db.Column(db.Integer)
    update_time = db.Column(db.DateTime(), default=datetime.utcnow)


    def __repr__(self):
        return '<PassProjectContainerInfo %r>' % self.container_name



class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    ename = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    phone = db.Column(db.String(64))
    email = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))

    def __repr__(self):
        return '<User %r>' % self.username

    def to_json(self):
        json_user = {
            'id': self.id,
            'username': self.username
            #'password': self.password,
            #'sex': self.sex
        }
        return json_user

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word())

            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False