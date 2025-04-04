/**
 * نظام تقييم BTEC - ملف مصادقة المستخدم
 */

document.addEventListener('DOMContentLoaded', function() {
    // التحقق من وجود المستخدم المسجل
    const token = localStorage.getItem('jwt_token');
    const userInfo = localStorage.getItem('user_info');
    
    if (token && userInfo) {
        try {
            // تحويل معلومات المستخدم من JSON
            const user = JSON.parse(userInfo);
            
            // تحديث واجهة المستخدم بناءً على حالة تسجيل الدخول
            updateUIForLoggedInUser(user);
            
            // التحقق من صلاحية الرمز (اختياري)
            validateToken(token);
        } catch (error) {
            console.error('خطأ في تحليل معلومات المستخدم:', error);
            // حذف البيانات غير الصالحة
            localStorage.removeItem('jwt_token');
            localStorage.removeItem('user_info');
        }
    }
    
    // معالجة نموذج تسجيل الدخول
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const email = document.getElementById('loginEmail').value;
            const password = document.getElementById('loginPassword').value;
            
            // إرسال بيانات تسجيل الدخول إلى الخادم
            fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, password })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // حفظ الرمز ومعلومات المستخدم
                    localStorage.setItem('jwt_token', data.access_token);
                    localStorage.setItem('user_info', JSON.stringify(data.user));
                    
                    // عرض رسالة نجاح
                    showNotification('تم تسجيل الدخول بنجاح!', 'success');
                    
                    // إعادة توجيه المستخدم إلى لوحة التحكم
                    setTimeout(() => {
                        window.location.href = '/dashboard';
                    }, 1000);
                } else {
                    // عرض رسالة الخطأ
                    showNotification(data.message || 'فشل تسجيل الدخول. يرجى التحقق من البريد الإلكتروني وكلمة المرور.', 'danger');
                }
            })
            .catch(error => {
                console.error('خطأ في تسجيل الدخول:', error);
                showNotification('حدث خطأ أثناء الاتصال بالخادم. يرجى المحاولة مرة أخرى.', 'danger');
            });
        });
    }
    
    // معالجة نموذج التسجيل
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const name = document.getElementById('registerName').value;
            const email = document.getElementById('registerEmail').value;
            const password = document.getElementById('registerPassword').value;
            
            // إرسال بيانات التسجيل إلى الخادم
            fetch('/api/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ name, email, password })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // حفظ الرمز ومعلومات المستخدم
                    localStorage.setItem('jwt_token', data.access_token);
                    localStorage.setItem('user_info', JSON.stringify(data.user));
                    
                    // عرض رسالة نجاح
                    showNotification('تم التسجيل بنجاح!', 'success');
                    
                    // إعادة توجيه المستخدم إلى لوحة التحكم
                    setTimeout(() => {
                        window.location.href = '/dashboard';
                    }, 1000);
                } else {
                    // عرض رسالة الخطأ
                    showNotification(data.message || 'فشل التسجيل. يرجى التحقق من البيانات المدخلة.', 'danger');
                }
            })
            .catch(error => {
                console.error('خطأ في التسجيل:', error);
                showNotification('حدث خطأ أثناء الاتصال بالخادم. يرجى المحاولة مرة أخرى.', 'danger');
            });
        });
    }
});

/**
 * تحديث واجهة المستخدم بناءً على حالة تسجيل الدخول
 * @param {Object} user - بيانات المستخدم
 */
function updateUIForLoggedInUser(user) {
    // إخفاء عناصر تسجيل الدخول/التسجيل
    const loginMenuItem = document.getElementById('loginMenuItem');
    const registerMenuItem = document.getElementById('registerMenuItem');
    
    if (loginMenuItem) loginMenuItem.classList.add('d-none');
    if (registerMenuItem) registerMenuItem.classList.add('d-none');
    
    // إظهار عناصر المستخدم المسجل
    const dashboardMenuItem = document.getElementById('dashboardMenuItem');
    const evaluationMenuItem = document.getElementById('evaluationMenuItem');
    const profileMenuItem = document.getElementById('profileMenuItem');
    const logoutMenuItem = document.getElementById('logoutMenuItem');
    
    if (dashboardMenuItem) dashboardMenuItem.classList.remove('d-none');
    if (evaluationMenuItem) evaluationMenuItem.classList.remove('d-none');
    if (profileMenuItem) profileMenuItem.classList.remove('d-none');
    if (logoutMenuItem) logoutMenuItem.classList.remove('d-none');
    
    // إظهار عناصر المسؤول إذا كان المستخدم مسؤولاً
    if (user.role === 'admin') {
        const adminMenuItems = document.querySelectorAll('.admin-only');
        adminMenuItems.forEach(item => item.classList.remove('d-none'));
    }
    
    // تحديث اسم المستخدم إذا كان هناك عنصر لذلك
    const userNameElement = document.getElementById('userName');
    if (userNameElement) {
        userNameElement.textContent = user.name || user.email;
    }
}

/**
 * التحقق من صلاحية الرمز
 * @param {string} token - رمز المصادقة
 */
function validateToken(token) {
    fetch('/api/auth/user', {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(response => {
        if (!response.ok) {
            // الرمز غير صالح، تسجيل الخروج
            localStorage.removeItem('jwt_token');
            localStorage.removeItem('user_info');
            
            // إعادة تحميل الصفحة لتحديث حالة واجهة المستخدم
            window.location.reload();
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            // تحديث معلومات المستخدم في التخزين المحلي (للتأكد من وجود أحدث المعلومات)
            localStorage.setItem('user_info', JSON.stringify(data.user));
            
            // تحديث واجهة المستخدم
            updateUIForLoggedInUser(data.user);
        }
    })
    .catch(error => {
        console.error('خطأ في التحقق من صلاحية الرمز:', error);
    });
}

/**
 * وظيفة للحصول على رمز المصادقة
 * @returns {string|null} رمز المصادقة أو null إذا لم يكن موجودًا
 */
function getAuthToken() {
    return localStorage.getItem('jwt_token');
}

/**
 * وظيفة للحصول على معلومات المستخدم
 * @returns {Object|null} بيانات المستخدم أو null إذا لم يكن موجودًا
 */
function getUserInfo() {
    const userInfo = localStorage.getItem('user_info');
    if (userInfo) {
        try {
            return JSON.parse(userInfo);
        } catch (error) {
            console.error('خطأ في تحليل معلومات المستخدم:', error);
            return null;
        }
    }
    return null;
}
