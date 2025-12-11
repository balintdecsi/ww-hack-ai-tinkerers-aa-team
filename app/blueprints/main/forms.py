from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SubmitField, SelectField
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
