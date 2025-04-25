// ملف لبدء تشغيل سريع للتطبيق

import('child_process').then(({ spawn }) => {
  console.log('⏳ بدء تشغيل إديوجينيس بلس...');
  
  // محاولة تشغيل السيرفر بنسخة مبسطة أولاً
  async function startMinimalServer() {
    const minimalServer = spawn('tsx', ['server/index.minimal.ts'], {
      stdio: 'inherit'
    });
    
    return new Promise((resolve, reject) => {
      minimalServer.on('error', (error) => {
        console.error(`❌ فشل تشغيل السيرفر المبسط: ${error.message}`);
        reject(error);
      });
      
      minimalServer.on('close', (code) => {
        if (code !== 0) {
          console.log(`⚠️ انتهى السيرفر المبسط برمز الخروج: ${code}`);
          resolve(false);
        } else {
          console.log('✅ تم تشغيل السيرفر المبسط بنجاح!');
          resolve(true);
        }
      });
    });
  }
  
  // تشغيل السيرفر الكامل
  async function startFullServer() {
    const fullServer = spawn('npm', ['run', 'dev'], {
      stdio: 'inherit',
      shell: true
    });
    
    return new Promise((resolve, reject) => {
      fullServer.on('error', (error) => {
        console.error(`❌ فشل تشغيل السيرفر الكامل: ${error.message}`);
        reject(error);
      });
      
      fullServer.on('close', (code) => {
        if (code !== 0) {
          console.log(`⚠️ انتهى السيرفر الكامل برمز الخروج: ${code}`);
          resolve(false);
        } else {
          console.log('✅ تم تشغيل السيرفر الكامل بنجاح!');
          resolve(true);
        }
      });
    });
  }
  
  // تنفيذ العملية
  startMinimalServer()
    .then((success) => {
      if (!success) {
        console.log('⏳ محاولة تشغيل السيرفر الكامل...');
        return startFullServer();
      }
    })
    .catch((error) => {
      console.error(`❌ فشل بدء التشغيل: ${error.message}`);
      process.exit(1);
    });
});