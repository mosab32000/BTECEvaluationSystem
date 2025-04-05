/**
 * الملف الرئيسي للجافاسكريبت في نظام تقييم BTEC
 */

// انتظار حتى تحميل الصفحة بالكامل
document.addEventListener('DOMContentLoaded', function() {
    console.log('تم تحميل نظام تقييم BTEC بنجاح!');
    
    // إخفاء رسائل الفلاش تلقائياً بعد 5 ثوانٍ
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(alert => {
            if (alert.querySelector('.btn-close')) {
                const closeButton = alert.querySelector('.btn-close');
                closeButton.click();
            }
        });
    }, 5000);
    
    // تمكين التمرير السلس للروابط الداخلية
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // إضافة تنشيط لعنصر القائمة النشط
    const currentLocation = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        if (linkPath === currentLocation || 
            (linkPath !== '/' && currentLocation.startsWith(linkPath))) {
            link.classList.add('active');
        }
    });
    
    // تهيئة نماذج التقييم إذا كانت موجودة
    setupEvaluationForms();
});

/**
 * تهيئة نماذج التقييم ومعالجة الأحداث المرتبطة بها
 */
function setupEvaluationForms() {
    // نموذج التقييم الجديد
    const newEvaluationForm = document.getElementById('newEvaluationForm');
    if (newEvaluationForm) {
        newEvaluationForm.addEventListener('submit', function(e) {
            const taskDescription = document.getElementById('task_description');
            const submissionText = document.getElementById('submission_text');
            
            if (!taskDescription.value.trim() || !submissionText.value.trim()) {
                e.preventDefault();
                alert('يرجى ملء جميع الحقول المطلوبة');
            }
        });
        
        // عرض/إخفاء اختيار معايير التقييم عند تحديد "استخدام الذكاء الاصطناعي"
        const useAiCheckbox = document.getElementById('use_ai');
        const rubricSection = document.getElementById('rubric-section');
        
        if (useAiCheckbox && rubricSection) {
            useAiCheckbox.addEventListener('change', function() {
                rubricSection.style.display = this.checked ? 'block' : 'none';
            });
        }
    }
    
    // نموذج التقييم اليدوي
    const manualGradeForm = document.getElementById('manualGradeForm');
    if (manualGradeForm) {
        manualGradeForm.addEventListener('submit', function(e) {
            const grade = document.getElementById('grade');
            const feedback = document.getElementById('feedback');
            
            if (!grade.value || !feedback.value.trim()) {
                e.preventDefault();
                alert('يرجى إدخال الدرجة والتغذية الراجعة');
            } else if (parseFloat(grade.value) < 0 || parseFloat(grade.value) > 100) {
                e.preventDefault();
                alert('يجب أن تكون الدرجة بين 0 و 100');
            }
        });
    }
}

/**
 * تأكيد حذف عنصر
 * @param {string} message رسالة التأكيد
 * @returns {boolean} true إذا أكد المستخدم، وإلا false
 */
function confirmDelete(message) {
    return confirm(message || 'هل أنت متأكد من رغبتك في الحذف؟');
}

/**
 * تحميل تقييم باستخدام الذكاء الاصطناعي
 * @param {number} evaluationId معرف التقييم
 */
function loadAiEvaluation(evaluationId) {
    // عرض مؤشر التحميل
    const loadingElement = document.getElementById('ai-loading');
    if (loadingElement) {
        loadingElement.style.display = 'block';
    }
    
    // نقل المستخدم إلى صفحة التقييم بالذكاء الاصطناعي
    window.location.href = `/evaluation/${evaluationId}/ai-evaluate`;
}

/**
 * تحقق من التقييم باستخدام البلوكتشين
 * @param {number} evaluationId معرف التقييم
 */
function verifyEvaluation(evaluationId) {
    // عرض مؤشر التحميل
    const loadingElement = document.getElementById('blockchain-loading');
    if (loadingElement) {
        loadingElement.style.display = 'block';
    }
    
    // نقل المستخدم إلى صفحة التحقق بالبلوكتشين
    window.location.href = `/evaluation/${evaluationId}/verify`;
}
