/**
 * مُدقِّق - منصة تدقيق المشاريع
 * الملف الرئيسي للسكربتات
 */

document.addEventListener('DOMContentLoaded', function() {
    // إخفاء رسائل التنبيه تلقائيًا بعد 5 ثوانٍ
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // تفعيل tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // معاينة الملفات قبل الرفع
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function() {
            const previewDiv = document.getElementById(`${input.id}-preview`);
            if (previewDiv) {
                previewDiv.innerHTML = '';
                if (input.files && input.files[0]) {
                    const fileName = input.files[0].name;
                    const fileSize = (input.files[0].size / 1024).toFixed(2) + ' KB';
                    
                    const fileInfo = document.createElement('div');
                    fileInfo.classList.add('alert', 'alert-info', 'mb-2');
                    fileInfo.innerHTML = `<i class="fas fa-file me-2"></i><strong>${fileName}</strong> (${fileSize})`;
                    
                    previewDiv.appendChild(fileInfo);
                    
                    // معاينة الصور إذا كان الملف صورة
                    if (input.files[0].type.match('image.*')) {
                        const reader = new FileReader();
                        reader.onload = function(e) {
                            const img = document.createElement('img');
                            img.src = e.target.result;
                            img.classList.add('img-thumbnail', 'mt-2');
                            img.style.maxHeight = '200px';
                            previewDiv.appendChild(img);
                        }
                        reader.readAsDataURL(input.files[0]);
                    }
                }
            }
        });
    });
    
    // تأكيد الحذف
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('هل أنت متأكد من رغبتك في الحذف؟ لا يمكن التراجع عن هذا الإجراء.')) {
                e.preventDefault();
            }
        });
    });
    
    // نموذج البحث
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const searchInput = document.getElementById('searchQuery');
            if (searchInput.value.trim() === '') {
                e.preventDefault();
                searchInput.focus();
            }
        });
    }
});

/**
 * تهيئة الرسوم البيانية (إذا تم تضمين Chart.js)
 */
function initCharts() {
    if (typeof Chart === 'undefined') return;
    
    // مثال على رسم بياني للمشاريع حسب الحالة
    const projectStatusChart = document.getElementById('projectStatusChart');
    if (projectStatusChart) {
        const statusData = JSON.parse(projectStatusChart.dataset.values || '[]');
        const statusLabels = JSON.parse(projectStatusChart.dataset.labels || '[]');
        
        new Chart(projectStatusChart, {
            type: 'pie',
            data: {
                labels: statusLabels,
                datasets: [{
                    data: statusData,
                    backgroundColor: [
                        '#ffc107', // قيد الانتظار
                        '#0dcaf0', // قيد التدقيق
                        '#198754', // مكتمل
                        '#dc3545'  // مرفوض
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                    }
                }
            }
        });
    }
    
    // مثال على رسم بياني لمتوسط الدرجات
    const scoresChart = document.getElementById('scoresChart');
    if (scoresChart) {
        const scoresData = JSON.parse(scoresChart.dataset.values || '[]');
        const scoresLabels = JSON.parse(scoresChart.dataset.labels || '[]');
        
        new Chart(scoresChart, {
            type: 'bar',
            data: {
                labels: scoresLabels,
                datasets: [{
                    label: 'متوسط الدرجات',
                    data: scoresData,
                    backgroundColor: '#0d6efd',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }
}

// استدعاء دالة تهيئة الرسوم البيانية إذا كانت متاحة
if (typeof Chart !== 'undefined') {
    document.addEventListener('DOMContentLoaded', initCharts);
}
