from datetime import datetime
from flask_login import UserMixin
from __main__ import db, login_manager

chat_user = db.Table('chat_user',
                     db.Column('chat_id', db.Integer, db.ForeignKey('chats.id')),
                     db.Column('user_id', db.Integer, db.ForeignKey('users.id'))
                     )


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    messages = db.relationship('Message', lazy=True, backref='user')
    chats = db.relationship('Chat', secondary=chat_user,
                            backref=db.backref('users'))

    def __repr__(self):
        return f"<User {self.username} {self.email}>"


class Chat(db.Model):
    __tablename__ = 'chats'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    messages = db.relationship('Message', lazy=True, backref='chat')

    def __repr__(self):
        return f"<Chat {self.name}>"


class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    time_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    chat_id = db.Column(db.Integer, db.ForeignKey('chats.id'), nullable=False)

    def __repr__(self):
        return f"<Message {self.content} {self.time_date}>"
