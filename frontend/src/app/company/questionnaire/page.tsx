'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useCompanyStore } from '@/stores/company';
import { questionsApi } from '@/services/api';
import Link from 'next/link';
import { Building2, ArrowLeft, ArrowRight, FileText, Upload, Send, CheckCircle, Users, Tag } from 'lucide-react';

export default function CompanyQuestionnaire() {
  const router = useRouter();
  const {
    currentCompany,
    questions,
    setQuestions,
    answers,
    setAnswer,
    currentQuestionIndex,
    setCurrentQuestionIndex,
    getProgress,
    getCurrentQuestion,
    isQuestionCompleted,
    canSubmit,
    submitAnswers,
    isSubmitted
  } = useCompanyStore();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!mounted) return;

    if (!currentCompany) {
      router.push('/company');
      return;
    }

    if (isSubmitted) {
      router.push('/company');
      return;
    }

    loadQuestions();
  }, [mounted, currentCompany, isSubmitted, router]);

  const loadQuestions = async () => {
    try {
      setLoading(true);
      const fetchedQuestions = await questionsApi.getAll();
      setQuestions(fetchedQuestions);
    } catch (err) {
      setError('Failed to load questions');
    } finally {
      setLoading(false);
    }
  };

  const currentQuestion = getCurrentQuestion();
  const progress = getProgress();
  const currentAnswer = currentQuestion ? answers[currentQuestion._id] : null;

  const handleAnswerChange = (value: string) => {
    if (!currentQuestion) return;
    setAnswer(currentQuestion._id, value);
  };

  const navigateToQuestion = (index: number) => {
    if (index >= 0 && index < questions.length) {
      setCurrentQuestionIndex(index);
    }
  };

  const handleSubmit = async () => {
    if (!canSubmit()) return;
    submitAnswers();
    router.push('/company');
  };

  if (!mounted || loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading questionnaire...</p>
        </div>
      </div>
    );
  }

  if (error || !currentQuestion) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Questionnaire</h2>
          <p className="text-gray-600 mb-4">{error || 'No questions available'}</p>
          <Link href="/company" className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            Back to Dashboard
          </Link>
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
              <Building2 className="h-8 w-8 text-blue-600" />
              <span className="text-2xl font-bold text-gray-900">CNAV</span>
            </Link>
            <Link href="/company" className="flex items-center space-x-2 text-gray-600 hover:text-gray-900">
              <ArrowLeft className="h-4 w-4" />
              <span>Back to Dashboard</span>
            </Link>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Progress Header */}
          <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
            <h1 className="text-2xl font-bold text-gray-900 mb-4">
              Cybersecurity Compliance Questionnaire
            </h1>
            <div className="flex justify-between text-sm text-gray-600 mb-2">
              <span>Question {currentQuestionIndex + 1} of {questions.length}</span>
              <span>{progress.toFixed(0)}% Complete</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
          </div>

          <div className="grid lg:grid-cols-4 gap-6">
            {/* Question Navigation */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-lg shadow-sm border p-4">
                <h3 className="font-semibold text-gray-900 mb-4">Questions</h3>
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {questions.map((question, index) => (
                    <button
                      key={question._id}
                      onClick={() => navigateToQuestion(index)}
                      className={`w-full text-left p-2 rounded-lg text-sm transition-colors ${
                        index === currentQuestionIndex
                          ? 'bg-blue-100 text-blue-800'
                          : isQuestionCompleted(question._id)
                            ? 'bg-green-50 text-green-800'
                            : 'text-gray-600 hover:bg-gray-50'
                      }`}
                    >
                      <div className="flex items-center space-x-2">
                        <span>#{index + 1}</span>
                        {isQuestionCompleted(question._id) && (
                          <CheckCircle className="h-4 w-4 text-green-600" />
                        )}
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Main Question */}
            <div className="lg:col-span-3">
              <div className="bg-white rounded-lg shadow-sm border p-8">
                <div className="mb-6">
                  <div className="flex items-center space-x-4 mb-4">
                    <div className="bg-blue-100 px-3 py-1 rounded-full text-sm font-medium">
                      #{currentQuestionIndex + 1}
                    </div>
                    {currentQuestion.audience && (
                      <div className="flex items-center space-x-1 text-sm text-gray-500">
                        <Users className="h-4 w-4" />
                        <span>{currentQuestion.audience.join(', ')}</span>
                      </div>
                    )}
                    {currentQuestion.group_tag && (
                      <div className="flex items-center space-x-1 text-sm text-gray-500">
                        <Tag className="h-4 w-4" />
                        <span>{currentQuestion.group_tag}</span>
                      </div>
                    )}
                  </div>
                  
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">
                    {currentQuestion.question}
                  </h2>
                  
                  {currentQuestion.cyberessentials_requirement && (
                    <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 mb-4">
                      <p className="text-sm text-amber-800">
                        <strong>Requirement:</strong> {currentQuestion.cyberessentials_requirement}
                      </p>
                    </div>
                  )}
                </div>

                {/* Answer Input */}
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Your Answer *
                  </label>
                  <textarea
                    value={currentAnswer?.answer || ''}
                    onChange={(e) => handleAnswerChange(e.target.value)}
                    placeholder="Please provide your detailed answer..."
                    rows={6}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder:text-gray-400"
                  />
                </div>

                {/* Navigation */}
                <div className="flex items-center justify-between pt-6 border-t">
                  <button
                    onClick={() => navigateToQuestion(currentQuestionIndex - 1)}
                    disabled={currentQuestionIndex === 0}
                    className="flex items-center space-x-2 px-4 py-2 text-gray-600 hover:text-gray-900 disabled:opacity-50"
                  >
                    <ArrowLeft className="h-4 w-4" />
                    <span>Previous</span>
                  </button>

                  {currentQuestionIndex === questions.length - 1 ? (
                    <button
                      onClick={handleSubmit}
                      disabled={!canSubmit()}
                      className="flex items-center space-x-2 px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-300"
                    >
                      <Send className="h-4 w-4" />
                      <span>Submit Questionnaire</span>
                    </button>
                  ) : (
                    <button
                      onClick={() => navigateToQuestion(currentQuestionIndex + 1)}
                      className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                      <span>Next</span>
                      <ArrowRight className="h-4 w-4" />
                    </button>
                  )}
                </div>
              </div>

              {/* Submission Status */}
              {canSubmit() && (
                <div className="mt-4 bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-center space-x-2 text-green-800">
                    <CheckCircle className="h-5 w-5" />
                    <span className="font-medium">Ready to Submit!</span>
                  </div>
                  <p className="text-sm text-green-700 mt-1">
                    All questions answered. You can submit your questionnaire for review.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}