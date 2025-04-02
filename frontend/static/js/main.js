/**
 * ملف JavaScript الرئيسي لنظام تقييم BTEC
 */

// تنفيذ الكود عند تحميل صفحة DOM بالكامل
document.addEventListener('DOMContentLoaded', function() {
    // تهيئة السلوك التفاعلي
    initInteractiveBehavior();
    
    // تعيين معالجات الأحداث لنماذج الإرسال
    setupFormHandlers();
    
    // تهيئة تأثيرات الحركة
    initAnimations();
    
    // تهيئة 3D للبطاقات
    init3DCards();
});

/**
 * تهيئة السلوك التفاعلي للعناصر
 */
function initInteractiveBehavior() {
    // تحديد الرابط النشط في القائمة الجانبية
    const currentPath = window.location.pathname;
    document.querySelectorAll('#sidebar .nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
    
    // إخفاء رسائل التنبيه بعد فترة
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert) {
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 500);
            }
        }, 4000);
    });
}

/**
 * تعيين معالجات الأحداث لنماذج الإرسال
 */
function setupFormHandlers() {
    // نموذج تسجيل الدخول
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // نموذج التسجيل
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
    
    // نموذج تقييم المهمة
    const evaluationForm = document.getElementById('evaluation-form');
    if (evaluationForm) {
        evaluationForm.addEventListener('submit', handleEvaluation);
    }
    
    // نموذج التحقق من التقييم
    const verifyForm = document.getElementById('verify-form');
    if (verifyForm) {
        verifyForm.addEventListener('submit', handleVerify);
    }
}

/**
 * معالجة نموذج تسجيل الدخول
 * @param {Event} e حدث النموذج
 */
async function handleLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    try {
        showLoading('btn-login');
        const response = await BTECApi.login({ email, password });
        
        if (response.token) {
            localStorage.setItem('token', response.token);
            localStorage.setItem('user_id', response.user_id);
            
            // إعادة توجيه المستخدم إلى لوحة التحكم
            window.location.href = '/dashboard';
        } else {
            showMessage('حدث خطأ أثناء تسجيل الدخول', 'error');
        }
    } catch (error) {
        console.error('خطأ في تسجيل الدخول:', error);
        showMessage(error.message || 'فشل تسجيل الدخول، يرجى التحقق من بيانات الاعتماد الخاصة بك', 'error');
    } finally {
        hideLoading('btn-login');
    }
}

/**
 * معالجة نموذج التسجيل
 * @param {Event} e حدث النموذج
 */
async function handleRegister(e) {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;
    
    // التحقق من تطابق كلمات المرور
    if (password !== confirmPassword) {
        showMessage('كلمات المرور غير متطابقة', 'error');
        return;
    }
    
    try {
        showLoading('btn-register');
        const response = await BTECApi.register({ email, password });
        
        if (response.success) {
            showMessage('تم التسجيل بنجاح! يرجى تسجيل الدخول الآن.', 'success');
            
            // إعادة توجيه المستخدم إلى صفحة تسجيل الدخول بعد ثانيتين
            setTimeout(() => {
                window.location.href = '/login';
            }, 2000);
        } else {
            showMessage('حدث خطأ أثناء التسجيل', 'error');
        }
    } catch (error) {
        console.error('خطأ في التسجيل:', error);
        showMessage(error.message || 'فشل التسجيل، يرجى المحاولة مرة أخرى', 'error');
    } finally {
        hideLoading('btn-register');
    }
}

/**
 * معالجة نموذج التقييم
 * @param {Event} e حدث النموذج
 */
async function handleEvaluation(e) {
    e.preventDefault();
    
    const task = document.getElementById('task-submission').value;
    const format = document.querySelector('input[name="response-format"]:checked').value;
    
    // التحقق من وجود محتوى المهمة
    if (!task.trim()) {
        showMessage('يرجى إدخال محتوى المهمة للتقييم', 'error');
        return;
    }
    
    try {
        showLoading('btn-evaluate');
        const response = await BTECApi.evaluateTask({ task, format });
        
        if (response.grade) {
            // عرض نتيجة التقييم
            showEvaluationResult(response);
        } else {
            showMessage('حدث خطأ أثناء تقييم المهمة', 'error');
        }
    } catch (error) {
        console.error('خطأ في التقييم:', error);
        showMessage(error.message || 'فشل تقييم المهمة، يرجى المحاولة مرة أخرى', 'error');
    } finally {
        hideLoading('btn-evaluate');
    }
}

