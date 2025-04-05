/**
 * نظام تقييم BTEC
 * الملف الرئيسي للواجهة الأمامية
 */

// تكوين Axios للطلبات
const axiosInstance = axios.create({
    baseURL: '/api/', // المسار النسبي للواجهة الخلفية
    timeout: 15000,
    headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    }
});

// إضافة اعتراض للطلبات لإضافة توكن JWT
axiosInstance.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// إضافة اعتراض للاستجابات للتعامل مع تجديد التوكن
axiosInstance.interceptors.response.use(
    (response) => {
        return response;
    },
    async (error) => {
        const originalRequest = error.config;
        
        // إذا كان الخطأ 401 وليس محاولة تجديد التوكن
        if (error.response && error.response.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;
            
            try {
                // محاولة تجديد التوكن
                const refreshToken = localStorage.getItem('refresh_token');
                if (!refreshToken) {
                    throw new Error('No refresh token found');
                }
                
                const response = await axios.post('/api/auth/refresh', {}, {
                    headers: {
                        'Authorization': `Bearer ${refreshToken}`
                    }
                });
                
                // تخزين التوكن الجديد
                localStorage.setItem('access_token', response.data.access_token);
                
                // إعادة المحاولة بالتوكن الجديد
                originalRequest.headers['Authorization'] = `Bearer ${response.data.access_token}`;
                return axiosInstance(originalRequest);
            } catch (err) {
                // فشل التجديد، تسجيل الخروج
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                localStorage.removeItem('user');
                window.location.href = '/auth/login';
                return Promise.reject(err);
            }
        }
        
        return Promise.reject(error);
    }
);

// واجهة برمجة تطبيقات المصادقة
const authAPI = {
    login: async (email, password) => {
        try {
            const response = await axiosInstance.post('/auth/login', { email, password });
            localStorage.setItem('access_token', response.data.access_token);
            localStorage.setItem('refresh_token', response.data.refresh_token);
            localStorage.setItem('user', JSON.stringify(response.data.user));
            return response.data;
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
    },
    
    logout: async () => {
        try {
            await axiosInstance.post('/auth/logout');
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('user');
            window.location.href = '/';
        }
    },
    
    register: async (name, email, password, passwordConfirm) => {
        try {
            const response = await axiosInstance.post('/auth/register', {
                name, email, password, password_confirm: passwordConfirm
            });
            return response.data;
        } catch (error) {
            console.error('Registration error:', error);
            throw error;
        }
    },
    
    getCurrentUser: () => {
        const userJson = localStorage.getItem('user');
        return userJson ? JSON.parse(userJson) : null;
    },
    
    isAuthenticated: () => {
        return !!localStorage.getItem('access_token');
    },
    
    hasRole: (role) => {
        const user = authAPI.getCurrentUser();
        return user && user.role === role;
    }
};

// واجهة برمجة تطبيقات التقييمات
const evaluationsAPI = {
    getEvaluations: async () => {
        try {
            const response = await axiosInstance.get('/evaluations');
            return response.data;
        } catch (error) {
            console.error('Error fetching evaluations:', error);
            throw error;
        }
    },
    
    getEvaluation: async (id) => {
        try {
            const response = await axiosInstance.get(`/evaluations/${id}`);
            return response.data;
        } catch (error) {
            console.error(`Error fetching evaluation ${id}:`, error);
            throw error;
        }
    },
    
    createEvaluation: async (data) => {
        try {
            const response = await axiosInstance.post('/evaluate', data);
            return response.data;
        } catch (error) {
            console.error('Error creating evaluation:', error);
            throw error;
        }
    },
    
    updateEvaluation: async (id, data) => {
        try {
            const response = await axiosInstance.put(`/evaluations/${id}`, data);
            return response.data;
        } catch (error) {
            console.error(`Error updating evaluation ${id}:`, error);
            throw error;
        }
    }
};

// واجهة برمجة تطبيقات معايير التقييم
const rubricsAPI = {
    getRubrics: async () => {
        try {
            const response = await axiosInstance.get('/rubrics');
            return response.data;
        } catch (error) {
            console.error('Error fetching rubrics:', error);
            throw error;
        }
    },
    
    getRubric: async (id) => {
        try {
            const response = await axiosInstance.get(`/rubrics/${id}`);
            return response.data;
        } catch (error) {
            console.error(`Error fetching rubric ${id}:`, error);
            throw error;
        }
    }
};

// وظائف مساعدة للواجهة
const UI = {
    showMessage: (message, type = 'info') => {
        const alertBox = document.createElement('div');
        alertBox.className = `alert alert-${type} alert-dismissible fade show`;
        alertBox.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        const alertContainer = document.getElementById('alert-container');
        if (alertContainer) {
            alertContainer.appendChild(alertBox);
            
            // إزالة الرسالة تلقائيًا بعد 5 ثوانٍ
            setTimeout(() => {
                alertBox.classList.remove('show');
                setTimeout(() => alertBox.remove(), 150);
            }, 5000);
        }
    },
    
    renderLoading: (container) => {
        container.innerHTML = `
            <div class="text-center p-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">جاري التحميل...</span>
                </div>
                <p class="mt-2">جاري التحميل...</p>
            </div>
        `;
    },
    
    formatDate: (dateString) => {
        if (!dateString) return '';
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('ar-SA', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(date);
    }
};

// تهيئة التطبيق عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', () => {
    // إعداد زر تسجيل الخروج
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            try {
                await authAPI.logout();
            } catch (error) {
                console.error('Logout error:', error);
            }
        });
    }
    
    // إعداد عناصر واجهة المستخدم التفاعلية
    setupUIInteractions();
    
    // تحقق من حالة المصادقة وتحديث واجهة المستخدم
    updateAuthUI();
});

