// ملف JavaScript الرئيسي لنظام تقييم BTEC

// إعدادات شاملة
const API_URL = '/api';
const AUTH_TOKEN_KEY = 'btec_auth_token';
const USER_DATA_KEY = 'btec_user_data';

// التأكد من وجود token صالح
function isAuthenticated() {
    const token = localStorage.getItem(AUTH_TOKEN_KEY);
    return token !== null && token !== undefined;
}

// الحصول على بيانات المستخدم من التخزين المحلي
function getCurrentUser() {
    const userData = localStorage.getItem(USER_DATA_KEY);
    return userData ? JSON.parse(userData) : null;
}

// طلب HTTP عام
async function fetchAPI(endpoint, options = {}) {
    // إضافة التوكن لجميع الطلبات المصادقة
    if (isAuthenticated()) {
        const token = localStorage.getItem(AUTH_TOKEN_KEY);
        options.headers = {
            ...options.headers,
            'Authorization': `Bearer ${token}`
        };
    }
    
    // إعداد الطلب
    const url = `${API_URL}${endpoint}`;
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        }
    };
    
    try {
        const response = await fetch(url, { ...defaultOptions, ...options });
        
        // التعامل مع الأخطاء
        if (!response.ok) {
            if (response.status === 401) {
                // انتهت صلاحية التوكن أو غير صالح
                localStorage.removeItem(AUTH_TOKEN_KEY);
                localStorage.removeItem(USER_DATA_KEY);
                window.location.href = '/login';
                return null;
            }
            
            const error = await response.json();
            throw new Error(error.message || 'حدث خطأ غير معروف');
        }
        
        // إرجاع البيانات
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// تسجيل الخروج
function logout() {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(USER_DATA_KEY);
    window.location.href = '/';
}

// التبديل بين القائمة في الأجهزة الصغيرة
function toggleMobileMenu() {
    const navLinks = document.querySelector('.nav-links');
    navLinks.classList.toggle('active');
}

// عرض/إخفاء العناصر المتعلقة بحالة تسجيل الدخول
function updateUIBasedOnAuth() {
    const isLoggedIn = isAuthenticated();
    
    // عناصر تظهر للمستخدمين المسجلين فقط
    document.querySelectorAll('.logged-in-only').forEach(el => {
        el.style.display = isLoggedIn ? 'block' : 'none';
    });
    
    // عناصر تظهر لغير المسجلين فقط
    document.querySelectorAll('.logged-out-only').forEach(el => {
        el.style.display = isLoggedIn ? 'none' : 'block';
    });
    
    // عناصر تظهر للمسؤولين فقط
    const currentUser = getCurrentUser();
    if (isLoggedIn && currentUser && currentUser.role === 'admin') {
        document.querySelectorAll('.admin-only').forEach(el => {
            el.style.display = 'block';
        });
    }
    
    // عناصر تظهر للمعلمين فقط
    if (isLoggedIn && currentUser && currentUser.role === 'teacher') {
        document.querySelectorAll('.teacher-only').forEach(el => {
            el.style.display = 'block';
        });
    }
}

// تنشيط عناصر الصفحة باستخدام التحريك
function animateElements() {
    const elements = document.querySelectorAll('[data-animate]');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
            }
        });
    }, { threshold: 0.1 });
    
    elements.forEach(element => {
        observer.observe(element);
    });
}

