/**
 * btec-app.js - الوظائف الرئيسية لنظام تقييم BTEC
 * تم إنشاؤه بواسطة: مصعب الحلحولي
 */

// متغيرات عامة
const messageTimeout = {
    id: null,
    duration: 5000 // مدة عرض الرسالة بالمللي ثانية
};

/**
 * إعداد التطبيق عند تحميل الصفحة
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('تم تحميل تطبيق BTEC بنجاح');
    
    // إنشاء عنصر صندوق الرسائل إذا لم يكن موجودًا
    if (!document.getElementById('message-box')) {
        const messageBox = document.createElement('div');
        messageBox.id = 'message-box';
        messageBox.className = 'message-box';
        document.body.appendChild(messageBox);
    }
    
    // إعداد أحداث الأزرار والنماذج
    setupEventListeners();
    
    // تحميل البيانات الأولية
    loadInitialData();
    
    // إنشاء تأثيرات بصرية
    initializeVisualEffects();
});

/**
 * إعداد مستمعي الأحداث
 */
function setupEventListeners() {
    // مثال: استجابة لنقر زر تسجيل الدخول
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            handleLogin();
        });
    }
    
    // مثال: استجابة لنقر زر التسجيل
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            handleRegister();
        });
    }
    
    // مثال: استجابة لأزرار التبديل بين علامات التبويب
    const tabButtons = document.querySelectorAll('.tab-button');
    if (tabButtons.length > 0) {
        tabButtons.forEach(button => {
            button.addEventListener('click', function() {
                const tabId = this.getAttribute('data-tab');
                switchTab(tabId);
            });
        });
    }
    
    // استجابة لأزرار التنقل بين الصفحات
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (this.getAttribute('data-page')) {
                e.preventDefault();
                navigateTo(this.getAttribute('data-page'));
            }
        });
    });
}

/**
 * تحميل البيانات الأولية
 */
function loadInitialData() {
    // التحقق من حالة تسجيل الدخول
    checkAuthStatus();
    
    // تحميل البيانات حسب الصفحة الحالية
    const currentPage = getCurrentPage();
    
    switch (currentPage) {
        case 'dashboard':
            loadDashboardData();
            break;
        case 'evaluations':
            loadEvaluations();
            break;
        case 'rubrics':
            loadRubrics();
            break;
        case 'classes':
            loadClasses();
            break;
        case 'profile':
            loadUserProfile();
            break;
    }
}

/**
 * التحقق من حالة تسجيل الدخول
 */
function checkAuthStatus() {
    const token = localStorage.getItem('authToken');
    if (token) {
        // إذا كان المستخدم قد سجل الدخول
        fetchUserData();
    } else {
        // إذا لم يكن المستخدم قد سجل الدخول
        const authRequiredPages = document.querySelectorAll('.auth-required');
        authRequiredPages.forEach(page => {
            page.style.display = 'none';
        });
        
        const loginSection = document.getElementById('login-section');
        if (loginSection) {
            loginSection.style.display = 'block';
        }
    }
}

/**
 * جلب بيانات المستخدم
 */
function fetchUserData() {
    const token = localStorage.getItem('authToken');
    if (!token) return;
    
    fetch('/api/user/me', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Failed to fetch user data');
        }
    })
    .then(data => {
        // تحديث واجهة المستخدم ببيانات المستخدم
        updateUserInterface(data);
    })
    .catch(error => {
        console.error('Error fetching user data:', error);
        // إذا انتهت صلاحية الرمز، قم بتسجيل الخروج
        if (error.message.includes('401')) {
            logout();
        }
    });
}

/**
 * تحديث واجهة المستخدم ببيانات المستخدم
 */
