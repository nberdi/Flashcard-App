from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from datetime import timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flashcard_app.db'    # database connection
app.config['SECRET_KEY'] = secrets.token_hex(16)    # generate a random secret key
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False    # disable track modifications
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'welcome_page'   # redirect to welcome page if not logged in


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    modules = db.relationship('Module', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text(), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    flashcards = db.relationship('FlashcardApp', backref='parent_module', cascade='all, delete', lazy=True)

    def __repr__(self):
        return f"<Module(id={self.id}, name='{self.name}')>"


class FlashcardApp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.String(500), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=False)
    module = db.relationship('Module', lazy=True)

    def __repr__(self):
        return f"<Flashcard(id={self.id})>"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('my_modules'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if len(username) < 5:
            flash('Username must be at least 5 characters long')
            return redirect(url_for('register'))

        if len(password) < 8:
            flash('Password must be at least 8 characters long')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('register'))

        # check for existing username
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))

        # create new user
        try:
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please log in')
            return redirect(url_for('welcome_page'))
        except Exception as e:
            db.session.rollback()   # rollback the session in case of error
            flash('Error during registration. Please try again')
            return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/', methods=['GET', 'POST'])
def welcome_page():        
    if current_user.is_authenticated:
        return redirect(url_for('my_modules'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            next_page = request.args.get('next')
            login_user(user)
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('my_modules'))
        flash('Invalid username or password')        
    return render_template('welcome_page.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('welcome_page'))

@app.before_request
def before_request():
    if current_user.is_authenticated:
        session.permanent = True    # make the session permanent
        app.permanent_session_lifetime = timedelta(minutes=60)   # logout after 60 minutes of inactivity

with app.app_context():
    db.create_all()

@app.route('/create_module', methods=['POST', 'GET'])
@login_required
def create_module():
    if request.method == 'POST':
        module_name = request.form['module_name']
        module_name_slug = module_name.replace(" ", "-")    # replace spaces with hyphens
        module_description = request.form['module_description']
        new_module = Module(name=module_name_slug, description=module_description, user_id=current_user.id)
        try:
            db.session.add(new_module)
            db.session.commit()
            return redirect(url_for('flashcard_module', name=new_module.name, id=new_module.id))
        except:
            return "There was an issue adding your module"
    else:
        return render_template('create_module.html')

@app.route('/flashcard_module/<string:name>/<int:id>')
@login_required
def flashcard_module(name, id):
    module = Module.query.filter_by(id=id, name=name, user_id=current_user.id).first_or_404()
    flashcards = FlashcardApp.query.filter_by(module_id=module.id).all()    # to display flashcards
    return render_template('flashcard_module.html', module=module, flashcards=flashcards)

@app.route('/add_flashcards/<int:module_id>', methods=['POST'])
@login_required
def add_flashcards(module_id):
    module = Module.query.filter_by(id=module_id, user_id=current_user.id).first_or_404()
    if request.method == 'POST':
        question = request.form['question']
        answer = request.form['answer']
        new_flashcard = FlashcardApp(question=question, answer=answer, module_id=module.id)

        try:
            db.session.add(new_flashcard)
            db.session.commit()
            return redirect(url_for('flashcard_module', name=module.name, id=module.id))
        except Exception as e:
            return "There was an issue adding your question"
    else:
        return render_template('flashcard_module.html')

@app.route('/delete/<int:id>', methods=['GET'])
@login_required
def delete(id):
    flashcard_to_delete = FlashcardApp.query.get_or_404(id)
    module = Module.query.get_or_404(flashcard_to_delete.module_id)
    try:
        db.session.delete(flashcard_to_delete)
        db.session.commit()
        return redirect(url_for('flashcard_module', name=module.name, id=module.id))
    except:
        return "There was an issue deleting your flashcard"

@app.route('/edit_flashcard/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_flashcard(id):
    card = FlashcardApp.query.get_or_404(id)
    module = Module.query.get_or_404(card.module_id)
    if request.method == 'POST':
        card.question = request.form['question']
        card.answer = request.form['answer']
        try:
            db.session.commit()
            return redirect(url_for('flashcard_module', name=module.name, id=module.id))
        except:
            return "There was an issue updating your flashcard"
    else:
        return render_template('edit_flashcard.html', card=card)

@app.route('/my_modules')
@login_required
def my_modules():
    modules = Module.query.filter_by(user_id=current_user.id).all()
    return render_template('my_modules.html', modules=modules)

@app.route('/delete_module/<int:id>',  methods=['GET', 'POST'])
@login_required
def delete_module(id):
    module_to_delete = Module.query.get_or_404(id)
    try:
        db.session.delete(module_to_delete)
        db.session.commit()
        return redirect('/my_modules')
    except:
        return "There was an issue deleting your module"

@app.route('/edit_module/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_module(id):
    pass
    module_to_edit = Module.query.get_or_404(id)
    if request.method == 'POST':
        module_to_edit.name = request.form['module_name'].replace(' ', '-').lower()
        module_to_edit.description = request.form['module_description'] 
        try:
            db.session.commit()
            return redirect('/my_modules')
        except Exception as e:
            return f"There was an issue updating the module: {e}"
    else:
        return render_template('edit_module.html', module=module_to_edit)


if __name__ == '__main__':
    app.run()
