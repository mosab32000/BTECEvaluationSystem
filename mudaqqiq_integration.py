#!/usr/bin/env python
"""
واجهة الربط بين نظام تقييم BTEC ومنصة مُدقِّق
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
import logging
import os
import json
import requests
from urllib.parse import urljoin

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# إنشاء مخطط Blueprint للربط مع مُدقِّق
mudaqqiq_bp = Blueprint('mudaqqiq_integration', __name__, url_prefix='/mudaqqiq_integration',
                        template_folder='templates/mudaqqiq_integration')

# عنوان الوصول إلى خدمة مُدقِّق
MUDAQQIQ_BASE_URL = os.environ.get('MUDAQQIQ_URL', 'http://localhost:5000/mudaqqiq')
API_KEY = os.environ.get('MUDAQQIQ_API_KEY', 'مفتاح_مؤقت_للتطوير')

@mudaqqiq_bp.route('/')
def index():
    """الصفحة الرئيسية لتكامل مُدقِّق"""
    return render_template('mudaqqiq_integration/index.html')

@mudaqqiq_bp.route('/redirect')
def redirect_to_mudaqqiq():
    """إعادة توجيه المستخدم إلى منصة مُدقِّق"""
    # يمكن إضافة منطق للمصادقة والتحقق من الصلاحيات هنا
    return redirect(MUDAQQIQ_BASE_URL)

@mudaqqiq_bp.route('/projects')
def list_projects():
    """عرض المشاريع من منصة مُدقِّق"""
    try:
        # استدعاء واجهة برمجة التطبيقات للحصول على المشاريع
        response = requests.get(
            urljoin(MUDAQQIQ_BASE_URL, '/api/projects'),
            headers={'Authorization': f'Bearer {API_KEY}'}
        )
        
        if response.status_code == 200:
            projects = response.json().get('projects', [])
            return render_template('mudaqqiq_integration/projects.html', projects=projects)
        else:
            flash(f'فشل في الحصول على المشاريع: {response.status_code}', 'error')
            return render_template('mudaqqiq_integration/error.html', 
                                 message='تعذر الاتصال بمنصة مُدقِّق. يرجى المحاولة مرة أخرى.')
    
    except Exception as e:
        logger.error(f"حدث خطأ أثناء الاتصال بمنصة مُدقِّق: {str(e)}")
        return render_template('mudaqqiq_integration/error.html', 
                             message='حدث خطأ أثناء الاتصال بمنصة مُدقِّق')

@mudaqqiq_bp.route('/stats')
def get_stats():
    """عرض إحصائيات من منصة مُدقِّق"""
    try:
        # استدعاء واجهة برمجة التطبيقات للحصول على الإحصائيات
        response = requests.get(
            urljoin(MUDAQQIQ_BASE_URL, '/api/stats'),
            headers={'Authorization': f'Bearer {API_KEY}'}
        )
        
        if response.status_code == 200:
            stats = response.json()
            return render_template('mudaqqiq_integration/stats.html', stats=stats)
        else:
            flash(f'فشل في الحصول على الإحصائيات: {response.status_code}', 'error')
            return render_template('mudaqqiq_integration/error.html', 
                                 message='تعذر الاتصال بمنصة مُدقِّق. يرجى المحاولة مرة أخرى.')
    
    except Exception as e:
        logger.error(f"حدث خطأ أثناء الاتصال بمنصة مُدقِّق: {str(e)}")
        return render_template('mudaqqiq_integration/error.html', 
                             message='حدث خطأ أثناء الاتصال بمنصة مُدقِّق')

# إنشاء مجلد القوالب
mkdir -p templates/mudaqqiq_integration

# إنشاء قالب الصفحة الرئيسية
cat > templates/mudaqqiq_integration/index.html << 'EOL'
{% extends "base.html" %}

{% block title %}منصة مُدقِّق - نظام تقييم BTEC{% endblock %}

{% block content %}
<div class="container py-5">
    <div class="text-center mb-5">
        <h1 class="display-4">منصة مُدقِّق لتدقيق المشاريع</h1>
        <p class="lead">منصة متكاملة لتدقيق وتقييم المشاريع بطريقة احترافية ضمن نظام تقييم BTEC</p>
    </div>
    
    <div class="row">
        <div class="col-md-6 mb-4">
            <div class="card h-100">
                <div class="card-body text-center">
                    <h2 class="card-title"><i class="fas fa-file-alt mb-3 text-primary" style="font-size: 3rem;"></i></h2>
                    <h3>تدقيق المشاريع</h3>
                    <p class="card-text">رفع وتدقيق المشاريع وفق معايير محددة مع إصدار تقارير مفصلة.</p>
                    <a href="{{ url_for('mudaqqiq_integration.redirect_to_mudaqqiq') }}" class="btn btn-primary">الانتقال إلى منصة مُدقِّق</a>
                </div>
            </div>
        </div>
        
        <div class="col-md-6 mb-4">
            <div class="card h-100">
                <div class="card-body text-center">
                    <h2 class="card-title"><i class="fas fa-chart-bar mb-3 text-primary" style="font-size: 3rem;"></i></h2>
                    <h3>إحصائيات التدقيق</h3>
                    <p class="card-text">عرض إحصائيات مفصلة عن عمليات التدقيق والمشاريع.</p>
                    <a href="{{ url_for('mudaqqiq_integration.get_stats') }}" class="btn btn-primary">عرض الإحصائيات</a>
                </div>
            </div>
        </div>
    </div>
    
    <div class="row mt-4">
        <div class="col-md-6 mb-4">
            <div class="card h-100">
                <div class="card-body text-center">
                    <h2 class="card-title"><i class="fas fa-list mb-3 text-primary" style="font-size: 3rem;"></i></h2>
                    <h3>قائمة المشاريع</h3>
                    <p class="card-text">عرض قائمة المشاريع التي تم تدقيقها أو قيد التدقيق.</p>
                    <a href="{{ url_for('mudaqqiq_integration.list_projects') }}" class="btn btn-primary">عرض المشاريع</a>
                </div>
            </div>
        </div>
        
        <div class="col-md-6 mb-4">
            <div class="card h-100">
                <div class="card-body text-center">
                    <h2 class="card-title"><i class="fas fa-book mb-3 text-primary" style="font-size: 3rem;"></i></h2>
                    <h3>معايير التدقيق</h3>
                    <p class="card-text">معايير تدقيق مخصصة حسب نوع المشروع وطبيعته.</p>
                    <a href="{{ url_for('mudaqqiq_integration.redirect_to_mudaqqiq') }}" class="btn btn-primary">عرض المعايير</a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
EOL

# إنشاء قالب صفحة الخطأ
cat > templates/mudaqqiq_integration/error.html << 'EOL'
{% extends "base.html" %}

{% block title %}خطأ - منصة مُدقِّق{% endblock %}

{% block content %}
<div class="container py-5 text-center">
    <div class="alert alert-danger p-5">
        <h1 class="mb-4"><i class="fas fa-exclamation-triangle"></i> حدث خطأ</h1>
        <p class="lead">{{ message }}</p>
        <a href="{{ url_for('mudaqqiq_integration.index') }}" class="btn btn-primary mt-3">العودة للصفحة الرئيسية</a>
    </div>
</div>
{% endblock %}
EOL

# إنشاء قالب صفحة المشاريع
cat > templates/mudaqqiq_integration/projects.html << 'EOL'
{% extends "base.html" %}

{% block title %}المشاريع - منصة مُدقِّق{% endblock %}

{% block content %}
<div class="container py-5">
    <h1 class="mb-4">قائمة المشاريع</h1>
    
    {% if projects %}
        <div class="table-responsive">
            <table class="table table-striped">
                <thead class="table-dark">
                    <tr>
                        <th>عنوان المشروع</th>
                        <th>النوع</th>
                        <th>تاريخ التقديم</th>
                        <th>الحالة</th>
                        <th>الإجراءات</th>
                    </tr>
                </thead>
                <tbody>
                    {% for project in projects %}
                        <tr>
                            <td>{{ project.title }}</td>
                            <td>{{ project.project_type }}</td>
                            <td>{{ project.submission_date }}</td>
                            <td>
                                {% if project.status == 'قيد الانتظار' %}
                                    <span class="badge bg-warning text-dark">قيد الانتظار</span>
                                {% elif project.status == 'قيد التدقيق' %}
                                    <span class="badge bg-info">قيد التدقيق</span>
                                {% elif project.status == 'مكتمل' %}
                                    <span class="badge bg-success">مكتمل</span>
                                {% elif project.status == 'مرفوض' %}
                                    <span class="badge bg-danger">مرفوض</span>
                                {% endif %}
                            </td>
                            <td>
                                <a href="{{ project.file_url }}" class="btn btn-sm btn-primary" target="_blank">
                                    <i class="fas fa-eye"></i> عرض
                                </a>
                            </td>
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    {% else %}
        <div class="alert alert-info">
            <p class="lead">لا توجد مشاريع متاحة حاليًا.</p>
        </div>
    {% endif %}
    
    <div class="mt-4">
        <a href="{{ url_for('mudaqqiq_integration.index') }}" class="btn btn-secondary">العودة</a>
        <a href="{{ url_for('mudaqqiq_integration.redirect_to_mudaqqiq') }}" class="btn btn-primary">إنشاء مشروع جديد</a>
    </div>
</div>
{% endblock %}
EOL

# إنشاء قالب صفحة الإحصائيات
cat > templates/mudaqqiq_integration/stats.html << 'EOL'
{% extends "base.html" %}

{% block title %}إحصائيات التدقيق - منصة مُدقِّق{% endblock %}

{% block content %}
<div class="container py-5">
    <h1 class="mb-5 text-center">إحصائيات منصة مُدقِّق</h1>
    
    <div class="row mb-5">
        <div class="col-md-3 mb-4">
            <div class="card text-center">
                <div class="card-body">
                    <h2 class="display-4 text-primary">{{ stats.total_projects }}</h2>
                    <p class="lead">إجمالي المشاريع</p>
                </div>
            </div>
        </div>
        <div class="col-md-3 mb-4">
            <div class="card text-center">
                <div class="card-body">
                    <h2 class="display-4 text-warning">{{ stats.pending_projects }}</h2>
                    <p class="lead">قيد الانتظار</p>
                </div>
            </div>
        </div>
        <div class="col-md-3 mb-4">
            <div class="card text-center">
                <div class="card-body">
                    <h2 class="display-4 text-success">{{ stats.completed_projects }}</h2>
                    <p class="lead">مكتملة</p>
                </div>
            </div>
        </div>
        <div class="col-md-3 mb-4">
            <div class="card text-center">
                <div class="card-body">
                    <h2 class="display-4 text-info">{{ stats.avg_score }}</h2>
                    <p class="lead">متوسط الدرجات</p>
                </div>
            </div>
        </div>
    </div>
    
    {% if stats.projects_by_type %}
        <div class="row mb-5">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header bg-primary text-white">
                        <h4 class="mb-0">توزيع المشاريع حسب النوع</h4>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>نوع المشروع</th>
                                        <th>عدد المشاريع</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for type, count in stats.projects_by_type.items() %}
                                        <tr>
                                            <td>{{ type }}</td>
                                            <td>{{ count }}</td>
                                        </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    {% endif %}
    
    <div class="text-center mt-4">
        <a href="{{ url_for('mudaqqiq_integration.index') }}" class="btn btn-secondary">العودة</a>
        <a href="{{ url_for('mudaqqiq_integration.redirect_to_mudaqqiq') }}" class="btn btn-primary">الانتقال إلى منصة مُدقِّق</a>
    </div>
</div>
{% endblock %}
EOL

cat > INTEGRATION.md << 'EOF'
# دليل تكامل منصة مُدقِّق مع نظام تقييم BTEC

هذا الدليل يشرح كيفية دمج منصة مُدقِّق مع نظام تقييم BTEC واستخدامها كمكون متكامل.

## طريقة التكامل

تم تطوير منصة مُدقِّق بحيث يمكن استخدامها من خلال طريقتين:

1. **كمنصة مستقلة**: يمكن تشغيل المنصة بشكل مستقل من خلال تنفيذ الأمر:
   ```
   python mudaqqiq/run_mudaqqiq.py
   ```

2. **كمكوّن ضمن نظام تقييم BTEC**: يمكن دمج المنصة مع نظام BTEC من خلال:
   ```
   python run_mudaqqiq_server.py
   ```

## كيفية استخدام التكامل

1. قم بإضافة مخطط Blueprint للتكامل مع منصة مُدقِّق في تطبيق Flask الرئيسي:

```python
from mudaqqiq_integration import mudaqqiq_bp

# تسجيل مخطط التكامل
app.register_blueprint(mudaqqiq_bp)
```

2. قم بإضافة رابط في قائمة التنقل للوصول إلى منصة مُدقِّق:

```html
<li class="nav-item">
    <a class="nav-link" href="{{ url_for('mudaqqiq_integration.index') }}">منصة مُدقِّق</a>
</li>
```

3. قم بضبط متغيرات البيئة اللازمة:

```
MUDAQQIQ_URL=http://localhost:5000/mudaqqiq
MUDAQQIQ_API_KEY=your_api_key_here
```

## واجهة برمجة التطبيقات (API)

يمكن استخدام واجهة برمجة التطبيقات (API) للتفاعل مع منصة مُدقِّق برمجيًا:

### المصادقة
```
POST /api/token
```

### المشاريع
```
GET /api/projects - الحصول على قائمة المشاريع
GET /api/projects/:id - الحصول على تفاصيل مشروع محدد
```

### التدقيق
```
GET /api/audit_criteria - الحصول على معايير التدقيق
```

### الإحصائيات
```
GET /api/stats - الحصول على إحصائيات عامة
```

## النماذج المشتركة

يمكن مشاركة بعض النماذج بين النظامين عن طريق:

1. إنشاء مكتبة مشتركة للنماذج.
2. استخدام قاعدة بيانات واحدة مع فصل الجداول.
3. استخدام واجهة برمجة التطبيقات للتفاعل بين النظامين.

## حل المشاكل الشائعة

- **مشكلة الاتصال**: تأكد من أن منصة مُدقِّق تعمل وأن عنوان URL صحيح.
- **مشكلة المصادقة**: تحقق من صحة مفتاح API.
- **خطأ في عرض البيانات**: تأكد من تنسيق البيانات المرسلة والمستقبلة بشكل صحيح.