// معالجة نموذج تسجيل الدخول
async function handleLogin(event) {
    if (!event) return;
    event.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const errorDiv = document.getElementById('login-error');
    const successDiv = document.getElementById('login-success');
    
    // إخفاء رسائل الخطأ والنجاح السابقة
    if (errorDiv) errorDiv.style.display = 'none';
    if (successDiv) successDiv.style.display = 'none';
    
    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'خطأ في تسجيل الدخول');
        }
        
        // حفظ توكن المصادقة وبيانات المستخدم
        localStorage.setItem(AUTH_TOKEN_KEY, data.token);
        localStorage.setItem(USER_DATA_KEY, JSON.stringify(data.user));
        
        // عرض رسالة النجاح وتحويل المستخدم
        if (successDiv) {
            successDiv.style.display = 'block';
            // تأخير قبل التحويل للسماح للمستخدم برؤية رسالة النجاح
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 1500);
        } else {
            window.location.href = '/dashboard';
        }
    } catch (error) {
        // عرض رسالة الخطأ
        if (errorDiv) {
            errorDiv.textContent = error.message || 'حدث خطأ في تسجيل الدخول';
            errorDiv.style.display = 'block';
            
            // إضافة تأثير رجة للنموذج
            const form = document.getElementById('login-form');
            if (form) {
                form.classList.add('shake');
                setTimeout(() => {
                    form.classList.remove('shake');
                }, 600);
            }
        }
    }
}

// معالجة نموذج التسجيل
async function handleRegister(event) {
    if (!event) return;
    event.preventDefault();
    
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;
    const errorDiv = document.getElementById('register-error');
    const successDiv = document.getElementById('register-success');
    
    // إخفاء رسائل الخطأ والنجاح السابقة
    if (errorDiv) errorDiv.style.display = 'none';
    if (successDiv) successDiv.style.display = 'none';
    
    // التحقق من تطابق كلمات المرور
    if (password !== confirmPassword) {
        if (errorDiv) {
            errorDiv.textContent = 'كلمات المرور غير متطابقة';
            errorDiv.style.display = 'block';
        }
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, email, password })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'خطأ في التسجيل');
        }
        
        // عرض رسالة النجاح وتحويل المستخدم
        if (successDiv) {
            successDiv.style.display = 'block';
            // تأخير قبل التحويل للسماح للمستخدم برؤية رسالة النجاح
            setTimeout(() => {
                window.location.href = '/login';
            }, 1500);
        } else {
            window.location.href = '/login';
        }
    } catch (error) {
        // عرض رسالة الخطأ
        if (errorDiv) {
            errorDiv.textContent = error.message || 'حدث خطأ في التسجيل';
            errorDiv.style.display = 'block';
            
            // إضافة تأثير رجة للنموذج
            const form = document.getElementById('register-form');
            if (form) {
                form.classList.add('shake');
                setTimeout(() => {
                    form.classList.remove('shake');
                }, 600);
            }
        }
    }
}

// معالجة نموذج التقييم
async function handleEvaluation(event) {
    if (!event) return;
    event.preventDefault();
    
    const taskContent = document.getElementById('task-content').value;
    const rubricId = document.getElementById('rubric-id').value;
    const customRubric = document.getElementById('custom-rubric').value;
    
    const loadingMessage = document.getElementById('loading-message');
    const evaluationResults = document.getElementById('evaluation-results');
    
    // عرض رسالة التحميل
    if (loadingMessage) loadingMessage.style.display = 'block';
    if (evaluationResults) evaluationResults.style.display = 'none';
    
    // إعداد البيانات المرسلة
    const requestData = {
        task: taskContent,
        rubric_id: rubricId === 'custom' ? null : rubricId,
        custom_rubric: rubricId === 'custom' ? customRubric : null
    };
    
    try {
        const response = await fetchAPI('/evaluations/evaluate', {
            method: 'POST',
            body: JSON.stringify(requestData)
        });
        
        // إخفاء رسالة التحميل
        if (loadingMessage) loadingMessage.style.display = 'none';
        
        if (response && evaluationResults) {
            // عرض نتائج التقييم
            displayEvaluationResults(response, evaluationResults);
            evaluationResults.style.display = 'block';
            
            // التمرير إلى نتائج التقييم
            evaluationResults.scrollIntoView({ behavior: 'smooth' });
        }
    } catch (error) {
        console.error('Evaluation Error:', error);
        
        // إخفاء رسالة التحميل
        if (loadingMessage) loadingMessage.style.display = 'none';
        
        // عرض رسالة خطأ
        const errorMessage = document.createElement('div');
        errorMessage.className = 'error-message';
        errorMessage.textContent = `خطأ في التقييم: ${error.message || 'حدث خطأ غير معروف'}`;
        
        if (evaluationResults) {
            evaluationResults.innerHTML = '';
            evaluationResults.appendChild(errorMessage);
            evaluationResults.style.display = 'block';
            evaluationResults.scrollIntoView({ behavior: 'smooth' });
        }
    }
}

