import os
from flask import Flask, render_template, redirect, url_for,request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField,validators
from wtforms.widgets import TextArea
from werkzeug.datastructures import MultiDict
import datetime


app= Flask(__name__)
app.config['SECRET_KEY'] = 'mykey'

## DATABASE
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+ os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Migrate(app,db)

######## Model #############
class Note(db.Model):
    __tablename__ = 'notes'

    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.Text)
    description = db.Column(db.Text)
    date = db.Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, title, description):
        self.title = title
        self.description = description
    def __repr__(self):
        return f" Note :  {self.title} "


############## Forms ######################
class AddForm(FlaskForm):
    title = StringField("Title ",[validators.DataRequired()])
    description = StringField(u'Description', widget=TextArea())
    submit = SubmitField('Add')
class EditForm(FlaskForm):
    title = StringField("Title ",[validators.DataRequired()])
    description = StringField(u'Description', widget=TextArea())
    submit = SubmitField('Edit')

################ Views ######################
@app.route('/')
def index():
    return render_template("home.html")


@app.route('/add', methods=['GET','POST'])
def add():
    form = AddForm()
    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        note = Note(title,description)
        db.session.add(note)
        db.session.commit()
        return redirect(url_for('list'))
    return render_template('add.html', form=form)


@app.route('/edit/<id>',methods=['GET','POST'])
def edit(id):
    note = Note.query.get(id)
    if request.method == 'GET':
        form = EditForm(formdata=MultiDict({'title': note.title, 'description': note.description}))
    else:
        form = EditForm()
    if form.validate_on_submit():
        note = Note.query.get(id)
        note.title = form.title.data
        note.description = form.description.data
        note.date = datetime.datetime.utcnow()
        db.session.add(note)
        db.session.commit()
        return redirect(url_for('list'))
    return render_template('edit.html',form=form)


@app.route('/list')
def list():
    notes = Note.query.all()
    return render_template('listNotes.html', notes=notes)


@app.route('/del/<id>')
def dele(id):
    note = Note.query.get(id)
    db.session.delete(note)
    db.session.commit()
    notes = Note.query.all()
    return redirect(url_for('list'))


@app.route('/search')
def search_note():
    searched = request.args.get('searched')
    found = True
    note = Note.query.filter_by(title = searched).first()
    if note is None:
        found = False
    return render_template('search.html', found=found, title=searched, note=note)


if __name__ == '__main__':
	app.run(debug=True)
