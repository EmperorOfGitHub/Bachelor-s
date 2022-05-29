from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from VGTUcoin.models import User


class RegistrationForm(FlaskForm):

    name = StringField('First Name', validators=[DataRequired()],
                       render_kw={"placeholder": "Vardas"})

    username = StringField('Username',
                           validators=[DataRequired(), Length(min=4, max=15)],
                           render_kw={"placeholder": "Pavardė"})

    email = StringField('Email', validators=[DataRequired(), Email()],
                        render_kw={"placeholder": "El. paštas"})

    password = PasswordField('Password', validators=[DataRequired()],
                             render_kw={"placeholder": "Slaptažodis"})

    confirmPassword = PasswordField('Confirm Password',
                                    validators=[
                                        DataRequired(), EqualTo('password')],
                                    render_kw={"placeholder": "Pakartokite slaptažodį"})

    submit = SubmitField('Užsiregistuoti')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                'Vartotojo vardas yra užimtas. Pasirinkite kitą vartotojo vardą')

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError(
                'El. paštas jau naudojamas.')


class LoginForm(FlaskForm):

    email = StringField('Email', validators=[DataRequired(), Email()],
                        render_kw={"placeholder": "El. paštas"})

    password = PasswordField('Password', validators=[DataRequired()],
                             render_kw={"placeholder": "Slaptažodis"})

    remember = BooleanField('Prisiminti mane')

    submit = SubmitField('Prisijungti')


class TransactionForm(FlaskForm):

    sender = StringField('Sender',
                         validators=[DataRequired(), Length(min=4, max=15)])

    reciever = StringField('Reciever',
                           validators=[DataRequired(), Length(min=4, max=15)])

    amount = IntegerField('Amount', validators=[DataRequired()])

    key = StringField('Key', validators=[DataRequired()])

    dummy = StringField('Dummy')

    submit = SubmitField('Atlikti pervedimą')


class TransactionFormNotLoggedIn(FlaskForm):

    sender = StringField('Sender')

    reciever = StringField('Reciever')

    amount = StringField('Amount')

    key = StringField('Key')

    dummy = StringField('Dummy')

    submit = SubmitField('Prisijunkite, kad atlikti pervedimą')

class BuyForm(FlaskForm):

    buyer = StringField('Buyer', validators=[DataRequired(), Length(min=4, max=15)])

    amount = IntegerField('Amount', validators=[DataRequired()])

    key = StringField('Key', validators=[DataRequired()])

    dummy = StringField('Dummy')

    submit = SubmitField('Pirkti')


class BuyFormNotLoggedIn(FlaskForm):

    buyer = StringField('Buyer')

    amount = StringField('Amount')

    key = StringField('Key')

    dummy = StringField('Dummy')

    submit = SubmitField('Prisijunkite, kad nusipirkti valiutos')