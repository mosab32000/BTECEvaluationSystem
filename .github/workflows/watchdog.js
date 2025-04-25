// مراقب العملية لضمان تشغيل السيرفر بشكل مستمر
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const http = require('http');

// عملية السيرفر الحالية
let serverProcess = null;

// وقت آخر إعادة تشغيل
let lastRestart = Date.now();

// حالة الخادم
let serverStatus = {
  isRunning: false,
  lastHeartbeat: Date.now(),
  startAttempts: 0,
  restartCount: 0
};

// ملف السجل
const logFile = path.join(__dirname, 'watchdog.log');

// وظيفة كتابة السجل
function log(message) {
  const timestamp = new Date().toISOString();
  const logMessage = `${timestamp} - ${message}\n`;
  
  console.log(message);
  
  try {
    fs.appendFileSync(logFile, logMessage);
  } catch (error) {
    console.error(`فشل كتابة السجل: ${error.message}`);
  }
}

// التحقق من صحة الخادم
function checkServerHealth() {
  try {
    const req = http.request({
      hostname: 'localhost',
      port: 5000,
      path: '/health',
      method: 'GET',
      timeout: 3000
    }, (res) => {
      let data = '';
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        if (res.statusCode === 200) {
          serverStatus.lastHeartbeat = Date.now();
          serverStatus.isRunning = true;
          // log('✅ تحقق النبض: الخادم يعمل بشكل صحيح');
        } else {
          log(`⚠️ تحقق النبض: استجابة غير متوقعة - الرمز ${res.statusCode}`);
          serverStatus.isRunning = false;
        }
      });
    });
    
    req.on('error', (error) => {
      // log(`⚠️ تحقق النبض: الخادم غير متاح - ${error.message}`);
      serverStatus.isRunning = false;
    });
    
    req.on('timeout', () => {
      // log('⚠️ تحقق النبض: انتهت مهلة الطلب');
      req.destroy();
      serverStatus.isRunning = false;
    });
    
    req.end();
  } catch (error) {
    log(`❌ خطأ أثناء التحقق من صحة الخادم: ${error.message}`);
    serverStatus.isRunning = false;
  }
}

// التحقق من صحة الخادم بشكل دوري وإعادة التشغيل إذا لزم الأمر
function startHealthCheck() {
  // التحقق من الصحة كل 10 ثوانٍ
  const healthInterval = setInterval(() => {
    checkServerHealth();
    
    // إذا كان الخادم غير متاح ومرّ أكثر من 20 ثانية منذ آخر نبض
    const now = Date.now();
    if (!serverStatus.isRunning && (now - serverStatus.lastHeartbeat > 20000)) {
      log(`⚠️ الخادم معطل منذ ${Math.floor((now - serverStatus.lastHeartbeat) / 1000)} ثانية. إعادة تشغيل...`);
      stopServer();
      
      // تأخير قصير قبل إعادة التشغيل
      setTimeout(() => {
        startServer();
      }, 2000);
    }
  }, 10000);
  
  // التأكد من تنظيف المؤقت عند إغلاق البرنامج
  process.on('exit', () => {
    clearInterval(healthInterval);
  });
}

