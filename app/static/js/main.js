/**
 * نظام تقييم BTEC - ملف جافاسكريبت الرئيسي
 */

// يتم تنفيذ الكود عند اكتمال تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    console.log('تم تحميل صفحة نظام تقييم BTEC');
    
    // إعداد إغلاق رسائل التنبيه تلقائيًا بعد فترة
    setupAlertDismissal();
    
    // إعداد تحديث حقول الإدخال عند التغيير
    setupFormValidation();
    
    // إعداد مؤثرات التمرير
    setupScrollEffects();
});

/**
 * إعداد إغلاق رسائل التنبيه تلقائيًا بعد فترة
 */
function setupAlertDismissal() {
    // العثور على جميع رسائل التنبيه
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    
    // إعداد مؤقت لإغلاق كل تنبيه بعد 5 ثوانٍ
    alerts.forEach(alert => {
        setTimeout(() => {
            // التحقق من أن التنبيه لا يزال موجودًا في الصفحة
            if (alert && alert.parentNode) {
                // إنشاء كائن Bootstrap لإغلاق التنبيه
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    });
}

/**
 * إعداد التحقق من النماذج وتحديثها
 */
function setupFormValidation() {
    // العثور على جميع النماذج في الصفحة
    const forms = document.querySelectorAll('form.needs-validation');
    
    // إعداد أحداث التحقق لكل نموذج
    forms.forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        });
    });
    
    // إعداد مطابقة كلمات المرور في نماذج التسجيل
    const passwordForms = document.querySelectorAll('form.password-validation');
    passwordForms.forEach(form => {
        const password = form.querySelector('input[name="password"]');
        const confirmPassword = form.querySelector('input[name="confirm_password"]');
        
        if (password && confirmPassword) {
            confirmPassword.addEventListener('input', () => {
                if (password.value !== confirmPassword.value) {
                    confirmPassword.setCustomValidity('كلمات المرور غير متطابقة');
                } else {
                    confirmPassword.setCustomValidity('');
                }
            });
            
            password.addEventListener('input', () => {
                if (confirmPassword.value) {
                    if (password.value !== confirmPassword.value) {
                        confirmPassword.setCustomValidity('كلمات المرور غير متطابقة');
                    } else {
                        confirmPassword.setCustomValidity('');
                    }
                }
            });
        }
    });
}

/**
 * إعداد مؤثرات التمرير
 */
function setupScrollEffects() {
    // إعداد زر العودة إلى الأعلى إذا كان موجودًا
    const backToTopButton = document.querySelector('.back-to-top');
    
    if (backToTopButton) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 300) {
                backToTopButton.classList.add('show');
            } else {
                backToTopButton.classList.remove('show');
            }
        });
        
        backToTopButton.addEventListener('click', (e) => {
            e.preventDefault();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }
    
    // إضافة مؤثرات ظهور العناصر عند التمرير
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    
    if (animatedElements.length > 0) {
        // إنشاء مراقب التقاطع
        const observer = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animated');
                    // إيقاف مراقبة العنصر بعد تحريكه
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        
        // مراقبة جميع العناصر
        animatedElements.forEach(element => {
            observer.observe(element);
        });
    }
}

/**
 * إظهار مربع حوار التأكيد قبل إرسال نموذج
 * @param {string} message رسالة التأكيد
 * @param {string} formId معرف النموذج
 * @returns {boolean} إعادة true للمتابعة، أو false للإلغاء
 */
function confirmAction(message, formId) {
    if (confirm(message)) {
        const form = document.getElementById(formId);
        if (form) {
            form.submit();
        }
        return true;
    }
    return false;
}

/**
 * استرجاع البيانات عن طريق AJAX
 * @param {string} url الرابط للاستعلام
 * @param {Function} successCallback دالة الاستدعاء عند النجاح
 */
function fetchData(url, successCallback) {
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('فشل استرجاع البيانات');
            }
            return response.json();
        })
        .then(data => {
            successCallback(data);
        })
        .catch(error => {
            console.error('خطأ:', error);
        });
}
