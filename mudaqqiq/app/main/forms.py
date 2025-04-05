from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Email

class ProfileForm(FlaskForm):
    full_name = StringField('الاسم الكامل', validators=[DataRequired(), Length(min=3, max=150)])
    about_me = TextAreaField('نبذة عني', validators=[Length(min=0, max=500)])
    profile_image = FileField('صورة الملف الشخصي', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'يجب أن تكون الصورة بتنسيق jpg أو png فقط.')
    ])
    submit = SubmitField('تحديث')

class ContactForm(FlaskForm):
    name = StringField('الاسم', validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField('البريد الإلكتروني', validators=[DataRequired(), Email()])
    subject = StringField('الموضوع', validators=[DataRequired(), Length(min=3, max=150)])
    message = TextAreaField('الرسالة', validators=[DataRequired(), Length(min=10, max=2000)])
    submit = SubmitField('إرسال')
