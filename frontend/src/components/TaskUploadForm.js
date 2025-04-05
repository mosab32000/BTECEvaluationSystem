
import React, { useState, useRef } from 'react';

// مكون نموذج رفع المهام
function TaskUploadForm({ onUploadSuccess }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  // معالجة اختيار الملف
  const handleFileChange = (event) => {
    if (event.target.files && event.target.files.length > 0) {
      const selectedFile = event.target.files[0];
      setFile(selectedFile);
      setError('');
    } else {
      setFile(null);
    }
  };

  // معالجة إرسال النموذج
  const handleSubmit = async (event) => {
    event.preventDefault();

    // التحقق الأساسي
    if (!file || !title.trim()) {
      setError('يرجى تقديم عنوان للمهمة واختيار ملف.');
      return;
    }

    setUploading(true);
    setError('');

    // إنشاء كائن FormData لإرسال الملف والبيانات الأخرى
    const formData = new FormData();
    formData.append('title', title.trim());
    formData.append('uploaded_file', file);
    if (description.trim()) {
      formData.append('description', description.trim());
    }

    try {
      // استخدام الدالة onUploadSuccess التي يجب أن تحتوي على منطق استدعاء axios
      await onUploadSuccess(formData);

      // إعادة تعيين حقول النموذج بعد الرفع الناجح
      setTitle('');
      setDescription('');
      setFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (err) {
      console.error('خطأ في محاولة الرفع:', err);
      setError('حدث خطأ غير متوقع أثناء الرفع.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="upload-form">
      <h2>رفع مهمة جديدة</h2>
      {error && <p className="error">{error}</p>}

      <div className="form-group">
        <label htmlFor="title">عنوان المهمة:</label>
        <input
          type="text"
          id="title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="أدخل عنوانًا للمهمة"
          required
          disabled={uploading}
        />
      </div>

      <div className="form-group">
        <label htmlFor="description">الوصف (اختياري):</label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="قدم أي تفاصيل ذات صلة حول المهمة أو المستند"
          rows="3"
          disabled={uploading}
        />
      </div>

      <div className="form-group">
        <label htmlFor="file">ملف المهمة:</label>
        <input
          type="file"
          id="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          required
          accept=".txt,.pdf,.docx,.png,.jpg,.jpeg,.tiff,.bmp"
          disabled={uploading}
         />
         {file && (
            <span className="file-info">
                المحدد: {file.name} ({(file.size / 1024).toFixed(1)} كيلوبايت)
            </span>
         )}
      </div>

      <button type="submit" disabled={uploading || !file}>
        {uploading ? 'جارٍ الرفع...' : 'رفع وتحليل المهمة'}
      </button>
    </form>
  );
}

export default TaskUploadForm;
