// سكربت بسيط لبدء تشغيل التطبيق بشكل فوري

import express from 'express';
import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const port = 4999; // استخدام منفذ مختلف عن الخادم الأصلي

// إضافة مسار صحة أساسي
app.get('/health', (req, res) => {
  res.json({ status: 'ok', time: new Date().toISOString() });
});

// إضافة صفحة انتظار جميلة للمستخدم
app.get('*', (req, res) => {
  res.send(`
    <html>
      <head>
        <title>إديوجينيس بلس - جاري التحميل</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
          body {
            font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            background-color: #f8f9fa;
            color: #333;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
            direction: rtl;
            box-sizing: border-box;
          }
          .container {
            max-width: 600px;
            width: 100%;
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            text-align: center;
          }
          h1 {
            color: #5E3CF5;
            margin-bottom: 20px;
            font-weight: bold;
          }
          p {
            margin-bottom: 15px;
            line-height: 1.6;
            color: #555;
          }
          .logo {
            width: 80px;
            height: 80px;
            margin-bottom: 20px;
          }
          .loader {
            display: inline-block;
            width: 50px;
            height: 50px;
            border: 3px solid rgba(94, 60, 245, 0.2);
            border-radius: 50%;
            border-top: 3px solid #5E3CF5;
            animation: spin 1s linear infinite;
            margin: 25px 0;
          }
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
          .progress-container {
            width: 100%;
            background-color: #f1f1f1;
            border-radius: 20px;
            margin: 20px 0;
            height: 8px;
            overflow: hidden;
          }
          .progress-bar {
            width: 0%;
            height: 100%;
            background-color: #5E3CF5;
            animation: progress 30s linear forwards;
          }
          @keyframes progress {
            0% { width: 0%; }
            100% { width: 100%; }
          }
          .footer {
            margin-top: 30px;
            font-size: 14px;
            color: #888;
          }
        </style>
      </head>
      <body>
        <div class="container">
          <svg class="logo" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L17 7V17L12 22L7 17V7L12 2Z" stroke="#5E3CF5" stroke-width="2" fill="rgba(94, 60, 245, 0.1)"></path>
            <circle cx="12" cy="12" r="3" fill="#5E3CF5"></circle>
          </svg>
          <h1>إديوجينيس بلس</h1>
          <p>جاري تحميل منصة التعليم المتقدمة...</p>
          <div class="loader"></div>
          <div class="progress-container">
            <div class="progress-bar"></div>
          </div>
          <p>يرجى الانتظار بينما نقوم بتجهيز البيئة التعليمية. سيتم إعادة توجيهك تلقائيًا عند اكتمال التحميل.</p>
          <div class="footer">
            <p>© إديوجينيس بلس - تطوير فريق أم الساتين</p>
          </div>
        </div>
        <script>
          // التحقق تلقائيًا من جاهزية التطبيق كل 3 ثوانٍ
          function checkAppReady() {
            fetch('http://localhost:5000/health')
              .then(response => {
                if (response.ok) {
                  window.location.href = 'http://localhost:5000/';
                } else {
                  setTimeout(checkAppReady, 3000);
                }
              })
              .catch(() => {
                setTimeout(checkAppReady, 3000);
              });
          }
          
          // بدء التحقق بعد 5 ثوانٍ
          setTimeout(checkAppReady, 5000);
          
          // إضافة زر لفتح التطبيق الرئيسي
          const openMainAppButton = document.createElement('button');
          openMainAppButton.innerText = 'فتح التطبيق الرئيسي';
          openMainAppButton.style.backgroundColor = '#5E3CF5';
          openMainAppButton.style.color = 'white';
          openMainAppButton.style.border = 'none';
          openMainAppButton.style.padding = '10px 20px';
          openMainAppButton.style.borderRadius = '5px';
          openMainAppButton.style.cursor = 'pointer';
          openMainAppButton.style.marginTop = '15px';
          openMainAppButton.style.fontWeight = 'bold';
          openMainAppButton.onclick = () => {
            window.location.href = 'http://localhost:5000/';
          };
          setTimeout(() => {
            document.querySelector('.footer').insertAdjacentElement('beforebegin', openMainAppButton);
          }, 15000);
        </script>
      </body>
    </html>
  `);
});

// بدء تشغيل الخادم البسيط
const server = app.listen(port, '0.0.0.0', () => {
  console.log(`\x1b[36m%s\x1b[0m`, `🚀 تم بدء الخادم البسيط على المنفذ ${port}`);
  
  // بدء تشغيل التطبيق الفعلي باستخدام watchdog
  console.log(`\x1b[36m%s\x1b[0m`, `⏳ بدء تشغيل مراقب التطبيق الرئيسي...`);
  
  // وظيفة لإعادة تشغيل مراقب التطبيق في حالة فشله
  function startWatchdog() {
    const mainAppProcess = spawn('node', ['watchdog.js'], {
      stdio: 'inherit',
      shell: true,
      detached: true
    });
    
    mainAppProcess.on('error', (error) => {
      console.error(`\x1b[31m%s\x1b[0m`, `❌ خطأ في تشغيل التطبيق الرئيسي: ${error.message}`);
      // إعادة محاولة تشغيل watchdog بعد 10 ثواني
      setTimeout(startWatchdog, 10000);
    });
    
    mainAppProcess.on('close', (code) => {
      console.log(`\x1b[33m%s\x1b[0m`, `⚠️ انتهى التطبيق الرئيسي برمز الخروج: ${code}`);
      // إعادة محاولة تشغيل watchdog بعد 10 ثواني
      setTimeout(startWatchdog, 10000);
    });
    
    // منع عملية watchdog من إنهاء العملية الرئيسية عند توقفها
    // هذا يضمن استمرار التطبيق حتى لو فشل مراقب العملية
    mainAppProcess.unref();
  }
  
  // بدء تشغيل مراقب التطبيق
  startWatchdog();
});