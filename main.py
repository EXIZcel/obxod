import os.path
from flask import Flask, render_template, redirect
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from werkzeug.utils import secure_filename

from data.articles import Article
from data.db_session import global_init, create_session
from data.users import User
from forms.edit_profile import EditProfileForm
from forms.login import LoginForm
from forms.register import RegisterForm


app = Flask(__name__)
app.config['SECRET_KEY'] = 'fdsafs'
chat_history = {}
login_manager = LoginManager()
login_manager.init_app(app)

UPLOAD_FOLDER = os.getcwd() + '\\static\\img'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
DEFAULT_IMAGE = 'default_image.jpg'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_HOSTS = ['*']


@app.route('/profile/<int:id>', methods=['GET', 'POST'])
def profile(id):
        #form = UploadImageForm()
        #if form.is_submitted():
         #   filename = secure_filename(form.file.data.filename)
          #  form.file.data.save(UPLOAD_FOLDER + '/' + filename)
           # sess = create_session()
            #user = sess.query(User).filter(User.id == id).first()
            #user.image = UPLOAD_FOLDER + '/' + filename
            #sess.merge(user)
            #return redirect(f'/profile/{id}')


        sess = create_session()
        user = sess.query(User).filter(User.id == id).first()
        context = {'title': 'Профиль', 'user': user, 'default_user_avatar': DEFAULT_IMAGE}
        #if current_user == user:
         #   context['form'] = UploadImageForm()
        return render_template('profile.html', **context)


@app.route('/f')
def index():
    sess = create_session()

    context = {'title': 'Главная', 'users': sess.query(User).all(),
               'default_user_avatar': DEFAULT_IMAGE}
    return render_template('index.html', **context)

@app.route('/')
def ind():
    return render_template('test2.html', title='Главная')

@app.route('/page')
def page():
    return render_template('page.html')

@app.route('/chat')
def chat():
    return render_template('chat.html', title='чат')

@app.route('/about')
def about():
    return render_template('about.html', title='О сайте')


@app.route('/delete_user/<int:id>', methods=['POST'])
def delete_user(id):
    sess = create_session()
    user = sess.query(User).filter(User.id == id).first()
    sess.delete(user)
    sess.commit()
    return redirect('/')



@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        sess = create_session()
        user = sess.query(User).filter(email == User.email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect('/')
        else:
            return render_template('login.html', form=form, message='Неверный Логин или Пароль')
    return render_template('login.html', form=form, title='Авторизация')



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

@app.route('/test')
def test():
    return render_template('test.html', title='Команда')


@app.route('/pred')
def pred():
    return render_template('pred.html', title='Предметы')

@app.route('/test2')
def test2():
    return render_template('test2.html', title='fds')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password2.data:
            return render_template('register.html', form=form, message='Пароль не совпадают', title='Регистрация')
        sess = create_session()
        if sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', form=form, message='Такой пользователь уже есть', title='Регистрация')
        user = User(email=form.email.data, name=form.name.data)
        user.set_password(form.password.data)
        sess.add(user)
        sess.commit()
        return redirect('/login')
    return render_template('register.html', form=form, title='Регистрация')


@app.route('/edit_profile', methods=['POST', 'GET'])
@login_required
def edit_profile():
    sess = create_session()
    user = sess.query(User).get(current_user.id)
    form = EditProfileForm()
    form.name.data = user.name
    if form.validate_on_submit():
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            form.image.data.save(UPLOAD_FOLDER + filename)
            user.image = filename
        user.name = form.name.data
        user.about = form.about.data
        sess.merge(user)
        sess.commit()
        return redirect(f'/profile/{current_user.id}')
    form.name.data = user.name
    form.about.data = user.about
    return render_template('edit_profile.html', form=form, title='Редактирование')


@app.route('/rules')
@login_required
def rule():
    return render_template('rules.html',title='Правила')

@app.route('/blog')
@login_required
def blog():
    return render_template('blog.html')


@login_manager.user_loader
def load_user(user_id):
    return create_session().query(User).get(user_id)


global_init('db/blogs.db')
app.run()

