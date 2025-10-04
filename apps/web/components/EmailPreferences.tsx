'use client';

import { useState, useEffect } from 'react';
import { CheckIcon, XMarkIcon } from '@heroicons/react/24/outline';

interface EmailPreferences {
  id: string;
  marketing_emails: boolean;
  transactional_emails: boolean;
  product_updates: boolean;
  security_alerts: boolean;
  billing_notifications: boolean;
  weekly_digest: boolean;
  created_at: string;
  updated_at: string;
}

export function EmailPreferences() {
  const [preferences, setPreferences] = useState<EmailPreferences | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    loadPreferences();
  }, []);

  const loadPreferences = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/email/preferences', {
        headers: {
          'Authorization': `Bearer ${await getAuthToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to load email preferences');
      }

      const data = await response.json();
      setPreferences(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load preferences');
    } finally {
      setLoading(false);
    }
  };

  const updatePreferences = async (updatedPreferences: Partial<EmailPreferences>) => {
    try {
      setSaving(true);
      setError(null);
      setSuccess(null);

      const response = await fetch('/api/email/preferences', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${await getAuthToken()}`,
        },
        body: JSON.stringify(updatedPreferences),
      });

      if (!response.ok) {
        throw new Error('Failed to update email preferences');
      }

      const data = await response.json();
      setPreferences(data);
      setSuccess('Email preferences updated successfully');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update preferences');
    } finally {
      setSaving(false);
    }
  };

  const handleToggle = (key: keyof EmailPreferences) => {
    if (!preferences) return;

    const updatedPreferences = {
      ...preferences,
      [key]: !preferences[key],
    };

    setPreferences(updatedPreferences);
    updatePreferences({ [key]: updatedPreferences[key] });
  };

  const handleTestEmail = async () => {
    try {
      setError(null);
      setSuccess(null);

      const response = await fetch('/api/email/test-welcome', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${await getAuthToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to send test email');
      }

      setSuccess('Test welcome email sent successfully');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send test email');
    }
  };

  const getAuthToken = async (): Promise<string> => {
    // This would typically get the token from your auth system
    // For now, we'll return a placeholder
    return 'your-auth-token-here';
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!preferences) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <div className="flex">
          <XMarkIcon className="h-5 w-5 text-red-400" />
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error</h3>
            <p className="mt-1 text-sm text-red-700">Failed to load email preferences</p>
          </div>
        </div>
      </div>
    );
  }

  const preferenceItems = [
    {
      key: 'marketing_emails' as keyof EmailPreferences,
      label: 'Marketing Emails',
      description: 'Receive promotional emails and special offers',
      required: false,
    },
    {
      key: 'transactional_emails' as keyof EmailPreferences,
      label: 'Transactional Emails',
      description: 'Account-related emails like welcome messages and confirmations',
      required: true,
    },
    {
      key: 'product_updates' as keyof EmailPreferences,
      label: 'Product Updates',
      description: 'New features, improvements, and product announcements',
      required: false,
    },
    {
      key: 'security_alerts' as keyof EmailPreferences,
      label: 'Security Alerts',
      description: 'Important security notifications and account activity',
      required: true,
    },
    {
      key: 'billing_notifications' as keyof EmailPreferences,
      label: 'Billing Notifications',
      description: 'Payment confirmations, invoices, and subscription updates',
      required: true,
    },
    {
      key: 'weekly_digest' as keyof EmailPreferences,
      label: 'Weekly Digest',
      description: 'Weekly summary of your activity and usage',
      required: false,
    },
  ];

  return (
    <div className="space-y-6">
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <XMarkIcon className="h-5 w-5 text-red-400" />
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Error</h3>
              <p className="mt-1 text-sm text-red-700">{error}</p>
            </div>
          </div>
        </div>
      )}

      {success && (
        <div className="bg-green-50 border border-green-200 rounded-md p-4">
          <div className="flex">
            <CheckIcon className="h-5 w-5 text-green-400" />
            <div className="ml-3">
              <h3 className="text-sm font-medium text-green-800">Success</h3>
              <p className="mt-1 text-sm text-green-700">{success}</p>
            </div>
          </div>
        </div>
      )}

      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-lg font-medium text-gray-900">Email Preferences</h2>
          <button
            onClick={handleTestEmail}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 text-sm"
          >
            Send Test Email
          </button>
        </div>

        <div className="space-y-6">
          {preferenceItems.map((item) => (
            <div key={item.key} className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center">
                  <h3 className="text-sm font-medium text-gray-900">
                    {item.label}
                    {item.required && (
                      <span className="ml-1 text-red-500">*</span>
                    )}
                  </h3>
                </div>
                <p className="mt-1 text-sm text-gray-600">{item.description}</p>
              </div>
              <div className="ml-4 flex-shrink-0">
                <button
                  type="button"
                  onClick={() => handleToggle(item.key)}
                  disabled={item.required || saving}
                  className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                    preferences[item.key]
                      ? 'bg-blue-600'
                      : 'bg-gray-200'
                  } ${item.required || saving ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  <span
                    className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                      preferences[item.key] ? 'translate-x-5' : 'translate-x-0'
                    }`}
                  />
                </button>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-6 pt-6 border-t border-gray-200">
          <p className="text-sm text-gray-600">
            <span className="text-red-500">*</span> Required emails cannot be disabled as they are essential for account security and billing.
          </p>
        </div>
      </div>

      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Email History</h3>
        <p className="text-sm text-gray-600">
          View your recent email notifications and delivery status in the{' '}
          <a href="/dashboard/notifications" className="text-blue-600 hover:text-blue-800">
            notifications section
          </a>
          .
        </p>
      </div>
    </div>
  );
}
