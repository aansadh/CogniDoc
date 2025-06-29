import React from 'react';
import { SignIn } from '@clerk/clerk-react';

function LoginPage() {
  return (
    <div className="flex items-center justify-center h-screen bg-gray-100">
      <SignIn path="/login" routing="path" redirectUrl="/dashboard" />
    </div>
  );
}

export default LoginPage;
