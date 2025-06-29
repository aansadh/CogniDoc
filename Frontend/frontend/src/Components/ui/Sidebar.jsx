import React from 'react';
import { Link } from 'react-router-dom';

function Sidebar() {
  return (
    <div className="w-64 h-full bg-gray-800 text-white fixed">
      <div className="p-4 text-lg font-bold border-b border-gray-700">CogniDoc</div>
      <nav className="p-4">
        <ul className="space-y-4">
          <li>
            <Link to="/dashboard" className="hover:text-gray-300">Dashboard</Link>
          </li>
          <li>
            <Link to="/dashboard/session" className="hover:text-gray-300">Session</Link>
          </li>
          <li>
            <Link to="/dashboard/upload-files" className="hover:text-gray-300">Upload Files</Link>
          </li>
          <li>
            <Link to="/dashboard/scrape-web" className="hover:text-gray-300">Scrape Web</Link>
          </li>
          <li>
            <Link to="/dashboard/create-api" className="hover:text-gray-300">Create API</Link>
          </li>
        </ul>
      </nav>
    </div>
  );
}

export default Sidebar;
