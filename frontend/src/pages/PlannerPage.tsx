import React, { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';
import { CreateTaskRequest, Task, taskService } from '../services/taskService';

interface ModelOption {
  id: string;
  name: string;
  provider: string;
  description: string;
}

const PlannerPage: React.FC = () => {
  const navigate = useNavigate();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [availableModels, setAvailableModels] = useState<{openai: ModelOption[], gemini: ModelOption[]}>({openai: [], gemini: []});
  const [loadingModels, setLoadingModels] = useState(false);
  
  const [formData, setFormData] = useState<CreateTaskRequest>({
    title: '',
    description: '',
    task_type: 'custom',
    llm_provider: 'gemini',
    model_name: 'gemini-2.5-pro',
  });
  const [useCustomRag, setUseCustomRag] = useState(false);

  useEffect(() => {
    loadTasks();
    loadAvailableModels();
  }, []);

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

  const loadTasks = async () => {
    try {
      const data = await taskService.listTasks();
      setTasks(data);
    } catch (error) {
      toast.error('Failed to load tasks');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const task = await taskService.createTask({
        ...formData,
        use_custom_rag: useCustomRag,
      });
      toast.success('Task created! Agents are working on your plan...');
      setShowForm(false);
      setFormData({
        title: '',
        description: '',
        task_type: 'custom',
        llm_provider: 'gemini',
        model_name: '',
      });
      loadTasks();
      navigate(`/task/${task.id}`);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to create task');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const badges = {
      pending: 'bg-gray-200 text-gray-800',
      processing: 'bg-blue-200 text-blue-800',
      completed: 'bg-green-200 text-green-800',
      failed: 'bg-red-200 text-red-800',
      reviewing: 'bg-yellow-200 text-yellow-800',
    };
    return badges[status as keyof typeof badges] || badges.pending;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Planning Tasks</h1>
          <p className="mt-1 text-sm text-gray-500">
            Create plans using AI-powered multi-agent system
          </p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="btn-primary"
        >
          {showForm ? 'Cancel' : '+ New Task'}
        </button>
      </div>

      {/* Creation Form */}
      {showForm && (
        <div className="card">
          <h2 className="text-2xl font-bold mb-6 text-gray-900">✨ Create Your Plan</h2>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                What do you want to accomplish?
              </label>
              <input
                type="text"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="e.g., Prepare for AWS certification, Build a mobile app, Learn React"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tell us more about your goal
                <span className="text-gray-500 text-xs ml-2">(Optional but recommended)</span>
              </label>
              <textarea
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                rows={6}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Share details like: your current level, available time, specific goals, deadlines, constraints..."
                required
              />
              <p className="text-xs text-gray-500 mt-1">
                💡 Tip: The more details you provide, the better we can tailor your plan!
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                What type of plan do you need?
              </label>
              <div className="grid grid-cols-2 md:grid-cols-2 gap-3">
                {[
                  { value: 'exam_preparation', label: 'Exam Prep', icon: '📚', desc: 'Study plans & schedules' },
                  { value: 'project_planning', label: 'Project', icon: '💼', desc: 'Project timelines' },
                  { value: 'learning_path', label: 'Learning', icon: '🎯', desc: 'Skill development' },
                  { value: 'custom', label: 'Custom', icon: '✨', desc: 'Your own plan' },
                ].map((type) => (
                  <button
                    key={type.value}
                    type="button"
                    onClick={() => setFormData({...formData, task_type: type.value})}
                    className={`p-4 border-2 rounded-lg text-left transition-all ${
                      formData.task_type === type.value
                        ? 'border-blue-500 bg-blue-50 shadow-md transform scale-105'
                        : 'border-gray-200 hover:border-blue-300 hover:shadow'
                    }`}
                  >
                    <div className="text-2xl mb-1">{type.icon}</div>
                    <div className="font-medium text-sm text-gray-900">{type.label}</div>
                    <div className="text-xs text-gray-500">{type.desc}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Model Picker */}
            <div className="border-t pt-6">
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Choose AI Model
              </label>
              <div className="space-y-3">
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-2">Provider</label>
                  <div className="grid grid-cols-2 gap-3">
                    <button
                      type="button"
                      onClick={() => setFormData({...formData, llm_provider: 'gemini', model_name: ''})}
                      className={`p-3 border-2 rounded-lg text-left transition-all ${
                        formData.llm_provider === 'gemini'
                          ? 'border-blue-500 bg-blue-50 shadow-md'
                          : 'border-gray-200 hover:border-blue-300'
                      }`}
                    >
                      <div className="font-medium text-sm">🤖 Google Gemini</div>
                      <div className="text-xs text-gray-500">Recommended</div>
                    </button>
                    <button
                      type="button"
                      onClick={() => setFormData({...formData, llm_provider: 'openai', model_name: ''})}
                      className={`p-3 border-2 rounded-lg text-left transition-all ${
                        formData.llm_provider === 'openai'
                          ? 'border-blue-500 bg-blue-50 shadow-md'
                          : 'border-gray-200 hover:border-blue-300'
                      }`}
                    >
                      <div className="font-medium text-sm">🧠 OpenAI</div>
                      <div className="text-xs text-gray-500">GPT Models</div>
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
                      value={formData.model_name}
                      onChange={(e) => setFormData({...formData, model_name: e.target.value})}
                    >
                      <option value="">Use Default Model</option>
                      {availableModels[formData.llm_provider as 'openai' | 'gemini']?.map((model) => (
                        <option key={model.id} value={model.id}>
                          {model.name} - {model.description}
                        </option>
                      ))}
                    </select>
                  )}
                  <p className="text-xs text-gray-500 mt-1">
                    💡 Default models work great for most tasks
                  </p>
                </div>
              </div>
            </div>

            {/* Use Custom RAG Data */}
            <div className="border-t pt-6">
              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={useCustomRag}
                  onChange={(e) => setUseCustomRag(e.target.checked)}
                  className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                />
                <div>
                  <div className="font-medium text-gray-900">📚 Use My Custom Knowledge Base</div>
                  <div className="text-xs text-gray-500">Force the AI to use only your uploaded documents for research</div>
                </div>
              </label>
            </div>

            <div className="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 font-medium transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading || !formData.title.trim()}
                className="px-8 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium text-lg shadow-lg hover:shadow-xl transition-all transform hover:scale-105"
              >
                {loading ? '✨ Creating Your Plan...' : '🚀 Create My Plan'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Tasks List */}
      <div className="space-y-4">
        {tasks.length === 0 ? (
          <div className="card text-center py-12">
            <p className="text-gray-500 text-lg">No tasks yet. Create your first planning task!</p>
          </div>
        ) : (
          tasks.map((task) => (
            <div
              key={task.id}
              onClick={() => navigate(`/task/${task.id}`)}
              className="card hover:shadow-lg transition-shadow cursor-pointer"
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900">{task.title}</h3>
                  <p className="mt-1 text-sm text-gray-600 line-clamp-2">{task.description}</p>
                  <div className="mt-2 flex items-center space-x-4 text-sm text-gray-500">
                    <span>📅 {new Date(task.created_at).toLocaleDateString()}</span>
                    <span>📝 {task.task_type.replace('_', ' ')}</span>
                  </div>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusBadge(task.status)}`}>
                  {task.status}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default PlannerPage;
