// برنامج ممهد Replit لضمان تشغيل التطبيق تلقائيًا
// هذا الملف يجب تشغيله مباشرة بواسطة الـ workflow

import { spawn } from 'child_process';
import fs from 'fs';
import { fileURLToPath } from 'url';
import path from 'path';

// الحصول على المسار الحالي
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const logFile = 'replit-init.log';

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

log('بدء تشغيل برنامج ممهد Replit');

// وظيفة لاكتشاف وقتل العمليات السابقة للملفات المطلوبة
async function killExistingProcesses() {
  log('جاري البحث عن عمليات سابقة...');
  
  const processesToCheck = ['forever.js', 'watchdog.js', 'run.js'];
  
  for (const procName of processesToCheck) {
    try {
      log(`البحث عن عمليات ${procName}...`);
      if (process.platform === 'win32') {
        spawn('taskkill', ['/F', '/FI', `IMAGENAME eq node.exe`, '/FI', `WINDOWTITLE eq *${procName}*`], { stdio: 'inherit' });
      } else {
        // Linux/macOS
        spawn('pkill', ['-f', procName], { stdio: 'inherit' });
      }
    } catch (error) {
      log(`خطأ أثناء إيقاف العمليات: ${error.message}`);
    }
  }
  
  // انتظار قليلاً للتأكد من إيقاف العمليات
  return new Promise(resolve => setTimeout(resolve, 2000));
}

// وظيفة لبدء تشغيل برنامج التشغيل المستمر
async function startForeverProcess() {
  log('بدء تشغيل برنامج التشغيل المستمر...');
  
  const foreverProcess = spawn('node', ['forever.js'], {
    stdio: 'inherit',
    detached: true, // تشغيل كعملية منفصلة
    shell: true
  });
  
  foreverProcess.unref(); // فصل العملية عن العملية الحالية
  
  foreverProcess.on('error', (error) => {
    log(`خطأ في بدء تشغيل برنامج التشغيل المستمر: ${error.message}`);
  });
  
  log('تم بدء برنامج التشغيل المستمر بنجاح!');
}

// تنفيذ البرنامج
async function main() {
  try {
    // إيقاف أي عمليات سابقة
    await killExistingProcesses();
    
    // بدء برنامج التشغيل المستمر
    await startForeverProcess();
    
    log('تم تنفيذ برنامج ممهد Replit بنجاح!');
    
    // الخروج بعد 10 ثوانٍ للسماح للعملية الأخرى بالانطلاق
    setTimeout(() => {
      log('إغلاق برنامج ممهد Replit...');
      process.exit(0);
    }, 10000);
    
  } catch (error) {
    log(`خطأ في تنفيذ البرنامج: ${error.message}`);
    process.exit(1);
  }
}

// تنفيذ البرنامج
main();