function updateUserInterface(userData) {
    // تحديث اسم المستخدم
    const userNameElements = document.querySelectorAll('.user-name');
    userNameElements.forEach(el => {
        el.textContent = userData.name;
    });
    
    // تحديث الصورة الرمزية للمستخدم
    const avatarElements = document.querySelectorAll('.user-avatar');
    avatarElements.forEach(el => {
        if (userData.avatar) {
            el.src = userData.avatar;
        }
    });
    
    // تحديث مستوى وصول المستخدم بناءً على دوره
    const role = userData.role;
    const adminElements = document.querySelectorAll('.admin-only');
    const teacherElements = document.querySelectorAll('.teacher-only');
    const studentElements = document.querySelectorAll('.student-only');
    
    adminElements.forEach(el => {
        el.style.display = (role === 'admin') ? 'block' : 'none';
    });
    
    teacherElements.forEach(el => {
        el.style.display = (role === 'admin' || role === 'teacher') ? 'block' : 'none';
    });
    
    studentElements.forEach(el => {
        el.style.display = (role === 'student') ? 'block' : 'none';
    });
}

/**
 * إظهار رسالة للمستخدم
 */
function showMessage(message, type = 'info') {
    const messageBox = document.getElementById('message-box');
    if (!messageBox) return;
    
    // إلغاء المؤقت السابق إذا كان موجودًا
    if (messageTimeout.id) {
        clearTimeout(messageTimeout.id);
    }
    
    // إنشاء محتوى الرسالة
    messageBox.innerHTML = `
        <div class="message-content">${message}</div>
        <button class="message-close" onclick="closeMessage()">&times;</button>
    `;
    
    // تعيين نوع الرسالة
    messageBox.className = 'message-box';
    messageBox.classList.add(type);
    
    // إظهار الرسالة
    setTimeout(() => {
        messageBox.classList.add('show');
    }, 10);
    
    // إخفاء الرسالة بعد فترة
    messageTimeout.id = setTimeout(() => {
        messageBox.classList.remove('show');
    }, messageTimeout.duration);
}

/**
 * إغلاق رسالة المستخدم
 */
function closeMessage() {
    const messageBox = document.getElementById('message-box');
    if (messageBox) {
        messageBox.classList.remove('show');
    }
}

/**
 * معالجة تسجيل الدخول
 */
function handleLogin() {
    const emailInput = document.getElementById('login-email');
    const passwordInput = document.getElementById('login-password');
    
    if (!emailInput || !passwordInput) {
        showMessage('خطأ في النموذج، يرجى المحاولة مرة أخرى', 'error');
        return;
    }
    
    const email = emailInput.value.trim();
    const password = passwordInput.value;
    
    if (!email || !password) {
        showMessage('يرجى إدخال البريد الإلكتروني وكلمة المرور', 'warning');
        return;
    }
    
    // إظهار مؤشر التحميل
    const loginButton = document.querySelector('#login-form button[type="submit"]');
    if (loginButton) {
        loginButton.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> جاري تسجيل الدخول...';
        loginButton.disabled = true;
    }
    
    // إرسال طلب تسجيل الدخول
    fetch('/api/auth/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Failed to login');
        }
    })
    .then(data => {
        // تخزين رمز المصادقة
        localStorage.setItem('authToken', data.token);
        
        // عرض رسالة نجاح
        showMessage('تم تسجيل الدخول بنجاح، جاري تحويلك...', 'success');
        
        // انتقال إلى لوحة التحكم بعد فترة قصيرة
        setTimeout(() => {
            window.location.href = '/dashboard';
        }, 1000);
    })
    .catch(error => {
        console.error('Login error:', error);
        showMessage('فشل تسجيل الدخول. يرجى التحقق من بياناتك والمحاولة مرة أخرى.', 'error');
    })
    .finally(() => {
        // إعادة زر تسجيل الدخول إلى حالته الطبيعية
        if (loginButton) {
            loginButton.innerHTML = 'تسجيل الدخول';
            loginButton.disabled = false;
        }
    });
}

/**
 * تسجيل خروج المستخدم
 */
function logout() {
    // إزالة رمز المصادقة
    localStorage.removeItem('authToken');
    
    // عرض رسالة
    showMessage('تم تسجيل الخروج بنجاح', 'info');
    
    // إعادة توجيه المستخدم إلى صفحة تسجيل الدخول
    setTimeout(() => {
        window.location.href = '/login';
    }, 1000);
}

/**
 * التبديل بين علامات التبويب
 */
