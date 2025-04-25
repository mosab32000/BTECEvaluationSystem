// برنامج بدء بسيط ولكن فعال لمنصة "إديوجينيس بلس"
// للاستخدام من قبل workflow أو مباشرة

console.log('🚀 بدء تشغيل منصة إديوجينيس بلس...');

// استيراد الوحدات اللازمة
import { spawn } from 'child_process';
import http from 'http';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// الحصول على المسار الحالي
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// تتبع حالة الخدمة
let serviceProcess = null;
let hasPort5000Listener = false;

// التحقق مما إذا كان هناك عملية أخرى تستمع بالفعل على المنفذ 5000
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
        hasPort5000Listener = true;
        resolve(true);
      } else {
        hasPort5000Listener = false;
        resolve(false);
      }
    });
    
    req.on('error', () => {
      hasPort5000Listener = false;
      resolve(false);
    });
    
    req.on('timeout', () => {
      req.destroy();
      hasPort5000Listener = false;
      resolve(false);
    });
    
    req.end();
  });
}

// اختيار ملف التشغيل الأنسب اعتمادًا على ظروف البيئة
function chooseBestStartupFile() {
  // الخيارات المتاحة مرتبة حسب الأفضلية
  const options = [
    { file: 'forever.js', exists: fs.existsSync(path.join(__dirname, 'forever.js')) },
    { file: 'run.js', exists: fs.existsSync(path.join(__dirname, 'run.js')) },
    { file: 'watchdog.js', exists: fs.existsSync(path.join(__dirname, 'watchdog.js')) },
    { file: 'server/index.minimal.ts', exists: fs.existsSync(path.join(__dirname, 'server/index.minimal.ts')) },
  ];
  
  // اختيار أول ملف موجود
  const chosenOption = options.find(option => option.exists);
  
  if (!chosenOption) {
    console.log('⚠️ لم يتم العثور على أي من ملفات التشغيل المطلوبة');
    console.log('⚠️ استخدام الأمر الافتراضي: npm run dev');
    return { command: 'npm', args: ['run', 'dev'] };
  }
  
  console.log(`✨ تم اختيار: ${chosenOption.file}`);
  
  if (chosenOption.file.endsWith('.ts')) {
    return { command: 'tsx', args: [chosenOption.file] };
  } else {
    return { command: 'node', args: [chosenOption.file] };
  }
}

// وظيفة بدء التشغيل الرئيسية
async function startService() {
  // التحقق مما إذا كان هناك خدمة تعمل بالفعل
  const isServiceRunning = await checkPort5000();
  
  if (isServiceRunning) {
    console.log('🟢 الخدمة تعمل بالفعل، لا حاجة لإعادة التشغيل');
    return;
  }
  
  // اختيار ملف البدء المناسب
  const startMethod = chooseBestStartupFile();
  
  console.log(`🚀 بدء تشغيل: ${startMethod.command} ${startMethod.args.join(' ')}`);
  
  // بدء الخدمة
  serviceProcess = spawn(startMethod.command, startMethod.args, {
    stdio: 'inherit',
    detached: true,
    shell: true
  });
  
  // فصل العملية لتعمل في الخلفية
  serviceProcess.unref();
  
  serviceProcess.on('error', (error) => {
    console.error(`❌ خطأ في بدء التشغيل: ${error.message}`);
    process.exit(1);
  });
  
  console.log('✅ تم بدء الخدمة. من المتوقع أن تكون جاهزة خلال دقيقة واحدة.');
}

// معالجة الإشارات والخروج
process.on('SIGINT', () => {
  console.log('⚠️ تم استلام إشارة إيقاف، جاري الخروج...');
  process.exit(0);
});

// بدء التنفيذ
startService()
  .then(() => {
    // الانتظار قليلاً ثم الخروج ليسمح للعملية الأخرى بالعمل
    setTimeout(() => {
      console.log('✅ انتهى برنامج البدء، الخدمة تعمل في الخلفية');
      // عدم إنهاء العملية إذا كان تشغيلها من workflow
      // process.exit(0);
    }, 3000);
  })
  .catch((error) => {
    console.error(`❌ خطأ غير متوقع: ${error.message}`);
    process.exit(1);
  });