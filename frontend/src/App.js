// src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import InteractiveSessions from './components/InteractiveSessions';
import AttendanceRecord from './components/AttendanceRecord';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app" dir="rtl">
        <header className="app-header">
          <h1>نظام تقييم BTEC</h1>
          <nav>
            <ul className="nav-menu">
              <li>
                <Link to="/">الرئيسية</Link>
              </li>
              <li>
                <Link to="/sessions">الحصص التفاعلية</Link>
              </li>
              <li>
                <Link to="/attendance">سجل الحضور والغياب</Link>
              </li>
            </ul>
          </nav>
        </header>

        <main className="app-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/sessions" element={<InteractiveSessions />} />
            <Route path="/attendance" element={<AttendanceRecord />} />
          </Routes>
        </main>

        <footer className="app-footer">
          <p>© {new Date().getFullYear()} نظام تقييم BTEC - تم التطوير بواسطة مصعب الحلالة</p>
        </footer>
      </div>
    </Router>
  );
}

// صفحة الرئيسية البسيطة
function Home() {
  return (
    <div className="home-page">
      <h1>مرحباً بك في نظام تقييم BTEC</h1>
      <p>نظام متكامل لإدارة وتقييم المهام الدراسية مع توثيق النتائج باستخدام تقنية البلوكتشين.</p>
      
      <div className="features">
        <div className="feature-card">
          <h3>الحصص التفاعلية</h3>
          <p>إنشاء وإدارة الحصص الدراسية التفاعلية مع الطلاب.</p>
          <Link to="/sessions" className="feature-link">انتقل إلى الحصص التفاعلية</Link>
        </div>
        
        <div className="feature-card">
          <h3>سجل الحضور والغياب</h3>
          <p>متابعة حضور وغياب الطلاب في الحصص الدراسية.</p>
          <Link to="/attendance" className="feature-link">انتقل إلى سجل الحضور</Link>
        </div>
      </div>
    </div>
  );
}

export default App;