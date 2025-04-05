from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Regexp
from app.models import User

class LoginForm(FlaskForm):
    email = StringField('البريد الإلكتروني', validators=[DataRequired(), Email()])
    password = PasswordField('كلمة المرور', validators=[DataRequired()])
    remember_me = BooleanField('تذكرني')
    submit = SubmitField('تسجيل الدخول')

class RegistrationForm(FlaskForm):
    username = StringField('اسم المستخدم', validators=[
        DataRequired(),
        Length(min=3, max=64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'يجب أن يبدأ اسم المستخدم بحرف ويمكن أن يحتوي فقط على أحرف وأرقام ونقاط وشرطات سفلية')
    ])
    email = StringField('البريد الإلكتروني', validators=[DataRequired(), Email()])
    full_name = StringField('الاسم الكامل', validators=[DataRequired(), Length(min=3, max=150)])
    password = PasswordField('كلمة المرور', validators=[
        DataRequired(),
        Length(min=8, message='يجب أن تتكون كلمة المرور من 8 أحرف على الأقل')
    ])
    password2 = PasswordField(
        'تأكيد كلمة المرور', validators=[DataRequired(), EqualTo('password', message='كلمة المرور غير متطابقة')]
    )
    submit = SubmitField('تسجيل')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('يرجى استخدام اسم مستخدم مختلف.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('هذا البريد الإلكتروني مسجل بالفعل.')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('البريد الإلكتروني', validators=[DataRequired(), Email()])
    submit = SubmitField('طلب إعادة تعيين كلمة المرور')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('كلمة المرور الجديدة', validators=[
        DataRequired(),
        Length(min=8, message='يجب أن تتكون كلمة المرور من 8 أحرف على الأقل')
    ])
    password2 = PasswordField(
        'تأكيد كلمة المرور الجديدة', 
        validators=[DataRequired(), EqualTo('password', message='كلمة المرور غير متطابقة')]
    )
    submit = SubmitField('تغيير كلمة المرور')