function switchTab(tabId) {
    // إخفاء جميع المحتويات
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => {
        content.style.display = 'none';
    });
    
    // إزالة الفئة النشطة من جميع الأزرار
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => {
        button.classList.remove('active');
    });
    
    // عرض المحتوى المطلوب
    const selectedContent = document.getElementById(`${tabId}-content`);
    if (selectedContent) {
        selectedContent.style.display = 'block';
    }
    
    // تحديد الزر النشط
    const selectedButton = document.querySelector(`.tab-button[data-tab="${tabId}"]`);
    if (selectedButton) {
        selectedButton.classList.add('active');
    }
}

/**
 * الحصول على الصفحة الحالية
 */
function getCurrentPage() {
    // يحاول الحصول على الصفحة الحالية من pathname
    const path = window.location.pathname;
    if (path === '/') return 'home';
    return path.split('/')[1] || 'home';
}

/**
 * الانتقال إلى صفحة محددة
 */
function navigateTo(page) {
    window.location.href = `/${page}`;
}

/**
 * تحميل بيانات لوحة التحكم
 */
function loadDashboardData() {
    // تحميل إحصائيات
    loadStatistics();
    
    // تحميل آخر التقييمات
    loadRecentEvaluations();
    
    // تحميل الإشعارات
    loadNotifications();
}

/**
 * تحميل إحصائيات لوحة التحكم
 */
function loadStatistics() {
    const token = localStorage.getItem('authToken');
    if (!token) return;
    
    fetch('/api/dashboard/stats', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Failed to fetch statistics');
        }
    })
    .then(data => {
        // تحديث العدادات
        updateStatisticCounters(data);
    })
    .catch(error => {
        console.error('Error loading statistics:', error);
        showMessage('تعذر تحميل الإحصائيات', 'error');
    });
}

/**
 * تحديث عدادات الإحصائيات
 */
function updateStatisticCounters(data) {
    // تحديث عدد التقييمات
    const evaluationsCounter = document.getElementById('evaluations-count');
    if (evaluationsCounter && data.evaluations) {
        animateCounter(evaluationsCounter, data.evaluations);
    }
    
    // تحديث عدد الفصول
    const classesCounter = document.getElementById('classes-count');
    if (classesCounter && data.classes) {
        animateCounter(classesCounter, data.classes);
    }
    
    // تحديث عدد الطلاب
    const studentsCounter = document.getElementById('students-count');
    if (studentsCounter && data.students) {
        animateCounter(studentsCounter, data.students);
    }
    
    // تحديث متوسط التقييم
    const avgScoreCounter = document.getElementById('avg-score');
    if (avgScoreCounter && data.averageScore) {
        animateCounter(avgScoreCounter, data.averageScore, 1);
    }
}

/**
 * عرض عداد مُتحرك
 */
function animateCounter(element, targetValue, decimals = 0) {
    const duration = 1500; // المدة بالمللي ثانية
    const startValue = 0;
    const startTime = performance.now();
    
    function updateCounter(currentTime) {
        const elapsedTime = currentTime - startTime;
        
        if (elapsedTime < duration) {
            const progress = elapsedTime / duration;
            const currentValue = startValue + progress * (targetValue - startValue);
            element.textContent = currentValue.toFixed(decimals);
            requestAnimationFrame(updateCounter);
        } else {
            element.textContent = targetValue.toFixed(decimals);
        }
    }
    
    requestAnimationFrame(updateCounter);
}

/**
 * تحميل آخر التقييمات
 */
function loadRecentEvaluations() {
    const token = localStorage.getItem('authToken');
    if (!token) return;
    
    fetch('/api/evaluations/recent', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Failed to fetch recent evaluations');
        }
    })
    .then(data => {
        // عرض آخر التقييمات
        displayRecentEvaluations(data);
    })
    .catch(error => {
        console.error('Error loading recent evaluations:', error);
    });
}

/**
 * عرض آخر التقييمات
 */
