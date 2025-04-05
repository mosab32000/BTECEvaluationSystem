/**
 * نظام تقييم BTEC - الملف الرئيسي للجافاسكريبت
 */

// تهيئة التلميحات
document.addEventListener('DOMContentLoaded', function() {
    // تفعيل التلميحات (Tooltips) في Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // تحديد الرابط النشط في شريط التنقل
    const currentPath = window.location.pathname;
    document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
        // استثناء القائمة المنسدلة
        if (!link.classList.contains('dropdown-toggle')) {
            const linkPath = link.getAttribute('href');
            if (linkPath && (currentPath === linkPath || currentPath.startsWith(linkPath + '/'))) {
                link.classList.add('active');
            }
        }
    });

    // إضافة تأثيرات عند مرور الماوس على البطاقات
    document.querySelectorAll('.card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            if (!this.classList.contains('no-hover-effect')) {
                this.style.transition = 'transform 0.3s ease, box-shadow 0.3s ease';
                this.style.transform = 'translateY(-5px)';
                this.style.boxShadow = '0 8px 15px rgba(0, 0, 0, 0.2)';
            }
        });
        
        card.addEventListener('mouseleave', function() {
            if (!this.classList.contains('no-hover-effect')) {
                this.style.transform = 'translateY(0)';
                this.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.1)';
            }
        });
    });
    
    // تحويل رسائل الفلاش لتختفي تلقائيًا بعد 5 ثوان
    setTimeout(function() {
        document.querySelectorAll('.alert:not(.alert-important)').forEach(alert => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // تفعيل تنسيق التواريخ - عند وجود حقول التاريخ
    const dateInputs = document.querySelectorAll('input[type="date"]');
    if (dateInputs.length > 0) {
        // تعيين تاريخ اليوم كقيمة افتراضية
        const today = new Date().toISOString().split('T')[0];
        dateInputs.forEach(input => {
            if (!input.value) {
                input.value = today;
            }
        });
    }
    
    // تفعيل العد التنازلي للحصص التفاعلية
    const countdownElements = document.querySelectorAll('.countdown-timer');
    if (countdownElements.length > 0) {
        updateCountdowns();
        // تحديث العد التنازلي كل ثانية
        setInterval(updateCountdowns, 1000);
    }
});

// تحديث العد التنازلي للحصص التفاعلية
function updateCountdowns() {
    document.querySelectorAll('.countdown-timer').forEach(element => {
        const startTime = new Date(element.dataset.startTime);
        const now = new Date();
        
        // حساب الوقت المتبقي بالمللي ثانية
        let diff = startTime - now;
        
        if (diff <= 0) {
            // انتهى الوقت، الحصة بدأت
            element.textContent = "الحصة بدأت!";
            element.classList.add('text-success');
            return;
        }
        
        // تحويل الفرق إلى أيام وساعات ودقائق وثواني
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        diff -= days * (1000 * 60 * 60 * 24);
        
        const hours = Math.floor(diff / (1000 * 60 * 60));
        diff -= hours * (1000 * 60 * 60);
        
        const minutes = Math.floor(diff / (1000 * 60));
        diff -= minutes * (1000 * 60);
        
        const seconds = Math.floor(diff / 1000);
        
        // عرض العد التنازلي بتنسيق مناسب
        let countdownText = '';
        
        if (days > 0) {
            countdownText += `${days} يوم `;
        }
        
        countdownText += `${hours}:${minutes < 10 ? '0' : ''}${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
        element.textContent = countdownText;
    });
}

// تحميل الحصص القادمة للفصل الدراسي
function loadUpcomingSessions(classroomId) {
    fetch(`/api/sessions/upcoming?classroom_id=${classroomId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('حدث خطأ في جلب البيانات');
            }
            return response.json();
        })
        .then(data => {
            const sessionsContainer = document.getElementById('upcoming-sessions');
            
            if (sessionsContainer && data.sessions && data.sessions.length > 0) {
                let html = '';
                data.sessions.forEach(session => {
                    const startDate = new Date(session.start_time);
                    const startTimeStr = startDate.toLocaleTimeString('ar-SA', { hour: '2-digit', minute: '2-digit' });
                    const startDateStr = startDate.toLocaleDateString('ar-SA');
                    
                    let statusBadge = '';
                    if (session.status === 'scheduled') {
                        statusBadge = '<span class="badge bg-info">مجدولة</span>';
                    } else if (session.status === 'active') {
                        statusBadge = '<span class="badge bg-success">نشطة</span>';
                    } else if (session.status === 'completed') {
                        statusBadge = '<span class="badge bg-secondary">مكتملة</span>';
                    } else if (session.status === 'cancelled') {
                        statusBadge = '<span class="badge bg-danger">ملغاة</span>';
                    }
                    
                    html += `
                        <tr>
                            <td>${session.title}</td>
                            <td>${startDateStr}</td>
                            <td>${startTimeStr}</td>
                            <td>${session.session_type === 'live' ? 'مباشرة' : (session.session_type === 'recorded' ? 'مسجلة' : 'مختلطة')}</td>
                            <td>${statusBadge}</td>
                            <td>
                                <a href="/sessions/${session.id}" class="btn btn-sm btn-primary">
                                    عرض
                                </a>
                            </td>
                        </tr>
                    `;
                });
                sessionsContainer.innerHTML = html;
            } else if (sessionsContainer) {
                sessionsContainer.innerHTML = '<tr><td colspan="6" class="text-center">لا توجد حصص تفاعلية قادمة لهذا الفصل</td></tr>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            const sessionsContainer = document.getElementById('upcoming-sessions');
            if (sessionsContainer) {
                sessionsContainer.innerHTML = 
                    '<tr><td colspan="6" class="text-center text-danger">حدث خطأ أثناء تحميل الحصص</td></tr>';
            }
        });
}

// تحميل المشاركين في الحصة
function loadParticipants(sessionId) {
    fetch(`/api/sessions/${sessionId}/participants`)
        .then(response => {
            if (!response.ok) {
                throw new Error('حدث خطأ في جلب البيانات');
            }
            return response.json();
        })
        .then(data => {
            const participantsList = document.getElementById('participants-list');
            
            if (participantsList && data.participants && data.participants.length > 0) {
                let html = '';
                data.participants.forEach(participant => {
                    const joinTime = participant.join_time ? new Date(participant.join_time).toLocaleTimeString('ar-SA') : '-';
                    const leaveTime = participant.leave_time ? new Date(participant.leave_time).toLocaleTimeString('ar-SA') : '-';
                    
                    let statusBadge = '';
                    if (participant.attendance_status === 'present') {
                        statusBadge = '<span class="badge bg-success">حاضر</span>';
                    } else if (participant.attendance_status === 'absent') {
                        statusBadge = '<span class="badge bg-danger">غائب</span>';
                    } else if (participant.attendance_status === 'late') {
                        statusBadge = '<span class="badge bg-warning">متأخر</span>';
                    } else {
                        statusBadge = '<span class="badge bg-secondary">معلق</span>';
                    }
                    
                    let participationScore = '';
                    if (participant.participation_score !== null) {
                        participationScore = `<div class="progress">
                            <div class="progress-bar" role="progressbar" style="width: ${participant.participation_score * 10}%;" 
                                aria-valuenow="${participant.participation_score}" aria-valuemin="0" aria-valuemax="10">
                                ${participant.participation_score}/10
                            </div>
                        </div>`;
                    } else {
                        participationScore = '<span class="text-muted">غير مقيم</span>';
                    }
                    
                    html += `
                        <tr>
                            <td>${participant.user_name || 'مشارك'}</td>
                            <td>${joinTime}</td>
                            <td>${leaveTime}</td>
                            <td>${statusBadge}</td>
                            <td>${participationScore}</td>
                        </tr>
                    `;
                });
                participantsList.innerHTML = html;
            } else if (participantsList) {
                participantsList.innerHTML = '<tr><td colspan="5" class="text-center">لا يوجد مشاركون في هذه الحصة حتى الآن</td></tr>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            const participantsList = document.getElementById('participants-list');
            if (participantsList) {
                participantsList.innerHTML = 
                    '<tr><td colspan="5" class="text-center text-danger">حدث خطأ أثناء تحميل قائمة المشاركين</td></tr>';
            }
        });
}
