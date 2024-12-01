from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flashcard_app.db'
db = SQLAlchemy(app)


class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
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
    

with app.app_context():
    db.create_all()

@app.route('/')
def welcome_page():
    return render_template('welcome_page.html')

@app.route('/create_module', methods=['POST', 'GET'])
def create_module():
    if request.method == 'POST':
        module_name = request.form['module_name']
        module_name_slug = module_name.replace(" ", "-")    # replace spaces with hyphens
        module_description = request.form['module_description']
        new_module = Module(name=module_name_slug, description=module_description)
        try:
            db.session.add(new_module)
            db.session.commit()
            return redirect(url_for('flashcard_module', name=new_module.name, id=new_module.id))
        except:
            return "There was an issue adding your module"
    else:
        return render_template('create_module.html')

@app.route('/flashcard_module/<string:name>/<int:id>')
def flashcard_module(name, id):
    module = Module.query.filter_by(id=id, name=name).first_or_404()
    if module is None:
        return "Module not found", 404  
    flashcards = FlashcardApp.query.filter_by(module_id=module.id).all()    # to display flashcards
    return render_template('flashcard_module.html', module=module, flashcards=flashcards)

@app.route('/add_flashcards/<int:module_id>', methods=['POST'])
def add_flashcards(module_id):
    # fetch a record based on its primary key.
    module = Module.query.get_or_404(module_id)
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
def my_modules():
    modules = Module.query.all() 
    return render_template('my_modules.html', modules=modules)

if __name__ == '__main__':
    app.run(debug=True)