function displayRecentEvaluations(evaluations) {
    const container = document.getElementById('recent-evaluations');
    if (!container || !evaluations.length) return;
    
    container.innerHTML = '';
    
    evaluations.forEach(evaluation => {
        const statusClass = getStatusClass(evaluation.status);
        const statusText = getStatusText(evaluation.status);
        
        const evaluationCard = document.createElement('div');
        evaluationCard.className = 'card magical-border';
        evaluationCard.innerHTML = `
            <div class="evaluation-header">
                <h4>${evaluation.assignment_name || 'تقييم'}</h4>
                <span class="badge ${statusClass}">${statusText}</span>
            </div>
            <div class="evaluation-details">
                <p>الطالب: ${evaluation.student_name}</p>
                <p>التاريخ: ${formatDate(evaluation.created_at)}</p>
                <p>الدرجة: <strong>${evaluation.score || '-'}/100</strong></p>
            </div>
            <div class="card-actions">
                <button class="btn btn-primary btn-sm" onclick="viewEvaluation(${evaluation.id})">
                    <i class="fas fa-eye"></i> عرض التفاصيل
                </button>
            </div>
        `;
        
        container.appendChild(evaluationCard);
    });
}

/**
 * الحصول على فئة CSS لحالة التقييم
 */
function getStatusClass(status) {
    switch (status) {
        case 'completed':
            return 'badge-success';
        case 'pending':
            return 'badge-warning';
        case 'in_progress':
            return 'badge-info';
        case 'rejected':
            return 'badge-error';
        default:
            return 'badge-info';
    }
}

/**
 * الحصول على نص حالة التقييم
 */
function getStatusText(status) {
    switch (status) {
        case 'completed':
            return 'مكتمل';
        case 'pending':
            return 'قيد الانتظار';
        case 'in_progress':
            return 'قيد التقييم';
        case 'rejected':
            return 'مرفوض';
        default:
            return 'غير معروف';
    }
}

/**
 * تنسيق التاريخ
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ar-SA', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

/**
 * عرض تفاصيل التقييم
 */
function viewEvaluation(evaluationId) {
    navigateTo(`evaluations/${evaluationId}`);
}

/**
 * تهيئة التأثيرات البصرية
 */
function initializeVisualEffects() {
    // إضافة تأثيرات انتقالية للبطاقات
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        // تأخير ظهور البطاقة حسب الترتيب
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100 * index);
    });
    
    // تنفيذ تأثير الكتابة للنصوص
    const typewriterElements = document.querySelectorAll('.typewriter');
    typewriterElements.forEach(element => {
        const text = element.textContent;
        element.textContent = '';
        let i = 0;
        
        function typeWriter() {
            if (i < text.length) {
                element.textContent += text.charAt(i);
                i++;
                setTimeout(typeWriter, 50);
            }
        }
        
        typeWriter();
    });
}

/**
 * تحميل معايير التقييم
 */
function loadRubrics() {
    const token = localStorage.getItem('authToken');
    if (!token) return;
    
    fetch('/api/rubrics', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Failed to fetch rubrics');
        }
    })
    .then(data => {
        displayRubrics(data);
    })
    .catch(error => {
        console.error('Error loading rubrics:', error);
        showMessage('تعذر تحميل معايير التقييم', 'error');
    });
}

/**
 * عرض معايير التقييم
 */
function displayRubrics(rubrics) {
    const container = document.getElementById('rubrics-list');
    if (!container || !rubrics.length) return;
    
    container.innerHTML = '';
    
    rubrics.forEach(rubric => {
        const rubricCard = document.createElement('div');
        rubricCard.className = 'card magical-border';
        
        let criteriaHtml = '';
        if (rubric.criteria) {
            criteriaHtml = '<ul class="criteria-list">';
            for (const [key, value] of Object.entries(rubric.criteria)) {
                criteriaHtml += `<li>${key}: ${value.weight}%</li>`;
            }
            criteriaHtml += '</ul>';
        }
        
        rubricCard.innerHTML = `
            <div class="card-title">
                <span class="icon"><i class="fas fa-list-check"></i></span>
                ${rubric.name}
            </div>
            <div class="card-body">
                <p>${rubric.description || 'لا يوجد وصف'}</p>
                ${criteriaHtml}
            </div>
            <div class="card-actions">
                <button class="btn btn-outline btn-sm" onclick="editRubric(${rubric.id})">
                    <i class="fas fa-edit"></i> تعديل
                </button>
                <button class="btn btn-primary btn-sm" onclick="viewRubric(${rubric.id})">
                    <i class="fas fa-eye"></i> عرض
                </button>
            </div>
        `;
        
        container.appendChild(rubricCard);
    });
}

