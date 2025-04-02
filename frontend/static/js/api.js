/**
 * ملف لإدارة طلبات API في نظام تقييم BTEC
 */

class BTECApi {
    /**
     * الحصول على URL الأساسي للـ API
     * @returns {string} عنوان URL الأساسي
     */
    static get baseUrl() {
        return '/api';
    }

    /**
     * إجراء طلب HTTP
     * @param {string} endpoint نقطة النهاية API
     * @param {string} method طريقة HTTP
     * @param {Object} data بيانات الطلب (اختياري)
     * @returns {Promise} وعد بالاستجابة
     */
    static async request(endpoint, method, data = null) {
        const url = `${this.baseUrl}${endpoint}`;
        
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json'
            }
        };
        
        // إضافة بيانات الجسم إذا كانت متوفرة
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        // إضافة رمز المصادقة إذا كان متوفرًا
        const token = localStorage.getItem('token');
        if (token) {
            options.headers['Authorization'] = `Bearer ${token}`;
        }
        
        try {
            const response = await fetch(url, options);
            const responseData = await response.json();
            
            if (!response.ok) {
                throw new Error(responseData.message || 'حدث خطأ في طلب API');
            }
            
            return responseData;
        } catch (error) {
            console.error(`خطأ في طلب API (${method} ${endpoint}):`, error);
            throw error;
        }
    }

    /**
     * تسجيل مستخدم جديد
     * @param {Object} userData بيانات المستخدم
     * @returns {Promise} وعد بالاستجابة
     */
    static async register(userData) {
        return this.request('/auth/register', 'POST', userData);
    }

    /**
     * تسجيل الدخول
     * @param {Object} credentials بيانات تسجيل الدخول
     * @returns {Promise} وعد بالاستجابة
     */
    static async login(credentials) {
        return this.request('/auth/login', 'POST', credentials);
    }

    /**
     * إرسال مهمة للتقييم
     * @param {Object} taskData بيانات المهمة
     * @returns {Promise} وعد بالاستجابة
     */
    static async evaluateTask(taskData) {
        return this.request('/evaluation/submit', 'POST', taskData);
    }

    /**
     * إرسال مهمة للتقييم مع معايير محددة
     * @param {Object} taskData بيانات المهمة مع معايير التقييم
     * @returns {Promise} وعد بالاستجابة
     */
    static async evaluateWithRubric(taskData) {
        return this.request('/evaluation/rubric', 'POST', taskData);
    }

    /**
     * الحصول على جميع التقييمات
     * @returns {Promise} وعد بالاستجابة
     */
    static async getEvaluations() {
        return this.request('/evaluation/list', 'GET');
    }

    /**
     * الحصول على تقييم محدد
     * @param {number} evaluationId معرف التقييم
     * @returns {Promise} وعد بالاستجابة
     */
    static async getEvaluation(evaluationId) {
        return this.request(`/evaluation/${evaluationId}`, 'GET');
    }

    /**
     * التحقق من صحة تقييم باستخدام blockchain
     * @param {number} evaluationId معرف التقييم
     * @returns {Promise} وعد بالاستجابة
     */
    static async verifyEvaluation(evaluationId) {
        return this.request(`/evaluation/${evaluationId}/verify`, 'GET');
    }

    /**
     * التحقق من صحة تقييم عام باستخدام رمز التحقق
     * @param {string} auditHash رمز التحقق
     * @returns {Promise} وعد بالاستجابة
     */
    static async verifyPublic(auditHash) {
        return this.request(`/evaluation/verify/${auditHash}`, 'GET');
    }

    /**
     * تسجيل الخروج
     */
    static logout() {
        localStorage.removeItem('token');
        localStorage.removeItem('user_id');
    }

    /**
     * التحقق مما إذا كان المستخدم مسجل الدخول
     * @returns {boolean} حالة تسجيل الدخول
     */
    static isLoggedIn() {
        return !!localStorage.getItem('token');
    }
}