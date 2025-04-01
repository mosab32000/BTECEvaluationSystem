import React, { createContext, useState, useEffect } from 'react';
import api from '../services/api';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    // Check if there's a token in local storage on app load
    const token = localStorage.getItem('token');
    if (token) {
      // Set the API token and authenticated state
      api.setToken(token);
      setIsAuthenticated(true);
    }
    setLoading(false);
  }, []);
  
  // Login function
  const login = async (email, password) => {
    try {
      const response = await api.login(email, password);
      const { token } = response.data;
      
      // Store token and set authenticated state
      localStorage.setItem('token', token);
      api.setToken(token);
      setIsAuthenticated(true);
      
      return true;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };
  
  // Logout function
  const logout = () => {
    localStorage.removeItem('token');
    api.setToken(null);
    setIsAuthenticated(false);
  };
  
  const value = {
    isAuthenticated,
    loading,
    login,
    logout
  };
  
  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
