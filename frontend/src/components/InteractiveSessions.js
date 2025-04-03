// src/components/InteractiveSessions.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const InteractiveSessions = () => {
  const [title, setTitle] = useState('');
  const [sessionDate, setSessionDate] = useState('');
  const [sessionTime, setSessionTime] = useState('');
  const [description, setDescription] = useState('');
  const [sessions, setSessions] = useState([]);

  // دالة لجلب جميع الجلسات من السيرفر
  const fetchSessions = async () => {
    try {
      const response = await axios.get('http://localhost:5000/sessions');
      setSessions(response.data);
    } catch (error) {
      console.error('خطأ في جلب الجلسات:', error);
    }
  };

  // استدعاء الدالة عند تحميل الصفحة
  useEffect(() => {
    fetchSessions();
  }, []);

  // دالة لإنشاء جلسة جديدة
  const createSession = async (e) => {
    e.preventDefault();
    try {
      // يجب إضافة توكن المصادقة في الهيدر إذا كان النظام يستخدم JWT
      const token = localStorage.getItem('token');
      await axios.post('http://localhost:5000/sessions', {
        title,
        session_date: sessionDate,
        session_time: sessionTime,
        description
      }, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setTitle('');
      setSessionDate('');
      setSessionTime('');
      setDescription('');
      fetchSessions();
    } catch (error) {
      console.error('خطأ في إنشاء الجلسة:', error);
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>الحصص التفاعلية</h1>
      <form onSubmit={createSession} style={{ marginBottom: '20px' }}>
        <div>
          <label>عنوان الجلسة:</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
        </div>
        <div>
          <label>تاريخ الجلسة:</label>
          <input
            type="date"
            value={sessionDate}
            onChange={(e) => setSessionDate(e.target.value)}
            required
          />
        </div>
        <div>
          <label>وقت الجلسة:</label>
          <input
            type="time"
            value={sessionTime}
            onChange={(e) => setSessionTime(e.target.value)}
            required
          />
        </div>
        <div>
          <label>الوصف:</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          ></textarea>
        </div>
        <button type="submit">إنشاء الجلسة</button>
      </form>

      <h2>قائمة الجلسات</h2>
      {sessions.length === 0 ? (
        <p>لا توجد جلسات متاحة.</p>
      ) : (
        <table border="1" cellPadding="10">
          <thead>
            <tr>
              <th>المعرف</th>
              <th>العنوان</th>
              <th>التاريخ</th>
              <th>الوقت</th>
              <th>الحالة</th>
            </tr>
          </thead>
          <tbody>
            {sessions.map((session) => (
              <tr key={session.id}>
                <td>{session.id}</td>
                <td>{session.title}</td>
                <td>{session.date}</td>
                <td>{session.time}</td>
                <td>{session.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default InteractiveSessions;