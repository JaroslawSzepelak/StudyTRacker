import re
from flask_wtf import FlaskForm
from wtforms import DateField, StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Regexp, NumberRange, InputRequired
from models import User
from wtforms.fields.html5 import DateField

class LoginForm(FlaskForm):
    username = StringField('Nazwa użytkownika', validators=[DataRequired(message='To pole jest wymagane.')])
    password = PasswordField('Hasło', validators=[DataRequired(message='To pole jest wymagane.')])
    remember = BooleanField('Zapamiętaj mnie')
    submit = SubmitField('Zaloguj się')

class RegistrationForm(FlaskForm):
    username = StringField('Nazwa użytkownika', validators=[DataRequired(message='To pole jest wymagane.'), Length(min=5, max=30, message='Nazwa użytkownika musi mieć od 5 do 30 znaków.')])
    password = PasswordField('Hasło', validators=[DataRequired(message='To pole jest wymagane.'), Length(min=8, message='Hasło musi mieć przynajmniej 8 znaków.')])
    confirm_password = PasswordField('Potwierdź hasło', validators=[DataRequired(message='To pole jest wymagane.'), EqualTo('password', message='Hasła muszą być takie same.')])
    submit = SubmitField('Zarejestruj się')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Nazwa użytkownika jest już zajęta. Wybierz inną.')

    def validate_password(self, password):
        if not any(char.isdigit() for char in password.data):
            raise ValidationError('Hasło musi zawierać co najmniej jedną cyfrę.')
        if not any(char.isupper() for char in password.data):
            raise ValidationError('Hasło musi zawierać co najmniej jedną wielką literę.')

class StudySessionForm(FlaskForm):
    subject = StringField('Przedmiot', validators=[InputRequired(message="To pole jest wymagane.")])
    duration = IntegerField('Czas trwania (minuty)', validators=[InputRequired(message="To pole jest wymagane."), NumberRange(min=0, message="Czas trwania musi być liczbą całkowitą nieujemną.")])
    session_date = DateField('Data sesji', format='%Y-%m-%d', validators=[InputRequired(message="To pole jest wymagane.")])

    submit = SubmitField('Dodaj sesję')

class AchievementForm(FlaskForm):
    description = StringField('Opis', validators=[DataRequired(message="To pole jest wymagane.")])
    subject = StringField('Przedmiot', validators=[DataRequired(message="To pole jest wymagane.")])  # Nowe pole nazwy przedmiotu
    achievement_date = DateField('Data osiągnięcia', format='%Y-%m-%d', validators=[DataRequired(message="To pole jest wymagane.")])
    
    submit = SubmitField('Dodaj osiągnięcie')

class StudyPlanForm(FlaskForm):
    subject = StringField('Przedmiot', validators=[InputRequired(message="To pole jest wymagane.")])
    planned_date = DateField('Data planowanej sesji', format='%Y-%m-%d', validators=[InputRequired(message="To pole jest wymagane.")])
    submit = SubmitField('Dodaj plan nauki')

