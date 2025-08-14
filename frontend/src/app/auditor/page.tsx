'use client';

import { useEffect, useState } from 'react';
import { useAuditorStore } from '@/stores/auditor';
import { companiesApi } from '@/services/api';
import Link from 'next/link';
import { UserCheck, Building2, Eye, CheckCircle, Clock, AlertCircle } from 'lucide-react';
import { Company } from '@/types';

export default function AuditorDashboard() {
  const { companies, setCompanies } = useAuditorStore();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadCompanies();
  }, []);

  const loadCompanies = async () => {
    try {
      setLoading(true);
      const fetchedCompanies = await companiesApi.getAll();
      setCompanies(fetchedCompanies);
    } catch (err) {
      setError('Failed to load companies');
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: Company['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'pending':
        return <Clock className="h-5 w-5 text-yellow-600" />;
      default:
        return <AlertCircle className="h-5 w-5 text-blue-600" />;
    }
  };

  const getStatusColor = (status: Company['status']) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-blue-100 text-blue-800';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading companies...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center space-x-2">
              <UserCheck className="h-8 w-8 text-indigo-600" />
              <span className="text-2xl font-bold text-gray-900">CNAV</span>
            </Link>
            <div className="text-sm text-gray-600">
              Auditor Dashboard
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          {/* Header Section */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Auditor Dashboard</h1>
            <p className="text-gray-600">
              Review and evaluate company compliance submissions. Access comprehensive audit tools to assess cybersecurity provisions.
            </p>
          </div>

          {/* Stats Overview */}
          <div className="grid md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <div className="flex items-center">
                <div className="bg-blue-100 p-3 rounded-lg">
                  <Building2 className="h-6 w-6 text-blue-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm text-gray-600">Total Companies</p>
                  <p className="text-2xl font-bold text-gray-900">{companies.length}</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border p-6">
              <div className="flex items-center">
                <div className="bg-green-100 p-3 rounded-lg">
                  <CheckCircle className="h-6 w-6 text-green-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm text-gray-600">Completed</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {companies.filter(c => c.status === 'completed').length}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border p-6">
              <div className="flex items-center">
                <div className="bg-yellow-100 p-3 rounded-lg">
                  <Clock className="h-6 w-6 text-yellow-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm text-gray-600">Pending Review</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {companies.filter(c => c.status === 'pending').length}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border p-6">
              <div className="flex items-center">
                <div className="bg-blue-100 p-3 rounded-lg">
                  <AlertCircle className="h-6 w-6 text-blue-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm text-gray-600">Active</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {companies.filter(c => c.status === 'active').length}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Companies List */}
          <div className="bg-white rounded-lg shadow-sm border">
            <div className="px-6 py-4 border-b">
              <h2 className="text-lg font-semibold text-gray-900">Companies</h2>
            </div>

            {error && (
              <div className="px-6 py-4 bg-red-50 border-b border-red-200">
                <p className="text-red-600">{error}</p>
              </div>
            )}

            {companies.length === 0 ? (
              <div className="px-6 py-12 text-center">
                <Building2 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No Companies Yet</h3>
                <p className="text-gray-600">Companies will appear here once they register and submit questionnaires.</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-200">
                {companies.map((company) => (
                  <div key={company.id} className="px-6 py-4 hover:bg-gray-50">
                    <div className="flex items-center justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <Building2 className="h-8 w-8 text-gray-400" />
                          </div>
                          <div className="ml-4 flex-1 min-w-0">
                            <h3 className="text-lg font-medium text-gray-900 truncate">
                              {company.name}
                            </h3>
                            <div className="mt-1 flex items-center space-x-4 text-sm text-gray-500">
                              <span>Contact: {company.contactPerson}</span>
                              <span>{company.contactEmail}</span>
                              <span>Registered: {new Date(company.registrationDate).toLocaleDateString()}</span>
                            </div>
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-2">
                          {getStatusIcon(company.status)}
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(company.status)}`}>
                            {company.status.charAt(0).toUpperCase() + company.status.slice(1)}
                          </span>
                        </div>

                        <Link
                          href={`/auditor/companies/${company.id}`}
                          className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                        >
                          <Eye className="h-4 w-4" />
                          <span>Review</span>
                        </Link>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Quick Actions */}
          <div className="mt-8 bg-indigo-50 border border-indigo-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-indigo-900 mb-3">Quick Actions</h3>
            <div className="space-y-2 text-indigo-800">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-indigo-600 rounded-full"></div>
                <span>Select a company to review their compliance questionnaire</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-indigo-600 rounded-full"></div>
                <span>Evaluate answers against cybersecurity provisions</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-indigo-600 rounded-full"></div>
                <span>Generate compliance reports and scores</span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}