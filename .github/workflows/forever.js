// ملف التشغيل المستمر لمنصة إديوجينيس بلس
// هذا الملف يضمن استمرارية تشغيل التطبيق في بيئة Replit

import { spawn, exec } from 'child_process';
import http from 'http';
import express from 'express';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// الحصول على المسار الحالي
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// تكوين المتغيرات الأساسية
const CONFIG = {
  mainPort: 5000,      // المنفذ الرئيسي للتطبيق
  healthPort: 4999,    // منفذ خادم المراقبة
  logFile: path.join(__dirname, 'forever.log'),
  restartDelay: 5000,  // تأخير إعادة التشغيل بالمللي ثانية
  healthCheckInterval: 10000, // فاصل زمني للتحقق من الصحة بالمللي ثانية
};

// تتبع حالة العمليات
const STATE = {
  mainAppProcess: null,
  isMainAppRunning: false,
  lastHeartbeat: Date.now(),
  startAttempts: 0,
  mainAppLogs: [],
};

// ---------- وظائف المساعدة ----------

// كتابة السجلات إلى ملف ومخرجات الطرفية
function log(message, level = 'info') {
  const timestamp = new Date().toISOString();
  const formattedMessage = `${timestamp} [${level.toUpperCase()}] ${message}`;
  
  // طباعة رسالة ملونة على حسب المستوى
  let colorCode = '\x1b[36m'; // أزرق فاتح للمعلومات
  
  if (level === 'error') {
    colorCode = '\x1b[31m'; // أحمر للأخطاء
  } else if (level === 'warn') {
    colorCode = '\x1b[33m'; // أصفر للتحذيرات
  } else if (level === 'success') {
    colorCode = '\x1b[32m'; // أخضر للنجاح
  }
  
  console.log(`${colorCode}%s\x1b[0m`, formattedMessage);
  
  // كتابة إلى ملف السجل
  try {
    fs.appendFileSync(CONFIG.logFile, formattedMessage + '\n');
  } catch (error) {
    console.error(`فشل كتابة السجل: ${error.message}`);
  }
  
  // حفظ آخر 100 رسالة سجل للعرض على واجهة المراقبة
  STATE.mainAppLogs.push(formattedMessage);
  if (STATE.mainAppLogs.length > 100) {
    STATE.mainAppLogs.shift();
  }
}

// التحقق من حالة التطبيق الرئيسي
function checkMainAppHealth() {
  return new Promise((resolve) => {
    const req = http.request({
      hostname: 'localhost',
      port: CONFIG.mainPort,
      path: '/health',
      method: 'GET',
      timeout: 3000,
    }, (res) => {
      if (res.statusCode === 200) {
        STATE.isMainAppRunning = true;
        STATE.lastHeartbeat = Date.now();
        resolve(true);
      } else {
        STATE.isMainAppRunning = false;
        resolve(false);
      }
    });
    
    req.on('error', () => {
      STATE.isMainAppRunning = false;
      resolve(false);
    });
    
    req.on('timeout', () => {
      req.destroy();
      STATE.isMainAppRunning = false;
      resolve(false);
    });
    
    req.end();
  });
}

// إيقاف العملية الرئيسية
function stopMainApp() {
  if (STATE.mainAppProcess) {
    log('إيقاف التطبيق الرئيسي...', 'warn');
    try {
      STATE.mainAppProcess.kill();
      STATE.mainAppProcess = null;
      STATE.isMainAppRunning = false;
      log('تم إيقاف التطبيق الرئيسي بنجاح', 'success');
      return true;
    } catch (error) {
      log(`فشل إيقاف التطبيق الرئيسي: ${error.message}`, 'error');
      return false;
    }
  }
  return true;
}

// تحديد أفضل طريقة لبدء التطبيق بناءً على تاريخ المحاولات
function getBestStartMethod() {
  // تناوب بين الطرق المختلفة عند فشل الطريقة الحالية
  if (STATE.startAttempts % 3 === 0) {
    return { command: 'tsx', args: ['server/index.minimal.ts'] };
  } else if (STATE.startAttempts % 3 === 1) {
    return { command: 'node', args: ['--experimental-modules', 'watchdog.mjs'] };
  } else {
    return { command: 'npm', args: ['run', 'dev'] };
  }
}

// ---------- الوظائف الرئيسية ----------

