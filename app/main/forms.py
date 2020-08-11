from flask_wtf import FlaskForm
import wtforms
from wtforms.validators import *
from flask_pagedown.fields import PageDownField


class NameForm(FlaskForm):
    name = wtforms.StringField('Your name: ', [DataRequired()])
    id = wtforms.IntegerField('id: ', [DataRequired()])
    submit = wtforms.SubmitField('Submit')


class PostForm(FlaskForm):
    body = PageDownField('what is on your mind?', validators=[DataRequired()])
    submit = wtforms.SubmitField('Submit')


class CommentForm(FlaskForm):
    body = wtforms.StringField('', validators=[DataRequired()])
    submit = wtforms.SubmitField('Comment')
