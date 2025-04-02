import requests
import json

# Base URL for the API
BASE_URL = 'http://0.0.0.0:5000'

def test_health():
    """Test the health endpoint"""
    response = requests.get(f'{BASE_URL}/health')
    print(f'Health check status: {response.status_code}')
    print(f'Response: {response.text}')
    print('-' * 50)

def test_register():
    """Test user registration"""
    payload = {
        'email': 'test2@example.com',
        'password': 'password123'
    }
    response = requests.post(f'{BASE_URL}/auth/register', json=payload)
    print(f'Registration status: {response.status_code}')
    print(f'Response: {response.json()}')
    print('-' * 50)

def test_login():
    """Test user login"""
    payload = {
        'email': 'test@example.com',
        'password': 'password123'
    }
    response = requests.post(f'{BASE_URL}/auth/login', json=payload)
    print(f'Login status: {response.status_code}')
    result = response.json()
    print(f'Response: {result}')
    
    if 'token' in result:
        return result['token']
    print('-' * 50)
    return None

def test_evaluate(token):
    """Test task evaluation"""
    if not token:
        print("No token available for evaluation test.")
        return
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    payload = {
        'task': """This is a sample BTEC assignment submission for IT Project Management.
        
Project Plan:
1. Project Initiation: I defined the project scope, gathered requirements, and identified key stakeholders.
2. Project Planning: I created a Gantt chart, allocated resources, and established milestones.
3. Risk Assessment: I identified potential risks and developed contingency plans.
4. Budget Planning: I estimated costs and created a budget plan with 10% contingency.
5. Communication Strategy: I established regular reporting methods and stakeholder communication channels.
        
The project was delivered on time and within budget, meeting all the specified requirements.
"""
    }
    
    response = requests.post(f'{BASE_URL}/evaluation/evaluate', headers=headers, json=payload)
    print(f'Evaluation status: {response.status_code}')
    print(f'Response: {json.dumps(response.json(), indent=2)}')
    print('-' * 50)

def test_get_evaluations(token):
    """Test retrieving evaluations"""
    if not token:
        print("No token available for getting evaluations.")
        return
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    response = requests.get(f'{BASE_URL}/evaluation/evaluations', headers=headers)
    print(f'Get evaluations status: {response.status_code}')
    print(f'Response: {json.dumps(response.json(), indent=2)}')
    print('-' * 50)

if __name__ == '__main__':
    print("Starting API tests...")
    try:
        test_health()
        # Uncomment the line below if you want to test registration
        # test_register()
        token = test_login()
        if token:
            test_evaluate(token)
            test_get_evaluations(token)
    except Exception as e:
        print(f"Error during testing: {e}")