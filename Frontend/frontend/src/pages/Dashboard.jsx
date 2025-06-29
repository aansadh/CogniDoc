import React from 'react';
import { Routes, Route } from 'react-router-dom';
import SessionRoute from './dashboard/SessionRoute';
import UploadFilesRoute from './dashboard/UploadFilesRoute';
import ScrapeWebRoute from './dashboard/ScrapeWebRoute';
import CreateAPIRoute from './dashboard/CreateAPIRoute';

function Dashboard() {
  return (
    <div>
      <h1>Dashboard</h1>
      <Routes>
        <Route path="session" element={<SessionRoute />} />
        <Route path="upload-files" element={<UploadFilesRoute />} />
        <Route path="scrape-web" element={<ScrapeWebRoute />} />
        <Route path="create-api" element={<CreateAPIRoute />} />
      </Routes>
    </div>
  );
}

export default Dashboard;
