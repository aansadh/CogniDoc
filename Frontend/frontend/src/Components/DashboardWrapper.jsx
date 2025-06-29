import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { useUser } from '@clerk/clerk-react';
import Dashboard from '../pages/Dashboard';

function DashboardWrapper() {
  const { user } = useUser();

  React.useEffect(() => {
    if (user) {
      localStorage.setItem('userId', user.id);
    }
  }, [user]);

  return (
    <Routes>
      <Route path="" element={<Dashboard />} />
      <Route path="session" element={<Dashboard />} />
      <Route path="upload-files" element={<Dashboard />} />
      <Route path="scrape-web" element={<Dashboard />} />
      <Route path="create-api" element={<Dashboard />} />
    </Routes>
  );
}

export default DashboardWrapper;
