from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, SelectField, SubmitField, MultipleFileField, FloatField, SelectMultipleField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

class ProjectForm(FlaskForm):
    title = StringField('عنوان المشروع', validators=[DataRequired(), Length(min=3, max=150)])
    description = TextAreaField('وصف المشروع', validators=[DataRequired(), Length(min=10, max=2000)])
    project_type = SelectField('نوع المشروع', validators=[DataRequired()], choices=[
        ('تطبيق ويب', 'تطبيق ويب'),
        ('تطبيق جوال', 'تطبيق جوال'),
        ('موقع إلكتروني', 'موقع إلكتروني'),
        ('مشروع برمجي', 'مشروع برمجي'),
        ('وثيقة بحثية', 'وثيقة بحثية'),
        ('أخرى', 'أخرى')
    ])
    project_file = FileField('ملف المشروع', validators=[
        FileAllowed(['pdf', 'docx', 'doc', 'zip', 'rar', 'xlsx', 'pptx', 'png', 'jpg', 'jpeg'], 
                   'يرجى رفع ملف بتنسيق مدعوم.')
    ])
    submit = SubmitField('إرسال')

class AuditForm(FlaskForm):
    criteria = SelectMultipleField('معايير التدقيق', validators=[DataRequired()], coerce=int)
    score = FloatField('النتيجة (من 100)', validators=[
        DataRequired(),
        NumberRange(min=0, max=100, message='يجب أن تكون النتيجة بين 0 و 100')
    ])
    feedback = TextAreaField('التقييم العام', validators=[DataRequired(), Length(min=10, max=2000)])
    notes = TextAreaField('ملاحظات إضافية', validators=[Optional(), Length(max=2000)])
    recommendations = TextAreaField('توصيات', validators=[Optional(), Length(max=2000)])
    submit = SubmitField('تسجيل التدقيق')
