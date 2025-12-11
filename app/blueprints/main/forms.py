from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired

class ProjectForm(FlaskForm):
    title = StringField('Project Title', validators=[DataRequired()])
    gender = SelectField('Protagonist Gender (for Voice)', choices=[
        ('male', 'Male'), 
        ('female', 'Female'), 
        ('neutral', 'Non-Binary/Other')
    ], validators=[DataRequired()])
    comic_file = FileField('Manga Comic', validators=[
        FileRequired(),
        FileAllowed(['pdf', 'jpg', 'png', 'jpeg'], 'Images or PDFs only!')
    ])
    protagonist_image = FileField('Protagonist Image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')
    ])
    submit = SubmitField('Create Avatar')

class MangaForm(FlaskForm):
    title = StringField('Manga Title', validators=[DataRequired()])
    plot = TextAreaField('Plot / Story', validators=[DataRequired()], render_kw={"rows": 5})
    style = StringField('Visual Style', default="In cute Kawaii style")
    reference_images = FileField('Reference Images', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')
    ], render_kw={'multiple': True})
    submit = SubmitField('Generate Manga & Voice')