// عرض نتائج التقييم
function displayEvaluationResults(evaluation, container) {
    if (!container) return;
    
    container.innerHTML = `
        <div class="card evaluation-result-card" data-animate="fade-in">
            <div class="card-header">
                <h2 class="card-title">
                    <svg class="svg-icon">
                        <use href="#icon-evaluation"></use>
                    </svg>
                    نتائج التقييم
                </h2>
            </div>
            <div class="card-content">
                <div class="evaluation-grade">
                    <div class="grade-circle">${evaluation.grade_numerical || '-'}</div>
                    <div>
                        <h2>${evaluation.grade || 'تقييم'}</h2>
                        <p>الدرجة النهائية</p>
                    </div>
                </div>
                
                <div class="evaluation-feedback">
                    <h3>
                        <svg class="svg-icon">
                            <use href="#icon-feedback"></use>
                        </svg>
                        ملاحظات التقييم
                    </h3>
                    <div class="feedback-content">${evaluation.feedback || 'لا توجد ملاحظات'}</div>
                </div>
                
                <div class="evaluation-rubric">
                    <h3>
                        <svg class="svg-icon">
                            <use href="#icon-rubric"></use>
                        </svg>
                        التقييم حسب المعايير
                    </h3>
                    <ul class="rubric-results">
                        ${displayRubricResults(evaluation.rubric_results)}
                    </ul>
                </div>
                
                <div class="evaluation-verification">
                    <h3>
                        <svg class="svg-icon">
                            <use href="#icon-blockchain"></use>
                        </svg>
                        حالة التحقق
                    </h3>
                    <div class="verification-status">
                        ${evaluation.verification_status ? 
                            `<span class="badge badge-success">تم التحقق</span>` : 
                            `<span class="badge badge-warning">لم يتم التحقق بعد</span>`}
                    </div>
                </div>
                
                <div class="evaluation-actions">
                    <button id="verify-evaluation-btn" class="btn btn-primary">
                        <svg class="svg-icon">
                            <use href="#icon-blockchain"></use>
                        </svg>
                        التحقق من النتائج
                    </button>
                    <button id="export-evaluation-btn" class="btn btn-outline">
                        <svg class="svg-icon">
                            <use href="#icon-export"></use>
                        </svg>
                        تصدير النتائج
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // تنشيط الأزرار
    const verifyBtn = document.getElementById('verify-evaluation-btn');
    if (verifyBtn) {
        verifyBtn.addEventListener('click', () => verifyEvaluation(evaluation.id));
    }
    
    const exportBtn = document.getElementById('export-evaluation-btn');
    if (exportBtn) {
        exportBtn.addEventListener('click', () => exportEvaluation(evaluation.id));
    }
    
    // تنشيط العناصر المتحركة
    animateElements();
}

// عرض نتائج معايير التقييم
function displayRubricResults(rubricResults) {
    if (!rubricResults) return '<li>لا توجد نتائج لمعايير التقييم</li>';
    
    try {
        // تحويل من سلسلة نصية JSON إذا لزم الأمر
        const results = typeof rubricResults === 'string' ? JSON.parse(rubricResults) : rubricResults;
        
        return Object.entries(results).map(([criterion, data]) => `
            <li>
                <strong>${criterion}:</strong> ${data.score || '-'}/100
                <p>${data.feedback || 'لا توجد ملاحظات'}</p>
            </li>
        `).join('');
    } catch (error) {
        console.error('Error parsing rubric results:', error);
        return '<li>خطأ في عرض نتائج معايير التقييم</li>';
    }
}

// التحقق من نتائج التقييم باستخدام البلوكتشين
async function verifyEvaluation(evaluationId) {
    try {
        const response = await fetchAPI(`/evaluations/${evaluationId}/verify`, {
            method: 'POST'
        });
        
        if (response && response.success) {
            alert('تم التحقق من التقييم بنجاح');
            window.location.reload();
        } else {
            throw new Error(response.message || 'فشل في التحقق من التقييم');
        }
    } catch (error) {
        console.error('Verification Error:', error);
        alert(`خطأ في التحقق: ${error.message || 'حدث خطأ غير معروف'}`);
    }
}

// تصدير نتائج التقييم
function exportEvaluation(evaluationId) {
    window.open(`${API_URL}/evaluations/${evaluationId}/export`, '_blank');
}

// عرض بيانات لوحة القياسات
async function loadDashboardData() {
    if (!isAuthenticated()) return;
    
    try {
        // الحصول على إحصائيات المستخدم
        const userStats = await fetchAPI('/user/stats');
        
        if (userStats) {
            // تحديث عناصر واجهة المستخدم
            const evaluationsCount = document.getElementById('evaluations-count');
            if (evaluationsCount) evaluationsCount.textContent = userStats.evaluations_count || 0;
            
            const verifiedCount = document.getElementById('verified-count');
            if (verifiedCount) verifiedCount.textContent = userStats.verified_count || 0;
            
            // عرض أحدث التقييمات
            loadRecentEvaluations(userStats.recent_evaluations);
        }
        
        // إذا كان المستخدم مسؤولاً، الحصول على إحصائيات إضافية
        const currentUser = getCurrentUser();
        if (currentUser && (currentUser.role === 'admin' || currentUser.role === 'teacher')) {
            const adminStats = await fetchAPI('/admin/stats');
            
            if (adminStats) {
                const usersCount = document.getElementById('users-count');
                if (usersCount) usersCount.textContent = adminStats.users_count || 0;
                
                const rubricsCount = document.getElementById('rubrics-count');
                if (rubricsCount) rubricsCount.textContent = adminStats.rubrics_count || 0;
            }
        }
    } catch (error) {
        console.error('Dashboard Data Error:', error);
    }
}

// عرض أحدث التقييمات في الجدول
function loadRecentEvaluations(evaluations) {
    const tableBody = document.getElementById('recent-evaluations-table');
    if (!tableBody || !evaluations || !evaluations.length) {
        if (tableBody) {
            tableBody.innerHTML = '<tr><td colspan="6" class="text-center">لا توجد تقييمات حديثة</td></tr>';
        }
        return;
    }
    
    tableBody.innerHTML = evaluations.map(evaluation => `
        <tr>
            <td>${evaluation.id}</td>
            <td>تقييم BTEC</td>
            <td><span class="badge ${getBadgeClassForGrade(evaluation.grade)}">${evaluation.grade || '-'}</span></td>
            <td>
                ${evaluation.verification_status ? 
                    '<span class="badge badge-success">تم التحقق</span>' : 
                    '<span class="badge badge-warning">لم يتم التحقق</span>'}
            </td>
            <td>${formatDate(evaluation.evaluated_at || evaluation.submitted_at)}</td>
            <td>
                <a href="/evaluations/${evaluation.id}" class="btn btn-sm">
                    <svg class="svg-icon">
                        <use href="#icon-evaluation"></use>
                    </svg>
                    عرض
                </a>
            </td>
        </tr>
    `).join('');
}

// تنسيق التاريخ
function formatDate(dateString) {
    if (!dateString) return '-';
    
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('ar-EG', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(date);
}

// الحصول على فئة الشارة المناسبة للدرجة
function getBadgeClassForGrade(grade) {
    if (!grade) return 'badge-secondary';
    
    if (grade.includes('Pass') || grade.includes('ناجح')) {
        if (grade.includes('Distinction') || grade.includes('امتياز')) {
            return 'badge-success';
        } else if (grade.includes('Merit') || grade.includes('جيد')) {
            return 'badge-info';
        } else {
            return 'badge-primary';
        }
    } else {
        return 'badge-danger';
    }
}

// تحميل بيانات صفحة تفاصيل التقييم
async function loadEvaluationDetails() {
    if (!isAuthenticated()) return;
    
    // استخراج معرف التقييم من عنوان URL
    const pathParts = window.location.pathname.split('/');
    const evaluationId = pathParts[pathParts.length - 1];
    
    if (!evaluationId || isNaN(parseInt(evaluationId))) return;
    
    try {
        const evaluation = await fetchAPI(`/evaluations/${evaluationId}`);
        
        if (evaluation) {
            // تحديث المعرف في العنوان
            const idElement = document.getElementById('evaluation-id');
            if (idElement) idElement.textContent = evaluation.id;
            
            const idTitleElement = document.getElementById('evaluation-id-title');
            if (idTitleElement) idTitleElement.textContent = `#${evaluation.id}`;
            
            // تحديث التاريخ
            const dateElement = document.getElementById('evaluation-date');
            if (dateElement) dateElement.textContent = formatDate(evaluation.evaluated_at || evaluation.submitted_at);
            
            // تحديث حالة التحقق
            const statusElement = document.getElementById('verification-status');
            if (statusElement) {
                statusElement.innerHTML = evaluation.verification_status ? 
                    '<span class="badge badge-success">تم التحقق</span>' : 
                    '<span class="badge badge-warning">لم يتم التحقق</span>';
            }
            
            // تحديث الدرجة
            const gradeNumericalElement = document.getElementById('grade-numerical');
            if (gradeNumericalElement) gradeNumericalElement.textContent = evaluation.grade_numerical || '-';
            
            const gradeTextElement = document.getElementById('grade-text');
            if (gradeTextElement) gradeTextElement.textContent = evaluation.grade || '-';
            
            // تحديث معلومات التحقق
            const verificationStatusElement = document.getElementById('verification-card-status');
            if (verificationStatusElement) {
                verificationStatusElement.innerHTML = evaluation.verification_status ? 
                    `<div class="status-badge verified">
                        <svg class="svg-icon">
                            <use href="#icon-success"></use>
                        </svg>
                        تم التحقق
                    </div>` : 
                    `<div class="status-badge unverified">
                        <svg class="svg-icon">
                            <use href="#icon-warning"></use>
                        </svg>
                        لم يتم التحقق بعد
                    </div>`;
            }
            
            const auditHashElement = document.getElementById('audit-hash');
            if (auditHashElement) auditHashElement.textContent = evaluation.audit_hash || 'لا يوجد';
            
            const verificationTimestampElement = document.getElementById('verification-timestamp');
            if (verificationTimestampElement) {
                verificationTimestampElement.textContent = evaluation.verification_timestamp ? 
                    `وقت التحقق: ${formatDate(evaluation.verification_timestamp)}` : 
                    'لم يتم التحقق بعد';
            }
            
            // تحديث محتوى المهمة
            const taskContentElement = document.getElementById('task-content');
            if (taskContentElement) taskContentElement.innerHTML = `<p>${evaluation.task || 'لا يوجد محتوى'}</p>`;
            
            // تحديث ملاحظات التقييم
            const feedbackContentElement = document.getElementById('feedback-content');
            if (feedbackContentElement) feedbackContentElement.innerHTML = `<p>${evaluation.feedback || 'لا توجد ملاحظات'}</p>`;
            
            // تحديث نتائج معايير التقييم
            const rubricResultsElement = document.getElementById('rubric-results');
            if (rubricResultsElement) {
                if (evaluation.rubric_results) {
                    try {
                        const rubricData = typeof evaluation.rubric_results === 'string' ? 
                            JSON.parse(evaluation.rubric_results) : evaluation.rubric_results;
                        
                        let rubricHTML = '<div class="rubric-criteria">';
                        
                        Object.entries(rubricData).forEach(([criterion, data]) => {
                            rubricHTML += `
                                <div class="rubric-criterion">
                                    <div class="criterion-header">
                                        <div class="criterion-name">${criterion}</div>
                                        <div class="criterion-score">${data.score || '-'}/100</div>
                                    </div>
                                    <div class="criterion-description">${data.description || 'لا يوجد وصف'}</div>
                                    <div class="criterion-feedback">${data.feedback || 'لا توجد ملاحظات'}</div>
                                </div>
                            `;
                        });
                        
                        rubricHTML += '</div>';
                        rubricResultsElement.innerHTML = rubricHTML;
                    } catch (error) {
                        console.error('Error parsing rubric results:', error);
                        rubricResultsElement.innerHTML = '<p>خطأ في عرض نتائج معايير التقييم</p>';
                    }
                } else {
                    rubricResultsElement.innerHTML = '<p>لا توجد نتائج لمعايير التقييم</p>';
                }
            }
            
            // تفعيل زر التحقق
            const verifyBtn = document.getElementById('verify-btn');
            if (verifyBtn) {
                verifyBtn.addEventListener('click', () => verifyEvaluation(evaluation.id));
                
                // تعطيل الزر إذا كان التقييم متحقق منه بالفعل
                if (evaluation.verification_status) {
                    verifyBtn.disabled = true;
                    verifyBtn.classList.add('btn-disabled');
                    verifyBtn.innerHTML = `
                        <svg class="svg-icon">
                            <use href="#icon-success"></use>
                        </svg>
                        تم التحقق
                    `;
                }
            }
            
            // تفعيل زر التصدير
            const exportBtn = document.getElementById('export-btn');
            if (exportBtn) {
                exportBtn.addEventListener('click', () => exportEvaluation(evaluation.id));
            }
        }
    } catch (error) {
        console.error('Evaluation Details Error:', error);
    }
}

