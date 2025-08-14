'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useCompanyStore } from '@/stores/company';
import Link from 'next/link';
import { Building2, FileText, CheckCircle, ArrowRight, Plus } from 'lucide-react';

export default function CompanyDashboard() {
  const router = useRouter();
  const { currentCompany, getProgress, canSubmit, isSubmitted } = useCompanyStore();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  const progress = getProgress();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center space-x-2">
              <Building2 className="h-8 w-8 text-blue-600" />
              <span className="text-2xl font-bold text-gray-900">CNAV</span>
            </Link>
            <div className="text-sm text-gray-600">
              Company Dashboard
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Welcome Section */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {currentCompany ? `Welcome, ${currentCompany.name}!` : 'Company Dashboard'}
            </h1>
            <p className="text-gray-600">
              Complete your cybersecurity compliance questionnaire to meet regulatory requirements.
            </p>
          </div>

          {/* Progress Overview */}
          {currentCompany && (
            <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Questionnaire Progress</h2>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm text-gray-600 mb-2">
                    <span>Completion Progress</span>
                    <span>{progress.toFixed(0)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${progress}%` }}
                    ></div>
                  </div>
                </div>
                
                {isSubmitted && (
                  <div className="flex items-center space-x-2 text-green-600">
                    <CheckCircle className="h-5 w-5" />
                    <span className="font-medium">Questionnaire submitted successfully!</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Action Cards */}
          <div className="grid md:grid-cols-2 gap-6">
            {/* Company Registration Card */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <div className="flex items-start space-x-4">
                <div className={`p-3 rounded-lg ${currentCompany ? 'bg-green-100' : 'bg-blue-100'}`}>
                  {currentCompany ? (
                    <CheckCircle className="h-6 w-6 text-green-600" />
                  ) : (
                    <Building2 className="h-6 w-6 text-blue-600" />
                  )}
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    Company Registration
                  </h3>
                  <p className="text-gray-600 mb-4">
                    {currentCompany 
                      ? `Registered as ${currentCompany.name}` 
                      : 'Register your company to start the questionnaire'
                    }
                  </p>
                  {currentCompany ? (
                    <div className="text-sm text-gray-500">
                      <p>Contact: {currentCompany.contactPerson}</p>
                      <p>Email: {currentCompany.contactEmail}</p>
                      <p>Registered: {new Date(currentCompany.registrationDate).toLocaleDateString()}</p>
                    </div>
                  ) : (
                    <Link
                      href="/company/register"
                      className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      <Plus className="h-4 w-4 mr-2" />
                      Register Company
                    </Link>
                  )}
                </div>
              </div>
            </div>

            {/* Questionnaire Card */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <div className="flex items-start space-x-4">
                <div className={`p-3 rounded-lg ${
                  isSubmitted ? 'bg-green-100' : 
                  currentCompany ? 'bg-blue-100' : 'bg-gray-100'
                }`}>
                  {isSubmitted ? (
                    <CheckCircle className="h-6 w-6 text-green-600" />
                  ) : (
                    <FileText className={`h-6 w-6 ${currentCompany ? 'text-blue-600' : 'text-gray-400'}`} />
                  )}
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    Compliance Questionnaire
                  </h3>
                  <p className="text-gray-600 mb-4">
                    {isSubmitted 
                      ? 'Questionnaire completed and submitted'
                      : currentCompany 
                        ? 'Answer cybersecurity compliance questions'
                        : 'Complete registration first to access questionnaire'
                    }
                  </p>
                  
                  {currentCompany && !isSubmitted && (
                    <Link
                      href="/company/questionnaire"
                      className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      <FileText className="h-4 w-4 mr-2" />
                      {progress > 0 ? 'Continue Questionnaire' : 'Start Questionnaire'}
                      <ArrowRight className="h-4 w-4 ml-2" />
                    </Link>
                  )}

                  {isSubmitted && (
                    <div className="space-y-2">
                      <div className="text-sm text-green-600 font-medium">
                        ✓ Submission complete
                      </div>
                      <p className="text-sm text-gray-500">
                        Your questionnaire has been submitted for review. 
                        You will be notified once the audit is complete.
                      </p>
                    </div>
                  )}

                  {!currentCompany && (
                    <div className="text-sm text-gray-500">
                      Register your company first to access the questionnaire
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Next Steps */}
          <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-blue-900 mb-3">Next Steps</h3>
            <div className="space-y-2 text-blue-800">
              {!currentCompany && (
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                  <span>Register your company with basic information</span>
                </div>
              )}
              {currentCompany && !isSubmitted && (
                <>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                    <span>Complete the cybersecurity questionnaire</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                    <span>Upload supporting documents where required</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                    <span>Review and submit your responses</span>
                  </div>
                </>
              )}
              {isSubmitted && (
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-600 rounded-full"></div>
                  <span>Wait for audit results and compliance report</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
} 