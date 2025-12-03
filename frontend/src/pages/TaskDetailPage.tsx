import React, { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import ReactMarkdown from 'react-markdown';
import { useNavigate, useParams } from 'react-router-dom';
import remarkGfm from 'remark-gfm';
import Timeline from '../components/Timeline';
import { Task, taskService } from '../services/taskService';

interface ModelOption {
  id: string;
  name: string;
  provider: string;
  description: string;
}

const TaskDetailPage: React.FC = () => {
  const { taskId } = useParams<{ taskId: string }>();
  const navigate = useNavigate();
  const [task, setTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(true);
  const [showModifyForm, setShowModifyForm] = useState(false);
  const [modificationRequest, setModificationRequest] = useState('');
  const [modifyLlmProvider, setModifyLlmProvider] = useState<string>('gemini');
  const [modifyModelName, setModifyModelName] = useState<string>('gemini-2.5-pro');
  const [modifyUseCustomRag, setModifyUseCustomRag] = useState<boolean>(false);
  const [availableModels, setAvailableModels] = useState<{openai: ModelOption[], gemini: ModelOption[]}>({openai: [], gemini: []});
  const [loadingModels, setLoadingModels] = useState(false);

  useEffect(() => {
    if (taskId) {
      loadTask();
      loadAvailableModels();
      const interval = setInterval(() => {
        if (task?.status === 'processing' || task?.status === 'reviewing') {
          loadTask();
        }
      }, 3000);
      return () => clearInterval(interval);
    }
  }, [taskId, task?.status]);

  const loadAvailableModels = async () => {
    setLoadingModels(true);
    setAvailableModels({
      openai: [
        { id: 'gpt-4o-mini', name: 'GPT-4o Mini', provider: 'openai', description: 'Fast and affordable' },
        { id: 'gpt-4o', name: 'GPT-4o', provider: 'openai', description: 'Most capable' },
      ],
      gemini: [
        { id: 'gemini-2.5-flash', name: 'Gemini 2.5 Flash', provider: 'gemini', description: 'Fast and efficient' },
        { id: 'gemini-2.5-pro', name: 'Gemini 2.5 Pro', provider: 'gemini', description: 'Most capable' },
      ],
    });
    setLoadingModels(false);
  };

  const loadTask = async () => {
    try {
      const data = await taskService.getTask(taskId!);
      setTask(data);
      // Remember original selections
      if (data.llm_provider) setModifyLlmProvider(data.llm_provider);
      if (data.model_name) setModifyModelName(data.model_name);
      if (data.use_custom_rag !== undefined) setModifyUseCustomRag(data.use_custom_rag);
    } catch (error) {
      toast.error('Failed to load task');
    } finally {
      setLoading(false);
    }
  };

  const handleModify = async () => {
    if (!modificationRequest.trim()) {
      toast.error('Please describe what you want to change');
      return;
    }

    try {
      await taskService.modifyTask(taskId!, { 
        modification_request: modificationRequest,
        llm_provider: modifyLlmProvider,
        model_name: modifyModelName || undefined,
        use_custom_rag: modifyUseCustomRag,
      });
      toast.success('Modification request submitted! Reviewing agent is working on it...');
      setShowModifyForm(false);
      setModificationRequest('');
      loadTask();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to modify task');
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!task) {
    return (
      <div className="card text-center">
        <p className="text-gray-500">Task not found</p>
        <button onClick={() => navigate('/')} className="btn-primary mt-4">
          Back to Tasks
        </button>
      </div>
    );
  }

  const getTimelineStages = (task: Task) => {
    const stages: Array<{
      id: string;
      name: string;
      icon: string;
      status: 'pending' | 'active' | 'completed' | 'error';
      description: string;
    }> = [
      {
        id: 'research',
        name: 'Gathering Information',
        icon: '🔍',
        status: 'pending',
        description: 'Analyzing requirements',
      },
      {
        id: 'plan',
        name: 'Creating Plan',
        icon: '📝',
        status: 'pending',
        description: 'Building your schedule',
      },
      {
        id: 'review',
        name: 'Quality Check',
        icon: '✅',
        status: 'pending',
        description: 'Refining details',
      },
      {
        id: 'complete',
        name: 'Ready',
        icon: '🎉',
        status: 'pending',
        description: 'Plan complete',
      },
    ];

    // Update stages based on task status and outputs
    if (task.status === 'processing' || task.status === 'completed') {
      if (task.research_output) {
        stages[0].status = 'completed';
        if (task.plan_output) {
          stages[1].status = 'completed';
          if (task.review_output) {
            stages[2].status = 'completed';
            if (task.status === 'completed') {
              stages[3].status = 'completed';
            } else {
              stages[3].status = 'active';
            }
          } else {
            stages[2].status = 'active';
          }
        } else {
          stages[1].status = 'active';
        }
      } else {
        stages[0].status = 'active';
      }
    } else if (task.status === 'failed') {
      // Determine which stage failed
      const activeIndex = task.research_output ? (task.plan_output ? 2 : 1) : 0;
      if (activeIndex > 0) stages[activeIndex - 1].status = 'completed';
      stages[activeIndex].status = 'error';
    }

    return stages;
  };

  const getTaskTypeInfo = (taskType: string) => {
    const taskTypes: Record<string, { icon: string; name: string; description: string }> = {
      exam_preparation: {
        icon: '📚',
        name: 'Exam Preparation',
        description: 'Structured study plan with topics, practice schedules, and revision strategies',
      },
      project_planning: {
        icon: '🚀',
        name: 'Project Planning',
        description: 'Milestone-based roadmap with tasks, timelines, and resource allocation',
      },
      learning_path: {
        icon: '🎓',
        name: 'Learning Path',
        description: 'Progressive curriculum with skill building, resources, and practice exercises',
      },
      custom: {
        icon: '✨',
        name: 'Custom Plan',
        description: 'Personalized planning based on your specific requirements and goals',
      },
    };
    return taskTypes[taskType] || taskTypes.custom;
  };

  const getStatusInfo = () => {
    if (!task) return { color: '', icon: '', message: '' };
    
    const info = {
      pending: { color: 'text-gray-600', icon: '⏳', message: 'Preparing your plan...' },
      processing: { color: 'text-blue-600', icon: '⚙️', message: 'Creating your personalized plan' },
      completed: { color: 'text-green-600', icon: '✅', message: 'Your plan is ready!' },
      failed: { color: 'text-red-600', icon: '❌', message: 'Something went wrong' },
      reviewing: { color: 'text-yellow-600', icon: '🔄', message: 'Updating your plan...' },
    };
    return info[task.status as keyof typeof info] || info.pending;
  };

  const statusInfo = getStatusInfo();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 shadow-sm">
        <button
          onClick={() => navigate('/')}
          className="text-sm text-blue-600 hover:text-blue-700 mb-3 flex items-center"
        >
          <span className="mr-1">←</span> Back to Plans
        </button>
        <div className="flex justify-between items-start">
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-gray-900">{task.title}</h1>
            <p className="mt-2 text-gray-700">{task.description}</p>
            
            {/* Task Type Info */}
            <div className="mt-4 p-3 bg-white/60 rounded-lg border border-blue-200">
              <div className="flex items-start space-x-2">
                <span className="text-2xl">{getTaskTypeInfo(task.task_type).icon}</span>
                <div>
                  <div className="font-semibold text-gray-900">{getTaskTypeInfo(task.task_type).name}</div>
                  <div className="text-sm text-gray-600">{getTaskTypeInfo(task.task_type).description}</div>
                </div>
              </div>
            </div>
            
            <div className="mt-3 flex items-center space-x-2">
              <span className={`${statusInfo.color} font-medium`}>
                {statusInfo.icon} {statusInfo.message}
              </span>
            </div>
          </div>
          {task.status === 'completed' && (
            <button
              onClick={() => setShowModifyForm(!showModifyForm)}
              className="ml-4 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium shadow-lg hover:shadow-xl transition-all"
            >
              {showModifyForm ? 'Cancel' : '✏️ Modify Plan'}
            </button>
          )}
        </div>
      </div>

      {/* Timeline with Background Work */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Progress Timeline</h2>
        <Timeline stages={getTimelineStages(task)} />
        
        {/* Expandable Background Work Details */}
        {task.status === 'completed' && (task.research_output?.content || task.plan_output?.content || task.review_output?.content) && (
          <details className="mt-6 border-t pt-6 group">
            <summary className="cursor-pointer list-none flex items-center justify-between p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg hover:from-blue-100 hover:to-indigo-100 transition-all">
              <div className="flex items-center space-x-3">
                <div className="flex items-center justify-center w-10 h-10 bg-blue-500 text-white rounded-full">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <div className="font-semibold text-gray-900">How was this plan created?</div>
                  <div className="text-xs text-gray-600 mt-0.5">View the research, planning, and review process behind your plan</div>
                </div>
              </div>
              <svg className="w-5 h-5 text-gray-500 transform transition-transform group-open:rotate-180" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </summary>
            
            <div className="mt-6 space-y-6">
              {/* Research Phase */}
              {task.research_output?.content && (
                <div className="relative pl-8 pb-6 border-l-2 border-blue-200">
                  <div className="absolute -left-3 top-0 flex items-center justify-center w-6 h-6 bg-blue-500 rounded-full ring-4 ring-white">
                    <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                  </div>
                  <div className="bg-white border border-blue-200 rounded-lg p-5 shadow-sm hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-base font-semibold text-gray-900 flex items-center">
                        <span className="mr-2">🔍</span>
                        Phase 1: Research & Analysis
                      </h3>
                      <span className="text-xs text-blue-600 font-medium bg-blue-100 px-2 py-1 rounded">Completed</span>
                    </div>
                    <p className="text-sm text-gray-600 mb-4 italic">
                      Deep analysis of your requirements, available resources, and best practices
                    </p>
                    <div className="prose prose-sm max-w-none text-gray-700 bg-gray-50 rounded p-4 max-h-96 overflow-y-auto">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {task.research_output.content}
                      </ReactMarkdown>
                    </div>
                  </div>
                </div>
              )}
              
              {/* Planning Phase */}
              {task.plan_output?.content && (
                <div className="relative pl-8 pb-6 border-l-2 border-indigo-200">
                  <div className="absolute -left-3 top-0 flex items-center justify-center w-6 h-6 bg-indigo-500 rounded-full ring-4 ring-white">
                    <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <div className="bg-white border border-indigo-200 rounded-lg p-5 shadow-sm hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-base font-semibold text-gray-900 flex items-center">
                        <span className="mr-2">📝</span>
                        Phase 2: Initial Draft Planning
                      </h3>
                      <span className="text-xs text-indigo-600 font-medium bg-indigo-100 px-2 py-1 rounded">Completed</span>
                    </div>
                    <p className="text-sm text-gray-600 mb-4 italic">
                      Structured plan creation based on research findings
                    </p>
                    <div className="prose prose-sm max-w-none text-gray-700 bg-gray-50 rounded p-4 max-h-96 overflow-y-auto">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {task.plan_output.content}
                      </ReactMarkdown>
                    </div>
                  </div>
                </div>
              )}
              
              {/* Review Phase */}
              {task.review_output?.content && (
                <div className="relative pl-8">
                  <div className="absolute -left-3 top-0 flex items-center justify-center w-6 h-6 bg-green-500 rounded-full ring-4 ring-white">
                    <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <div className="bg-white border border-green-200 rounded-lg p-5 shadow-sm hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-base font-semibold text-gray-900 flex items-center">
                        <span className="mr-2">✅</span>
                        Phase 3: Quality Review & Optimization
                      </h3>
                      <span className="text-xs text-green-600 font-medium bg-green-100 px-2 py-1 rounded">Completed</span>
                    </div>
                    <p className="text-sm text-gray-600 mb-4 italic">
                      Final review and optimization for clarity, completeness, and actionability
                    </p>
                    <div className="prose prose-sm max-w-none text-gray-700 bg-gray-50 rounded p-4 max-h-96 overflow-y-auto">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {task.review_output.content}
                      </ReactMarkdown>
                    </div>
                  </div>
                </div>
              )}
              
              {/* Completion Indicator if no review output */}
              {!task.review_output?.content && (
                <div className="relative pl-8">
                  <div className="absolute -left-3 top-0 flex items-center justify-center w-6 h-6 bg-green-500 rounded-full ring-4 ring-white">
                    <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <div className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-lg p-4">
                    <h3 className="text-sm font-semibold text-gray-900 flex items-center mb-2">
                      <span className="mr-2">✅</span>
                      Phase 3: Quality Review & Finalization
                    </h3>
                    <p className="text-xs text-gray-600">
                      The draft was reviewed, refined, and optimized to create your final plan below.
                    </p>
                  </div>
                </div>
              )}
            </div>
          </details>
        )}
      </div>

      {/* Modification Form */}
      {showModifyForm && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-xl font-semibold mb-4 text-gray-900">Request Changes</h3>
          <p className="text-sm text-gray-600 mb-4">
            Describe what you'd like to adjust in your plan. Be specific about what changes you want.
          </p>
          <textarea
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            rows={5}
            value={modificationRequest}
            onChange={(e) => setModificationRequest(e.target.value)}
            placeholder="e.g., Add more time for practice exercises, reduce the weekly study hours, focus more on data structures..."
          />

          {/* Model Picker for Modification */}
          <div className="mt-6 border-t pt-6">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              AI Model for Modification
            </label>
            <div className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-2">Provider</label>
                <div className="grid grid-cols-2 gap-3">
                  <button
                    type="button"
                    onClick={() => { setModifyLlmProvider('gemini'); setModifyModelName('gemini-2.5-pro'); }}
                    className={`p-3 border-2 rounded-lg text-left transition-all ${
                      modifyLlmProvider === 'gemini'
                        ? 'border-blue-500 bg-blue-50 shadow-md'
                        : 'border-gray-200 hover:border-blue-300'
                    }`}
                  >
                    <div className="font-medium text-sm">🤖 Google Gemini</div>
                    <div className="text-xs text-gray-500">Original: {task?.llm_provider === 'gemini' ? '✓' : ''}</div>
                  </button>
                  <button
                    type="button"
                    onClick={() => { setModifyLlmProvider('openai'); setModifyModelName('gpt-4o-mini'); }}
                    className={`p-3 border-2 rounded-lg text-left transition-all ${
                      modifyLlmProvider === 'openai'
                        ? 'border-blue-500 bg-blue-50 shadow-md'
                        : 'border-gray-200 hover:border-blue-300'
                    }`}
                  >
                    <div className="font-medium text-sm">🧠 OpenAI</div>
                    <div className="text-xs text-gray-500">Original: {task?.llm_provider === 'openai' ? '✓' : ''}</div>
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-600 mb-2">Model</label>
                {loadingModels ? (
                  <div className="text-sm text-gray-500 p-3 bg-gray-50 rounded-lg">Loading models...</div>
                ) : (
                  <select
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                    value={modifyModelName}
                    onChange={(e) => setModifyModelName(e.target.value)}
                  >
                    {availableModels[modifyLlmProvider as 'openai' | 'gemini']?.map((model) => (
                      <option key={model.id} value={model.id}>
                        {model.name} {task?.model_name === model.id ? '(Original)' : ''}
                      </option>
                    ))}
                  </select>
                )}
              </div>
            </div>
          </div>

          {/* Use Custom RAG Checkbox */}
          <div className="mt-6 border-t pt-6">
            <label className="flex items-center space-x-3 cursor-pointer">
              <input
                type="checkbox"
                checked={modifyUseCustomRag}
                onChange={(e) => setModifyUseCustomRag(e.target.checked)}
                className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
              />
              <div>
                <div className="font-medium text-gray-900">📚 Use My Custom Knowledge Base</div>
                <div className="text-xs text-gray-500">Force the AI to use only your uploaded documents for research</div>
              </div>
            </label>
          </div>

          <div className="mt-4 flex justify-end space-x-3">
            <button 
              onClick={() => setShowModifyForm(false)} 
              className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 font-medium transition-colors"
            >
              Cancel
            </button>
            <button 
              onClick={handleModify} 
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium shadow-md hover:shadow-lg transition-all"
            >
              Submit Changes
            </button>
          </div>
        </div>
      )}

      {/* Final Plan - Clean and Direct */}
      {task.status === 'completed' && task.review_output?.content && (
        <div className="bg-white rounded-lg shadow-sm p-8">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Your Plan</h2>
            <p className="text-gray-600">Here's your complete, ready-to-follow plan.</p>
          </div>
          
          <div className="prose prose-lg max-w-none prose-headings:text-gray-900 prose-p:text-gray-700 prose-strong:text-gray-900 prose-ul:text-gray-700">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {task.review_output.content}
            </ReactMarkdown>
          </div>
        </div>
      )}

      {/* Processing State */}
      {(task.status === 'processing' || task.status === 'reviewing') && (
        <div className="bg-white rounded-lg shadow-sm p-12 text-center">
          <div className="animate-spin text-6xl mb-4">⚙️</div>
          <p className="text-xl text-gray-700 font-medium">{statusInfo.message}</p>
          <p className="text-sm text-gray-500 mt-2">This usually takes 1-2 minutes...</p>
          <div className="mt-6 max-w-md mx-auto bg-gray-50 rounded-lg p-4">
            <p className="text-xs text-gray-600">
              💡 <strong>Tip:</strong> We're analyzing your requirements, creating a detailed schedule, and ensuring quality. You can close this page and come back later!
            </p>
          </div>
        </div>
      )}

      {/* Error State */}
      {task.status === 'failed' && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-8 text-center">
          <div className="text-5xl mb-4">⚠️</div>
          <h3 className="text-xl font-semibold text-red-900 mb-2">
            Something Went Wrong
          </h3>
          <p className="text-red-700 mb-6">
            We encountered an issue while creating your plan. This could be due to a temporary problem.
          </p>
          <button
            onClick={() => window.location.reload()}
            className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 font-medium shadow-md hover:shadow-lg transition-all"
          >
            Try Again
          </button>
        </div>
      )}
    </div>
  );
};

export default TaskDetailPage;