// بدء تشغيل التطبيق الرئيسي
function startMainApp() {
  if (STATE.mainAppProcess) {
    log('التطبيق الرئيسي يعمل بالفعل. إيقافه أولاً...', 'warn');
    stopMainApp();
  }
  
  STATE.startAttempts++;
  const startMethod = getBestStartMethod();
  
  log(`محاولة بدء التطبيق الرئيسي (${STATE.startAttempts}): ${startMethod.command} ${startMethod.args.join(' ')}`, 'info');
  
  STATE.mainAppProcess = spawn(startMethod.command, startMethod.args, {
    stdio: 'inherit',
    shell: true
  });
  
  STATE.mainAppProcess.on('error', (error) => {
    log(`فشل بدء التطبيق الرئيسي: ${error.message}`, 'error');
    STATE.mainAppProcess = null;
    STATE.isMainAppRunning = false;
    
    // إعادة المحاولة بعد التأخير
    setTimeout(startMainApp, CONFIG.restartDelay);
  });
  
  STATE.mainAppProcess.on('close', (code) => {
    log(`تم إغلاق التطبيق الرئيسي برمز الخروج: ${code}`, 'warn');
    STATE.mainAppProcess = null;
    STATE.isMainAppRunning = false;
    
    // إعادة المحاولة بعد التأخير
    setTimeout(startMainApp, CONFIG.restartDelay);
  });
  
  // فترة سماح للتطبيق الرئيسي للبدء
  setTimeout(async () => {
    const isRunning = await checkMainAppHealth();
    if (isRunning) {
      log('التطبيق الرئيسي يعمل بنجاح!', 'success');
    } else {
      log('التطبيق الرئيسي لم يستجب للتحقق. سيتم المحاولة مرة أخرى...', 'warn');
    }
  }, 15000); // انتظر 15 ثانية للبدء
}

// تنفيذ فحص صحة دوري
function startHealthCheck() {
  const healthInterval = setInterval(async () => {
    const isMainAppRunning = await checkMainAppHealth();
    
    if (!isMainAppRunning) {
      const now = Date.now();
      const downtime = Math.floor((now - STATE.lastHeartbeat) / 1000);
      
      if (downtime > 30) { // إذا كان متوقفًا لأكثر من 30 ثانية
        log(`التطبيق الرئيسي معطل منذ ${downtime} ثانية. جاري إعادة التشغيل...`, 'warn');
        stopMainApp();
        setTimeout(startMainApp, 2000); // بدء التشغيل بعد إيقافه
      }
    }
  }, CONFIG.healthCheckInterval);
  
  // تنظيف المؤقت عند الخروج
  process.on('exit', () => {
    clearInterval(healthInterval);
  });
}

// ---------- خادم المراقبة ----------

