/**
 * JavaScript الرئيسي لواجهة قلعة Grok الأسطورية
 */

document.addEventListener('DOMContentLoaded', function() {
    // -------------- تهيئة عارض PDF --------------
    let pdfDoc = null; // المستند الحالي
    let pageNum = 1; // رقم الصفحة الحالية
    let pageRendering = false; // هل يتم عرض صفحة الآن
    let pageNumPending = null; // رقم الصفحة المعلقة
    let scale = 1.5; // مقياس العرض
    const canvas = document.getElementById('pdf-canvas');
    const ctx = canvas.getContext('2d');

    /**
     * عرض صفحة من ملف PDF
     * @param {number} num رقم الصفحة المراد عرضها
     */
    function renderPage(num) {
        pageRendering = true;
        if (!pdfDoc) return; // تجنب الأخطاء إذا لم يتم تحميل أي مستند

        // الحصول على الصفحة المطلوبة
        pdfDoc.getPage(num).then(function(page) {
            const viewport = page.getViewport({ scale: scale });
            canvas.height = viewport.height;
            canvas.width = viewport.width;

            // عرض الصفحة على الكانفاس
            const renderContext = {
                canvasContext: ctx,
                viewport: viewport
            };
            const renderTask = page.render(renderContext);

            // الانتظار حتى اكتمال العرض
            renderTask.promise.then(function() {
                pageRendering = false;
                if (pageNumPending !== null) {
                    // إذا كان هناك صفحة معلقة، عرضها الآن
                    renderPage(pageNumPending);
                    pageNumPending = null;
                }
            });
        });

        // تحديث معلومات الصفحة الحالية
        document.getElementById('page-current').textContent = num;
    }

    /**
     * إذا كانت هناك عملية عرض صفحة، قم بتعليق الطلب الجديد، وإلا قم بالعرض مباشرة
     */
    function queueRenderPage(num) {
        if (pageRendering) {
            pageNumPending = num;
        } else {
            renderPage(num);
        }
    }

    /**
     * الانتقال إلى الصفحة السابقة
     */
    function prevPage() {
        if (pageNum <= 1 || !pdfDoc) return;
        pageNum--;
        queueRenderPage(pageNum);
    }

    /**
     * الانتقال إلى الصفحة التالية
     */
    function nextPage() {
        if (!pdfDoc || pageNum >= pdfDoc.numPages) return;
        pageNum++;
        queueRenderPage(pageNum);
    }

    /**
     * تكبير المستند
     */
    function zoomIn() {
        scale += 0.2;
        queueRenderPage(pageNum);
    }

    /**
     * تصغير المستند
     */
    function zoomOut() {
        if (scale <= 0.5) return; // منع التصغير المفرط
        scale -= 0.2;
        queueRenderPage(pageNum);
    }

    // إضافة أحداث المستمعين لأزرار التنقل
    document.getElementById('prev-page').addEventListener('click', prevPage);
    document.getElementById('next-page').addEventListener('click', nextPage);
    document.getElementById('zoom-in').addEventListener('click', zoomIn);
    document.getElementById('zoom-out').addEventListener('click', zoomOut);

    // تحميل ملف PDF افتراضي (إذا كان هناك)
    /*
    pdfjsLib.getDocument('https://mozilla.github.io/pdf.js/web/compressed.tracemonkey-pldi-09.pdf')
        .promise.then(function(pdf) {
            pdfDoc = pdf;
            document.getElementById('page-total').textContent = pdf.numPages;
            renderPage(pageNum);
        });
    */

    // -------------- نظام إرسال المهام --------------

    const taskForm = document.getElementById('task-form');
    const tasksContainer = document.getElementById('tasks-container');

    if (taskForm) {
        taskForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // الحصول على قيم المدخلات
            const taskTitle = document.getElementById('task-title').value;
            const taskDescription = document.getElementById('task-description').value;
            const criteriaSelect = document.getElementById('criteria-select').value;
            
            if (!taskTitle || !taskDescription) {
                alert('يرجى ملء كل الحقول المطلوبة');
                return;
            }
            
            // عادة هنا سيتم إرسال البيانات إلى الخادم
            // لكن في النموذج الأولي، سنضيف المهمة مباشرة إلى واجهة المستخدم
            
            const currentDate = new Date();
            const formattedDate = `${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, '0')}-${String(currentDate.getDate()).padStart(2, '0')}`;
            
            const taskItem = document.createElement('div');
            taskItem.className = 'task-item';
            taskItem.innerHTML = `
                <h4>${taskTitle}</h4>
                <p class="task-meta">تم التقديم في: <span>${formattedDate}</span> | الحالة: <span class="status-pending">قيد التقييم</span></p>
                <p class="task-excerpt">${taskDescription.substring(0, 100)}${taskDescription.length > 100 ? '...' : ''}</p>
                <div class="task-actions">
                    <button class="view-btn"><i class="fas fa-eye"></i> عرض</button>
                    <button class="edit-btn"><i class="fas fa-edit"></i> تعديل</button>
                </div>
            `;
            
            // إضافة المهمة الجديدة في بداية القائمة
            tasksContainer.insertBefore(taskItem, tasksContainer.firstChild);
            
            // إعادة تعيين النموذج
            taskForm.reset();
            
            // رسالة تأكيد
            alert('تم تقديم المهمة بنجاح وهي الآن قيد التقييم.');
        });
    }

    // -------------- نظام الدردشة --------------

    const chatInput = document.getElementById('chat-message');
    const sendBtn = document.getElementById('send-btn');
    const voiceBtn = document.getElementById('voice-btn');
    const chatContainer = document.getElementById('chat-container');

    if (sendBtn && chatInput && chatContainer) {
        sendBtn.addEventListener('click', sendMessage);
        
        // إضافة استماع لضغط Enter لإرسال الرسالة
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        // تبديل حالة زر الصوت
        if (voiceBtn) {
            voiceBtn.addEventListener('click', function() {
                this.classList.toggle('active');
                if (this.classList.contains('active')) {
                    // بدء تسجيل الصوت (في تطبيق حقيقي)
                    alert('تم تفعيل التسجيل الصوتي. تحدث الآن...');
                } else {
                    // إيقاف تسجيل الصوت
                    alert('تم إيقاف التسجيل الصوتي');
                }
            });
        }
    }

    /**
     * إرسال رسالة دردشة
     */
    function sendMessage() {
        if (!chatInput || !chatInput.value.trim()) return;
        
        const message = chatInput.value.trim();
        
        // إضافة رسالة المستخدم
        const userMessage = document.createElement('p');
        userMessage.innerHTML = `<strong>أنت:</strong> ${message}`;
        chatContainer.appendChild(userMessage);
        
        // مسح حقل الإدخال
        chatInput.value = '';
        
        // تمرير إلى الأسفل
        chatContainer.scrollTop = chatContainer.scrollHeight;
        
        // محاكاة استجابة Grok (في تطبيق حقيقي، سيتم إرسال الرسالة إلى الخادم)
        setTimeout(function() {
            // محاكاة "جاري الكتابة"
            const typingIndicator = document.createElement('p');
            typingIndicator.id = 'typing-indicator';
            typingIndicator.innerHTML = '<strong>Grok:</strong> <em>جاري الكتابة...</em>';
            chatContainer.appendChild(typingIndicator);
            chatContainer.scrollTop = chatContainer.scrollHeight;
            
            // بعد فترة، استبدل مؤشر الكتابة بالرد
            setTimeout(function() {
                const responses = [
                    'هذا سؤال مثير للاهتمام! دعني أفكر في ذلك...',
                    'يمكنني مساعدتك في هذا الموضوع. ببساطة، يمكنك البدء بـ...',
                    'لقد صادفت هذا السؤال من قبل. الإجابة تعتمد على عدة عوامل...',
                    'هناك عدة طرق للتعامل مع هذه المسألة. أولاً، يجب أن تفكر في...',
                    'رائع! هذا موضوع أحب التحدث عنه. دعني أشارك معك بعض الأفكار...'
                ];
                const randomResponse = responses[Math.floor(Math.random() * responses.length)];
                
                // استبدال مؤشر الكتابة بالرد الفعلي
                typingIndicator.innerHTML = `<strong>Grok:</strong> ${randomResponse}`;
                typingIndicator.id = '';
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }, 1500);
        }, 800);
    }

    // -------------- نظام تسجيل الحضور --------------

    const checkInBtn = document.getElementById('check-in-btn');
    const checkOutBtn = document.getElementById('check-out-btn');
    const attendanceLog = document.getElementById('attendance-log');

    if (checkInBtn && attendanceLog) {
        checkInBtn.addEventListener('click', function() {
            // في تطبيق حقيقي، سيتم إرسال طلب تسجيل الحضور إلى الخادم
            const now = new Date();
            const formattedTime = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
            const formattedDate = now.toLocaleDateString('ar-EG', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
            
            // إنشاء سجل حضور جديد
            const record = document.createElement('div');
            record.className = 'attendance-record';
            record.innerHTML = `
                <p class="attendance-date">${formattedDate}</p>
                <p class="attendance-course">تطوير تطبيقات الويب المتقدمة</p>
                <p class="attendance-time">
                    <span class="check-in"><i class="fas fa-sign-in-alt"></i> الحضور: ${formattedTime}</span>
                    <span class="check-out pending"><i class="fas fa-hourglass-half"></i> الانصراف: لم يسجل بعد</span>
                </p>
                <p class="attendance-status in-progress"><i class="fas fa-spinner fa-spin"></i> جاري</p>
            `;
            
            // إضافة السجل في بداية القائمة
            attendanceLog.insertBefore(record, attendanceLog.firstChild);
            
            // تعطيل زر تسجيل الحضور وتفعيل زر تسجيل الانصراف
            checkInBtn.disabled = true;
            if (checkOutBtn) checkOutBtn.disabled = false;
            
            alert('تم تسجيل حضورك بنجاح!');
        });
    }

    if (checkOutBtn && attendanceLog) {
        checkOutBtn.addEventListener('click', function() {
            // البحث عن أول سجل بحالة "جاري"
            const inProgressRecord = attendanceLog.querySelector('.attendance-status.in-progress');
            if (!inProgressRecord) {
                alert('لم يتم العثور على سجل حضور نشط');
                return;
            }
            
            const record = inProgressRecord.closest('.attendance-record');
            const now = new Date();
            const formattedTime = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
            
            // تحديث وقت الانصراف
            const checkOutElement = record.querySelector('.check-out');
            checkOutElement.innerHTML = `<i class="fas fa-sign-out-alt"></i> الانصراف: ${formattedTime}`;
            checkOutElement.classList.remove('pending');
            
            // تحديث حالة السجل
            inProgressRecord.innerHTML = '<i class="fas fa-check-circle"></i> مكتمل';
            inProgressRecord.classList.remove('in-progress');
            inProgressRecord.classList.add('completed');
            
            // إعادة تفعيل زر تسجيل الحضور وتعطيل زر تسجيل الانصراف
            if (checkInBtn) checkInBtn.disabled = false;
            checkOutBtn.disabled = true;
            
            alert('تم تسجيل انصرافك بنجاح!');
        });
    }

    // -------------- رسم مخطط المهارات بـ Chart.js --------------
    
    const skillsCanvas = document.getElementById('skills-radar-chart');
    
    if (skillsCanvas && typeof Chart !== 'undefined') {
        new Chart(skillsCanvas, {
            type: 'radar',
            data: {
                labels: ['البرمجة', 'تحليل البيانات', 'الأمن السيبراني', 'تطوير الويب', 'الذكاء الاصطناعي', 'قواعد البيانات'],
                datasets: [{
                    label: 'مهاراتك الحالية',
                    data: [85, 70, 65, 90, 75, 80],
                    backgroundColor: 'rgba(255, 215, 0, 0.2)',
                    borderColor: 'rgba(255, 215, 0, 1)',
                    pointBackgroundColor: 'gold',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'gold'
                }]
            },
            options: {
                elements: {
                    line: {
                        borderWidth: 3
                    }
                },
                scales: {
                    r: {
                        angleLines: {
                            color: 'rgba(255, 255, 255, 0.2)'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.2)'
                        },
                        pointLabels: {
                            color: '#ddd',
                            font: {
                                size: 14
                            }
                        },
                        ticks: {
                            color: '#bbb',
                            backdropColor: 'rgba(0, 0, 0, 0.7)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        labels: {
                            color: '#ddd'
                        }
                    }
                }
            }
        });
    }

    // -------------- فلترة معرض السحر --------------
    
    const filterButtons = document.querySelectorAll('.filter-btn');
    const galleryItems = document.querySelectorAll('.gallery-item');
    
    if (filterButtons.length > 0 && galleryItems.length > 0) {
        filterButtons.forEach(button => {
            button.addEventListener('click', function() {
                // إزالة الفئة النشطة من جميع الأزرار
                filterButtons.forEach(btn => btn.classList.remove('active'));
                // إضافة الفئة النشطة إلى الزر المنقور
                this.classList.add('active');
                
                const filter = this.getAttribute('data-filter');
                
                galleryItems.forEach(item => {
                    if (filter === 'all' || item.classList.contains(filter)) {
                        item.style.display = 'block';
                    } else {
                        item.style.display = 'none';
                    }
                });
            });
        });
    }

    // -------------- البحث في مكتبة المخطوطات --------------
    
    const bookSearch = document.getElementById('book-search');
    const bookCategory = document.getElementById('book-category');
    const filterBtn = document.getElementById('filter-btn');
    const bookItems = document.querySelectorAll('.book-item');
    
    if (filterBtn && bookItems.length > 0) {
        filterBtn.addEventListener('click', filterBooks);
        
        if (bookSearch) {
            bookSearch.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    filterBooks();
                }
            });
        }
    }
    
    function filterBooks() {
        const searchTerm = bookSearch ? bookSearch.value.toLowerCase() : '';
        const category = bookCategory ? bookCategory.value : 'all';
        
        bookItems.forEach(book => {
            const title = book.querySelector('h4').textContent.toLowerCase();
            const excerpt = book.querySelector('.book-excerpt').textContent.toLowerCase();
            const tags = Array.from(book.querySelectorAll('.tag')).map(tag => tag.textContent.toLowerCase());
            
            // تطبيق البحث النصي
            const matchesSearch = searchTerm === '' || 
                title.includes(searchTerm) || 
                excerpt.includes(searchTerm) || 
                tags.some(tag => tag.includes(searchTerm));
            
            // تطبيق تصفية الفئة
            const matchesCategory = category === 'all' || 
                tags.some(tag => tag === category || 
                        (category === 'programming' && (tag === 'برمجة' || tag === 'أساسيات')) ||
                        (category === 'data' && (tag === 'بيانات' || tag === 'تحليل')) ||
                        (category === 'ai' && (tag === 'ذكاء اصطناعي' || tag === 'تعلم آلة')) ||
                        (category === 'security' && (tag === 'أمن' || tag === 'حماية')));
            
            book.style.display = matchesSearch && matchesCategory ? 'flex' : 'none';
        });
    }

    // -------------- انتقال سلس للروابط الداخلية --------------
    
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 20,
                    behavior: 'smooth'
                });
            }
        });
    });

    // -------------- تذكيرات الحصص --------------
    
    const reminderButtons = document.querySelectorAll('.reminder-btn');
    
    if (reminderButtons.length > 0) {
        reminderButtons.forEach(button => {
            button.addEventListener('click', function() {
                const scheduleItem = this.closest('.schedule-item');
                const className = scheduleItem.querySelector('h4').textContent;
                const scheduleTime = scheduleItem.querySelector('.schedule-time').textContent;
                
                // في تطبيق حقيقي، سيتم حفظ التذكير في الخادم
                alert(`تم إعداد تذكير لحصة: ${className}\nالموعد: ${scheduleTime}`);
                
                // تغيير زر التذكير
                this.innerHTML = '<i class="fas fa-check"></i> تم التذكير';
                this.style.background = 'linear-gradient(to bottom, #28a745, #1e7e34)';
                this.disabled = true;
            });
        });
    }

    // -------------- فتح المخطوطات --------------
    
    const openScrollButtons = document.querySelectorAll('.open-scroll-btn');
    
    if (openScrollButtons.length > 0) {
        openScrollButtons.forEach(button => {
            button.addEventListener('click', function() {
                const bookItem = this.closest('.book-item');
                const bookTitle = bookItem.querySelector('h4').textContent;
                
                // في تطبيق حقيقي، سيتم تحميل ملف PDF
                alert(`جاري فتح الكتاب: ${bookTitle}`);
                
                // محاكاة تحميل PDF (في تطبيق حقيقي)
                const pdfSection = document.querySelector('.pdf-viewer-container');
                if (pdfSection) {
                    pdfSection.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });
    }
});