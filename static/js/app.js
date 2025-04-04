/**
 * نظام تقييم BTEC - ملف JavaScript الرئيسي
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('تم تحميل نظام تقييم BTEC بنجاح!');
    
    // زر العودة للأعلى
    const backToTopButton = document.createElement('a');
    backToTopButton.href = '#';
    backToTopButton.className = 'back-to-top';
    backToTopButton.innerHTML = '<i class="fas fa-arrow-up"></i>';
    document.body.appendChild(backToTopButton);
    
    // إظهار/إخفاء زر العودة للأعلى عند التمرير
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            backToTopButton.style.display = 'block';
        } else {
            backToTopButton.style.display = 'none';
        }
    });
    
    // تمرير سلس عند النقر على زر العودة للأعلى
    backToTopButton.addEventListener('click', function(e) {
        e.preventDefault();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    
    // معالجة نماذج التسجيل/تسجيل الدخول
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // تطبيق تأثيرات متحركة إضافية
    const animatedElements = document.querySelectorAll('.animate');
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animated');
                }
            });
        }, { threshold: 0.1 });
        
        animatedElements.forEach(element => {
            observer.observe(element);
        });
    } else {
        // للمتصفحات القديمة التي لا تدعم IntersectionObserver
        animatedElements.forEach(element => {
            element.classList.add('animated');
        });
    }
    
    // معالجة الارتباط الخروج
    const logoutLink = document.getElementById('logoutLink');
    if (logoutLink) {
        logoutLink.addEventListener('click', function(e) {
            e.preventDefault();
            if (confirm('هل أنت متأكد من رغبتك في تسجيل الخروج؟')) {
                // حذف رمز JWT من التخزين المحلي
                localStorage.removeItem('jwt_token');
                localStorage.removeItem('user_info');
                
                // إعادة توجيه المستخدم إلى الصفحة الرئيسية
                window.location.href = '/';
            }
        });
    }
});

/**
 * وظيفة لعرض رسائل الإشعارات
 * @param {string} message - نص الرسالة
 * @param {string} type - نوع الإشعار (success, danger, warning, info)
 */
function showNotification(message, type = 'info') {
    // إنشاء عنصر الإشعار
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show notification`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="إغلاق"></button>
    `;
    
    // إضافة الإشعار إلى الصفحة
    const notificationContainer = document.getElementById('notification-container');
    if (notificationContainer) {
        notificationContainer.appendChild(notification);
    } else {
        // إنشاء حاوية إذا لم تكن موجودة
        const container = document.createElement('div');
        container.id = 'notification-container';
        container.className = 'notification-container';
        container.style.cssText = 'position: fixed; top: 20px; left: 20px; z-index: 9999;';
        container.appendChild(notification);
        document.body.appendChild(container);
    }
    
    // إخفاء الإشعار تلقائيًا بعد 5 ثوانٍ
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

/**
 * وظيفة لتنسيق التاريخ
 * @param {string} dateString - سلسلة التاريخ بتنسيق ISO
 * @returns {string} التاريخ المنسق بالعربية
 */
function formatDate(dateString) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    const options = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    
    return date.toLocaleDateString('ar-SA', options);
}