// وظيفة بدء تشغيل السيرفر
function startServer() {
  // منع إعادة التشغيل المتكررة خلال فترة قصيرة
  const now = Date.now();
  if (now - lastRestart < 10000) { // 10 ثوانٍ
    log('⚠️ تم منع إعادة تشغيل متكررة للسيرفر');
    return;
  }
  
  lastRestart = now;
  serverStatus.startAttempts++;
  
  if (serverProcess) {
    log('⚠️ السيرفر يعمل بالفعل، يتم إيقافه أولاً...');
    try {
      serverProcess.kill();
      serverProcess = null;
    } catch (error) {
      log(`❌ خطأ عند محاولة إيقاف السيرفر: ${error.message}`);
    }
  }
  
  log('🚀 بدء تشغيل السيرفر (محاولة #' + serverStatus.startAttempts + ')...');
  
  // استخدام السيرفر المبسط أولاً لبيئة Replit
  serverProcess = spawn('tsx', ['server/index.minimal.ts'], {
    stdio: 'inherit',
    detached: false
  });
  
  serverProcess.on('error', (error) => {
    log(`❌ فشل بدء تشغيل السيرفر: ${error.message}`);
    serverProcess = null;
    serverStatus.isRunning = false;
    
    // إعادة المحاولة بعد 5 ثوانٍ
    setTimeout(() => {
      log('🔄 محاولة التشغيل باستخدام الخادم الكامل...');
      startFullServer();
    }, 5000);
  });
  
  serverProcess.on('close', (code) => {
    log(`⚠️ تم إغلاق السيرفر برمز الخروج: ${code}`);
    serverProcess = null;
    serverStatus.isRunning = false;
    
    // إعادة المحاولة بعد 5 ثوانٍ
    setTimeout(() => {
      if (serverStatus.startAttempts % 2 === 0) {
        // تبديل بين أسلوب البدء المبسط والكامل
        log('🔄 محاولة التشغيل باستخدام الخادم الكامل...');
        startFullServer();
      } else {
        startServer(); 
      }
    }, 5000);
  });
}

// تشغيل الخادم بالطريقة الكاملة
function startFullServer() {
  serverStatus.startAttempts++;
  
  // باستخدام أمر npm run dev
  serverProcess = spawn('npm', ['run', 'dev'], {
    stdio: 'inherit',
    shell: true
  });
  
  serverProcess.on('error', (error) => {
    log(`❌ فشل بدء تشغيل الخادم الكامل: ${error.message}`);
    serverProcess = null;
    serverStatus.isRunning = false;
    
    // إعادة المحاولة مع الطريقة البديلة بعد 5 ثوانٍ
    setTimeout(startServer, 5000);
  });
  
  serverProcess.on('close', (code) => {
    log(`⚠️ تم إغلاق الخادم الكامل برمز الخروج: ${code}`);
    serverProcess = null;
    serverStatus.isRunning = false;
    
    // إعادة المحاولة بعد 5 ثوانٍ
    setTimeout(startServer, 5000);
  });
}

// وظيفة إيقاف السيرفر
function stopServer() {
  if (serverProcess) {
    log('🛑 إيقاف تشغيل السيرفر...');
    try {
      serverProcess.kill();
      serverProcess = null;
      log('✅ تم إيقاف السيرفر بنجاح');
    } catch (error) {
      log(`❌ فشل إيقاف السيرفر: ${error.message}`);
    }
  } else {
    log('ℹ️ السيرفر غير مشغل حاليًا');
  }
}

// وظيفة إعادة تشغيل السيرفر
function restartServer() {
  log('🔄 إعادة تشغيل السيرفر...');
  stopServer();
  setTimeout(startServer, 1000);
}

// التعامل مع إشارات النظام
process.on('SIGINT', () => {
  log('🛑 تم استلام إشارة SIGINT، إيقاف السيرفر...');
  stopServer();
  process.exit(0);
});

process.on('SIGTERM', () => {
  log('🛑 تم استلام إشارة SIGTERM، إيقاف السيرفر...');
  stopServer();
  process.exit(0);
});

// التعامل مع الأخطاء غير المتوقعة
process.on('uncaughtException', (error) => {
  log(`❌ خطأ غير متوقع: ${error.message}`);
  log(error.stack);
  restartServer();
});

// بدء تشغيل السيرفر
log('🚀 بدء تشغيل مراقب السيرفر...');
startServer();

// بدء التحقق الدوري من صحة الخادم
startHealthCheck();

// تصدير الوظائف للاستخدام الخارجي
module.exports = {
  startServer,
  stopServer,
  restartServer
};