// إنشاء خادم مراقبة بسيط
function setupMonitoringServer() {
  const app = express();
  
  // صفحة واجهة المراقبة الرئيسية
  app.get('/', (req, res) => {
    const uptimeSeconds = Math.floor((Date.now() - STATE.lastHeartbeat) / 1000);
    const html = `
      <!DOCTYPE html>
      <html lang="ar" dir="rtl">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>إديوجينيس بلس - مراقبة الخادم</title>
        <style>
          body {
            font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            color: #333;
            background-color: #f5f5f5;
          }
          .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 20px;
          }
          h1 {
            color: #5E3CF5;
            margin-top: 0;
          }
          .status {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-weight: bold;
          }
          .status.running {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
          }
          .status.stopped {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
          }
          .card {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
          }
          .card h2 {
            margin-top: 0;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
            color: #5E3CF5;
          }
          .log-container {
            background-color: #f8f9fa;
            border: 1px solid #eee;
            border-radius: 4px;
            padding: 10px;
            height: 300px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 12px;
            color: #333;
          }
          .log-line {
            margin: 0;
            padding: 2px 0;
            border-bottom: 1px solid #f0f0f0;
          }
          .log-line:last-child {
            border-bottom: none;
          }
          .actions {
            margin-top: 20px;
            display: flex;
            gap: 10px;
          }
          .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            text-decoration: none;
            display: inline-block;
            text-align: center;
          }
          .btn-primary {
            background-color: #5E3CF5;
            color: white;
          }
          .btn-primary:hover {
            background-color: #4a2fc5;
          }
          .btn-danger {
            background-color: #dc3545;
            color: white;
          }
          .btn-danger:hover {
            background-color: #bd2130;
          }
          .btn-success {
            background-color: #28a745;
            color: white;
          }
          .btn-success:hover {
            background-color: #218838;
          }
          .stats {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
          }
          .stat-card {
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
          }
          .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #5E3CF5;
            margin: 10px 0;
          }
          .stat-label {
            color: #6c757d;
            font-size: 14px;
          }
          .refresh {
            margin-bottom: 20px;
          }
        </style>
      </head>
      <body>
        <div class="container">
          <h1>لوحة تحكم إديوجينيس بلس</h1>
          
          <div class="status ${STATE.isMainAppRunning ? 'running' : 'stopped'}">
            الحالة: ${STATE.isMainAppRunning ? '🟢 قيد التشغيل' : '🔴 متوقف'}
          </div>
          
          <div class="stats">
            <div class="stat-card">
              <div class="stat-label">وقت التشغيل</div>
              <div class="stat-value">${uptimeSeconds} ثانية</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">محاولات البدء</div>
              <div class="stat-value">${STATE.startAttempts}</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">المنفذ</div>
              <div class="stat-value">${CONFIG.mainPort}</div>
            </div>
          </div>
          
          <div class="card">
            <h2>سجلات النظام</h2>
            <div class="log-container">
              ${STATE.mainAppLogs.map(log => `<p class="log-line">${log}</p>`).join('')}
            </div>
          </div>
          
          <div class="refresh">
            <small>يتم تحديث هذه الصفحة تلقائيًا كل 30 ثانية</small>
          </div>
          
          <div class="actions">
            <a href="/" class="btn btn-primary">تحديث</a>
            <a href="/restart" class="btn btn-danger">إعادة تشغيل</a>
            <a href="http://localhost:${CONFIG.mainPort}" target="_blank" class="btn btn-success">
              فتح التطبيق الرئيسي
            </a>
          </div>
        </div>
        
        <script>
          // تحديث الصفحة كل 30 ثانية
          setTimeout(() => {
            window.location.reload();
          }, 30000);
        </script>
      </body>
      </html>
    `;
    res.send(html);
  });
  
  // التحقق من صحة الخادم
  app.get('/health', (req, res) => {
    res.json({
      status: 'ok',
      monitor: true,
      mainApp: STATE.isMainAppRunning,
      uptime: process.uptime(),
      lastHeartbeat: STATE.lastHeartbeat,
      startAttempts: STATE.startAttempts,
      timestamp: new Date().toISOString()
    });
  });
  
  // إعادة تشغيل التطبيق الرئيسي
  app.get('/restart', (req, res) => {
    log('طلب إعادة تشغيل عبر واجهة المراقبة', 'info');
    stopMainApp();
    setTimeout(startMainApp, 2000);
    
    res.redirect('/');
  });
  
  // الاستماع إلى المنفذ المحدد
  const server = app.listen(CONFIG.healthPort, '0.0.0.0', () => {
    log(`تم بدء خادم المراقبة على المنفذ ${CONFIG.healthPort}`, 'success');
  });
  
  return server;
}

// ---------- التعامل مع إشارات النظام ----------

// إدارة الإنهاء النظيف للعملية
process.on('SIGINT', () => {
  log('تم استلام إشارة SIGINT، إيقاف جميع العمليات...', 'warn');
  stopMainApp();
  process.exit(0);
});

process.on('SIGTERM', () => {
  log('تم استلام إشارة SIGTERM، إيقاف جميع العمليات...', 'warn');
  stopMainApp();
  process.exit(0);
});

// التعامل مع الأخطاء غير المتوقعة
process.on('uncaughtException', (error) => {
  log(`خطأ غير متوقع: ${error.message}`, 'error');
  log(error.stack, 'error');
});

// ---------- بدء التشغيل ----------

// وظيفة البدء الرئيسية
async function main() {
  // التحقق من وجود ملف السجل
  if (fs.existsSync(CONFIG.logFile)) {
    // مسح ملف السجل إذا كان أكبر من 5 ميجابايت
    const stats = fs.statSync(CONFIG.logFile);
    if (stats.size > 5 * 1024 * 1024) {
      fs.writeFileSync(CONFIG.logFile, '');
      log('تم مسح ملف السجل القديم بسبب حجمه الكبير', 'warn');
    }
  } else {
    // إنشاء ملف سجل جديد
    fs.writeFileSync(CONFIG.logFile, '');
  }

  // بدء التشغيل والمراقبة
  log('بدء تشغيل منصة إديوجينيس بلس...', 'info');

  // إنشاء خادم المراقبة
  setupMonitoringServer();

  // بدء مراقبة الصحة
  startHealthCheck();

  // بدء التطبيق الرئيسي
  startMainApp();

  // رسالة لإظهار عناوين الوصول
  log(`منصة إديوجينيس بلس قيد التشغيل!`, 'success');
  log(`- التطبيق الرئيسي: http://localhost:${CONFIG.mainPort}`, 'info');
  log(`- لوحة المراقبة: http://localhost:${CONFIG.healthPort}`, 'info');
}

// تنفيذ وظيفة البدء
main().catch(error => {
  console.error(`خطأ غير متوقع: ${error.message}`);
});