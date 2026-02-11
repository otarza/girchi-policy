import React, { createContext, useContext, useState, type ReactNode } from 'react';
import { mockUser, type User } from '@/src/mock';

interface AppState {
  isAuthenticated: boolean;
  isOnboarded: boolean;
  user: User;
  setAuthenticated: (val: boolean) => void;
  setOnboarded: (val: boolean) => void;
  logout: () => void;
}

const AppContext = createContext<AppState | null>(null);

export function AppProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setAuthenticated] = useState(false);
  const [isOnboarded, setOnboarded] = useState(false);

  const logout = () => {
    setAuthenticated(false);
    setOnboarded(false);
  };

  return (
    <AppContext.Provider
      value={{
        isAuthenticated,
        isOnboarded,
        user: mockUser,
        setAuthenticated,
        setOnboarded,
        logout,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp must be used within AppProvider');
  return ctx;
}