/**
 * تعديل معيار تقييم
 */
function editRubric(rubricId) {
    navigateTo(`rubrics/${rubricId}/edit`);
}

/**
 * عرض معيار تقييم
 */
function viewRubric(rubricId) {
    navigateTo(`rubrics/${rubricId}`);
}

/**
 * تحميل قائمة الفصول
 */
function loadClasses() {
    const token = localStorage.getItem('authToken');
    if (!token) return;
    
    fetch('/api/classes', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Failed to fetch classes');
        }
    })
    .then(data => {
        displayClasses(data);
    })
    .catch(error => {
        console.error('Error loading classes:', error);
        showMessage('تعذر تحميل الفصول الدراسية', 'error');
    });
}

/**
 * عرض قائمة الفصول
 */
function displayClasses(classes) {
    const container = document.getElementById('classes-list');
    if (!container || !classes.length) return;
    
    container.innerHTML = '';
    
    classes.forEach(classItem => {
        const classCard = document.createElement('div');
        classCard.className = 'card magical-border';
        
        classCard.innerHTML = `
            <div class="card-title">
                <span class="icon"><i class="fas fa-chalkboard"></i></span>
                ${classItem.name}
            </div>
            <div class="card-body">
                <p>${classItem.description || 'لا يوجد وصف'}</p>
                <p>عدد الطلاب: <strong>${classItem.students_count || 0}</strong></p>
            </div>
            <div class="card-actions">
                <button class="btn btn-outline btn-sm" onclick="manageClassAttendance(${classItem.id})">
                    <i class="fas fa-clipboard-list"></i> الحضور
                </button>
                <button class="btn btn-primary btn-sm" onclick="viewClass(${classItem.id})">
                    <i class="fas fa-eye"></i> عرض
                </button>
            </div>
        `;
        
        container.appendChild(classCard);
    });
}

/**
 * إدارة حضور الفصل
 */
function manageClassAttendance(classId) {
    navigateTo(`classes/${classId}/attendance`);
}

/**
 * عرض الفصل
 */
function viewClass(classId) {
    navigateTo(`classes/${classId}`);
}

/**
 * تحميل التقييمات
 */
function loadEvaluations() {
    const token = localStorage.getItem('authToken');
    if (!token) return;
    
    fetch('/api/evaluations', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Failed to fetch evaluations');
        }
    })
    .then(data => {
        displayEvaluations(data);
    })
    .catch(error => {
        console.error('Error loading evaluations:', error);
        showMessage('تعذر تحميل التقييمات', 'error');
    });
}

/**
 * عرض التقييمات
 */
function displayEvaluations(evaluations) {
    const container = document.getElementById('evaluations-list');
    if (!container || !evaluations.length) return;
    
    container.innerHTML = '';
    
    evaluations.forEach(evaluation => {
        const statusClass = getStatusClass(evaluation.status);
        const statusText = getStatusText(evaluation.status);
        
        const evaluationCard = document.createElement('div');
        evaluationCard.className = 'card magical-border';
        
        evaluationCard.innerHTML = `
            <div class="card-title">
                <span class="icon"><i class="fas fa-clipboard-check"></i></span>
                ${evaluation.assignment_name || 'تقييم'}
                <span class="badge ${statusClass}">${statusText}</span>
            </div>
            <div class="card-body">
                <p>الطالب: <strong>${evaluation.student_name}</strong></p>
                <p>المهمة: ${evaluation.assignment_name || '-'}</p>
                <p>التاريخ: ${formatDate(evaluation.created_at)}</p>
                <p>الدرجة: <strong>${evaluation.score || '-'}/100</strong></p>
            </div>
            <div class="card-actions">
                <button class="btn btn-primary btn-sm" onclick="viewEvaluation(${evaluation.id})">
                    <i class="fas fa-eye"></i> عرض التفاصيل
                </button>
            </div>
        `;
        
        container.appendChild(evaluationCard);
    });
}

