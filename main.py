from flask import Flask, render_template, request, redirect, session, make_response, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from datetime import datetime
import os
from werkzeug.utils import secure_filename
app = Flask(__name__)
app.secret_key = 'my_top_secret_123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diary.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# путь к папке для сохранения файлов
UPLOAD_FOLDER = os.path.join(app.root_path, 'user_img')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
created_at = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/search')
def search():
    query = request.args.get('query', '').strip()
    if not query:
        # Если поиск пустой, можно либо перенаправить на страницу со всеми постами
        return redirect(url_for('all_cards'))
    # Поиск по заголовкам или другим полям
    cards = Card.query.filter(
        or_(
            Card.title.ilike(f'%{query}%')
        )
    ).all()
    return render_template('all_cards.html', cards=cards)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = file.filename
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(save_path)
            return 'Файл сохранен!'


class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #Заголовок
    title = db.Column(db.String(100), nullable=False)
    #Текст
    text = db.Column(db.Text, nullable=False)
    #email
    user_email = db.Column(db.String(100), nullable=False)
    #ФОТО
    user_img = db.Column(db.String(255), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return f'<Card {self.id}>'
    



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

#Запуск страницы с контентом
@app.route('/log', methods=['GET','POST'])
def login():
    error = ''
    if request.method == 'POST':
        form_login = request.form['email']
        form_password = request.form['password']
        # проверкa пользователей
        users_db = User.query.all()
        for user in users_db:
            if form_login == user.email and form_password == user.password:
                session['user_email'] = user.email
                return redirect('/index')
        else:
            error = 'Неправильно указан пользователь или пароль'
            return render_template('login.html', error=error)
     
    else:
        return render_template('login.html')




@app.route('/reg', methods=['GET','POST'])
def reg():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()

        return redirect('/')
    
    else:    
        return render_template('registration.html')
    
# свои карты
@app.route('/index')
def index():
    email = session.get('user_email')
    cards = Card.query.filter_by(user_email=email).all()
    return render_template('index.html', cards=cards)

@app.route('/')
def allcards():
    cards = Card.query.order_by(Card.created_at.desc()).all()
    return render_template('all_cards.html', cards=cards)

@app.route('/all')
def allcardslog():
    cards = Card.query.order_by(Card.created_at.desc()).all()
    return render_template('all_cards_log.html', cards=cards)

@app.route('/info')
def info():
    return render_template('info.html')

@app.route('/info_al')
def info_al():
    return render_template('info_al.html')

@app.route('/card/<int:id>')
def card(id):
    card = Card.query.get(id)

    return render_template('card.html', card=card)

@app.route('/card_al/<int:id>')
def card_al(id):
    card = Card.query.get(id)

    return render_template('card_al.html', card=card)

@app.route('/create')
def create():
    return render_template('create_card.html')

@app.route('/form_create', methods=['GET', 'POST'])
def form_create():
    if request.method == 'POST':
        title = request.form['title']
        text = request.form['text']
        file = request.files['user_img']
        if file:
            # Вставьте сюда
            filename = secure_filename(file.filename)
            static_path = os.path.join('static', 'user_img', filename)
            save_path = os.path.join(app.root_path, static_path)
            file.save(save_path)
            # сохраняем относительный путь для использования в шаблоне
            user_img_path = static_path
        else:
            error = 'Пожалуйста, выберите изображение для загрузки'
            return render_template('create_card.html', error=error)
        # далее сохраняете карточку, передавая user_img=user_img_path
        user_email = session.get('user_email')
        card = Card(title=title, text=text, user_email=user_email, user_img=user_img_path)
        db.session.add(card)
        db.session.commit()
        return redirect('/index')
    return render_template('create_card.html')


#  Курсы---------------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/courses_al')
def courses_al():
    return render_template('courses_al.html', questions=questions)

@app.route('/courses')
def courses():
    return render_template('courses.html', questions=questions)

@app.route('/submit_al', methods=['POST'])
def submit_al():
    answers = {}
    for i in range(1, 22):
        answer = request.form.get(f'question_{i}')
        answers[f'question_{i}'] = answer
    # Можно обработать ответы, например, подсчитать результаты или сохранить
    return render_template('results_al.html', answers=answers)


@app.route('/submit', methods=["POST"])
def submit():
    answers = {}
    score = 0
    total_questions = len(correct_answers)
    for key in correct_answers.keys():
        user_answer = request.form.get(key)
        answers[key] = user_answer
        if user_answer and user_answer.strip().lower() == correct_answers[key].lower():
            score += 1
    return render_template('results.html', answers=answers, score=score, total=total_questions)


@app.route('/submit_al', methods=["POST"])
def submit_al1():
    answers = {}
    score = 0
    total_questions = len(correct_answers)
    for key in correct_answers.keys():
        user_answer = request.form.get(key)
        answers[key] = user_answer
        if user_answer and user_answer.strip().lower() == correct_answers[key].lower():
            score += 1
    return render_template('results_al.html', answers=answers, score=score, total=total_questions)


# списки---------------------------------------------------------------------------------------------------------------------------------------------------------------
questions = [
# Вопрос - 1
    "<p class='test-title'>Что вызывает глобальное потепление?"\
        "<p class='test-text'>A) Рост населения мира</p>"\
            "<p class='test-text'>B) Увеличение концентрации парниковых газов в атмосфере</p>"\
                "<p class='test-text'>C) Повышение уровня воды в океанах</p>"\
                "<p class='test-text'>D) Распространение вредных бактерий</p></p>",
# Вопрос - 2
    "<p class='test-title'>Какое из следующих последствий не связано напрямую с глобальным потеплением?</p>"\
        "<p class='test-text'>А) Расширение ареалов переносчиков болезней</p>"\
            "<p class='test-text'>B) Повышение уровня моря</p>"\
                "<p class='test-text'>C) Увеличение числа террористических актов</p>"\
                "<p class='test-text'>D) Распространение инфекционных заболеваний</p>",
# Вопрос - 3
    "<p class='test-title'>Какие меры рекомендуется предпринимать для снижения угроз, связанных с глобальным потеплением?</p>"\
        "<p class='test-text'>a) Повышение добычи угля и нефти</p>"\
            "<p class='test-text'>b) Сокращение выбросов парниковых газов и переход на возобновляемые источники энергии</p>"\
                "<p class='test-text'>c) Увеличение использования пластика</p>"\
                "<p class='test-text'>d) Ограничение использования возобновляемых источников энергии</p>",
# Вопрос - 4
    "<p class='test-title'>Какие категории людей наиболее уязвимы к последствиям экстремальных погодных условий, вызванных глобальным потеплением?</p>"\
        "<p class='test-text'>a) Люди преклонного возраста, дети и жители бедных районов</p>"\
            "<p class='test-text'>b) Молодые, здоровые спортсмены</p>"\
                "<p class='test-text'>c) Люди, живущие в пустынях без воды</p>"\
                "<p class='test-text'>d) Все пользователи интернета</p>",
# Вопрос - 5
    "<p class='test-title'>Что происходит с ледниками из-за глобального потепления?</p>"\
        "<p class='test-text'>a) Они увеличиваются в размерах</p>"\
            "<p class='test-text'>b) Они постепенно тают и сокращаются</p>"\
                "<p class='test-text'>c) Они превращаются в горные хребты</p>"\
                "<p class='test-text'>d) Они остаются без изменений</p>",
# Вопрос - 6
    "<p class='test-title'>Как изменение климата способствует распространению болезней?</p>"\
        "<p class='test-text'>a) Снижает количество переносчиков болезней</p>"\
            "<p class='test-text'>b) Обезвоживает организм человека</p>"\
                "<p class='test-text'>c) Расширяет ареалы переносчиков болезней, таких как комары</p>"\
                "<p class='test-text'>d) Заменяет вирусы бактериями</p>",
# Вопрос - 7
    "<p class='test-title'>Что увеличивается в результате повышения температуры и изменяющихся условий атмосферы?</p>"\
        "<p class='test-text'> a) Концентрация аллергенов и загрязняющих веществ </p>"\
            "<p class='test-text'> b) Способность растений к фотосинтезу </p>"\
                "<p class='test-text'> c) Уровень кислорода в воздухе </p>"\
                "<p class='test-text'> d) Рост лесных массивов </p>",
# Вопрос - 8
    "<p class='test-title'> Каким образом изменение климата влияет на сельское хозяйство? </p>"\
        "<p class='test-text'> a) Оно увеличивает урожайность во всех регионах </p>"\
            "<p class='test-text'> b) Оно негативно сказывается на урожаях, вызывая голод и недоедание </p>"\
                "<p class='test-text'> c) Оно не влияет на сельское хозяйство </p>"\
                "<p class='test-text'> d) Оно приводит к исчезновению всех сельскохозяйственных культур </p>",
# Вопрос - 9
    "<p class='test-title'> Какие экстремальные погодные явления увеличиваются в результате глобального потепления? </p>"\
        "<p class='test-text'> a) Туман и холодные ветры </p>"\
            "<p class='test-text'> b) Штормы, наводнения и засухи </p>"\
                "<p class='test-text'> c) Землетрясения и цунами </p>"\
                "<p class='test-text'> d) Лиственный сезон и снежные бури </p>",
# Вопрос - 10
    "<p class='test-title'> Почему изменения климата могут вызывать психологические проблемы? </p>"\
        "<p class='test-text'> a) Из-за появления новых видов животных </p>"\
            "<p class='test-text'> b) Из-за стихийных бедствий и связанных с ними стрессов и тревог </p>"\
                "<p class='test-text'> c) Потому что все люди начинают бояться дождя </p>"\
                "<p class='test-text'> d) Потому что растет уровень интеллекта у людей </p>",
# Вопрос - 11
    "<p class='test-title'> Чем вызвано увеличение количества выбросов парниковых газов? </p>"\
        "<p class='test-text'> a) Рост использования возобновляемых источников энергии </p>"\
            "<p class='test-text'> b) Антропогенная деятельность, такая как сжигание угля и нефти </p>"\
                "<p class='test-text'> c) Увеличение численности диких животных </p>"\
                "<p class='test-text'> d) Появление новых видов растений </p>",
# Вопрос - 12
    "<p class='test-title'> Что является основной причиной повышения уровня моря? </p>"\
        "<p class='test-text'> a) Расплавление ледников и таяние полярных льдов </p>"\
            "<p class='test-text'> b) Размножение водных организмов </p>"\
                "<p class='test-text'> c) Увеличение осадков на суше </p>"\
                "<p class='test-text'> d) Усиление ветров </p>",
# Вопрос - 13
    "<p class='test-title'> Что важно делать для повышения готовности обществ к последствиям глобального потепления? </p>"\
        "<p class='test-text'> a) Сокращать инвестиции в здравоохранение и экологию </p>"\
            "<p class='test-text'> b) Развивать системы экстренного реагирования и укреплять медицинские учреждения </p>"\
                "<p class='test-text'> c) Игнорировать изменения климата </p>"\
                "<p class='test-text'> d) Уменьшать число школ и больниц </p>",
# Вопрос - 14
    "<p class='test-title'> Какое из следующих утверждений верно? </p>"\
        "<p class='test-text'> a) Глобальное потепление не влияет на здоровье человека </p>"\
            "<p class='test-text'> b) Глобальное потепление способствует улучшению условий жизни </p>"\
                "<p class='test-text'> c) Глобальное потепление увеличивает риски для здоровья и безопасности людей </p>"\
                "<p class='test-text'> d) Глобальное потепление полностью предотвращено </p>",
# Вопрос - 15
    "<p class='test-title'> Что происходит с уровнем земли в прибрежных районах из-за глобального потепления? </p>"\
        "<p class='test-text'> a) Он остается постоянным </p>"\
            "<p class='test-text'> b) Он опускается до уровня моря </p>"\
                "<p class='test-text'> c) Он повышается из-за подъема уровня воды </p>"\
                "<p class='test-text'> d) Он опускается из-за дisalппения </p>",
# Вопрос - 16
    "<p class='test-title'> Какая из следующих мер НЕ способствует борьбе с глобальным потеплением? </p>"\
        "<p class='test-text'> a) Переключение на солнечную и ветровую энергию </p>"\
            "<p class='test-text'> b) Использование энергоэффективных технологий </p>"\
                "<p class='test-text'> c) Увеличение добычи нефти и угля </p>"\
                "<p class='test-text'> d) Снижение выбросов парниковых газов </p>",
# Вопрос - 17
    "<p class='test-title'> Почему важно понимать и бороться с глобальным потеплением? </p>"\
        "<p class='test-text'> a) Потому что оно не имеет никакого отношения к здоровью человека </p>"\
            "<p class='test-text'> b) Потому что оно способствует развитию новых технологий </p>"\
                "<p class='test-text'> c) Потому что оно угрожает жизни и здоровью людей и требует совместных усилий </p>"\
                "<p class='test-text'> d) Потому что оно уменьшает глобальное население </p>",
# Вопрос - 18
    "<p class='test-title'> Как изменение климата влияет на рост и распространение вредных организмов? </p>"\
        "<p class='test-text'> a) Оно замедляет их развитие и распространение </p>"\
            "<p class='test-text'> b) Оно не оказывает никакого влияния </p>"\
                "<p class='test-text'> c) Оно способствует росту и расширению ареалов вредных организмов, таких как гельминты и бактерии </p>"\
                "<p class='test-text'> d) Оно уничтожает всех вредных организмов </p>",
# Вопрос - 19
    "<p class='test-title'> Что способствует увеличению риска возникновения стихийных бедствий? </p>"\
        "<p class='test-text'> a) Уменьшение выбросов парниковых газов </p>"\
            "<p class='test-text'> b) Глобальное похолодание </p>"\
                "<p class='test-text'> c) Глобальное потепление и изменение климата </p>"\
                "<p class='test-text'> d) Стабильный и предсказуемый климат </p>",
# Вопрос - 20
    "<p class='test-title'> Какие социальные группы наиболее уязвимы к последствиям климатических изменений? </p>"\
        "<p class='test-text'> a) Молодое и здоровое население </p>"\
            "<p class='test-text'> b) Люди с высокими доходами и хорошим доступом к ресурсам </p>"\
                "<p class='test-text'> c) Люди преклонного возраста, дети и жители бедных районов </p>"\
                "<p class='test-text'> d) Все люди одинаково уязвимы </p>",
# Вопрос - 21
    "<p class='test-title'> Почему важно снижать выбросы парниковых газов? </p>"\
        "<p class='test-text'> a) Чтобы ускорить глобальное потепление </p>"\
            "<p class='test-text'> b) Чтобы уменьшить угрозу изменения климата и угрозы для жизни людей и окружающей среды </p>"\
                "<p class='test-text'> c) Для увеличения промышленного производства без ограничений </p>"\
                "<p class='test-text'> d) Потому что это не влияет на климат </p>",
]

correct_answers = {
    "Вопрос: 1": "b",
    "Вопрос: 2": "c",
    "Вопрос: 3": "b",
    "Вопрос: 4": "a",
    "Вопрос: 5": "b",
    "Вопрос: 6": "c",
    "Вопрос: 7": "a",
    "Вопрос: 8": "b",
    "Вопрос: 9": "b",
    "Вопрос: 10": "b",
    "Вопрос: 11": "b",
    "Вопрос: 12": "a",
    "Вопрос: 13": "b",
    "Вопрос: 14": "c",
    "Вопрос: 15": "c",
    "Вопрос: 16": "c",
    "Вопрос: 16": "c",
    "Вопрос: 18": "c",
    "Вопрос: 19": "c",
    "Вопрос: 20": "c",
    "Вопрос: 21": "b",



}





if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