// تحميل قائمة التقييمات
async function loadEvaluationsList() {
    if (!isAuthenticated()) return;
    
    try {
        // الحصول على معلمات البحث من URL
        const urlParams = new URLSearchParams(window.location.search);
        const page = parseInt(urlParams.get('page')) || 1;
        const searchQuery = urlParams.get('q') || '';
        const status = urlParams.get('status') || '';
        const fromDate = urlParams.get('from') || '';
        const toDate = urlParams.get('to') || '';
        
        // تحديث نموذج البحث إذا كان موجوداً
        const searchQueryInput = document.getElementById('search-query');
        if (searchQueryInput) searchQueryInput.value = searchQuery;
        
        const filterStatusSelect = document.getElementById('filter-status');
        if (filterStatusSelect) filterStatusSelect.value = status;
        
        const filterDateFromInput = document.getElementById('filter-date-from');
        if (filterDateFromInput) filterDateFromInput.value = fromDate;
        
        const filterDateToInput = document.getElementById('filter-date-to');
        if (filterDateToInput) filterDateToInput.value = toDate;
        
        // طلب التقييمات
        const evaluations = await fetchAPI(`/evaluations?page=${page}&q=${searchQuery}&status=${status}&from=${fromDate}&to=${toDate}`);
        
        if (evaluations && evaluations.data) {
            // تحديث جدول التقييمات
            const tableBody = document.getElementById('evaluations-table');
            if (tableBody) {
                if (evaluations.data.length > 0) {
                    tableBody.innerHTML = evaluations.data.map(evaluation => `
                        <tr>
                            <td>${evaluation.id}</td>
                            <td>${truncateText(evaluation.task || 'لا يوجد محتوى', 50)}</td>
                            <td><span class="badge ${getBadgeClassForGrade(evaluation.grade)}">${evaluation.grade || '-'}</span></td>
                            <td>${evaluation.grade_numerical || '-'}</td>
                            <td>${formatDate(evaluation.evaluated_at || evaluation.submitted_at)}</td>
                            <td>
                                ${evaluation.verification_status ? 
                                    '<span class="badge badge-success">تم التحقق</span>' : 
                                    '<span class="badge badge-warning">لم يتم التحقق</span>'}
                            </td>
                            <td>
                                <a href="/evaluations/${evaluation.id}" class="btn btn-sm">
                                    <svg class="svg-icon">
                                        <use href="#icon-evaluation"></use>
                                    </svg>
                                    عرض
                                </a>
                                <button class="btn btn-sm" onclick="showEvaluationDetails(${evaluation.id})">
                                    <svg class="svg-icon">
                                        <use href="#icon-search"></use>
                                    </svg>
                                    تفاصيل
                                </button>
                            </td>
                        </tr>
                    `).join('');
                } else {
                    tableBody.innerHTML = '<tr><td colspan="7" class="text-center">لا توجد تقييمات</td></tr>';
                }
            }
            
            // تحديث ترقيم الصفحات
            const paginationElement = document.getElementById('pagination-pages');
            if (paginationElement && evaluations.pagination) {
                let paginationHTML = '';
                
                for (let i = 1; i <= evaluations.pagination.total_pages; i++) {
                    const isActivePage = i === evaluations.pagination.current_page;
                    paginationHTML += `
                        <a href="?page=${i}&q=${searchQuery}&status=${status}&from=${fromDate}&to=${toDate}" 
                           class="pagination-page ${isActivePage ? 'active' : ''}">
                            ${i}
                        </a>
                    `;
                }
                
                paginationElement.innerHTML = paginationHTML;
            }
        }
    } catch (error) {
        console.error('Evaluations List Error:', error);
        
        const tableBody = document.getElementById('evaluations-table');
        if (tableBody) {
            tableBody.innerHTML = '<tr><td colspan="7" class="text-center">حدث خطأ في تحميل التقييمات</td></tr>';
        }
    }
}

