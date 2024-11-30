from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flashcard_app.db'
db = SQLAlchemy(app)


class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f"<Module(id={self.id}, name='{self.name}')>"

@app.route('/')
def welcome_page():
    return render_template('welcome_page.html')

@app.route('/create_module')
def create_module():
    return render_template('create_module.html')

if __name__ == '__main__':
    app.run(debug=True)