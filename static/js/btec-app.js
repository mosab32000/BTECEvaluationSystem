/**
 * نظام تقييم BTEC - سكريبت جافاسكريبت الرئيسي
 */

// كائن لإدارة التطبيق
const BTECApp = {
  // المتغيرات
  config: {
    apiBaseUrl: '/api',
    authTokenKey: 'btec_auth_token',
    refreshTokenKey: 'btec_refresh_token',
  },
  
  // حالة التطبيق
  state: {
    user: null,
    isAuthenticated: false,
    pendingRequests: 0,
    flashMessages: [],
    currentView: null
  },
  
  // التهيئة
  init: function() {
    // فحص ما إذا كان المستخدم مسجل الدخول
    this.checkAuth();
    
    // تهيئة المستمعين للأحداث
    this.setupEventListeners();
    
    // تهيئة التنقل
    this.setupNavigation();
    
    // توجيه المستخدم إلى الصفحة المناسبة
    this.handleInitialRoute();
    
    console.log('تم تهيئة تطبيق BTEC');
  },
  
  // فحص حالة المصادقة
  checkAuth: function() {
    const token = localStorage.getItem(this.config.authTokenKey);
    
    if (token) {
      try {
        // التحقق من صلاحية الرمز
        const payload = this.parseJwt(token);
        const now = Math.floor(Date.now() / 1000);
        
        if (payload.exp > now) {
          // الرمز صالح
          this.state.isAuthenticated = true;
          this.state.user = payload;
          this.updateAuthUI();
          return true;
        } else {
          // الرمز منتهي الصلاحية - محاولة التحديث
          this.refreshToken();
        }
      } catch (error) {
        console.error('خطأ في التحقق من المصادقة:', error);
        this.logout();
      }
    }
    
    this.state.isAuthenticated = false;
    this.state.user = null;
    this.updateAuthUI();
    return false;
  },
  
  // تحديث واجهة المستخدم بناءً على حالة المصادقة
  updateAuthUI: function() {
    const guestElements = document.querySelectorAll('.guest-only');
    const authElements = document.querySelectorAll('.auth-only');
    const adminElements = document.querySelectorAll('.admin-only');
    const userNameElements = document.querySelectorAll('.user-name');
    
    if (this.state.isAuthenticated) {
      // إظهار عناصر المستخدمين المسجلين وإخفاء عناصر الزوار
      guestElements.forEach(el => el.style.display = 'none');
      authElements.forEach(el => el.style.display = '');
      
      // إظهار/إخفاء عناصر المسؤول بناءً على دور المستخدم
      if (this.state.user && this.state.user.role === 'admin') {
        adminElements.forEach(el => el.style.display = '');
      } else {
        adminElements.forEach(el => el.style.display = 'none');
      }
      
      // عرض اسم المستخدم
      if (this.state.user && this.state.user.name) {
        userNameElements.forEach(el => el.textContent = this.state.user.name);
      }
    } else {
      // إظهار عناصر الزوار وإخفاء عناصر المستخدمين المسجلين
      guestElements.forEach(el => el.style.display = '');
      authElements.forEach(el => el.style.display = 'none');
      adminElements.forEach(el => el.style.display = 'none');
    }
  },
  
  // تحليل رمز JWT
  parseJwt: function(token) {
    try {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
      }).join(''));
      
      return JSON.parse(jsonPayload);
    } catch (error) {
      console.error('خطأ في تحليل الرمز:', error);
      return null;
    }
  },
  
  // تحديث الرمز باستخدام refresh token
  refreshToken: function() {
    const refreshToken = localStorage.getItem(this.config.refreshTokenKey);
    
    if (!refreshToken) {
      this.logout();
      return Promise.reject('لا يوجد refresh token');
    }
    
    return fetch(`${this.config.apiBaseUrl}/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${refreshToken}`
      }
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('فشل تحديث الرمز');
      }
      return response.json();
    })
    .then(data => {
      localStorage.setItem(this.config.authTokenKey, data.access_token);
      localStorage.setItem(this.config.refreshTokenKey, data.refresh_token);
      
      this.state.isAuthenticated = true;
      this.state.user = this.parseJwt(data.access_token);
      this.updateAuthUI();
      
      return true;
    })
    .catch(error => {
      console.error('خطأ في تحديث الرمز:', error);
      this.logout();
      return false;
    });
  },
  
  // تسجيل الدخول
  login: function(email, password) {
    this.startLoading();
    
    return fetch(`${this.config.apiBaseUrl}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ email, password })
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('فشل تسجيل الدخول');
      }
      return response.json();
    })
    .then(data => {
      localStorage.setItem(this.config.authTokenKey, data.access_token);
      localStorage.setItem(this.config.refreshTokenKey, data.refresh_token);
      
      this.state.isAuthenticated = true;
      this.state.user = this.parseJwt(data.access_token);
      this.updateAuthUI();
      
      this.showMessage('success', 'تم تسجيل الدخول بنجاح!');
      this.navigateTo('/dashboard');
      
      return true;
    })
    .catch(error => {
      console.error('خطأ في تسجيل الدخول:', error);
      this.showMessage('danger', 'فشل تسجيل الدخول. يرجى التحقق من بيانات الاعتماد الخاصة بك.');
      return false;
    })
    .finally(() => {
      this.stopLoading();
    });
  },
  
  // تسجيل الخروج
  logout: function() {
    localStorage.removeItem(this.config.authTokenKey);
    localStorage.removeItem(this.config.refreshTokenKey);
    
    this.state.isAuthenticated = false;
    this.state.user = null;
    this.updateAuthUI();
    
    this.showMessage('info', 'تم تسجيل الخروج بنجاح');
    this.navigateTo('/');
  },
  
  // تسجيل مستخدم جديد
  register: function(userData) {
    this.startLoading();
    
    return fetch(`${this.config.apiBaseUrl}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(userData)
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('فشل التسجيل');
      }
      return response.json();
    })
    .then(data => {
      this.showMessage('success', 'تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول.');
      this.navigateTo('/login');
      return true;
    })
    .catch(error => {
      console.error('خطأ في التسجيل:', error);
      this.showMessage('danger', 'فشل إنشاء الحساب. يرجى المحاولة مرة أخرى.');
      return false;
    })
    .finally(() => {
      this.stopLoading();
    });
  },
  
  // إرسال طلب API مع معالجة المصادقة
  api: function(url, options = {}) {
    this.startLoading();
    
    // إضافة رمز المصادقة إذا كان المستخدم مسجل الدخول
    const token = localStorage.getItem(this.config.authTokenKey);
    if (token) {
      options.headers = options.headers || {};
      options.headers['Authorization'] = `Bearer ${token}`;
    }
    
    // إضافة رؤوس JSON افتراضية إذا لم يتم تحديدها
    if (!options.headers || !options.headers['Content-Type']) {
      options.headers = options.headers || {};
      options.headers['Content-Type'] = 'application/json';
    }
    
    return fetch(`${this.config.apiBaseUrl}${url}`, options)
      .then(response => {
        if (response.status === 401) {
          // محاولة تحديث الرمز إذا انتهت صلاحيته
          return this.refreshToken().then(refreshed => {
            if (refreshed) {
              // إعادة محاولة الطلب الأصلي بالرمز الجديد
              const newToken = localStorage.getItem(this.config.authTokenKey);
              options.headers['Authorization'] = `Bearer ${newToken}`;
              return fetch(`${this.config.apiBaseUrl}${url}`, options);
            } else {
              throw new Error('انتهت صلاحية الجلسة');
            }
          });
        }
        
        return response;
      })
      .then(response => {
        if (!response.ok) {
          return response.json().then(data => {
            throw new Error(data.message || 'حدث خطأ في الخادم');
          });
        }
        
        // التحقق مما إذا كان هناك محتوى للرد
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.indexOf('application/json') !== -1) {
          return response.json();
        } else {
          return response.text();
        }
      })
      .catch(error => {
        console.error('خطأ في طلب API:', error);
        
        if (error.message === 'انتهت صلاحية الجلسة') {
          this.showMessage('warning', 'انتهت صلاحية الجلسة. يرجى تسجيل الدخول مرة أخرى.');
          this.logout();
        } else {
          this.showMessage('danger', `خطأ: ${error.message}`);
        }
        
        throw error;
      })
      .finally(() => {
        this.stopLoading();
      });
  },
  
  // إظهار رسالة للمستخدم
  showMessage: function(type, text, timeout = 5000) {
    const id = Date.now();
    this.state.flashMessages.push({ id, type, text });
    
    // إنشاء عنصر التنبيه
    const alertContainer = document.getElementById('alert-container') || this.createAlertContainer();
    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${type}`;
    alertElement.setAttribute('role', 'alert');
    alertElement.setAttribute('data-id', id);
    alertElement.innerHTML = `
      <span>${text}</span>
      <button type="button" class="close" aria-label="Close">
        <span aria-hidden="true">&times;</span>
      </button>
    `;
    
    // إضافة مستمع الأحداث لزر الإغلاق
    const closeButton = alertElement.querySelector('.close');
    closeButton.addEventListener('click', () => {
      this.dismissMessage(id);
    });
    
    // إضافة التنبيه إلى الحاوية
    alertContainer.appendChild(alertElement);
    
    // إزالة التنبيه تلقائيًا بعد فترة زمنية محددة
    if (timeout > 0) {
      setTimeout(() => {
        this.dismissMessage(id);
      }, timeout);
    }
    
    return id;
  },
  
  // إنشاء حاوية للتنبيهات إذا لم تكن موجودة
  createAlertContainer: function() {
    const container = document.createElement('div');
    container.id = 'alert-container';
    container.className = 'alert-container';
    document.body.prepend(container);
    return container;
  },
  
  // إزالة رسالة
  dismissMessage: function(id) {
    const alertContainer = document.getElementById('alert-container');
    if (!alertContainer) return;
    
    const alertElement = alertContainer.querySelector(`[data-id="${id}"]`);
    if (alertElement) {
      // إضافة تأثير الاختفاء التدريجي
      alertElement.style.opacity = '0';
      
      // إزالة العنصر بعد اكتمال التأثير
      setTimeout(() => {
        if (alertElement.parentNode) {
          alertElement.parentNode.removeChild(alertElement);
        }
        
        // تحديث حالة الرسائل
        this.state.flashMessages = this.state.flashMessages.filter(msg => msg.id !== id);
      }, 300);
    }
  },
  
  // إعداد أحداث النقر والنماذج
  setupEventListeners: function() {
    // مستمع النقر العام
    document.addEventListener('click', event => {
      // التعامل مع روابط التنقل
      if (event.target.matches('a[data-route]') || event.target.closest('a[data-route]')) {
        const link = event.target.matches('a[data-route]') ? event.target : event.target.closest('a[data-route]');
        event.preventDefault();
        const route = link.getAttribute('data-route');
        this.navigateTo(route);
      }
      
      // زر تسجيل الخروج
      if (event.target.matches('#logout-btn') || event.target.closest('#logout-btn')) {
        event.preventDefault();
        this.logout();
      }
    });
    
    // مستمع تقديم النماذج
    document.addEventListener('submit', event => {
      // نموذج تسجيل الدخول
      if (event.target.matches('#login-form')) {
        event.preventDefault();
        const email = event.target.querySelector('#email').value;
        const password = event.target.querySelector('#password').value;
        this.login(email, password);
      }
      
      // نموذج التسجيل
      if (event.target.matches('#register-form')) {
        event.preventDefault();
        const formData = new FormData(event.target);
        const userData = {
          name: formData.get('name'),
          email: formData.get('email'),
          password: formData.get('password')
        };
        
        // التحقق من تطابق كلمات المرور
        const passwordConfirm = formData.get('password_confirm');
        if (userData.password !== passwordConfirm) {
          this.showMessage('danger', 'كلمات المرور غير متطابقة');
          return;
        }
        
        this.register(userData);
      }
      
      // نموذج التقييم
      if (event.target.matches('#evaluation-form')) {
        event.preventDefault();
        this.submitEvaluation(event.target);
      }
    });
  },
  
  // إعداد نظام التنقل
  setupNavigation: function() {
    // تعريف المسارات
    this.routes = {
      '/': {
        template: '#home-template',
        title: 'الصفحة الرئيسية - نظام تقييم BTEC',
        init: () => {
          console.log('تم تحميل الصفحة الرئيسية');
        }
      },
      '/login': {
        template: '#login-template',
        title: 'تسجيل الدخول - نظام تقييم BTEC',
        init: () => {
          console.log('تم تحميل صفحة تسجيل الدخول');
        }
      },
      '/register': {
        template: '#register-template',
        title: 'إنشاء حساب - نظام تقييم BTEC',
        init: () => {
          console.log('تم تحميل صفحة التسجيل');
        }
      },
      '/dashboard': {
        template: '#dashboard-template',
        title: 'لوحة التحكم - نظام تقييم BTEC',
        auth: true,
        init: () => {
          console.log('تم تحميل لوحة التحكم');
          this.loadDashboardData();
        }
      },
      '/evaluations': {
        template: '#evaluations-template',
        title: 'التقييمات - نظام تقييم BTEC',
        auth: true,
        init: () => {
          console.log('تم تحميل صفحة التقييمات');
          this.loadEvaluations();
        }
      },
      '/evaluation/new': {
        template: '#evaluation-form-template',
        title: 'تقييم جديد - نظام تقييم BTEC',
        auth: true,
        init: () => {
          console.log('تم تحميل نموذج التقييم الجديد');
          this.loadRubrics();
        }
      },
      '/evaluation/:id': {
        template: '#evaluation-details-template',
        title: 'تفاصيل التقييم - نظام تقييم BTEC',
        auth: true,
        init: (params) => {
          console.log('تم تحميل تفاصيل التقييم', params.id);
          this.loadEvaluationDetails(params.id);
        }
      },
      '/rubrics': {
        template: '#rubrics-template',
        title: 'معايير التقييم - نظام تقييم BTEC',
        auth: true,
        init: () => {
          console.log('تم تحميل صفحة معايير التقييم');
          this.loadRubrics();
        }
      },
      '/profile': {
        template: '#profile-template',
        title: 'الملف الشخصي - نظام تقييم BTEC',
        auth: true,
        init: () => {
          console.log('تم تحميل صفحة الملف الشخصي');
          this.loadUserProfile();
        }
      },
      '/about': {
        template: '#about-template',
        title: 'حول النظام - نظام تقييم BTEC',
        init: () => {
          console.log('تم تحميل صفحة حول النظام');
        }
      },
      '/error404': {
        template: '#error-404-template',
        title: 'الصفحة غير موجودة - نظام تقييم BTEC'
      }
    };
    
    // استمع لتغييرات URL
    window.addEventListener('popstate', () => {
      this.handleRoute();
    });
  },
  
  // معالجة المسار الأولي
  handleInitialRoute: function() {
    this.handleRoute();
  },
  
  // التنقل إلى مسار معين
  navigateTo: function(path) {
    history.pushState(null, null, path);
    this.handleRoute();
  },
  
  // معالجة المسار الحالي
  handleRoute: function() {
    const path = window.location.pathname;
    
    // البحث عن مسار مطابق
    let matchedRoute = null;
    let params = {};
    
    // تحقق من المسارات المحددة أولاً
    for (const routePath in this.routes) {
      // تجاهل الخصائص الموروثة
      if (!this.routes.hasOwnProperty(routePath)) continue;
      
      // التعامل مع المسارات الديناميكية (مثل /evaluation/:id)
      if (routePath.includes(':')) {
        const routeParts = routePath.split('/');
        const pathParts = path.split('/');
        
        if (routeParts.length === pathParts.length) {
          let isMatch = true;
          
          for (let i = 0; i < routeParts.length; i++) {
            if (routeParts[i].startsWith(':')) {
              // جزء ديناميكي - استخراج المعلمة
              const paramName = routeParts[i].substring(1);
              params[paramName] = pathParts[i];
            } else if (routeParts[i] !== pathParts[i]) {
              // جزء ثابت لا يتطابق
              isMatch = false;
              break;
            }
          }
          
          if (isMatch) {
            matchedRoute = this.routes[routePath];
            break;
          }
        }
      } else if (routePath === path) {
        // مسار ثابت مطابق تمامًا
        matchedRoute = this.routes[routePath];
        break;
      }
    }
    
    // إذا لم يتم العثور على مطابقة، استخدم مسار 404
    if (!matchedRoute) {
      matchedRoute = this.routes['/error404'];
      params = {};
    }
    
    // التحقق من متطلبات المصادقة
    if (matchedRoute.auth && !this.state.isAuthenticated) {
      this.showMessage('warning', 'يرجى تسجيل الدخول للوصول إلى هذه الصفحة');
      this.navigateTo('/login');
      return;
    }
    
    // عرض القالب
    this.renderTemplate(matchedRoute.template, params);
    
    // تحديث عنوان الصفحة
    document.title = matchedRoute.title || 'نظام تقييم BTEC';
    
    // تنفيذ التهيئة إذا كانت موجودة
    if (matchedRoute.init) {
      matchedRoute.init(params);
    }
    
    // تمييز الرابط النشط في شريط التنقل
    this.updateActiveNavLink(path);
  },
  
  // عرض القالب المطلوب
  renderTemplate: function(templateId, params = {}) {
    const appContainer = document.getElementById('app');
    if (!appContainer) {
      console.error('لم يتم العثور على حاوية التطبيق!');
      return;
    }
    
    const template = document.querySelector(templateId);
    if (!template) {
      console.error(`لم يتم العثور على القالب: ${templateId}`);
      appContainer.innerHTML = '<div class="alert alert-danger">خطأ في تحميل القالب</div>';
      return;
    }
    
    // نسخ محتوى القالب
    let content = template.innerHTML;
    
    // استبدال المعلمات في القالب
    for (const key in params) {
      if (params.hasOwnProperty(key)) {
        const regex = new RegExp(`\\{\\{\\s*${key}\\s*\\}\\}`, 'g');
        content = content.replace(regex, params[key]);
      }
    }
    
    // عرض المحتوى
    appContainer.innerHTML = content;
    
    // تحديث واجهة المصادقة
    this.updateAuthUI();
  },
  
  // تحديث الرابط النشط في شريط التنقل
  updateActiveNavLink: function(path) {
    // إزالة الفئة النشطة من جميع الروابط
    document.querySelectorAll('.nav-link').forEach(link => {
      link.classList.remove('active');
    });
    
    // إضافة الفئة النشطة إلى الرابط المطابق
    document.querySelectorAll(`.nav-link[data-route="${path}"]`).forEach(link => {
      link.classList.add('active');
    });
  },
  
  // تحميل بيانات لوحة التحكم
  loadDashboardData: function() {
    this.api('/dashboard')
      .then(data => {
        // تحديث إحصائيات لوحة التحكم
        if (data.stats) {
          document.getElementById('total-evaluations').textContent = data.stats.totalEvaluations || 0;
          document.getElementById('pending-evaluations').textContent = data.stats.pendingEvaluations || 0;
          document.getElementById('completed-evaluations').textContent = data.stats.completedEvaluations || 0;
          document.getElementById('average-score').textContent = data.stats.averageScore ? `${data.stats.averageScore.toFixed(1)}%` : 'غير متوفر';
        }
        
        // تحميل التقييمات الأخيرة
        if (data.recentEvaluations && data.recentEvaluations.length) {
          const tableBody = document.getElementById('recent-evaluations-table').querySelector('tbody');
          tableBody.innerHTML = '';
          
          data.recentEvaluations.forEach(evaluation => {
            const row = document.createElement('tr');
            row.innerHTML = `
              <td>${evaluation.id}</td>
              <td>${evaluation.assignment_id || 'غير محدد'}</td>
              <td>${this.formatDate(evaluation.created_at)}</td>
              <td>${this.getStatusBadge(evaluation.status)}</td>
              <td>${evaluation.score !== null ? `${evaluation.score.toFixed(1)}%` : '-'}</td>
              <td>
                <a href="/evaluation/${evaluation.id}" class="btn btn-sm btn-primary">عرض</a>
              </td>
            `;
            tableBody.appendChild(row);
          });
        } else {
          document.getElementById('recent-evaluations-container').innerHTML = 
            '<div class="alert alert-info">لا توجد تقييمات حديثة</div>';
        }
      })
      .catch(error => {
        console.error('خطأ في تحميل بيانات لوحة التحكم:', error);
      });
  },
  
  // تحميل التقييمات
  loadEvaluations: function() {
    this.api('/evaluations')
      .then(data => {
        const tableBody = document.getElementById('evaluations-table').querySelector('tbody');
        tableBody.innerHTML = '';
        
        if (data.evaluations && data.evaluations.length) {
          data.evaluations.forEach(evaluation => {
            const row = document.createElement('tr');
            row.innerHTML = `
              <td>${evaluation.id}</td>
              <td>${evaluation.assignment_id || 'غير محدد'}</td>
              <td>${this.formatDate(evaluation.created_at)}</td>
              <td>${this.getStatusBadge(evaluation.status)}</td>
              <td>${evaluation.score !== null ? `${evaluation.score.toFixed(1)}%` : '-'}</td>
              <td>
                <a href="/evaluation/${evaluation.id}" class="btn btn-sm btn-primary">عرض</a>
              </td>
            `;
            tableBody.appendChild(row);
          });
        } else {
          document.getElementById('evaluations-container').innerHTML = 
            '<div class="alert alert-info">لا توجد تقييمات</div>';
        }
      })
      .catch(error => {
        console.error('خطأ في تحميل التقييمات:', error);
      });
  },
  
  // تحميل تفاصيل التقييم
  loadEvaluationDetails: function(id) {
    this.api(`/evaluation/${id}`)
      .then(data => {
        if (!data.evaluation) {
          this.showMessage('danger', 'لم يتم العثور على التقييم');
          this.navigateTo('/evaluations');
          return;
        }
        
        const evaluation = data.evaluation;
        
        // تحديث معلومات التقييم
        document.getElementById('evaluation-id').textContent = evaluation.id;
        document.getElementById('evaluation-assignment').textContent = evaluation.assignment_id || 'غير محدد';
        document.getElementById('evaluation-status').innerHTML = this.getStatusBadge(evaluation.status);
        document.getElementById('evaluation-score').textContent = evaluation.score !== null ? `${evaluation.score.toFixed(1)}%` : 'غير متوفر';
        document.getElementById('evaluation-date').textContent = this.formatDate(evaluation.created_at);
        
        // عرض نص المهمة المقدمة
        const submissionContainer = document.getElementById('submission-text');
        submissionContainer.textContent = evaluation.submission_text || 'لا يوجد نص مقدم';
        
        // عرض نتائج التقييم
        const resultsContainer = document.getElementById('evaluation-results');
        
        if (evaluation.evaluation_result && Object.keys(evaluation.evaluation_result).length) {
          let resultsHtml = '<div class="criteria-list">';
          
          Object.entries(evaluation.evaluation_result).forEach(([criterion, result]) => {
            resultsHtml += `
              <div class="criteria-item">
                <div class="criteria-header">
                  <div class="criteria-title">${criterion}</div>
                  <div class="criteria-score">${result.score !== undefined ? `${result.score} / ${result.max_score || 100}` : 'غير مقيم'}</div>
                </div>
                <div class="criteria-feedback">${result.feedback || 'لا توجد ملاحظات'}</div>
              </div>
            `;
          });
          
          resultsHtml += '</div>';
          resultsContainer.innerHTML = resultsHtml;
        } else {
          resultsContainer.innerHTML = '<div class="alert alert-info">لم يتم إكمال نتائج التقييم بعد</div>';
        }
        
        // عرض تعليقات المقيم
        document.getElementById('evaluator-comments').textContent = evaluation.evaluator_comments || 'لا توجد تعليقات';
        
        // إظهار/إخفاء زر تصدير PDF بناءً على ما إذا كان التقييم مكتملاً
        const exportBtn = document.getElementById('export-pdf-btn');
        if (exportBtn) {
          exportBtn.style.display = evaluation.status === 'completed' ? '' : 'none';
        }
      })
      .catch(error => {
        console.error('خطأ في تحميل تفاصيل التقييم:', error);
      });
  },
  
  // تحميل معايير التقييم
  loadRubrics: function() {
    this.api('/rubrics')
      .then(data => {
        if (!data.rubrics || !data.rubrics.length) {
          const container = document.getElementById('rubrics-container') || document.getElementById('rubric-select-container');
          if (container) {
            container.innerHTML = '<div class="alert alert-info">لا توجد معايير تقييم متاحة</div>';
          }
          return;
        }
        
        // تحقق مما إذا كنا في صفحة معايير التقييم أو نموذج التقييم
        const rubricsContainer = document.getElementById('rubrics-container');
        const rubricSelect = document.getElementById('rubric-select');
        
        if (rubricsContainer) {
          // عرض قائمة معايير التقييم
          rubricsContainer.innerHTML = '';
          
          data.rubrics.forEach(rubric => {
            const card = document.createElement('div');
            card.className = 'card';
            card.innerHTML = `
              <div class="card-title">${rubric.name}</div>
              <div class="card-subtitle">الدرجة الكلية: ${rubric.max_score}</div>
              <div class="card-body">
                <p>${rubric.description || 'لا يوجد وصف'}</p>
                <div class="criteria-list">
                  ${this.renderRubricCriteria(rubric.criteria)}
                </div>
              </div>
              <div class="card-footer">
                <button data-rubric-id="${rubric.id}" class="btn btn-primary use-rubric-btn">استخدام هذا المعيار</button>
              </div>
            `;
            
            rubricsContainer.appendChild(card);
          });
          
          // إضافة مستمعي الأحداث لأزرار استخدام المعيار
          document.querySelectorAll('.use-rubric-btn').forEach(btn => {
            btn.addEventListener('click', (event) => {
              const rubricId = event.target.getAttribute('data-rubric-id');
              this.navigateTo(`/evaluation/new?rubric=${rubricId}`);
            });
          });
        } else if (rubricSelect) {
          // ملء قائمة منسدلة لاختيار معيار التقييم
          rubricSelect.innerHTML = '<option value="">اختر معيار التقييم...</option>';
          
          data.rubrics.forEach(rubric => {
            const option = document.createElement('option');
            option.value = rubric.id;
            option.textContent = rubric.name;
            rubricSelect.appendChild(option);
          });
          
          // التحقق مما إذا كان هناك معيار محدد في المعلمات
          const urlParams = new URLSearchParams(window.location.search);
          const selectedRubric = urlParams.get('rubric');
          
          if (selectedRubric) {
            rubricSelect.value = selectedRubric;
            this.loadRubricDetails(selectedRubric);
          }
          
          // إضافة مستمع حدث لتحميل تفاصيل المعيار عند التغيير
          rubricSelect.addEventListener('change', () => {
            const rubricId = rubricSelect.value;
            if (rubricId) {
              this.loadRubricDetails(rubricId);
            } else {
              document.getElementById('criteria-container').innerHTML = 
                '<div class="alert alert-info">يرجى اختيار معيار تقييم</div>';
            }
          });
        }
      })
      .catch(error => {
        console.error('خطأ في تحميل معايير التقييم:', error);
      });
  },
  
  // عرض معايير التقييم
  renderRubricCriteria: function(criteria) {
    if (!criteria || Object.keys(criteria).length === 0) {
      return '<div class="alert alert-info">لا توجد معايير محددة</div>';
    }
    
    let html = '';
    
    Object.entries(criteria).forEach(([criterion, details]) => {
      html += `
        <div class="criteria-item">
          <div class="criteria-header">
            <div class="criteria-title">${criterion}</div>
            <div class="criteria-score">${details.max_score || 100} نقطة</div>
          </div>
          <div class="criteria-description">${details.description || 'لا يوجد وصف'}</div>
        </div>
      `;
    });
    
    return html;
  },
  
  // تحميل تفاصيل معيار التقييم
  loadRubricDetails: function(rubricId) {
    this.api(`/rubric/${rubricId}`)
      .then(data => {
        if (!data.rubric) {
          this.showMessage('danger', 'لم يتم العثور على معيار التقييم');
          return;
        }
        
        const criteriaContainer = document.getElementById('criteria-container');
        criteriaContainer.innerHTML = '';
        
        if (data.rubric.criteria && Object.keys(data.rubric.criteria).length) {
          Object.entries(data.rubric.criteria).forEach(([criterion, details]) => {
            const criterionElement = document.createElement('div');
            criterionElement.className = 'criteria-item';
            criterionElement.innerHTML = `
              <div class="criteria-header">
                <div class="criteria-title">${criterion}</div>
                <div class="criteria-score">
                  <input type="range" class="score-slider" name="criteria[${criterion}][score]" 
                         min="0" max="${details.max_score || 100}" value="0" step="1">
                  <span class="score-value">0</span> / ${details.max_score || 100}
                </div>
              </div>
              <div class="criteria-description">${details.description || 'لا يوجد وصف'}</div>
              <div class="form-group">
                <label for="feedback-${criterion.replace(/\s+/g, '-').toLowerCase()}">ملاحظات:</label>
                <textarea class="form-control" name="criteria[${criterion}][feedback]" 
                          id="feedback-${criterion.replace(/\s+/g, '-').toLowerCase()}" 
                          rows="3"></textarea>
              </div>
            `;
            
            criteriaContainer.appendChild(criterionElement);
            
            // إضافة مستمع أحداث لشريط التمرير
            const slider = criterionElement.querySelector('.score-slider');
            const scoreValue = criterionElement.querySelector('.score-value');
            
            slider.addEventListener('input', () => {
              scoreValue.textContent = slider.value;
            });
          });
          
          // إظهار زر التقديم
          document.getElementById('submit-btn').style.display = '';
        } else {
          criteriaContainer.innerHTML = '<div class="alert alert-info">لا توجد معايير محددة لهذا المعيار</div>';
          // إخفاء زر التقديم
          document.getElementById('submit-btn').style.display = 'none';
        }
      })
      .catch(error => {
        console.error('خطأ في تحميل تفاصيل معيار التقييم:', error);
      });
  },
  
  // تقديم نموذج التقييم
  submitEvaluation: function(form) {
    const formData = new FormData(form);
    const rubricId = formData.get('rubric_id');
    const assignmentId = formData.get('assignment_id');
    const submissionText = formData.get('submission_text');
    
    if (!rubricId) {
      this.showMessage('danger', 'يرجى اختيار معيار تقييم');
      return;
    }
    
    if (!submissionText) {
      this.showMessage('danger', 'يرجى إدخال نص المهمة المقدمة');
      return;
    }
    
    // جمع بيانات المعايير
    const criteria = {};
    const criteriaInputs = form.querySelectorAll('[name^="criteria["]');
    
    criteriaInputs.forEach(input => {
      const matches = input.name.match(/criteria\[(.*?)\]\[(.*?)\]/);
      if (matches && matches.length === 3) {
        const criterion = matches[1];
        const field = matches[2];
        
        if (!criteria[criterion]) {
          criteria[criterion] = {};
        }
        
        criteria[criterion][field] = input.value;
      }
    });
    
    // إعداد بيانات النموذج
    const evaluationData = {
      rubric_id: rubricId,
      assignment_id: assignmentId,
      submission_text: submissionText,
      evaluation_result: criteria
    };
    
    // إرسال التقييم
    this.api('/evaluations', {
      method: 'POST',
      body: JSON.stringify(evaluationData)
    })
    .then(data => {
      this.showMessage('success', 'تم تقديم التقييم بنجاح');
      this.navigateTo(`/evaluation/${data.evaluation_id}`);
    })
    .catch(error => {
      console.error('خطأ في تقديم التقييم:', error);
    });
  },
  
  // تحميل الملف الشخصي للمستخدم
  loadUserProfile: function() {
    this.api('/user/profile')
      .then(data => {
        if (!data.user) {
          this.showMessage('danger', 'لم يتم العثور على معلومات المستخدم');
          return;
        }
        
        // تحديث معلومات الملف الشخصي
        document.getElementById('profile-name').value = data.user.name || '';
        document.getElementById('profile-email').value = data.user.email || '';
        
        // إعداد مستمع الأحداث لنموذج تحديث الملف الشخصي
        const profileForm = document.getElementById('profile-form');
        if (profileForm) {
          profileForm.addEventListener('submit', (event) => {
            event.preventDefault();
            this.updateUserProfile(profileForm);
          });
        }
        
        // إعداد مستمع الأحداث لنموذج تغيير كلمة المرور
        const passwordForm = document.getElementById('password-form');
        if (passwordForm) {
          passwordForm.addEventListener('submit', (event) => {
            event.preventDefault();
            this.updateUserPassword(passwordForm);
          });
        }
      })
      .catch(error => {
        console.error('خطأ في تحميل معلومات الملف الشخصي:', error);
      });
  },
  
  // تحديث الملف الشخصي للمستخدم
  updateUserProfile: function(form) {
    const formData = new FormData(form);
    const userData = {
      name: formData.get('name'),
      email: formData.get('email')
    };
    
    this.api('/user/profile', {
      method: 'PUT',
      body: JSON.stringify(userData)
    })
    .then(data => {
      this.showMessage('success', 'تم تحديث الملف الشخصي بنجاح');
      
      // تحديث اسم المستخدم المعروض
      if (this.state.user) {
        this.state.user.name = userData.name;
        this.updateAuthUI();
      }
    })
    .catch(error => {
      console.error('خطأ في تحديث الملف الشخصي:', error);
    });
  },
  
  // تحديث كلمة مرور المستخدم
  updateUserPassword: function(form) {
    const formData = new FormData(form);
    const currentPassword = formData.get('current_password');
    const newPassword = formData.get('new_password');
    const confirmPassword = formData.get('confirm_password');
    
    if (!currentPassword || !newPassword || !confirmPassword) {
      this.showMessage('danger', 'يرجى ملء جميع الحقول');
      return;
    }
    
    if (newPassword !== confirmPassword) {
      this.showMessage('danger', 'كلمات المرور الجديدة غير متطابقة');
      return;
    }
    
    this.api('/user/password', {
      method: 'PUT',
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword
      })
    })
    .then(data => {
      this.showMessage('success', 'تم تحديث كلمة المرور بنجاح');
      form.reset();
    })
    .catch(error => {
      console.error('خطأ في تحديث كلمة المرور:', error);
    });
  },
  
  // مؤشر التحميل
  startLoading: function() {
    this.state.pendingRequests++;
    this.updateLoadingState();
  },
  
  stopLoading: function() {
    this.state.pendingRequests = Math.max(0, this.state.pendingRequests - 1);
    this.updateLoadingState();
  },
  
  updateLoadingState: function() {
    const loadingIndicator = document.getElementById('loading-indicator');
    
    if (!loadingIndicator) {
      // إنشاء مؤشر التحميل إذا لم يكن موجودًا
      const indicator = document.createElement('div');
      indicator.id = 'loading-indicator';
      indicator.className = 'loading-indicator';
      indicator.innerHTML = '<div class="spinner"></div>';
      document.body.appendChild(indicator);
    }
    
    const indicator = document.getElementById('loading-indicator');
    
    if (this.state.pendingRequests > 0) {
      indicator.classList.add('active');
    } else {
      indicator.classList.remove('active');
    }
  },
  
  // دوال مساعدة
  formatDate: function(dateString) {
    if (!dateString) return 'غير متوفر';
    
    const date = new Date(dateString);
    const options = { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    };
    
    return date.toLocaleDateString('ar-SA', options);
  },
  
  getStatusBadge: function(status) {
    let badgeClass = 'badge ';
    let statusText = '';
    
    switch (status) {
      case 'pending':
        badgeClass += 'bg-warning';
        statusText = 'قيد الانتظار';
        break;
      case 'in_progress':
        badgeClass += 'bg-info';
        statusText = 'قيد التنفيذ';
        break;
      case 'completed':
        badgeClass += 'bg-success';
        statusText = 'مكتمل';
        break;
      case 'rejected':
        badgeClass += 'bg-danger';
        statusText = 'مرفوض';
        break;
      default:
        badgeClass += 'bg-secondary';
        statusText = status || 'غير معروف';
    }
    
    return `<span class="${badgeClass}">${statusText}</span>`;
  }
};

// تهيئة التطبيق عند تحميل المستند
document.addEventListener('DOMContentLoaded', function() {
  BTECApp.init();
});