/**
 * معالجة نموذج التحقق
 * @param {Event} e حدث النموذج
 */
async function handleVerify(e) {
    e.preventDefault();
    
    const auditHash = document.getElementById('audit-hash').value;
    
    if (!auditHash.trim()) {
        showMessage('يرجى إدخال رمز التحقق', 'error');
        return;
    }
    
    try {
        showLoading('btn-verify');
        const response = await BTECApi.verifyPublic(auditHash);
        
        // عرض نتيجة التحقق
        const resultContainer = document.getElementById('verification-result');
        resultContainer.innerHTML = '';
        resultContainer.style.display = 'block';
        
        if (response.verified) {
            const resultHTML = `
                <div class="verification-result verification-success animated">
                    <div class="text-center mb-4">
                        <i class="fas fa-check-circle fa-4x text-success mb-3"></i>
                        <h3>تم التحقق بنجاح!</h3>
                    </div>
                    <div class="verification-details">
                        <p class="mb-3">تم التحقق من صحة هذا التقييم على سلسلة الكتل.</p>
                        <p class="mb-2"><strong>تاريخ التقييم:</strong> ${new Date(response.evaluation_date).toLocaleString('ar-SA')}</p>
                        <p class="mb-2"><strong>الدرجة:</strong> ${response.grade}</p>
                        <div class="mt-4 p-3 border border-secondary rounded">
                            <h4>تفاصيل المعاملة:</h4>
                            <p class="mt-2 mb-1"><strong>رمز التحقق:</strong></p>
                            <p class="text-break">${response.hash}</p>
                        </div>
                    </div>
                </div>
            `;
            resultContainer.innerHTML = resultHTML;
        } else {
            const resultHTML = `
                <div class="verification-result verification-error animated">
                    <div class="text-center mb-4">
                        <i class="fas fa-times-circle fa-4x text-danger mb-3"></i>
                        <h3>فشل التحقق!</h3>
                    </div>
                    <p>تعذر التحقق من صحة هذا التقييم. الرجاء التأكد من صحة رمز التحقق.</p>
                </div>
            `;
            resultContainer.innerHTML = resultHTML;
        }
    } catch (error) {
        console.error('خطأ في التحقق:', error);
        showMessage(error.message || 'فشل التحقق، يرجى المحاولة مرة أخرى', 'error');
    } finally {
        hideLoading('btn-verify');
    }
}

/**
 * عرض نتيجة التقييم
 * @param {Object} result نتيجة التقييم
 */
function showEvaluationResult(result) {
    const resultContainer = document.getElementById('evaluation-result');
    resultContainer.style.display = 'block';
    
    if (typeof result.grade === 'object') {
        // عرض نتيجة التقييم بتنسيق JSON
        const rubricHTML = generateRubricHTML(result.grade);
        resultContainer.innerHTML = rubricHTML;
    } else {
        // عرض التقييم النصي البسيط
        resultContainer.innerHTML = `
            <div class="card card-3d animated">
                <div class="card-header">
                    <h3 class="mb-0">نتيجة التقييم</h3>
                </div>
                <div class="card-body">
                    <div class="text-center mb-4">
                        <div class="grade-indicator">${result.grade.split(' ')[0]}</div>
                        <span class="blockchain-verified"><i class="fas fa-shield-alt"></i> موثق بواسطة Blockchain</span>
                    </div>
                    <div class="evaluation-feedback">
                        <h4>التعليقات والملاحظات:</h4>
                        <div class="p-3 bg-dark rounded">
                            ${result.grade.split('\n').map(line => `<p>${line}</p>`).join('')}
                        </div>
                    </div>
                    <div class="mt-4">
                        <p><strong>رمز التحقق:</strong></p>
                        <p class="text-break">${result.audit_hash}</p>
                        <p class="text-muted">يمكن استخدام هذا الرمز للتحقق من صحة هذا التقييم في أي وقت.</p>
                    </div>
                </div>
            </div>
        `;
    }
    
    // التمرير إلى النتيجة
    resultContainer.scrollIntoView({ behavior: 'smooth' });
}

