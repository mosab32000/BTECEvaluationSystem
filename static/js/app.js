// ملف JavaScript الرئيسي لنظام تقييم BTEC

document.addEventListener('DOMContentLoaded', function() {
    console.log('تم تحميل نظام تقييم BTEC');
    
    // التحقق من حالة الخادم
    checkServerStatus();
});

// التحقق من حالة الخادم
async function checkServerStatus() {
    try {
        const response = await fetch('/health');
        const data = await response.json();
        
        if (data.status === 'healthy') {
            console.log('الخادم يعمل بشكل صحيح!');
        } else {
            console.error('هناك مشكلة في الخادم');
        }
    } catch (error) {
        console.error('لا يمكن الاتصال بالخادم:', error);
    }
}
