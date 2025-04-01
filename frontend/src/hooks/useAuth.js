import { useContext } from 'react';
import { AuthContext } from '../contexts/AuthContext';

// Custom hook to simplify accessing auth context
export default function useAuth() {
  return useContext(AuthContext);
}
