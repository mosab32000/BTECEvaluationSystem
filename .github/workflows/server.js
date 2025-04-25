#!/usr/bin/env node

// سكربت بسيط لبدء تشغيل السيرفر

const { spawn } = require('child_process');
const http = require('http');
const path = require('path');

// تكوين
const config = {
  port: 5000,
  command: 'npm',
  args: ['run', 'dev'],
  retryDelay: 2000,
  maxRetries: 5
};

// وظيفة للتحقق من حالة الخادم
function checkServerStatus() {
  return new Promise((resolve) => {
    const req = http.get(`http://localhost:${config.port}/health`, (res) => {
      if (res.statusCode === 200) {
        let data = '';
        res.on('data', (chunk) => {
          data += chunk;
        });
        res.on('end', () => {
          resolve(true);
        });
      } else {
        resolve(false);
      }
    });
    
    req.on('error', () => {
      resolve(false);
    });
    
    req.setTimeout(1000, () => {
      req.destroy();
      resolve(false);
    });
  });
}

// وظيفة لبدء تشغيل الخادم
async function startServer(retryCount = 0) {
  console.log(`\x1b[36m%s\x1b[0m`, `🚀 بدء تشغيل إديوجينيس بلس (محاولة ${retryCount + 1}/${config.maxRetries + 1})...`);
  
  const serverProcess = spawn(config.command, config.args, {
    stdio: 'inherit',
    shell: true
  });
  
  serverProcess.on('error', (error) => {
    console.error(`\x1b[31m%s\x1b[0m`, `❌ خطأ في بدء تشغيل الخادم: ${error.message}`);
    if (retryCount < config.maxRetries) {
      console.log(`\x1b[33m%s\x1b[0m`, `⏳ إعادة المحاولة بعد ${config.retryDelay / 1000} ثوانٍ...`);
      setTimeout(() => startServer(retryCount + 1), config.retryDelay);
    } else {
      console.error(`\x1b[31m%s\x1b[0m`, `❌ فشل في بدء تشغيل الخادم بعد ${config.maxRetries + 1} محاولات. يرجى التحقق من الأخطاء وإعادة المحاولة.`);
      process.exit(1);
    }
  });
  
  serverProcess.on('close', (code) => {
    if (code !== 0) {
      console.log(`\x1b[33m%s\x1b[0m`, `⚠️ انتهى الخادم برمز الخروج ${code}`);
      if (retryCount < config.maxRetries) {
        console.log(`\x1b[33m%s\x1b[0m`, `⏳ إعادة المحاولة بعد ${config.retryDelay / 1000} ثوانٍ...`);
        setTimeout(() => startServer(retryCount + 1), config.retryDelay);
      } else {
        console.error(`\x1b[31m%s\x1b[0m`, `❌ فشل في بدء تشغيل الخادم بعد ${config.maxRetries + 1} محاولات. يرجى التحقق من الأخطاء وإعادة المحاولة.`);
        process.exit(1);
      }
    }
  });
  
  // التحقق من حالة الخادم كل 5 ثوانٍ
  const interval = setInterval(async () => {
    const isServerRunning = await checkServerStatus();
    if (isServerRunning) {
      clearInterval(interval);
      console.log(`\x1b[32m%s\x1b[0m`, `✅ تم بدء تشغيل الخادم بنجاح على المنفذ ${config.port}!`);
    }
  }, 5000);
  
  return serverProcess;
}

// بدء تشغيل الخادم
startServer().catch((error) => {
  console.error(`\x1b[31m%s\x1b[0m`, `❌ خطأ غير متوقع: ${error.message}`);
  process.exit(1);
});