/**
 * إنشاء HTML لعرض تقييم مبني على معايير التقييم
 * @param {Object} rubricResult نتيجة التقييم بالمعايير
 * @returns {string} HTML محتوى
 */
function generateRubricHTML(rubricResult) {
    let html = `
        <div class="card card-3d animated">
            <div class="card-header">
                <h3 class="mb-0">نتيجة التقييم المفصل</h3>
            </div>
            <div class="card-body">
                <div class="text-center mb-4">
                    <div class="grade-indicator">${rubricResult.overall_grade || rubricResult.finalGrade || 'غير محدد'}</div>
                    <span class="blockchain-verified"><i class="fas fa-shield-alt"></i> موثق بواسطة Blockchain</span>
                </div>
    `;
    
    // إضافة الأقسام
    if (rubricResult.sections) {
        html += '<div class="rubric-sections mt-4">';
        
        rubricResult.sections.forEach(section => {
            html += `
                <div class="rubric-section">
                    <h4 class="rubric-title">${section.name} (${section.score}/${section.max_score})</h4>
                    <div class="progress mb-3">
                        <div class="progress-bar bg-info" role="progressbar" style="width: ${(section.score / section.max_score) * 100}%" 
                            aria-valuenow="${section.score}" aria-valuemin="0" aria-valuemax="${section.max_score}"></div>
                    </div>
                    <div class="criteria-list">
            `;
            
            section.criteria.forEach(criterion => {
                html += `
                    <div class="criteria-item">
                        <div class="d-flex justify-content-between">
                            <span>${criterion.name}</span>
                            <span class="badge ${getCriterionBadgeClass(criterion.score)}">${criterion.score}/5</span>
                        </div>
                        <p class="text-muted mt-2 mb-0">${criterion.feedback}</p>
                    </div>
                `;
            });
            
            html += `
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
    }
    
    // إضافة التعليقات العامة والمجالات التي تحتاج إلى تحسين
    if (rubricResult.feedback || rubricResult.general_feedback) {
        html += `
            <div class="mt-4">
                <h4>التعليق العام:</h4>
                <div class="p-3 bg-dark rounded">
                    <p>${rubricResult.feedback || rubricResult.general_feedback}</p>
                </div>
            </div>
        `;
    }
    
    if (rubricResult.areas_for_improvement || rubricResult.improvement_areas) {
        const areas = rubricResult.areas_for_improvement || rubricResult.improvement_areas;
        html += `
            <div class="mt-4">
                <h4>مجالات للتحسين:</h4>
                <ul class="list-group">
        `;
        
        if (Array.isArray(areas)) {
            areas.forEach(area => {
                html += `<li class="list-group-item bg-dark">${area}</li>`;
            });
        } else {
            html += `<li class="list-group-item bg-dark">${areas}</li>`;
        }
        
        html += `
                </ul>
            </div>
        `;
    }
    
    // إضافة رمز التحقق
    html += `
            <div class="mt-4">
                <p><strong>رمز التحقق:</strong></p>
                <p class="text-break">${rubricResult.audit_hash}</p>
                <p class="text-muted">يمكن استخدام هذا الرمز للتحقق من صحة هذا التقييم في أي وقت.</p>
            </div>
        </div>
    </div>
    `;
    
    return html;
}

/**
 * الحصول على فئة البادج المناسبة لدرجة المعيار
 * @param {number} score درجة المعيار
 * @returns {string} فئة CSS
 */
function getCriterionBadgeClass(score) {
    if (score >= 4) return 'bg-success';
    if (score >= 3) return 'bg-info';
    if (score >= 2) return 'bg-warning';
    return 'bg-danger';
}

/**
 * تحميل قائمة التقييمات السابقة
 */
async function loadEvaluations() {
    const evaluationsContainer = document.getElementById('evaluations-list');
    if (!evaluationsContainer) return;
    
    try {
        showLoading('evaluations-container');
        const evaluations = await BTECApi.getEvaluations();
        
        if (evaluations && evaluations.length > 0) {
            let html = '';
            
            evaluations.forEach(evaluation => {
                const submittedDate = new Date(evaluation.submitted_at).toLocaleString('ar-SA');
                
                html += `
                    <div class="col-md-6 mb-4">
                        <div class="card card-3d h-100">
                            <div class="card-header d-flex justify-content-between align-items-center">
                                <h5 class="mb-0">تقييم #${evaluation.id}</h5>
                                <span class="badge bg-info">${evaluation.grade.split(' ')[0]}</span>
                            </div>
                            <div class="card-body">
                                <p class="text-muted mb-3">تاريخ التقديم: ${submittedDate}</p>
                                <div class="d-grid gap-2">
                                    <a href="/evaluation/${evaluation.id}" class="btn btn-primary">
                                        <i class="fas fa-eye"></i> عرض التفاصيل
                                    </a>
                                    <button class="btn btn-secondary" onclick="verifyEvaluation(${evaluation.id})">
                                        <i class="fas fa-shield-alt"></i> التحقق من صحة التقييم
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            evaluationsContainer.innerHTML = html;
        } else {
            evaluationsContainer.innerHTML = `
                <div class="col-12">
                    <div class="alert alert-info text-center">
                        <i class="fas fa-info-circle fa-2x mb-3"></i>
                        <h4>لا توجد تقييمات سابقة</h4>
                        <p>لم تقم بإجراء أي تقييمات بعد. يمكنك البدء بتقييم مهمة جديدة من صفحة التقييم.</p>
                        <a href="/evaluate" class="btn btn-primary mt-3">إنشاء تقييم جديد</a>
                    </div>
                </div>
            `;
        }
    } catch (error) {
        console.error('خطأ في تحميل التقييمات:', error);
        evaluationsContainer.innerHTML = `
            <div class="col-12">
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle"></i>
                    حدث خطأ أثناء تحميل التقييمات. يرجى المحاولة مرة أخرى.
                </div>
            </div>
        `;
    } finally {
        hideLoading('evaluations-container');
    }
}

/**
 * تحميل تفاصيل تقييم محدد
 * @param {number} evaluationId معرف التقييم
 */
async function loadEvaluationDetail(evaluationId) {
    const detailContainer = document.getElementById('evaluation-detail');
    if (!detailContainer) return;
    
    try {
        showLoading('detail-container');
        const evaluation = await BTECApi.getEvaluation(evaluationId);
        
        if (evaluation) {
            const submittedDate = new Date(evaluation.submitted_at).toLocaleString('ar-SA');
            
            let html = `
                <div class="evaluation-detail animated">
                    <div class="text-center mb-4">
                        <div class="grade-indicator">${evaluation.grade.split(' ')[0]}</div>
                        <span class="blockchain-verified"><i class="fas fa-shield-alt"></i> موثق بواسطة Blockchain</span>
                    </div>
                    
                    <div class="row mt-4">
                        <div class="col-md-6">
                            <p><strong>رقم التقييم:</strong> #${evaluation.id}</p>
                        </div>
                        <div class="col-md-6">
                            <p><strong>تاريخ التقديم:</strong> ${submittedDate}</p>
                        </div>
                    </div>
                    
                    <div class="mt-4">
                        <h4>نص المهمة المقدمة:</h4>
                        <div class="p-3 bg-dark rounded">
                            <pre class="mb-0">${evaluation.task}</pre>
                        </div>
                    </div>
                    
                    <div class="mt-4">
                        <h4>التقييم:</h4>
                        <div class="p-3 bg-dark rounded">
                            ${evaluation.grade.split('\n').map(line => `<p>${line}</p>`).join('')}
                        </div>
                    </div>
                    
                    <div class="mt-4">
                        <p><strong>رمز التحقق:</strong></p>
                        <p class="text-break">${evaluation.audit_hash}</p>
                    </div>
                    
                    <div class="mt-4 text-center">
                        <button class="btn btn-primary" onclick="verifyEvaluation(${evaluation.id})">
                            <i class="fas fa-shield-alt"></i> التحقق من صحة التقييم
                        </button>
                    </div>
                </div>
            `;
            
            detailContainer.innerHTML = html;
        } else {
            detailContainer.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle"></i>
                    لم يتم العثور على التقييم المطلوب.
                </div>
            `;
        }
    } catch (error) {
        console.error('خطأ في تحميل تفاصيل التقييم:', error);
        detailContainer.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle"></i>
                حدث خطأ أثناء تحميل تفاصيل التقييم. يرجى المحاولة مرة أخرى.
            </div>
        `;
    } finally {
        hideLoading('detail-container');
    }
}

/**
 * التحقق من صحة تقييم
 * @param {number} evaluationId معرف التقييم
 */
async function verifyEvaluation(evaluationId) {
    try {
        const response = await BTECApi.verifyEvaluation(evaluationId);
        
        let message, type;
        if (response.verified) {
            message = 'تم التحقق بنجاح! هذا التقييم موثق وصحيح على سلسلة الكتل.';
            type = 'success';
        } else {
            message = 'فشل التحقق! لا يمكن التحقق من صحة هذا التقييم.';
            type = 'error';
        }
        
        showMessage(message, type);
    } catch (error) {
        console.error('خطأ في التحقق:', error);
        showMessage('حدث خطأ أثناء التحقق من صحة التقييم.', 'error');
    }
}

/**
 * عرض مؤشر التحميل
 * @param {string} elementId معرف العنصر
 */
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    if (element.tagName === 'BUTTON') {
        // حفظ النص الأصلي للزر
        element.dataset.originalText = element.innerHTML;
        element.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> جاري التحميل...';
        element.disabled = true;
    } else {
        // إضافة مؤشر تحميل إلى الحاوية
        const loader = document.createElement('div');
        loader.className = 'text-center my-5';
        loader.id = `${elementId}-loader`;
        loader.innerHTML = `
            <div class="spinner-border text-info" role="status">
                <span class="visually-hidden">جاري التحميل...</span>
            </div>
            <p class="mt-2">جاري التحميل...</p>
        `;
        
        element.prepend(loader);
    }
}

/**
 * إخفاء مؤشر التحميل
 * @param {string} elementId معرف العنصر
 */
function hideLoading(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    if (element.tagName === 'BUTTON') {
        // استعادة النص الأصلي للزر
        element.innerHTML = element.dataset.originalText || 'تنفيذ';
        element.disabled = false;
    } else {
        // إزالة مؤشر التحميل من الحاوية
        const loader = document.getElementById(`${elementId}-loader`);
        if (loader) {
            loader.remove();
        }
    }
}

/**
 * عرض رسالة للمستخدم
 * @param {string} message نص الرسالة
 * @param {string} type نوع الرسالة (success, error, info)
 */
function showMessage(message, type = 'info') {
    // تحويل نوع الرسالة إلى فئة Bootstrap Alert
    let alertClass;
    switch (type) {
        case 'success':
            alertClass = 'alert-success';
            break;
        case 'error':
            alertClass = 'alert-danger';
            break;
        default:
            alertClass = 'alert-info';
    }
    
    // إنشاء عنصر التنبيه
    const alertElement = document.createElement('div');
    alertElement.className = `alert ${alertClass} alert-dismissible fade show animated`;
    alertElement.role = 'alert';
    alertElement.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="إغلاق"></button>
    `;
    
    // إضافة التنبيه إلى بداية المحتوى
    const contentContainer = document.querySelector('.content-container');
    contentContainer.prepend(alertElement);
    
    // إزالة التنبيه تلقائيًا بعد 5 ثوانٍ
    setTimeout(() => {
        alertElement.classList.remove('show');
        setTimeout(() => alertElement.remove(), 300);
    }, 5000);
}

/**
 * تهيئة تأثيرات الحركة
 */
function initAnimations() {
    // تطبيق الحركة على العناصر عند ظهورها في العرض
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    // العناصر التي سيتم تطبيق الحركة عليها
    const animatableElements = document.querySelectorAll('.card, .feature-card, .hero-section h1, .evaluation-detail');
    animatableElements.forEach(el => {
        observer.observe(el);
    });
}

/**
 * تهيئة تأثير 3D للبطاقات
 */
function init3DCards() {
    const cards = document.querySelectorAll('.card-3d');
    
    cards.forEach(card => {
        card.addEventListener('mousemove', e => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const rotateX = (y - centerY) / 20;
            const rotateY = (centerX - x) / 20;
            
            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0)';
        });
    });
}