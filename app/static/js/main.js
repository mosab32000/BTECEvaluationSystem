/**
 * نظام تقييم BTEC - الوظائف JavaScript الرئيسية
 */

document.addEventListener('DOMContentLoaded', function() {
    // إظهار الرسائل التنبيهية لمدة محددة ثم إخفاؤها
    const alerts = document.querySelectorAll('.alert');
    if (alerts.length > 0) {
        setTimeout(function() {
            alerts.forEach(function(alert) {
                // إزالة التنبيه بأسلوب متدرج
                alert.style.transition = 'opacity 0.5s ease';
                alert.style.opacity = '0';
                setTimeout(function() {
                    alert.remove();
                }, 500);
            });
        }, 5000);
    }

    // تنشيط مؤشرات الشرح (Tooltips)
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // التحقق من صحة كلمة المرور في صفحة التسجيل
    const passwordField = document.getElementById('password');
    const confirmPasswordField = document.getElementById('confirm_password');
    
    if (passwordField && confirmPasswordField) {
        function validatePassword() {
            if (passwordField.value != confirmPasswordField.value) {
                confirmPasswordField.setCustomValidity('كلمات المرور غير متطابقة');
            } else {
                confirmPasswordField.setCustomValidity('');
            }
        }

        passwordField.addEventListener('change', validatePassword);
        confirmPasswordField.addEventListener('keyup', validatePassword);
    }

    // إضافة تأثيرات بصرية لعناصر القائمة عند التمرير
    document.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar');
        if (navbar) {
            if (window.scrollY > 50) {
                navbar.classList.add('navbar-scrolled');
            } else {
                navbar.classList.remove('navbar-scrolled');
            }
        }
    });

    // تتبع نقرات الزر بهدف تحليل السلوك (Analytics)
    const trackButtons = document.querySelectorAll('[data-track]');
    trackButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            const action = button.getAttribute('data-track');
            // يمكن إضافة كود تتبع هنا (مثل Google Analytics)
            console.log('تتبع الحدث:', action);
        });
    });
});

/**
 * وظيفة للتأكد من موافقة المستخدم على عملية مهمة
 * 
 * @param {string} message رسالة التأكيد
 * @returns {boolean} نتيجة التأكيد
 */
function confirmAction(message) {
    return confirm(message || 'هل أنت متأكد من هذا الإجراء؟');
}

/**
 * وظيفة لعرض تنبيه للمستخدم
 * 
 * @param {string} message الرسالة المراد عرضها
 * @param {string} type نوع التنبيه (success, error, warning)
 */
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="إغلاق"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // إزالة التنبيه تلقائيًا بعد 5 ثوانٍ
    setTimeout(() => {
        alertDiv.classList.remove('show');
        setTimeout(() => {
            alertDiv.remove();
        }, 150);
    }, 5000);
}
