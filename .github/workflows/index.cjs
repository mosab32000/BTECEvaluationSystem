#!/usr/bin/env node

/**
 * ملف بدء تشغيل بسيط ودائم لمنصة إديوجينيس بلس
 * هذا الملف يستخدم صيغة CommonJS لتجنب مشاكل وحدات ES
 */

// لتعريف المستخدم بأن العملية قيد التنفيذ
console.log('🚀 بدء تشغيل منصة إديوجينيس بلس (إصدار CommonJS)...');

// استيراد الوحدات اللازمة
const { spawn } = require('child_process');
const http = require('http');
const fs = require('fs');
const path = require('path');

// تتبع حالة الخدمة
let serviceProcess = null;
let exitOnError = false;

// التحقق مما إذا كان المنفذ 5000 مفتوحًا
function checkPort5000() {
  return new Promise((resolve) => {
    const req = http.request({
      hostname: 'localhost',
      port: 5000,
      path: '/health',
      method: 'GET',
      timeout: 1000
    }, (res) => {
      if (res.statusCode === 200) {
        console.log('✅ الخدمة تعمل بالفعل على المنفذ 5000');
        resolve(true);
      } else {
        resolve(false);
      }
    });
    
    req.on('error', () => {
      resolve(false);
    });
    
    req.on('timeout', () => {
      req.destroy();
      resolve(false);
    });
    
    req.end();
  });
}

// تشغيل العملية وإعادة تشغيلها عند الحاجة
function startAndMonitor(command, args, options = {}) {
  console.log(`🚀 بدء تشغيل: ${command} ${args.join(' ')}`);
  
  // بدء العملية
  serviceProcess = spawn(command, args, {
    stdio: 'inherit',
    shell: true,
    ...options
  });
  
  serviceProcess.on('error', (error) => {
    console.error(`❌ خطأ في بدء التشغيل: ${error.message}`);
    if (exitOnError) {
      process.exit(1);
    } else {
      // إعادة التشغيل بعد 5 ثوانٍ
      setTimeout(() => startAndMonitor(command, args, options), 5000);
    }
  });
  
  serviceProcess.on('close', (code) => {
    console.log(`⚠️ انتهت العملية برمز الخروج: ${code}`);
    if (exitOnError) {
      process.exit(code || 1);
    } else {
      // إعادة التشغيل بعد 5 ثوانٍ
      setTimeout(() => startAndMonitor(command, args, options), 5000);
    }
  });
  
  return serviceProcess;
}

// البحث عن أفضل أمر لتشغيل المشروع
async function findBestCommand() {
  // قائمة بالأوامر المحتملة مرتبة حسب الأفضلية
  const commands = [
    { exists: fs.existsSync(path.join(__dirname, 'forever.js')), command: 'node', args: ['--experimental-modules', 'forever.js'] },
    { exists: fs.existsSync(path.join(__dirname, 'watchdog.mjs')), command: 'node', args: ['--experimental-modules', 'watchdog.mjs'] },
    { exists: fs.existsSync(path.join(__dirname, 'server/index.minimal.ts')), command: 'tsx', args: ['server/index.minimal.ts'] },
    { exists: true, command: 'npm', args: ['run', 'dev'] } // الأمر الافتراضي
  ];
  
  const command = commands.find(cmd => cmd.exists);
  return command;
}

// وظيفة البدء الرئيسية
async function main() {
  try {
    // التحقق مما إذا كان التطبيق يعمل بالفعل
    const isRunning = await checkPort5000();
    
    if (isRunning) {
      console.log('✓ التطبيق قيد التشغيل بالفعل على المنفذ 5000');
      
      // إبقاء هذه العملية قيد التشغيل للحفاظ على workflow
      console.log('✓ إبقاء عملية المراقبة قيد التشغيل...');
      setInterval(() => {
        checkPort5000().then(running => {
          if (!running) {
            console.log('⚠️ توقف التطبيق، جاري إعادة التشغيل...');
            startApplication();
          }
        });
      }, 30000); // التحقق كل 30 ثانية
      
      return;
    }
    
    // بدء التطبيق
    startApplication();
    
  } catch (error) {
    console.error(`❌ خطأ غير متوقع: ${error.message}`);
    process.exit(1);
  }
}

// وظيفة بدء التطبيق
async function startApplication() {
  // البحث عن أفضل أمر للتشغيل
  const bestCommand = await findBestCommand();
  
  // بدء التطبيق ومراقبته
  exitOnError = false; // عدم الخروج عند حدوث خطأ
  startAndMonitor(bestCommand.command, bestCommand.args);
  
  console.log('✓ بدأت منصة إديوجينيس بلس (التطبيق وخادم المراقبة)');
}

// التعامل مع إشارات النظام
process.on('SIGINT', () => {
  console.log('⚠️ تم استلام إشارة إيقاف SIGINT، جاري الخروج...');
  
  if (serviceProcess) {
    serviceProcess.kill();
  }
  
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('⚠️ تم استلام إشارة إيقاف SIGTERM، جاري الخروج...');
  
  if (serviceProcess) {
    serviceProcess.kill();
  }
  
  process.exit(0);
});

// التعامل مع الأخطاء غير المتوقعة
process.on('uncaughtException', (error) => {
  console.error(`❌ خطأ غير متوقع: ${error.message}`);
  
  // إعادة التشغيل بدلاً من الخروج
  if (serviceProcess) {
    serviceProcess.kill();
    serviceProcess = null;
  }
  
  // إعادة تشغيل التطبيق بعد 5 ثوانٍ
  setTimeout(startApplication, 5000);
});

// بدء التنفيذ
main();