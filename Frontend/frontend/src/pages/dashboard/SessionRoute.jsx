import React, { useState, useEffect } from 'react';
import axiosInstance from '../../lib/axiosInstance';

function SessionRoute() {
  const [currentSession, setCurrentSession] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  useEffect(() => {
    const fetchSessions = async () => {
      const userId = localStorage.getItem('userId');
      try {
        const response = await axiosInstance.get('/session/get-sessions', {
          headers: {
            'Session-ID': currentSession || null,
          },
        });
        setSessions(response.data);
      } catch (error) {
        console.error('Error fetching sessions:', error);
      }
    };

    fetchSessions();
  }, [currentSession]);

  const handleSwitchSession = (sessionId) => {
    setCurrentSession(sessionId);
    setIsDialogOpen(false);
  };

  return (
    <div className="p-4">
      <h1>Current Session: {currentSession || 'None'}</h1>
      <button
        className="mt-4 px-4 py-2 bg-blue-500 text-white rounded"
        onClick={() => setIsDialogOpen(true)}
      >
        Manage Sessions
      </button>

      {isDialogOpen && (
        <div className="fixed inset-0 bg-gray-800 bg-opacity-50 flex items-center justify-center">
          <div className="bg-white p-6 rounded shadow-lg">
            <h2 className="text-lg font-bold mb-4">Sessions</h2>
            <ul className="space-y-2">
              {sessions.map((session) => (
                <li key={session._id}>
                  <button
                    className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300"
                    onClick={() => handleSwitchSession(session._id)}
                  >
                    Switch to Session {session._id}
                  </button>
                </li>
              ))}
            </ul>
            <button
              className="mt-4 px-4 py-2 bg-red-500 text-white rounded"
              onClick={() => setIsDialogOpen(false)}
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default SessionRoute;
