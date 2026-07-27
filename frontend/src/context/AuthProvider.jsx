import { useEffect, useState } from 'react';
import { setUnauthorizedHandler } from '../api/client';
import { AuthContext } from './authContext';

export function AuthProvider({ children }) {
  const [token, setToken] = useState(null);

  const login = (newToken) => setToken(newToken);
  const logout = () => setToken(null);

  // При 401 от любого запроса client.js вызовет logout - токен обнулится,
  // и ProtectedRoute сам перекинет на /login.
  useEffect(() => {
    setUnauthorizedHandler(logout);
  }, []);

  return (
    <AuthContext.Provider value={{ token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
