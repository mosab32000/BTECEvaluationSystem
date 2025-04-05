from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, FloatField, BooleanField, SelectMultipleField
from wtforms.validators import DataRequired, Length, NumberRange

class AuditCriteriaForm(FlaskForm):
    name = StringField('اسم المعيار', validators=[DataRequired(), Length(min=3, max=100)])
    description = TextAreaField('وصف المعيار', validators=[DataRequired(), Length(min=10, max=1000)])
    category = SelectField('الفئة', validators=[DataRequired()])
    weight = FloatField('الوزن', validators=[DataRequired(), NumberRange(min=0.1, max=10)], default=1.0)
    submit = SubmitField('حفظ')

class UserRoleForm(FlaskForm):
    is_active = BooleanField('حساب نشط')
    roles = SelectMultipleField('الأدوار', validators=[DataRequired()], coerce=int)
    submit = SubmitField('تحديث')
