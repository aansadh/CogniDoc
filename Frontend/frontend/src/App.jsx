import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { ClerkProvider, RedirectToSignIn, SignedIn, SignedOut } from '@clerk/clerk-react';

import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import APIDocumentation from './pages/APIDocumentation';
import Dashboard from './pages/Dashboard';
import Sidebar from './Components/ui/Sidebar';
import DashboardWrapper from './Components/DashboardWrapper';

const CLERK_PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;

function App() {
  return (
    <ClerkProvider publishableKey={CLERK_PUBLISHABLE_KEY}>
      <Router>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route path="/api-docs" element={<APIDocumentation />} />

          {/* Protected Routes */}
          <Route
            path="/dashboard/*"
            element={
              <SignedIn>
                <Sidebar />
                <DashboardWrapper />
              </SignedIn>
            }
          />

          {/* Redirect to login if signed out */}
          <Route
            path="*"
            element={
              <SignedOut>
                <RedirectToSignIn />
              </SignedOut>
            }
          />
        </Routes>
      </Router>
    </ClerkProvider>
  );
}

export default App;