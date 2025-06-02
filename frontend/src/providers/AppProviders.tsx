// src/providers/AppProviders.tsx

import { ReactNode } from 'react';
import { AppProvider } from '../context/AppContext';
import { ProjectProvider } from '../context/ProjectContext';

interface AppProvidersProps {
  children: ReactNode;
}

export function AppProviders({ children }: AppProvidersProps) {
  return (
    <AppProvider>
      <ProjectProvider>
        {children}
      </ProjectProvider>
    </AppProvider>
  );
}

export default AppProviders;
