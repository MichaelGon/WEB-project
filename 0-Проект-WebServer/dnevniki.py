from add_news import AddNewsForm
from add_users import AddNewUser
from db import DB
from flask import Flask, redirect, render_template, session
from loginform import LoginForm
from news_model import NewsModel
from users_model import UsersModel

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
#инициализируем таблицу
db = DB('db.db')
NewsModel(db.get_connection()).init_table()
UsersModel(db.get_connection()).init_table()


# http://127.0.0.1:8080/login
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data
        user_model = UsersModel(db.get_connection())
        exists = user_model.exists(user_name, password)
        if (exists[0]):
            session['username'] = user_name
            session['user_id'] = exists[1]
        return redirect("/index")
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
def logout():
    session.pop('username', 0)
    session.pop('user_id', 0)
    return redirect('/index')


@app.route('/')
@app.route('/index')
def index():
    if 'username' not in session:
        usname = None
    else:
        usname=session['username']
    
    news = NewsModel(db.get_connection()).get_all()
    return render_template('index.html', username=usname, news=news)


@app.route('/add_news', methods=['GET', 'POST'])
def add_news():
    if 'username' not in session:
        return redirect('/login')
    form = AddNewsForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        nm = NewsModel(db.get_connection())
        nm.insert(title, content, session['user_id'])
        return redirect("/index")
    return render_template('add_news.html', title='Добавление новости', form=form, username=session['username'])


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    form = AddNewUser()
    if form.validate_on_submit():
        user_name = form.username.data
        pass_word = form.password.data
        um = UsersModel(db.get_connection())
        um.insert(user_name, pass_word) #проверить, что его нет
    return render_template('add_user.html', title='Добавление пользователя', form=form)
    


@app.route('/delete_news/<int:news_id>', methods=['GET'])
def delete_news(news_id):
    if 'username' not in session:
        return redirect('/login')
    nm = NewsModel(db.get_connection())
    nm.delete(news_id)
    return redirect("/index")


@app.route('/stats')
def stats():
    um = UsersModel(db.get_connection())
    users_list = um.get_all()
    nm = NewsModel(db.get_connection())
    news_list = nm.get_all()
    stats_list = []
    for item in users_list:
        hobosti = list(filter(lambda x: x == item[0],
                              map(lambda x: x[3], news_list)))
        stats_list.append([item[1], len(hobosti)])
    return render_template('stats.html', stats_list=stats_list )


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1', debug=True)
