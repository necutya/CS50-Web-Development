from flask import Flask, render_template, redirect, request, session, url_for, make_response, flash
from flask_session import Session
from flask_socketio import emit, SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from forms import LoginForm, RegisterForm, NewChatForm, ConnectToChatForm
import os


# Create flask app
app = Flask(__name__)


# Create bcrypt
bcrypt = Bcrypt()

# Configure app
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = f'postgresql+psycopg2://{os.getenv("PSQL_USERNAME")}:' \
                                        f'{os.getenv("PSQL_PASSWORD")}@localhost/flask_messenger'


# Create a db variable
db = SQLAlchemy(app)

# Create login manager
login_manager = LoginManager(app)
login_manager.login_view = "login"

from models import User, Chat, Message

Session(app)
soketio = SocketIO(app)


@app.route("/", methods=["GET", "POST"])
@app.route("/register", methods=["GET", "POST"])
def register():
    """
    User register
    """
    form = RegisterForm()
    if request.method == "POST":
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data)
            user = User(username=form.username.data,
                        email=form.email.data, password=hashed_password.decode("utf-8"))
            db.session.add(user)
            db.session.commit()
            flash("You have been successfully register", 'success')
            return redirect(url_for('login'))
    return render_template("register.html", title='Register', form=form)



@app.route("/login", methods=["GET", "POST"])
def login():
    """
    User login
    """
    form = LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            username = form.username.data
            user = db.session.query(User).filter_by(username=username).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                flash("You have been successfully login", 'success')
                login_user(user, remember=form.remember_me)
                return redirect(url_for('main'))
            flash("Incorrect email or password", 'failed')
            return redirect(url_for('login'))
    return render_template("index.html", title='Log in', form=form)


@app.route("/logout")
def logout():
    """
    User logout
    """
    logout_user()
    # resp.set_cookie('name', session['username'])
    resp = make_response(redirect(url_for('login')))
    return resp


@app.route("/main", methods=["GET", "POST"])
@login_required
def main():
    """
    authentication option providing by Flask
    :return: Response object
    """
    if request.method == "POST":
        if request.form.get('create') == "Create":
            return redirect('create')
    # chats = db.session.query(Chat).all()
    chats = current_user.chats
    resp = make_response(render_template('main.html', title='Chatrooms',
                                         channels=chats))
    return resp


"""
Previous variant with self realization of authentication verification option 
"""
# @app.route("/main", methods=["GET", "POST"])
# def main():
#     if not session.get('username'):
#         return redirect('login')
#     if request.method == "POST":
#         if request.form.get('create') == "Create":
#             return redirect('create')
#         if request.form.get('logout') == "Log out":
#             return redirect('logout')
#     chats = db.session.query(Chat).all()
#     resp = make_response(render_template('main.html', name=session['username'], title='Chatroom',
#                                          channels=chats))
#     resp.set_cookie('name', session['username'])
#     return resp



@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    """
    Create a new chat"""
    form = NewChatForm()
    if request.method =="POST":
        if form.validate_on_submit():
            new_chat = Chat(name=form.name.data)
            db.session.add(new_chat)
            current_user.chats.append(new_chat)
            db.session.commit()
        return redirect(url_for('main'))
    return render_template('create.html', form=form)



@app.route("/show_all")
@login_required
def show_all():
    """
    Show all chats
    """
    form = ConnectToChatForm()
    chats = db.session.query(Chat).all()
    return render_template('all_chats.html', form=form, chats=chats)



@app.route("/connect/<int:chat_id>", methods=["POST"])
@login_required
def connect(chat_id):
    """
    Connect to chat
    """
    chat = db.session.query(Chat).get_or_404(chat_id)
    if chat in current_user.chats:
        flash(f"You have been joined to this chat early'{chat.name}'", 'failed')
        return redirect(url_for('main'))
    current_user.chats.append(chat)
    db.session.commit()
    flash(f"You have been successfully joined to '{chat.name}'", 'success')
    return redirect(url_for('main'))


@soketio.on("send_message")
@login_required
def send(data):
    """
    Send message using web-sockets
    :param data:
    :return:
    """
    content = data['content']
    chat = db.session.query(Chat).get(int(data['chat_id']))
    message = Message(content=content, user_id=current_user.id, chat_id=chat.id)
    db.session.add(message)
    db.session.commit()

    emit("send_message", {'content': message.content, "name": current_user.username,
                          'time': message.time_date.strftime("%I %M %p "),
                          "name": message.user.username,
                          "remember_token": request.cookies.get('remember_token')}, broadcast=True)


@soketio.on("show_messages")
@login_required
def show(data):
    """
    return all messages using web-sockets
    :param data:
    :return:
    """

    chat = db.session.query(Chat).get(int(data['channel_id']))
    messages = list()
    for message in chat.messages:
        messages.append({"content": message.content, "time": message.time_date.strftime("%I %M %p "),
                         'message_username': message.user.username})

    emit("chat_messages", {'messages': messages, "name": current_user.username})




if __name__ == '__main__':
    soketio.run(app, debug=True)