// اقتطاع النص الطويل
function truncateText(text, maxLength) {
    if (!text) return '';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
}

// عرض تفاصيل التقييم في نافذة منبثقة
async function showEvaluationDetails(evaluationId) {
    try {
        const evaluation = await fetchAPI(`/evaluations/${evaluationId}`);
        
        if (evaluation) {
            const modal = document.getElementById('evaluation-details-modal');
            const modalBody = document.getElementById('evaluation-details-body');
            
            if (modal && modalBody) {
                modalBody.innerHTML = `
                    <h3>تفاصيل التقييم #${evaluation.id}</h3>
                    
                    <div class="modal-section">
                        <h4>محتوى المهمة</h4>
                        <div class="task-preview">${evaluation.task || 'لا يوجد محتوى'}</div>
                    </div>
                    
                    <div class="modal-section">
                        <h4>نتيجة التقييم</h4>
                        <div class="result-card">
                            <div class="grade-display">
                                <div class="grade-circle">${evaluation.grade_numerical || '-'}</div>
                                <div class="grade-info">
                                    <h3>${evaluation.grade || '-'}</h3>
                                    <p>تاريخ التقييم: ${formatDate(evaluation.evaluated_at || evaluation.submitted_at)}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="modal-section">
                        <h4>ملاحظات التقييم</h4>
                        <div class="evaluation-feedback">${evaluation.feedback || 'لا توجد ملاحظات'}</div>
                    </div>
                `;
                
                // تفعيل أزرار النافذة المنبثقة
                const modalVerifyBtn = document.getElementById('modal-verify-btn');
                if (modalVerifyBtn) {
                    modalVerifyBtn.onclick = () => verifyEvaluation(evaluation.id);
                    
                    // تعطيل الزر إذا كان التقييم متحقق منه بالفعل
                    if (evaluation.verification_status) {
                        modalVerifyBtn.disabled = true;
                        modalVerifyBtn.classList.add('btn-disabled');
                        modalVerifyBtn.innerHTML = `
                            <svg class="svg-icon">
                                <use href="#icon-success"></use>
                            </svg>
                            تم التحقق
                        `;
                    }
                }
                
                const modalExportBtn = document.getElementById('modal-export-btn');
                if (modalExportBtn) {
                    modalExportBtn.onclick = () => exportEvaluation(evaluation.id);
                }
                
                // عرض النافذة المنبثقة
                modal.classList.add('show');
                
                // تفعيل زر الإغلاق
                const closeButtons = modal.querySelectorAll('.modal-close');
                closeButtons.forEach(button => {
                    button.onclick = () => {
                        modal.classList.remove('show');
                    };
                });
            }
        }
    } catch (error) {
        console.error('Evaluation Details Modal Error:', error);
        alert('حدث خطأ في تحميل تفاصيل التقييم');
    }
}

