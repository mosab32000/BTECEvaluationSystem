// src/components/AttendanceRecord.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const AttendanceRecord = () => {
  const [studentId, setStudentId] = useState('');
  const [attendanceDate, setAttendanceDate] = useState('');
  const [status, setStatus] = useState('present');
  const [records, setRecords] = useState([]);

  // دالة لجلب سجلات الحضور من السيرفر
  const fetchAttendance = async () => {
    try {
      const response = await axios.get('http://localhost:3000/api/attendance/attendance', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      setRecords(response.data);
    } catch (error) {
      console.error('خطأ في جلب سجلات الحضور:', error);
    }
  };

  // استدعاء الدالة عند تحميل الصفحة
  useEffect(() => {
    fetchAttendance();
  }, []);

  // دالة لتسجيل الحضور أو الغياب
  const recordAttendance = async (e) => {
    e.preventDefault();
    try {
      await axios.post('http://localhost:3000/api/attendance/attendance', {
        student_id: studentId,
        attendance_date: attendanceDate || new Date().toISOString().split('T')[0],
        status
      }, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      setStudentId('');
      setAttendanceDate('');
      setStatus('present');
      fetchAttendance();
    } catch (error) {
      console.error('خطأ في تسجيل الحضور:', error);
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>سجل الحضور والغياب</h1>
      <form onSubmit={recordAttendance} style={{ marginBottom: '20px' }}>
        <div>
          <label>معرف الطالب:</label>
          <input
            type="number"
            value={studentId}
            onChange={(e) => setStudentId(e.target.value)}
            required
          />
        </div>
        <div>
          <label>تاريخ الحضور:</label>
          <input
            type="date"
            value={attendanceDate}
            onChange={(e) => setAttendanceDate(e.target.value)}
          />
        </div>
        <div>
          <label>الحالة:</label>
          <select value={status} onChange={(e) => setStatus(e.target.value)}>
            <option value="present">حاضر</option>
            <option value="absent">غائب</option>
          </select>
        </div>
        <button type="submit">تسجيل الحضور</button>
      </form>
      <h2>سجلات الحضور</h2>
      {records.length === 0 ? (
        <p>لا توجد سجلات متاحة.</p>
      ) : (
        <table border="1" cellPadding="10">
          <thead>
            <tr>
              <th>معرف الطالب</th>
              <th>التاريخ</th>
              <th>الحالة</th>
            </tr>
          </thead>
          <tbody>
            {records.map((record, index) => (
              <tr key={index}>
                <td>{record.student_id}</td>
                <td>{record.date}</td>
                <td>{record.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default AttendanceRecord;