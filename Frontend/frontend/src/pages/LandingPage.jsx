import React from 'react';
import { Link } from 'react-router-dom';

function LandingPage() {
  return (
    <div className="p-4">
      <h1>Welcome to the Landing Page!</h1>
      <nav className="mt-4">
        <ul className="space-y-2">
          <li><Link to="/login">Login</Link></li>
          <li><Link to="/signup">Signup</Link></li>
          <li><Link to="/api-docs">API Documentation</Link></li>
          <li><Link to="/dashboard">Dashboard</Link></li>
          <li><Link to="/dashboard/session">Session</Link></li>
          <li><Link to="/dashboard/upload-files">Upload Files</Link></li>
          <li><Link to="/dashboard/scrape-web">Scrape Web</Link></li>
          <li><Link to="/dashboard/create-api">Create API</Link></li>
        </ul>
      </nav>
    </div>
  );
}

export default LandingPage;