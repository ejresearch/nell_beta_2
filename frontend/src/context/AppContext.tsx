import React, { createContext, useContext, useState, ReactNode } from 'react';

interface UserSettings {
  apiUrl: string;
  openaiApiKey: string;
  defaultModel: string;
  theme: 'light' | 'dark';
}

interface AppSettings extends UserSettings {
  // Additional app-specific settings can go here
}

interface AppState {
  isOnline: boolean;
  mirandaVisible: boolean;
  sidebarCollapsed: boolean;
  notifications: Notification[];
}

interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
}

interface AppContextType {
  settings: AppSettings;
  state: AppState;
  updateSettings: (updates: Partial<AppSettings>) => void;
  updateState: (updates: Partial<AppState>) => void;
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => void;
  markNotificationRead: (id: string) => void;
  clearNotifications: () => void;
}

const defaultSettings: AppSettings = {
  apiUrl: 'http://localhost:8000',
  openaiApiKey: '',
  defaultModel: 'gpt-4o-mini',
  theme: 'light'
};

const defaultState: AppState = {
  isOnline: true,
  mirandaVisible: false,
  sidebarCollapsed: false,
  notifications: []
};

const AppContext = createContext<AppContextType | undefined>(undefined);

export const useAppState = () => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useAppState must be used within an AppProvider');
  }
  return context;
};

interface AppProviderProps {
  children: ReactNode;
}

export const AppProvider: React.FC<AppProviderProps> = ({ children }) => {
  const [settings, setSettings] = useState<AppSettings>(defaultSettings);
  const [state, setState] = useState<AppState>(defaultState);

  const updateSettings = (updates: Partial<AppSettings>) => {
    setSettings(prev => ({ ...prev, ...updates }));
    
    // Save to localStorage
    const newSettings = { ...settings, ...updates };
    localStorage.setItem('nell-settings', JSON.stringify(newSettings));
  };

  const updateState = (updates: Partial<AppState>) => {
    setState(prev => ({ ...prev, ...updates }));
  };

  const addNotification = (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => {
    const newNotification: Notification = {
      ...notification,
      id: Date.now().toString(),
      timestamp: new Date(),
      read: false
    };

    setState(prev => ({
      ...prev,
      notifications: [newNotification, ...prev.notifications]
    }));
  };

  const markNotificationRead = (id: string) => {
    setState(prev => ({
      ...prev,
      notifications: prev.notifications.map(notif =>
        notif.id === id ? { ...notif, read: true } : notif
      )
    }));
  };

  const clearNotifications = () => {
    setState(prev => ({
      ...prev,
      notifications: []
    }));
  };

  // Load settings from localStorage on mount
  React.useEffect(() => {
    const savedSettings = localStorage.getItem('nell-settings');
    if (savedSettings) {
      try {
        const parsed = JSON.parse(savedSettings);
        setSettings(prev => ({ ...prev, ...parsed }));
      } catch (error) {
        console.warn('Failed to parse saved settings:', error);
      }
    }
  }, []);

  const value = {
    settings,
    state,
    updateSettings,
    updateState,
    addNotification,
    markNotificationRead,
    clearNotifications
  };

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
};
