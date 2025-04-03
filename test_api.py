#!/usr/bin/env python3
"""
برنامج لاختبار واجهة برمجة التطبيقات (API) لنظام تقييم BTEC
"""

import json
import requests
import sys
import random
import string

# تهيئة عنوان الخادم
BASE_URL = "http://localhost:5000"

def test_health():
    """Test the health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health check status: {response.status_code}")
    print(f"Health check response: {response.text}")
    return response.status_code == 200

def test_register():
    """Test user registration"""
    # إنشاء بيانات تسجيل عشوائية لتجنب التكرار
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    email = f"user{random_str}@example.com"
    password = "Password123!"
    
    payload = {
        "email": email,
        "password": password
    }
    
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(
        f"{BASE_URL}/api/auth/register", 
        headers=headers,
        data=json.dumps(payload)
    )
    
    print(f"Registration status: {response.status_code}")
    print(f"Registration response: {response.text}")
    
    if response.status_code == 201:
        return email, password
    return None, None

def test_login():
    """Test user login"""
    # أولا، نقوم بتسجيل مستخدم جديد
    email, password = test_register()
    
    if not email:
        # إذا فشل التسجيل، استخدم بيانات اعتماد ثابتة للاختبار
        email = "test@example.com"
        password = "Password123!"
    
    payload = {
        "email": email,
        "password": password
    }
    
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(
        f"{BASE_URL}/api/auth/login", 
        headers=headers,
        data=json.dumps(payload)
    )
    
    print(f"Login status: {response.status_code}")
    print(f"Login response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        return data.get("token")
    return None

def test_evaluate(token):
    """Test task evaluation"""
    if not token:
        print("No authentication token available. Skipping evaluation test.")
        return
    
    payload = {
        "task": """
        BTEC Level 3 Unit 1: Information Technology Systems
        
        Task: Explain the characteristics and features of a modern computer system.
        
        My Answer:
        A modern computer system has several key characteristics. It typically includes hardware components such as a CPU, RAM, storage devices, and input/output devices. The CPU (Central Processing Unit) is the brain of the computer, responsible for executing instructions and performing calculations. RAM (Random Access Memory) provides temporary storage for data that the CPU needs to access quickly. Storage devices like SSDs or HDDs provide permanent storage for the operating system, applications, and user data.
        
        Modern computer systems also rely on software, including operating systems (like Windows, macOS, or Linux), which manage hardware resources and provide services to applications. Applications software allows users to perform specific tasks, while system software helps the computer manage its internal operations.
        
        Connectivity is another critical feature of modern computer systems. They typically include networking capabilities like Wi-Fi, Bluetooth, and Ethernet connections, allowing them to communicate with other devices and access the internet.
        
        Security features have become increasingly important in modern systems, including hardware-level security measures, encryption capabilities, and various authentication methods to protect against unauthorized access and malware.
        
        Finally, user interfaces have evolved significantly, with modern systems offering intuitive graphical user interfaces, touchscreens, voice recognition, and other natural interaction methods that make computers more accessible to a wider range of users.
        """,
        "format": "json"
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/evaluation/evaluate", 
        headers=headers,
        data=json.dumps(payload)
    )
    
    print(f"Evaluation status: {response.status_code}")
    print(f"Evaluation response: {response.text[:500]}...")  # Only show first 500 chars
    
    return response.status_code == 200

def test_get_evaluations(token):
    """Test retrieving evaluations"""
    if not token:
        print("No authentication token available. Skipping get evaluations test.")
        return
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(
        f"{BASE_URL}/api/evaluation/", 
        headers=headers
    )
    
    print(f"Get evaluations status: {response.status_code}")
    print(f"Get evaluations response: {response.text[:500]}...")  # Only show first 500 chars
    
    return response.status_code == 200

if __name__ == "__main__":
    print("Testing BTEC Evaluation System API...")
    test_health()
    
    if len(sys.argv) > 1 and sys.argv[1] == "full":
        token = test_login()
        if token:
            test_evaluate(token)
            test_get_evaluations(token)
    else:
        print("\nFor full API testing including auth and evaluation routes, run: python test_api.py full")