/**
 * تحميل الملف الشخصي للمستخدم
 */
function loadUserProfile() {
    const token = localStorage.getItem('authToken');
    if (!token) return;
    
    fetch('/api/user/me', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Failed to fetch user profile');
        }
    })
    .then(data => {
        displayUserProfile(data);
    })
    .catch(error => {
        console.error('Error loading user profile:', error);
        showMessage('تعذر تحميل الملف الشخصي', 'error');
    });
}

/**
 * عرض الملف الشخصي للمستخدم
 */
function displayUserProfile(user) {
    // تحديث اسم المستخدم
    const nameInput = document.getElementById('profile-name');
    if (nameInput) {
        nameInput.value = user.name || '';
    }
    
    // تحديث البريد الإلكتروني
    const emailInput = document.getElementById('profile-email');
    if (emailInput) {
        emailInput.value = user.email || '';
    }
    
    // تحديث الدور
    const roleElement = document.getElementById('profile-role');
    if (roleElement) {
        let roleName = '';
        switch (user.role) {
            case 'admin':
                roleName = 'مدير النظام';
                break;
            case 'teacher':
                roleName = 'معلم';
                break;
            case 'student':
                roleName = 'طالب';
                break;
            default:
                roleName = user.role || 'مستخدم';
        }
        roleElement.textContent = roleName;
    }
    
    // تحديث صورة المستخدم
    const avatarElement = document.getElementById('profile-avatar');
    if (avatarElement && user.avatar) {
        avatarElement.src = user.avatar;
    }
}

/**
 * تحديث الملف الشخصي للمستخدم
 */
function updateUserProfile() {
    const token = localStorage.getItem('authToken');
    if (!token) return;
    
    const nameInput = document.getElementById('profile-name');
    const passwordInput = document.getElementById('profile-password');
    const passwordConfirmInput = document.getElementById('profile-password-confirm');
    
    if (!nameInput) {
        showMessage('خطأ في النموذج، يرجى المحاولة مرة أخرى', 'error');
        return;
    }
    
    const name = nameInput.value.trim();
    
    if (!name) {
        showMessage('يرجى إدخال الاسم', 'warning');
        return;
    }
    
    // التحقق من كلمة المرور إذا تم إدخالها
    if (passwordInput && passwordConfirmInput) {
        const password = passwordInput.value;
        const passwordConfirm = passwordConfirmInput.value;
        
        if (password && password !== passwordConfirm) {
            showMessage('كلمتا المرور غير متطابقتين', 'error');
            return;
        }
    }
    
    // بناء بيانات التحديث
    const userData = { name };
    
    if (passwordInput && passwordInput.value) {
        userData.password = passwordInput.value;
    }
    
    // إظهار مؤشر التحميل
    const updateButton = document.querySelector('#profile-form button[type="submit"]');
    if (updateButton) {
        updateButton.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> جاري التحديث...';
        updateButton.disabled = true;
    }
    
    // إرسال طلب تحديث البيانات
    fetch('/api/user/update', {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(userData)
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Failed to update profile');
        }
    })
    .then(data => {
        showMessage('تم تحديث الملف الشخصي بنجاح', 'success');
        
        // إعادة تعيين حقول كلمة المرور
        if (passwordInput) passwordInput.value = '';
        if (passwordConfirmInput) passwordConfirmInput.value = '';
    })
    .catch(error => {
        console.error('Profile update error:', error);
        showMessage('فشل تحديث الملف الشخصي. يرجى المحاولة مرة أخرى.', 'error');
    })
    .finally(() => {
        // إعادة زر التحديث إلى حالته الطبيعية
        if (updateButton) {
            updateButton.innerHTML = 'تحديث البيانات';
            updateButton.disabled = false;
        }
    });
}

/**
 * تهيئة وظائف الذكاء الاصطناعي للتقييم
 */
function initializeAI() {
    const aiEvaluateButton = document.getElementById('ai-evaluate-button');
    if (aiEvaluateButton) {
        aiEvaluateButton.addEventListener('click', performAIEvaluation);
    }
}

