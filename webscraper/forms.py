from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import (DataRequired, Email, EqualTo, Length,
                                ValidationError)

from webscraper.models import User


class RegisterForm(FlaskForm):
    def validate_username(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError('Username already exist. Please try a different username.')

    def validate_email_address(self, email_address_to_check):
        email_address = User.query.filter_by(email_address=email_address_to_check.data).first()
        if email_address:
            raise ValidationError('Email address is already taken. Please try a different email address.')

    username = StringField(label='Username:', validators=[Length(min=6, max=30), DataRequired()])
    email_address = StringField(label='Email:', validators=[Email(), DataRequired()])
    password1 = PasswordField(label='Password:', validators=[Length(min=8), DataRequired()])
    password2 = PasswordField(label='Confirm Password:', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='Create Account:')


class LoginForm(FlaskForm):
    username = StringField(label='Username or Email: ', validators=[DataRequired()])
    password = PasswordField(label='Password: ', validators=[DataRequired()])
    submit = SubmitField(label='Sign In')


class ForgotPasswordForm(FlaskForm):
    username = StringField(label='Username', validators=[DataRequired()])
    email = StringField(label='Registered Email', validators=[Email(), DataRequired()])
    submit = SubmitField(label='Reset Password')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(label='Old Password:', validators=[Length(min=8), DataRequired()])
    new_password = PasswordField(label='New Password:', validators=[Length(min=8), DataRequired()])
    confirm_new_password = PasswordField(label='Confirm Password:',
                                         validators=[EqualTo('new_password'), DataRequired()])
    submit = SubmitField(label='Change Password')


class AddToFavoritesForm(FlaskForm):
    submit = SubmitField(label='Add To Favorites')


class RemoveToFavoritesForm(FlaskForm):
    submit = SubmitField(label='Remove To Favorites')


class ReplaceProductModalForm(FlaskForm):
    submit = SubmitField(label='Replace the following item')


class UpdateProductModalForm(FlaskForm):
    submit = SubmitField(label='Update')


class LoadReviewsForm(FlaskForm):
    submit = SubmitField(label='Load')


class UpdateReviewsForm(FlaskForm):
    submit = SubmitField(label='Update')


class LoadRecommendedProductsForm(FlaskForm):
    submit = SubmitField(label='Load')


class ViewRecommendedProductForm(FlaskForm):
    submit = SubmitField(label='Replace')


class ClearProductViewForm(FlaskForm):
    submit = SubmitField(label='Clear View')
