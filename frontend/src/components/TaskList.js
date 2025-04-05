
import React from 'react';

// مكون لعرض قائمة المهام المرفوعة ونتائجها
function TaskList({ tasks, onAnalyze, onEvaluate, analysisResults, evaluationResults, loadingState, onDelete }) {

  if (!tasks || tasks.length === 0) {
    return (
      <div className="task-list">
        <h2>المهام المرفوعة</h2>
        <p>لا توجد مهام مرفوعة بعد. استخدم النموذج أعلاه لرفع أول مهمة.</p>
      </div>
    );
  }

  return (
    <div className="task-list">
      <h2>المهام المرفوعة</h2>
      <ul>
        {tasks.map(task => (
          <li key={task.id} className="task-item">
            {/* معلومات المهمة */}
            <div className="task-info">
              <h3>{task.title || 'مهمة بدون عنوان'}</h3>
              <p className="task-meta">
                <span>المعرف: {task.id} | </span>
                <span>تاريخ الرفع: {new Date(task.created_at).toLocaleString()} | </span>
                {task.filename && <span>الملف: {task.filename} </span>}
                {task.uploaded_file_url && (
                    <a href={task.uploaded_file_url} target="_blank" rel="noopener noreferrer" title="عرض الملف الأصلي">
                       (عرض الملف)
                    </a>
                )}
              </p>
              {task.description && <p className="task-description">{task.description}</p>}
            </div>

            {/* إجراءات المهمة */}
            <div className="task-actions">
               <button
                  onClick={() => onAnalyze(task.id)}
                  disabled={loadingState[task.id]?.analyzing || loadingState[task.id]?.deleting}
                  title="تشغيل تحليل NLP (أخطاء، كيانات)"
               >
                 {loadingState[task.id]?.analyzing ? 'جارٍ التحليل...' : 'تحليل النص'}
               </button>
               <button
                  onClick={() => onEvaluate(task.id)}
                  disabled={loadingState[task.id]?.evaluating || loadingState[task.id]?.deleting}
                  title="تشغيل نموذج تقييم الجودة"
               >
                 {loadingState[task.id]?.evaluating ? 'جارٍ التقييم...' : 'تقييم الجودة'}
               </button>
               <button
                  className="delete-button"
                  onClick={() => onDelete(task.id)}
                  disabled={loadingState[task.id]?.deleting || loadingState[task.id]?.analyzing || loadingState[task.id]?.evaluating}
                  title="حذف هذه المهمة وملفها"
                >
                 {loadingState[task.id]?.deleting ? 'جارٍ الحذف...' : 'حذف المهمة'}
               </button>
            </div>

            {/* عرض نتائج التحليل */}
            {loadingState[task.id]?.analyzeError && (
              <p className="error analysis-error">
                خطأ في التحليل: {loadingState[task.id]?.analyzeError}
              </p>
            )}
            {analysisResults[task.id] && !loadingState[task.id]?.analyzing && (
              <div className="results analysis-results">
                <h4>نتائج التحليل:</h4>
                {analysisResults[task.id].error ? (
                  <p className='error'>{analysisResults[task.id].error}</p>
                ) : (
                 <>
                    {analysisResults[task.id].warning && <p className='warning'>ملاحظة: {analysisResults[task.id].warning}</p>}
                    {/* عرض نتائج التحليل المحددة */}
                    <p>الكلمات: {analysisResults[task.id].word_count ?? 'غير متاح'} | الجمل: {analysisResults[task.id].sentence_count ?? 'غير متاح'}</p>

                    {analysisResults[task.id].potential_spelling_errors?.length > 0 ? (
                      <>
                        <h5>أخطاء إملائية محتملة:</h5>
                        <ul>{analysisResults[task.id].potential_spelling_errors.map((err, i) =>
                           <li key={`spell-err-${i}`}>{err.suggestion || err.term} (عند {err.position})</li>)}
                        </ul>
                      </>
                    ) : <p>لم يتم العثور على أخطاء إملائية كبيرة.</p>}

                    {analysisResults[task.id].entities?.length > 0 ? (
                      <>
                        <h5>الكيانات المكتشفة:</h5>
                        <ul className="entity-list">
                            {analysisResults[task.id].entities.map((ent, i) =>
                               <li key={`ent-${i}`}>
                                 <strong>{ent.text}</strong> <span className="entity-label">({ent.label})</span>
                               </li>
                            )}
                        </ul>
                      </>
                    ) : <p>لم يتم التعرف على أي كيانات.</p>}
                 </>
                )}
              </div>
            )}

            {/* عرض نتائج التقييم */}
             {loadingState[task.id]?.evaluateError && (
               <p className="error evaluation-error">
                 خطأ في التقييم: {loadingState[task.id]?.evaluateError}
               </p>
             )}
             {evaluationResults[task.id] && !loadingState[task.id]?.evaluating && (
              <div className="results evaluation-results">
                <h4>نتائج التقييم:</h4>
                 {evaluationResults[task.id].error ? (
                   <p className='error'>{evaluationResults[task.id].error}</p>
                 ) : (
                  <>
                    <p>تصنيف الجودة: <strong>{evaluationResults[task.id].label ?? 'غير متاح'}</strong></p>
                    {/* عرض الدرجة فقط إذا كانت متاحة */}
                    {evaluationResults[task.id].score !== undefined && evaluationResults[task.id].score !== null && (
                       <p>درجة الثقة: {evaluationResults[task.id].score.toFixed(3)}</p>
                    )}
                  </>
                 )}
              </div>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default TaskList;
