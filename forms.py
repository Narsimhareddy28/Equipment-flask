# forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, DateField, DecimalField,TextAreaField,FloatField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ClientRegistrationForm(FlaskForm):
    client_name = StringField('Name', validators=[DataRequired()])
    client_address = StringField('Address', validators=[DataRequired()])
    telephone_number = StringField('Telephone Number', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Register')

class ManagerRegistrationForm(FlaskForm):
    manager_name = StringField('Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Register')
    
class RentForm(FlaskForm):
    equipment = SelectField('Select Equipment', coerce=int, validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    total_amount = DecimalField('Total Amount', places=2, render_kw={'readonly': True})
    amount_paid= DecimalField('Amount to Pay', validators=[DataRequired()])
    submit = SubmitField('Rent')
    
class UpdateEquipmentForm(FlaskForm):
    equipment_name = StringField('Equipment Name', validators=[DataRequired()])
    manufacturer = StringField('Manufacturer', validators=[DataRequired()])
    description = TextAreaField('Description')
    rent_price_per_day = FloatField('Rent per Day', validators=[DataRequired()])
    quantity_in_store = IntegerField('Quantity in Store', validators=[DataRequired()])

class AddEquipmentForm(FlaskForm):
    equipment_name = StringField('Equipment Name', validators=[DataRequired()])
    manufacturer = StringField('Manufacturer', validators=[DataRequired()])
    description = TextAreaField('Description')
    rent_price_per_day = FloatField('Rent per Day', validators=[DataRequired()])
    quantity_in_store = IntegerField('Quantity in Store', validators=[DataRequired()])
    supplier_id =IntegerField('supplier', validators=[DataRequired()])
    
class OrderForm(FlaskForm):
    client_selection = SelectField('Client', coerce=int, validators=[DataRequired()])
    equipment = SelectField('Equipment', coerce=int, validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[DataRequired()])
    amount_paid = FloatField('Amount Paid', validators=[DataRequired()])