// إعداد المستمعين للأحداث عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    // تحديث واجهة المستخدم بناءً على حالة المصادقة
    updateUIBasedOnAuth();
    
    // تفعيل تأثيرات الحركة
    animateElements();
    
    // تفعيل تبديل القائمة في الأجهزة الصغيرة
    const navToggle = document.querySelector('.nav-toggle');
    if (navToggle) {
        navToggle.addEventListener('click', toggleMobileMenu);
    }
    
    // تفعيل زر تسجيل الخروج
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(event) {
            event.preventDefault();
            logout();
        });
    }
    
    // تفعيل نموذج تسجيل الدخول
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // تفعيل نموذج التسجيل
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
    
    // تفعيل نموذج التقييم
    const evaluationForm = document.getElementById('evaluation-form');
    if (evaluationForm) {
        evaluationForm.addEventListener('submit', handleEvaluation);
    }
    
    // تحميل بيانات لوحة القياسات إذا كنا في صفحة لوحة التحكم
    if (window.location.pathname === '/dashboard') {
        loadDashboardData();
    }
    
    // تحميل تفاصيل التقييم إذا كنا في صفحة تفاصيل التقييم
    if (window.location.pathname.startsWith('/evaluations/') && !window.location.pathname.endsWith('/evaluations/')) {
        loadEvaluationDetails();
    }
    
    // تحميل قائمة التقييمات إذا كنا في صفحة التقييمات
    if (window.location.pathname === '/evaluations') {
        loadEvaluationsList();
    }
    
    // تفعيل نموذج البحث في صفحة التقييمات
    const searchForm = document.getElementById('search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            const searchQuery = document.getElementById('search-query').value;
            const filterStatus = document.getElementById('filter-status').value;
            const filterDateFrom = document.getElementById('filter-date-from').value;
            const filterDateTo = document.getElementById('filter-date-to').value;
            
            window.location.href = `/evaluations?q=${searchQuery}&status=${filterStatus}&from=${filterDateFrom}&to=${filterDateTo}`;
        });
    }
});

