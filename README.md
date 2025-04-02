# نظام تقييم BTEC - BTEC Evaluation System

<div style="direction: rtl; text-align: right;">

## نظرة عامة

نظام تقييم BTEC هو منصة متطورة تسمح بالتقييم الآلي لمهام وتسليمات طلاب BTEC باستخدام الذكاء الاصطناعي. يوفر النظام تقييمًا دقيقًا وشفافًا مع إمكانية التحقق من صحة التقييمات باستخدام تقنية blockchain.

## الميزات الرئيسية

- **التقييم المدعوم بالذكاء الاصطناعي**: يستخدم نماذج OpenAI المتقدمة لتحليل وتقييم المهام.
- **التحقق باستخدام Blockchain**: تسجيل تقييمات مقاومة للتلاعب يمكن التحقق منها لاحقًا.
- **الأمان**: تشفير المحتوى الحساس في قاعدة البيانات وتوثيق قوي.
- **معايير تقييم BTEC**: تقييم بناءً على معايير BTEC الرسمية (Pass/Merit/Distinction).
- **مرونة التقييم**: إمكانية استخدام معايير تقييم مخصصة.
- **واجهة برمجة تطبيقات قوية**: واجهة برمجة RESTful كاملة للتكامل مع أنظمة أخرى.

## التقنيات المستخدمة

- **Backend**: Flask, SQLAlchemy, PostgreSQL
- **AI**: OpenAI GPT-4o API
- **الأمان**: JWT, تشفير Fernet
- **التحقق**: تقنية Blockchain (Ethereum)

## البنية التقنية

- نظام مقسم إلى خدمات منفصلة للمصادقة والتقييم والتشفير والتحقق
- دعم كامل للغة العربية في التقييمات والنتائج
- تنظيم قاعدة بيانات بعلاقات واضحة
- سجل تدقيق كامل للتقييمات

## واجهة برمجة التطبيقات (API)

### المصادقة

- `POST /auth/register`: تسجيل مستخدم جديد
- `POST /auth/login`: تسجيل الدخول والحصول على رمز JWT

### التقييم

- `POST /evaluation/evaluate`: تقييم مهمة BTEC (نص أو JSON)
- `GET /evaluation/evaluations`: الحصول على جميع تقييمات المستخدم
- `GET /evaluation/evaluation/{id}`: الحصول على تقييم محدد
- `POST /evaluation/evaluate/rubric`: تقييم باستخدام معايير مخصصة
- `GET /evaluation/verify/{hash}`: التحقق من تقييم باستخدام رمز التدقيق
- `GET /evaluation/evaluation/{id}/verify`: التحقق من تقييم المستخدم

## التثبيت والإعداد

1. استنساخ المستودع
2. تثبيت المتطلبات: `pip install -r backend/requirements.txt`
3. إعداد متغيرات البيئة في ملف `.env`:
   - `DATABASE_URL`: عنوان قاعدة البيانات PostgreSQL
   - `SECRET_KEY`: مفتاح سري لجلسات Flask
   - `JWT_SECRET_KEY`: مفتاح سري لرموز JWT
   - `ENCRYPTION_KEY`: مفتاح لتشفير البيانات الحساسة
   - `OPENAI_API_KEY`: مفتاح API لـ OpenAI
   - (اختياري) مفاتيح Blockchain - `INFURA_URL`, `CONTRACT_ADDRESS`, `SIGNER_PRIVATE_KEY`

4. تهيئة قاعدة البيانات: `flask db upgrade`
5. تشغيل الخادم: `python run_flask_server.py`

## التطوير المستقبلي

- واجهة مستخدم رسومية كاملة
- دعم للتقييم بلغات متعددة
- تحليلات متقدمة للتقييمات
- تكامل كامل مع blockchain الإنتاجية

</div>

--- 

<div style="direction: ltr; text-align: left;">

## Overview

The BTEC Evaluation System is an advanced platform that enables automated assessment of BTEC student submissions using AI. The system provides accurate and transparent evaluation with blockchain verification capabilities.

## Key Features

- **AI-Powered Assessment**: Utilizes advanced OpenAI models to analyze and evaluate submissions.
- **Blockchain Verification**: Tamper-resistant evaluation records that can be verified later.
- **Security**: Encryption of sensitive content in the database and robust authentication.
- **BTEC Grading Standards**: Evaluation based on official BTEC criteria (Pass/Merit/Distinction).
- **Flexible Assessment**: Ability to use custom rubrics for evaluation.
- **Robust API**: Complete RESTful API for integration with other systems.

## Technologies Used

- **Backend**: Flask, SQLAlchemy, PostgreSQL
- **AI**: OpenAI GPT-4o API
- **Security**: JWT, Fernet encryption
- **Verification**: Blockchain technology (Ethereum)

## Technical Architecture

- System divided into separate services for authentication, evaluation, encryption, and verification
- Full Arabic language support in evaluations and results
- Organized database with clear relationships
- Complete audit trail of evaluations

## API Reference

### Authentication

- `POST /auth/register`: Register a new user
- `POST /auth/login`: Login and obtain JWT token

### Evaluation

- `POST /evaluation/evaluate`: Evaluate a BTEC task (text or JSON)
- `GET /evaluation/evaluations`: Get all user evaluations
- `GET /evaluation/evaluation/{id}`: Get a specific evaluation
- `POST /evaluation/evaluate/rubric`: Evaluate using custom rubric
- `GET /evaluation/verify/{hash}`: Verify an evaluation by audit hash
- `GET /evaluation/evaluation/{id}/verify`: Verify a user's evaluation

## Installation & Setup

1. Clone the repository
2. Install requirements: `pip install -r backend/requirements.txt`
3. Set up environment variables in `.env` file:
   - `DATABASE_URL`: PostgreSQL database URL
   - `SECRET_KEY`: Secret key for Flask sessions
   - `JWT_SECRET_KEY`: Secret key for JWT tokens
   - `ENCRYPTION_KEY`: Key for encrypting sensitive data
   - `OPENAI_API_KEY`: API key for OpenAI
   - (Optional) Blockchain keys - `INFURA_URL`, `CONTRACT_ADDRESS`, `SIGNER_PRIVATE_KEY`

4. Initialize database: `flask db upgrade`
5. Run the server: `python run_flask_server.py`

## Future Development

- Complete graphical user interface
- Support for multi-language evaluation
- Advanced analytics for evaluations
- Full integration with production blockchain

</div>