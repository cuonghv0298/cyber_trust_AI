'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useAuditorStore } from '@/stores/auditor';
import { companiesApi, answersApi, questionsApi, provisionsApi } from '@/services/api';
import Link from 'next/link';
import { 
  UserCheck, 
  ArrowLeft, 
  Building2, 
  CheckCircle, 
  XCircle, 
  Clock, 
  FileText,
  Users,
  Tag,
  Save,
  Download,
  AlertTriangle
} from 'lucide-react';
import { Company, Question, Answer, Provision, Evaluation } from '@/types';

export default function CompanyEvaluation() {
  const params = useParams();
  const router = useRouter();
  const companyId = params.id as string;

  const {
    selectedCompany,
    setSelectedCompany,
    questions,
    setQuestions,
    provisions,
    setProvisions,
    answers,
    setAnswers,
    evaluations,
    setEvaluation,
    getOverallComplianceScore
  } = useAuditorStore();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [currentTab, setCurrentTab] = useState<'questions' | 'provisions' | 'report'>('questions');

  useEffect(() => {
    loadCompanyData();
  }, [companyId]);

  const loadCompanyData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load company details
      const company = await companiesApi.getById(companyId);
      if (!company) {
        setError('Company not found');
        return;
      }
      setSelectedCompany(company);

      // Load questions, provisions, and answers in parallel
      const [questionsData, provisionsData, answersData] = await Promise.all([
        questionsApi.getAll(),
        provisionsApi.getAll(),
        answersApi.getByCompanyId(companyId)
      ]);

      setQuestions(questionsData);
      setProvisions(provisionsData);
      setAnswers(answersData);

    } catch (err) {
      setError('Failed to load company data');
      console.error('Error loading company data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleEvaluation = async (questionId: string, result: 'pass' | 'fail', reason?: string, notes?: string) => {
    const question = questions.find(q => q._id === questionId);
    const answer = answers.find(a => a.questionId === questionId);
    
    if (!question || !answer) return;

    const evaluation: Evaluation = {
      questionId,
      answer: answer.answer,
      result,
      reason,
      auditorNotes: notes,
      evaluatedBy: 'Current Auditor', // This should come from auth context
      evaluatedAt: new Date().toISOString()
    };

    setEvaluation(questionId, evaluation);

    // Auto-save evaluation
    setSaving(true);
    try {
      // Save to localStorage for demo - in real app this would be an API call
      const evaluationsKey = `evaluations_${companyId}`;
      const currentEvaluations = JSON.parse(localStorage.getItem(evaluationsKey) || '{}');
      currentEvaluations[questionId] = evaluation;
      localStorage.setItem(evaluationsKey, JSON.stringify(currentEvaluations));
    } catch (err) {
      console.error('Failed to save evaluation:', err);
    } finally {
      setSaving(false);
    }
  };

  const getAnswerForQuestion = (questionId: string): Answer | undefined => {
    return answers.find(a => a.questionId === questionId);
  };

  const getEvaluationForQuestion = (questionId: string): Evaluation | undefined => {
    return evaluations[questionId];
  };

  const getEvaluationStats = () => {
    const totalQuestions = questions.length;
    const evaluatedQuestions = Object.keys(evaluations).length;
    const passedQuestions = Object.values(evaluations).filter(e => e.result === 'pass').length;
    const failedQuestions = Object.values(evaluations).filter(e => e.result === 'fail').length;

    return {
      total: totalQuestions,
      evaluated: evaluatedQuestions,
      passed: passedQuestions,
      failed: failedQuestions,
      pending: totalQuestions - evaluatedQuestions,
      completionPercentage: totalQuestions > 0 ? (evaluatedQuestions / totalQuestions) * 100 : 0,
      passPercentage: evaluatedQuestions > 0 ? (passedQuestions / evaluatedQuestions) * 100 : 0
    };
  };

  const generateReport = () => {
    const stats = getEvaluationStats();
    const report = {
      company: selectedCompany,
      evaluationDate: new Date().toISOString(),
      stats,
      evaluations: Object.values(evaluations),
      overallScore: stats.passPercentage
    };

    // In a real app, this would generate a proper report
    console.log('Generated Report:', report);
    alert(`Report generated! Overall compliance score: ${stats.passPercentage.toFixed(1)}%`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading company evaluation...</p>
        </div>
      </div>
    );
  }

  if (error || !selectedCompany) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Company</h2>
          <p className="text-gray-600 mb-4">{error || 'Company not found'}</p>
          <Link href="/auditor" className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
            Back to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  const stats = getEvaluationStats();

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
            <div className="flex items-center space-x-4">
              {saving && (
                <div className="flex items-center space-x-2 text-sm text-gray-500">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-400"></div>
                  <span>Saving...</span>
                </div>
              )}
              <Link
                href="/auditor"
                className="flex items-center space-x-2 text-gray-600 hover:text-gray-900"
              >
                <ArrowLeft className="h-4 w-4" />
                <span>Back to Dashboard</span>
              </Link>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="max-w-7xl mx-auto">
          {/* Company Header */}
          <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="bg-indigo-100 p-3 rounded-lg">
                  <Building2 className="h-8 w-8 text-indigo-600" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">{selectedCompany.name}</h1>
                  <div className="text-sm text-gray-600 space-y-1">
                    <p>Contact: {selectedCompany.contactPerson} • {selectedCompany.contactEmail}</p>
                    <p>Registered: {new Date(selectedCompany.registrationDate).toLocaleDateString()}</p>
                  </div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold text-indigo-600">
                  {stats.passPercentage.toFixed(1)}%
                </div>
                <div className="text-sm text-gray-600">Compliance Score</div>
              </div>
            </div>
          </div>

          {/* Stats Overview */}
          <div className="grid md:grid-cols-5 gap-4 mb-6">
            <div className="bg-white rounded-lg shadow-sm border p-4">
              <div className="text-2xl font-bold text-gray-900">{stats.total}</div>
              <div className="text-sm text-gray-600">Total Questions</div>
            </div>
            <div className="bg-white rounded-lg shadow-sm border p-4">
              <div className="text-2xl font-bold text-blue-600">{stats.evaluated}</div>
              <div className="text-sm text-gray-600">Evaluated</div>
            </div>
            <div className="bg-white rounded-lg shadow-sm border p-4">
              <div className="text-2xl font-bold text-green-600">{stats.passed}</div>
              <div className="text-sm text-gray-600">Passed</div>
            </div>
            <div className="bg-white rounded-lg shadow-sm border p-4">
              <div className="text-2xl font-bold text-red-600">{stats.failed}</div>
              <div className="text-sm text-gray-600">Failed</div>
            </div>
            <div className="bg-white rounded-lg shadow-sm border p-4">
              <div className="text-2xl font-bold text-yellow-600">{stats.pending}</div>
              <div className="text-sm text-gray-600">Pending</div>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="bg-white rounded-lg shadow-sm border mb-6">
            <div className="border-b border-gray-200">
              <nav className="-mb-px flex space-x-8 px-6">
                <button
                  onClick={() => setCurrentTab('questions')}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    currentTab === 'questions'
                      ? 'border-indigo-500 text-indigo-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  Question Evaluation
                </button>
                <button
                  onClick={() => setCurrentTab('provisions')}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    currentTab === 'provisions'
                      ? 'border-indigo-500 text-indigo-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  Provision Mapping
                </button>
                <button
                  onClick={() => setCurrentTab('report')}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    currentTab === 'report'
                      ? 'border-indigo-500 text-indigo-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  Compliance Report
                </button>
              </nav>
            </div>

            {/* Tab Content */}
            <div className="p-6">
              {currentTab === 'questions' && (
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <h2 className="text-lg font-semibold text-gray-900">Question-by-Question Evaluation</h2>
                    <div className="text-sm text-gray-600">
                      Progress: {stats.evaluated}/{stats.total} questions evaluated
                    </div>
                  </div>

                  {questions.map((question) => {
                    const answer = getAnswerForQuestion(question._id);
                    const evaluation = getEvaluationForQuestion(question._id);

                    return (
                      <QuestionEvaluationCard
                        key={question._id}
                        question={question}
                        answer={answer}
                        evaluation={evaluation}
                        onEvaluate={(result, reason, notes) =>
                          handleEvaluation(question._id, result, reason, notes)
                        }
                      />
                    );
                  })}
                </div>
              )}

              {currentTab === 'provisions' && (
                <div className="text-center py-12">
                  <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Provision Mapping</h3>
                  <p className="text-gray-600">
                    This feature will map questions to specific compliance provisions and show provision-level compliance.
                  </p>
                  <p className="text-sm text-gray-500 mt-2">Coming soon...</p>
                </div>
              )}

              {currentTab === 'report' && (
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <h2 className="text-lg font-semibold text-gray-900">Compliance Report</h2>
                    <button
                      onClick={generateReport}
                      disabled={stats.evaluated === 0}
                      className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
                    >
                      <Download className="h-4 w-4" />
                      <span>Generate Report</span>
                    </button>
                  </div>

                  <div className="grid md:grid-cols-2 gap-6">
                    <div className="bg-gray-50 rounded-lg p-6">
                      <h3 className="font-semibold text-gray-900 mb-4">Evaluation Summary</h3>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span>Completion Rate:</span>
                          <span className="font-medium">{stats.completionPercentage.toFixed(1)}%</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Pass Rate:</span>
                          <span className="font-medium text-green-600">{stats.passPercentage.toFixed(1)}%</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Questions Passed:</span>
                          <span>{stats.passed}/{stats.total}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Questions Failed:</span>
                          <span>{stats.failed}/{stats.total}</span>
                        </div>
                      </div>
                    </div>

                    <div className="bg-gray-50 rounded-lg p-6">
                      <h3 className="font-semibold text-gray-900 mb-4">Next Steps</h3>
                      <div className="space-y-2 text-sm">
                        {stats.pending > 0 && (
                          <div className="flex items-center space-x-2 text-yellow-600">
                            <Clock className="h-4 w-4" />
                            <span>Complete evaluation of remaining {stats.pending} questions</span>
                          </div>
                        )}
                        {stats.failed > 0 && (
                          <div className="flex items-center space-x-2 text-red-600">
                            <XCircle className="h-4 w-4" />
                            <span>Review {stats.failed} failed questions with company</span>
                          </div>
                        )}
                        {stats.pending === 0 && (
                          <div className="flex items-center space-x-2 text-green-600">
                            <CheckCircle className="h-4 w-4" />
                            <span>Evaluation complete - ready to generate final report</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

// Question Evaluation Card Component
interface QuestionEvaluationCardProps {
  question: Question;
  answer?: Answer;
  evaluation?: Evaluation;
  onEvaluate: (result: 'pass' | 'fail', reason?: string, notes?: string) => void;
}

function QuestionEvaluationCard({ question, answer, evaluation, onEvaluate }: QuestionEvaluationCardProps) {
  const [result, setResult] = useState<'pass' | 'fail' | null>(evaluation?.result || null);
  const [reason, setReason] = useState(evaluation?.reason || '');
  const [notes, setNotes] = useState(evaluation?.auditorNotes || '');
  const [isExpanded, setIsExpanded] = useState(false);

  const handleSubmitEvaluation = () => {
    if (result) {
      onEvaluate(result, reason, notes);
    }
  };

  return (
    <div className="border border-gray-200 rounded-lg p-6 bg-white">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center space-x-3 mb-2">
            <div className="flex items-center space-x-2">
              {question.audience && (
                <div className="flex items-center space-x-1 text-sm text-gray-500">
                  <Users className="h-4 w-4" />
                  <span>{question.audience.join(', ')}</span>
                </div>
              )}
              {question.group_tag && (
                <div className="flex items-center space-x-1 text-sm text-gray-500">
                  <Tag className="h-4 w-4" />
                  <span>{question.group_tag}</span>
                </div>
              )}
            </div>
          </div>
          <h3 className="font-medium text-gray-900 mb-2">{question.question}</h3>
          {question.cyberessentials_requirement && (
            <div className="text-sm text-amber-700 bg-amber-50 rounded px-2 py-1 inline-block mb-3">
              Requirement: {question.cyberessentials_requirement}
            </div>
          )}
        </div>
        
        <div className="flex items-center space-x-2">
          {evaluation && (
            <div className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium ${
              evaluation.result === 'pass' 
                ? 'bg-green-100 text-green-800' 
                : 'bg-red-100 text-red-800'
            }`}>
              {evaluation.result === 'pass' ? (
                <CheckCircle className="h-3 w-3" />
              ) : (
                <XCircle className="h-3 w-3" />
              )}
              <span>{evaluation.result}</span>
            </div>
          )}
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-sm text-indigo-600 hover:text-indigo-800"
          >
            {isExpanded ? 'Collapse' : 'Evaluate'}
          </button>
        </div>
      </div>

      {/* Company Answer */}
      <div className="mb-4">
        <h4 className="text-sm font-medium text-gray-700 mb-2">Company Answer:</h4>
        <div className="bg-gray-50 rounded-lg p-3 text-sm text-gray-800">
          {answer?.answer || 'No answer provided'}
        </div>
      </div>

      {/* Evaluation Section */}
      {isExpanded && (
        <div className="border-t pt-4 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Evaluation Result *
            </label>
            <div className="flex space-x-3">
              <button
                onClick={() => setResult('pass')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg border ${
                  result === 'pass'
                    ? 'bg-green-50 border-green-200 text-green-800'
                    : 'border-gray-300 text-gray-700 hover:bg-gray-50'
                }`}
              >
                <CheckCircle className="h-4 w-4" />
                <span>Pass</span>
              </button>
              <button
                onClick={() => setResult('fail')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg border ${
                  result === 'fail'
                    ? 'bg-red-50 border-red-200 text-red-800'
                    : 'border-gray-300 text-gray-700 hover:bg-gray-50'
                }`}
              >
                <XCircle className="h-4 w-4" />
                <span>Fail</span>
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Reason (Optional)
            </label>
            <input
              type="text"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="Brief reason for this evaluation..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-gray-900 placeholder:text-gray-400"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Auditor Notes (Optional)
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Additional notes or recommendations..."
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-gray-900 placeholder:text-gray-400"
            />
          </div>

          <div className="flex justify-end">
            <button
              onClick={handleSubmitEvaluation}
              disabled={!result}
              className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              <Save className="h-4 w-4" />
              <span>Save Evaluation</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
} 