/**
 * إجراء تقييم باستخدام الذكاء الاصطناعي
 */
function performAIEvaluation() {
    const submissionId = document.getElementById('submission-id').value;
    const rubricId = document.getElementById('rubric-id').value;
    
    if (!submissionId || !rubricId) {
        showMessage('يرجى تحديد التسليم ومعيار التقييم', 'warning');
        return;
    }
    
    const token = localStorage.getItem('authToken');
    if (!token) return;
    
    // إظهار مؤشر التحميل
    const aiEvaluateButton = document.getElementById('ai-evaluate-button');
    if (aiEvaluateButton) {
        aiEvaluateButton.innerHTML = '<i class="fas fa-robot fa-spin"></i> جاري التقييم...';
        aiEvaluateButton.disabled = true;
    }
    
    fetch('/api/ai/evaluate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
            submission_id: submissionId,
            rubric_id: rubricId
        })
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Failed to perform AI evaluation');
        }
    })
    .then(data => {
        showMessage('تم إجراء التقييم بنجاح', 'success');
        
        // عرض نتائج التقييم
        displayAIEvaluationResults(data);
    })
    .catch(error => {
        console.error('AI evaluation error:', error);
        showMessage('فشل إجراء التقييم. يرجى المحاولة مرة أخرى.', 'error');
    })
    .finally(() => {
        // إعادة زر التقييم إلى حالته الطبيعية
        if (aiEvaluateButton) {
            aiEvaluateButton.innerHTML = '<i class="fas fa-robot"></i> تقييم باستخدام الذكاء الاصطناعي';
            aiEvaluateButton.disabled = false;
        }
    });
}

/**
 * عرض نتائج تقييم الذكاء الاصطناعي
 */
function displayAIEvaluationResults(results) {
    const resultsContainer = document.getElementById('ai-results-container');
    if (!resultsContainer) return;
    
    resultsContainer.innerHTML = '';
    
    // إنشاء عنصر النتائج
    const resultsCard = document.createElement('div');
    resultsCard.className = 'card magical-border';
    
    // بناء HTML للمعايير
    let criteriaHtml = '';
    if (results.criteria) {
        criteriaHtml = '<div class="ai-criteria-results">';
        for (const [key, value] of Object.entries(results.criteria)) {
            criteriaHtml += `
                <div class="criterion-result">
                    <div class="criterion-result-header">
                        <h4>${key}</h4>
                        <span class="criterion-score">${value.score}/${value.max_score}</span>
                    </div>
                    <div class="criterion-result-feedback">
                        <p>${value.feedback}</p>
                    </div>
                </div>
            `;
        }
        criteriaHtml += '</div>';
    }
    
    // إنشاء HTML للنتائج
    resultsCard.innerHTML = `
        <div class="card-title">
            <span class="icon"><i class="fas fa-robot"></i></span>
            نتائج التقييم الآلي
        </div>
        <div class="ai-score-summary">
            <div class="ai-score-circle">
                <span class="ai-score-value">${results.overall_score || 0}</span>
                <span class="ai-score-max">/100</span>
            </div>
            <div class="ai-score-label">الدرجة الإجمالية</div>
        </div>
        <div class="card-body">
            <h3>ملاحظات عامة</h3>
            <p>${results.overall_feedback || 'لا توجد ملاحظات'}</p>
            
            <h3>تفاصيل التقييم</h3>
            ${criteriaHtml}
        </div>
        <div class="card-actions">
            <button class="btn btn-primary" onclick="saveAIEvaluation()">
                <i class="fas fa-save"></i> حفظ التقييم
            </button>
            <button class="btn btn-outline" onclick="modifyAIEvaluation()">
                <i class="fas fa-edit"></i> تعديل التقييم
            </button>
        </div>
    `;
    
    resultsContainer.appendChild(resultsCard);
    
    // تمرير النتائج إلى المتصفح
    window.aiResults = results;
    
    // التمرير إلى النتائج
    resultsContainer.scrollIntoView({ behavior: 'smooth' });
}

/**
 * حفظ تقييم الذكاء الاصطناعي
 */