// تحديث واجهة المستخدم بناءً على حالة المصادقة
function updateAuthUI() {
    const isAuthenticated = authAPI.isAuthenticated();
    const user = authAPI.getCurrentUser();
    
    // عناصر خاصة بالمستخدمين المسجلين
    document.querySelectorAll('.auth-only').forEach(el => {
        el.style.display = isAuthenticated ? '' : 'none';
    });
    
    // عناصر خاصة بالمستخدمين غير المسجلين
    document.querySelectorAll('.guest-only').forEach(el => {
        el.style.display = isAuthenticated ? 'none' : '';
    });
    
    // عناصر خاصة بالمشرفين
    document.querySelectorAll('.admin-only').forEach(el => {
        el.style.display = (isAuthenticated && user && user.role === 'admin') ? '' : 'none';
    });
    
    // عناصر خاصة بالمعلمين
    document.querySelectorAll('.teacher-only').forEach(el => {
        el.style.display = (isAuthenticated && user && user.role === 'teacher') ? '' : 'none';
    });
    
    // عناصر خاصة بالطلاب
    document.querySelectorAll('.student-only').forEach(el => {
        el.style.display = (isAuthenticated && user && user.role === 'student') ? '' : 'none';
    });
    
    // عرض اسم المستخدم
    const userNameElement = document.getElementById('user-name');
    if (userNameElement && user) {
        userNameElement.textContent = user.name;
    }
}

// إعداد التفاعلات في واجهة المستخدم
function setupUIInteractions() {
    // نموذج تسجيل الدخول
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            try {
                await authAPI.login(email, password);
                window.location.href = '/dashboard';
            } catch (error) {
                UI.showMessage('فشل تسجيل الدخول. يرجى التحقق من بريدك الإلكتروني وكلمة المرور.', 'danger');
            }
        });
    }
    
    // نموذج التسجيل
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const name = document.getElementById('name').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const passwordConfirm = document.getElementById('password_confirm').value;
            
            if (password !== passwordConfirm) {
                UI.showMessage('كلمات المرور غير متطابقة.', 'danger');
                return;
            }
            
            try {
                await authAPI.register(name, email, password, passwordConfirm);
                UI.showMessage('تم إنشاء الحساب بنجاح. يمكنك الآن تسجيل الدخول.', 'success');
                setTimeout(() => {
                    window.location.href = '/auth/login';
                }, 2000);
            } catch (error) {
                UI.showMessage('فشل التسجيل. يرجى المحاولة مرة أخرى.', 'danger');
            }
        });
    }
    
    // أزرار موجودة أخرى يمكن إضافتها هنا
}