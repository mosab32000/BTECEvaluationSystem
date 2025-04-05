/* نظام تقييم BTEC - ملف JavaScript الرئيسي */

document.addEventListener("DOMContentLoaded", function() {
    console.log("تم تحميل نظام تقييم BTEC");
    
    // إظهار ورسائل الخطأ والنجاح
    const flashMessages = document.querySelectorAll(".alert");
    if (flashMessages.length > 0) {
        flashMessages.forEach(message => {
            setTimeout(() => {
                message.classList.add("fade-out");
                setTimeout(() => {
                    message.style.display = "none";
                }, 500);
            }, 5000);
        });
    }
    
    // تفعيل التلميحات
    const tooltips = document.querySelectorAll("[data-toggle=\"tooltip\"]");
    if (tooltips.length > 0) {
        tooltips.forEach(tooltip => {
            new bootstrap.Tooltip(tooltip);
        });
    }
    
    // مربع البحث
    const searchInput = document.getElementById("search-input");
    if (searchInput) {
        searchInput.addEventListener("input", function() {
            const searchTerm = this.value.toLowerCase();
            const items = document.querySelectorAll(".searchable-item");
            
            items.forEach(item => {
                const text = item.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    item.style.display = "block";
                } else {
                    item.style.display = "none";
                }
            });
        });
    }
});

// تأكيد الحذف
function confirmDelete(event, message) {
    if (!confirm(message || "هل أنت متأكد من أنك تريد الحذف؟")) {
        event.preventDefault();
    }
}
