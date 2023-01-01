from wtforms import StringField, IntegerField, SubmitField, RadioField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from datetime import date
from flask_wtf import FlaskForm


now = date.today().year

class AddMemberForm(FlaskForm):
	firstMemberName = StringField('First Name !', validators=[DataRequired(), Length(min=3, max=40)] )
	LastMemberName = StringField('Last Name !', validators=[DataRequired(), Length(min=3, max=40)] )
	birthMemberYear = IntegerField('Birth Year !', validators=[DataRequired(), NumberRange(min=0, max=now)], default = now )
	deathMemberYear = IntegerField('Death Year', validators=[Optional(), NumberRange(min=0, max=now)] )
	marriageMemberYear = IntegerField('Marriage Year', validators=[Optional(), NumberRange(min=0, max=now)] )

	submit = SubmitField('Add member')

class FindRelationsForm(FlaskForm):
	submit = SubmitField('Search Relations')

class RemoveForm(FlaskForm):
	submit = SubmitField('Remove member')

class CleanDatabaseForm(FlaskForm):
	clean_option = RadioField('Clean & Reload', choices=[('delete','Empty whole database'), ('reload','Remove and reload template data')], validators=[DataRequired(),] )
	submit = SubmitField('Clean')