"use client";

import { signOut } from "next-auth/react";
import { User } from "next-auth";

interface DashboardHeaderProps {
  user: User;
}

export function DashboardHeader({ user }: DashboardHeaderProps) {
  return (
    <header className="bg-white shadow">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-6">
          <div className="flex items-center">
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-700">
              Welcome, {user.name || user.email}
            </span>
            <button onClick={() => signOut()} className="btn-secondary">
              Sign Out
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