// أنماط CSS إضافية
document.head.insertAdjacentHTML('beforeend', `
<style>
    /* شارات الحالة */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: var(--radius-full);
        font-size: 0.75rem;
        font-weight: 600;
        text-align: center;
        white-space: nowrap;
        vertical-align: baseline;
    }
    
    .badge-primary {
        background-color: rgba(59, 130, 246, 0.1);
        color: var(--primary-color);
    }
    
    .badge-success {
        background-color: rgba(16, 185, 129, 0.1);
        color: var(--success-color);
    }
    
    .badge-warning {
        background-color: rgba(245, 158, 11, 0.1);
        color: var(--warning-color);
    }
    
    .badge-danger {
        background-color: rgba(239, 68, 68, 0.1);
        color: var(--danger-color);
    }
    
    .badge-info {
        background-color: rgba(14, 165, 233, 0.1);
        color: #0EA5E9;
    }
    
    .badge-secondary {
        background-color: rgba(100, 116, 139, 0.1);
        color: var(--text-secondary);
    }
    
    /* أزرار معطلة */
    .btn-disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }
    
    /* النافذة المنبثقة - أنماط إضافية */
    .modal-section {
        margin-bottom: 1.5rem;
    }
    
    .modal-section h4 {
        margin-bottom: 0.75rem;
        color: var(--primary-color);
        font-size: 1.1rem;
    }
    
    .result-card {
        background-color: var(--off-white);
        padding: 1.5rem;
        border-radius: var(--radius-md);
    }
    
    .grade-info h3 {
        margin-bottom: 0.5rem;
    }
    
    .grade-info p {
        margin-bottom: 0;
        font-size: 0.9rem;
        color: var(--text-secondary);
    }
    
    .grade-circle {
        width: 80px;
        height: 80px;
        margin-right: 1.5rem;
    }
</style>
`);