function saveAIEvaluation() {
    if (!window.aiResults) {
        showMessage('لا توجد نتائج تقييم للحفظ', 'warning');
        return;
    }
    
    const token = localStorage.getItem('authToken');
    if (!token) return;
    
    const submissionId = document.getElementById('submission-id').value;
    
    fetch('/api/evaluations/save', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
            submission_id: submissionId,
            ai_results: window.aiResults
        })
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Failed to save AI evaluation');
        }
    })
    .then(data => {
        showMessage('تم حفظ التقييم بنجاح', 'success');
        
        // الانتقال إلى صفحة التقييم المحفوظ
        setTimeout(() => {
            navigateTo(`evaluations/${data.evaluation_id}`);
        }, 1000);
    })
    .catch(error => {
        console.error('Save evaluation error:', error);
        showMessage('فشل حفظ التقييم. يرجى المحاولة مرة أخرى.', 'error');
    });
}

/**
 * تعديل تقييم الذكاء الاصطناعي
 */
function modifyAIEvaluation() {
    // تمكين المستخدم من تعديل نتائج التقييم
    const criteriaElements = document.querySelectorAll('.criterion-score');
    criteriaElements.forEach(element => {
        const scoreText = element.textContent;
        const [score, maxScore] = scoreText.split('/');
        
        const inputElement = document.createElement('input');
        inputElement.type = 'number';
        inputElement.min = '0';
        inputElement.max = maxScore;
        inputElement.value = score;
        inputElement.className = 'criterion-score-input';
        inputElement.style.width = '60px';
        
        // تحديث النتيجة عند التغيير
        inputElement.addEventListener('change', function() {
            // تحديث النتيجة في aiResults
            const criterionName = this.closest('.criterion-result').querySelector('h4').textContent;
            window.aiResults.criteria[criterionName].score = parseFloat(this.value);
            
            // حساب النتيجة الإجمالية الجديدة
            let totalScore = 0;
            let totalWeight = 0;
            
            for (const criterion of Object.values(window.aiResults.criteria)) {
                totalScore += (criterion.score / criterion.max_score) * criterion.weight;
                totalWeight += criterion.weight;
            }
            
            const overallScore = totalWeight > 0 ? (totalScore / totalWeight) * 100 : 0;
            window.aiResults.overall_score = Math.round(overallScore);
            
            // تحديث عرض النتيجة الإجمالية
            const scoreValueElement = document.querySelector('.ai-score-value');
            if (scoreValueElement) {
                scoreValueElement.textContent = Math.round(overallScore);
            }
        });
        
        element.replaceWith(inputElement);
        inputElement.after(document.createTextNode('/' + maxScore));
    });
    
    // تمكين تعديل التعليقات
    const feedbackElements = document.querySelectorAll('.criterion-result-feedback p');
    feedbackElements.forEach(element => {
        const feedbackText = element.textContent;
        
        const textareaElement = document.createElement('textarea');
        textareaElement.value = feedbackText;
        textareaElement.className = 'criterion-feedback-input';
        textareaElement.rows = 3;
        
        // تحديث التعليقات عند التغيير
        textareaElement.addEventListener('change', function() {
            const criterionName = this.closest('.criterion-result').querySelector('h4').textContent;
            window.aiResults.criteria[criterionName].feedback = this.value;
        });
        
        element.replaceWith(textareaElement);
    });
    
    // تعديل التعليقات العامة
    const overallFeedbackElement = document.querySelector('.card-body > p');
    if (overallFeedbackElement) {
        const feedbackText = overallFeedbackElement.textContent;
        
        const textareaElement = document.createElement('textarea');
        textareaElement.value = feedbackText;
        textareaElement.className = 'overall-feedback-input';
        textareaElement.rows = 5;
        
        // تحديث التعليقات العامة عند التغيير
        textareaElement.addEventListener('change', function() {
            window.aiResults.overall_feedback = this.value;
        });
        
        overallFeedbackElement.replaceWith(textareaElement);
    }
    
    showMessage('يمكنك الآن تعديل نتائج التقييم', 'info');
}

// تحميل وظائف الذكاء الاصطناعي عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    initializeAI();
});