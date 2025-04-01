import axios from 'axios';

// Create an axios instance
const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle token expiration
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // If we get a 401 response, clear the token and redirect to login
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API service functions
const apiService = {
  // Auth endpoints
  setToken: (token) => {
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      delete api.defaults.headers.common['Authorization'];
    }
  },
  
  register: (email, password) => {
    return api.post('/auth/register', { email, password });
  },
  
  login: (email, password) => {
    return api.post('/auth/login', { email, password });
  },
  
  // Evaluation endpoints
  evaluateTask: (task) => {
    return api.post('/evaluation/evaluate', { task });
  },
  
  getEvaluations: () => {
    return api.get('/evaluation/evaluations');
  }
};

export default apiService;
