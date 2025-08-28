/**
 * Configuration Tab Component
 * Reddit API and LLM provider configuration forms
 */

import React, { useState, useEffect } from 'react';
import Input from '@/components/ui/Input';
import Button from '@/components/ui/Button';
import { ConfirmModal } from '@/components/ui/Modal';
import ConnectionTest from './ConnectionTest';
import { Eye, EyeOff } from 'lucide-react';
import type { RedditConfigUpdate, LLMConfigUpdate, ConfigurationStatus } from '@/types/api';
import { useUpdateRedditConfig, useUpdateLLMConfig, useTestConnections, useClearAllData, useResetConfiguration } from '@/hooks/useSettings';

interface ConfigurationTabProps {
    /** Current configuration status */
    configStatus?: ConfigurationStatus;
    /** Whether configuration status is loading */
    statusLoading: boolean;
    /** Function to call when configuration is saved */
    onSave?: () => void;
    /** Function to call when operations are completed */
    onOperationComplete?: () => void;
  }

export const ConfigurationTab: React.FC<ConfigurationTabProps> = ({
  configStatus,
  statusLoading,
  onSave,
  onOperationComplete
}) => {
  // Form state for Reddit configuration
    const [redditConfig, setRedditConfig] = useState<RedditConfigUpdate>({
        client_id: '',
        client_secret: '',
        user_agent: 'Sentopic (by u/yourusername)'
    });

  // Form state for LLM configuration
  const [llmConfig, setLLMConfig] = useState<LLMConfigUpdate>({
    enabled: false,
    default_provider: 'anthropic',
    providers: {
      anthropic: {
        api_key: '',
        model: 'claude-3-5-sonnet-20240620',
        max_tokens: 4000,
        temperature: 0.1
      },
      openai: {
        api_key: '',
        model: 'gpt-4o',
        max_tokens: 4000,
        temperature: 0.1
      }
    },
    features: {
      keyword_suggestion: true,
      summarization: true,
      rag_search: true,
      chat_agent: true
    },
    embeddings: {
      provider: 'openai',
      model: 'text-embedding-3-small',
      storage: 'sqlite'
    }
  });

  // Password visibility state
  const [showPasswords, setShowPasswords] = useState<Record<string, boolean>>({
    reddit_client_secret: false,
    anthropic_api_key: false,
    openai_api_key: false
  });

  // Modal state for confirmation dialogs
  const [showClearDataModal, setShowClearDataModal] = useState(false);
  const [showResetConfigModal, setShowResetConfigModal] = useState(false);

  // Mutation hooks
  const updateRedditMutation = useUpdateRedditConfig();
  const updateLLMMutation = useUpdateLLMConfig();
  const testConnectionsMutation = useTestConnections();
  const clearDataMutation = useClearAllData();
  const resetConfigMutation = useResetConfiguration();

  // Initialize form with current configuration status
  useEffect(() => {
    if (configStatus) {
      // Load Reddit configuration
      if (configStatus.reddit?.current_config) {
        const { current_config } = configStatus.reddit;
        setRedditConfig(prev => ({
          ...prev,
          client_id: current_config.client_id || '',
          client_secret: current_config.client_secret || '',
          user_agent: current_config.user_agent || 'Sentopic (by u/yourusername)',
        }));
      }

      // Load LLM configuration
      if (configStatus.llm) {
        const newLLMConfig: LLMConfigUpdate = {
          enabled: configStatus.llm.enabled,
          default_provider: configStatus.llm.current_config?.default_provider || 'anthropic',
          providers: {
            anthropic: {
              api_key: configStatus.llm.current_config?.providers?.anthropic?.api_key || '',
              model: configStatus.llm.current_config?.providers?.anthropic?.model || 'claude-3-5-sonnet-20240620',
              max_tokens: configStatus.llm.current_config?.providers?.anthropic?.max_tokens || 4000,
              temperature: configStatus.llm.current_config?.providers?.anthropic?.temperature || 0.1
            },
            openai: {
              api_key: configStatus.llm.current_config?.providers?.openai?.api_key || '',
              model: configStatus.llm.current_config?.providers?.openai?.model || 'gpt-4o',
              max_tokens: configStatus.llm.current_config?.providers?.openai?.max_tokens || 4000,
              temperature: configStatus.llm.current_config?.providers?.openai?.temperature || 0.1
            }
          },
          features: {
            keyword_suggestion: true,
            summarization: true,
            rag_search: true,
            chat_agent: true
          },
          embeddings: {
            provider: 'openai',
            model: 'text-embedding-3-small',
            storage: 'sqlite'
          }
        };

        setLLMConfig(newLLMConfig);
      }
    }
  }, [configStatus]);

  const togglePasswordVisibility = (field: string) => {
    setShowPasswords(prev => ({
      ...prev,
      [field]: !prev[field]
    }));
  };

  const handleRedditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      await updateRedditMutation.mutateAsync(redditConfig);
      onSave?.();
    } catch (error) {
      // Error handling is managed by the mutation
      console.error('Failed to update Reddit config:', error);
    }
  };

  const handleLLMSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      await updateLLMMutation.mutateAsync(llmConfig);
      onSave?.();
    } catch (error) {
      // Error handling is managed by the mutation
      console.error('Failed to update LLM config:', error);
    }
  };

  const handleTestAllConnections = () => {
    testConnectionsMutation.mutate();
  };

  const handleClearAllData = async () => {
    try {
      await clearDataMutation.mutateAsync();
      setShowClearDataModal(false);
      onOperationComplete?.();
    } catch (error) {
      // Error handling is managed by the mutation
      console.error('Failed to clear data:', error);
    }
  };

  const handleResetConfiguration = async () => {
    try {
      await resetConfigMutation.mutateAsync();
      setShowResetConfigModal(false);
      onOperationComplete?.();
    } catch (error) {
      // Error handling is managed by the mutation
      console.error('Failed to reset configuration:', error);
    }
  };

  // Validation function for LLM configuration
  const isLLMConfigValid = () => {
    // Check if at least one provider has all required fields filled
    const anthropicValid = llmConfig.providers.anthropic.api_key.trim() !== '' && 
                          llmConfig.providers.anthropic.model.trim() !== '';
    
    const openaiValid = llmConfig.providers.openai.api_key.trim() !== '' && 
                       llmConfig.providers.openai.model.trim() !== '';
    
    // At least one provider must be fully configured
    return anthropicValid || openaiValid;
  };

  return (
    <div className="space-y-8">
      {/* Reddit API Configuration */}
      <section>
        <div className="mb-4">
          <h3 className="font-subsection text-text-primary mb-2">Reddit API Configuration</h3>
          <p className="font-body text-text-secondary">
            Configure your Reddit API credentials to enable data collection from Reddit.
          </p>
        </div>

        <form onSubmit={handleRedditSubmit} className="space-y-4">
          <Input
            label="Client ID"
            type="text"
            value={redditConfig.client_id}
            onChange={(e) => setRedditConfig(prev => ({ ...prev, client_id: e.target.value }))}
            placeholder="Your Reddit API Client ID"
            fullWidth
            required
          />

            <div>
            <Input
              label="Client Secret"
              type={showPasswords.reddit_client_secret ? "text" : "password"}
              value={redditConfig.client_secret}
              onChange={(e) => setRedditConfig(prev => ({ ...prev, client_secret: e.target.value }))}
              placeholder="Your Reddit API Client Secret"
              fullWidth
              required
            />
            <div className="flex justify-end mt-1">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => togglePasswordVisibility('reddit_client_secret')}
                className="text-text-tertiary hover:text-text-primary"
              >
                {showPasswords.reddit_client_secret ? 'HIDE' : 'SHOW'}
              </Button>
            </div>
          </div>

          <Input
            label="User Agent"
            type="text"
            value={redditConfig.user_agent}
            onChange={(e) => setRedditConfig(prev => ({ ...prev, user_agent: e.target.value }))}
            placeholder="Sentopic (by u/yourusername)"
            helpText="Include your Reddit username for better API compliance"
            fullWidth
            required
          />

          <div className="flex justify-end">
            <Button
              type="submit"
              variant="primary"
              loading={updateRedditMutation.isPending}
              disabled={!redditConfig.client_id || !redditConfig.client_secret || !redditConfig.user_agent}
            >
              Save Reddit Configuration
            </Button>
          </div>

          {/* Display success/error messages */}
          {updateRedditMutation.isSuccess && (
            <div className="p-3 bg-green-50 border border-green-200 rounded-input">
              <p className="font-small text-success">Reddit configuration saved successfully!</p>
            </div>
          )}
          {updateRedditMutation.isError && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-input">
              <p className="font-small text-danger">
                Failed to save Reddit configuration: {updateRedditMutation.error?.message}
              </p>
            </div>
          )}
        </form>
      </section>

      {/* LLM Configuration */}
      <section>
        <div className="mb-4">
          <h3 className="font-subsection text-text-primary mb-2">LLM Configuration</h3>
          <p className="font-body text-text-secondary">
            Configure AI language model providers for advanced features like keyword suggestions and chat.
          </p>
        </div>

        <form onSubmit={handleLLMSubmit} className="space-y-6">
            <>
              {/* Default Provider Selection */}
              <div>
                <label className="block font-medium text-text-primary mb-2">Default Provider</label>
                <select
                  value={llmConfig.default_provider}
                  onChange={(e) => setLLMConfig(prev => ({ ...prev, default_provider: e.target.value }))}
                  className="w-full px-3 py-2 border border-border-secondary rounded-input focus:border-accent focus:ring-accent bg-content"
                >
                  <option value="anthropic">Anthropic (Claude)</option>
                  <option value="openai">OpenAI (ChatGPT)</option>
                </select>
              </div>

              {/* Anthropic Configuration */}
              <div className="bg-panel border border-border-primary rounded-default p-4">
                <h4 className="font-medium text-text-primary mb-3">Anthropic (Claude)</h4>
                <div className="space-y-3">
                <div>
                    <Input
                      label="API Key"
                      type={showPasswords.anthropic_api_key ? "text" : "password"}
                      value={llmConfig.providers.anthropic.api_key}
                      onChange={(e) => setLLMConfig(prev => ({
                        ...prev,
                        providers: {
                          ...prev.providers,
                          anthropic: { ...prev.providers.anthropic, api_key: e.target.value }
                        }
                      }))}
                      placeholder="sk-ant-api03-..."
                      fullWidth
                    />
                    <div className="flex justify-end mt-1">
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => togglePasswordVisibility('anthropic_api_key')}
                        className="text-text-tertiary hover:text-text-primary"
                      >
                        {showPasswords.anthropic_api_key ? 'HIDE' : 'SHOW'}
                      </Button>
                    </div>
                  </div>
                  <Input
                    label="Model"
                    type="text"
                    value={llmConfig.providers.anthropic.model}
                    onChange={(e) => setLLMConfig(prev => ({
                      ...prev,
                      providers: {
                        ...prev.providers,
                        anthropic: { ...prev.providers.anthropic, model: e.target.value }
                      }
                    }))}
                    placeholder="e.g., claude-3-5-sonnet-20240620, claude-3-5-haiku-20241022, claude-3-opus-20240229"
                    fullWidth
                  />
                </div>
              </div>

              {/* OpenAI Configuration */}
              <div className="bg-panel border border-border-primary rounded-default p-4">
                <h4 className="font-medium text-text-primary mb-3">OpenAI (ChatGPT)</h4>
                <div className="space-y-3">
                <div>
                    <Input
                      label="API Key"
                      type={showPasswords.openai_api_key ? "text" : "password"}
                      value={llmConfig.providers.openai.api_key}
                      onChange={(e) => setLLMConfig(prev => ({
                        ...prev,
                        providers: {
                          ...prev.providers,
                          openai: { ...prev.providers.openai, api_key: e.target.value }
                        }
                      }))}
                      placeholder="sk-..."
                      fullWidth
                    />
                    <div className="flex justify-end mt-1">
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => togglePasswordVisibility('openai_api_key')}
                        className="text-text-tertiary hover:text-text-primary"
                      >
                        {showPasswords.openai_api_key ? 'HIDE' : 'SHOW'}
                      </Button>
                    </div>
                  </div>
                  <Input
                    label="Model"
                    type="text"
                    value={llmConfig.providers.openai.model}
                    onChange={(e) => setLLMConfig(prev => ({
                      ...prev,
                      providers: {
                        ...prev.providers,
                        openai: { ...prev.providers.openai, model: e.target.value }
                      }
                    }))}
                    placeholder="e.g., gpt-4o, gpt-4o-mini, gpt-4-turbo, o1-preview, o1-mini"
                    fullWidth
                  />
                </div>
                </div>
            </>

            <div className="flex justify-end">
            <Button
              type="submit"
              variant="primary"
              loading={updateLLMMutation.isPending}
              disabled={!isLLMConfigValid()}
            >
              Save LLM Configuration
            </Button>
          </div>

          {/* Display success/error messages */}
          {updateLLMMutation.isSuccess && (
            <div className="p-3 bg-green-50 border border-green-200 rounded-input">
              <p className="font-small text-success">LLM configuration saved successfully!</p>
            </div>
          )}
          {updateLLMMutation.isError && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-input">
              <p className="font-small text-danger">
                Failed to save LLM configuration: {updateLLMMutation.error?.message}
              </p>
            </div>
          )}
        </form>
      </section>

      {/* Connection Tests */}
      <section>
      <div className="mb-4">
          <h3 className="font-subsection text-text-primary mb-2">Connection Tests</h3>
          <p className="font-body text-text-secondary">
            Test your API connections to ensure everything is working properly.
          </p>
        </div>

        <div className="space-y-3 mb-4">
          <ConnectionTest
            label="Reddit API"
            isConfigured={configStatus?.reddit.configured || false}
            isConnected={configStatus?.reddit.connected || false}
            error={configStatus?.reddit.error}
            isTesting={testConnectionsMutation.isPending}
            onTest={() => {}}
            showTestButton={false}
          />

          {configStatus?.llm.enabled && Object.entries(configStatus.llm.providers).map(([provider, status]) => (
            <ConnectionTest
              key={provider}
              label={provider === 'openai' ? 'OpenAI API' : `${provider.charAt(0).toUpperCase() + provider.slice(1)} API`}
              isConfigured={status.configured}
              isConnected={status.connected}
              error={status.error}
              isTesting={testConnectionsMutation.isPending}
              onTest={() => {}}
              showTestButton={false}
            />
          ))}
        </div>

        <div className="flex justify-end">
        <Button
            variant="secondary"
            onClick={handleTestAllConnections}
            loading={testConnectionsMutation.isPending}
            className="px-6"
            >
            Test All Connections
            </Button>
        </div>
        </section>

        {/* Data Management Section */}
        <section>
        <div className="mb-4">
            <h3 className="font-subsection text-text-primary mb-2">Data Management</h3>
            <p className="font-body text-text-secondary">
            Manage your application data and reset options. These operations cannot be undone.
            </p>
        </div>

        <div className="space-y-4">
            {/* Clear All Data */}
            <div className="bg-content border border-border-primary rounded-default p-6">
            <div className="flex items-start justify-between">
                <div className="flex-1 mr-4">
                <h4 className="font-medium text-text-primary mb-2">Clear All Data</h4>
                <p className="font-body text-text-secondary mb-2">
                    Permanently delete all projects, analysis sessions, Reddit collections, chat history, 
                    and AI summaries from the application.
                </p>
                <p className="font-small text-danger">
                    ⚠️ This will delete all your research data and cannot be undone.
                </p>
                </div>
                <Button
                variant="danger"
                onClick={() => setShowClearDataModal(true)}
                disabled={clearDataMutation.isPending}
                >
                Clear All Data
                </Button>
            </div>

            {/* Success/Error Messages */}
            {clearDataMutation.isSuccess && (
                <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-input">
                <p className="font-small text-success">
                    All application data has been cleared successfully.
                </p>
                </div>
            )}
            {clearDataMutation.isError && (
                <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-input">
                <p className="font-small text-danger">
                    Failed to clear data: {clearDataMutation.error?.message}
                </p>
                </div>
            )}
            </div>

            {/* Reset Configuration */}
            <div className="bg-content border border-border-primary rounded-default p-6">
            <div className="flex items-start justify-between">
                <div className="flex-1 mr-4">
                <h4 className="font-medium text-text-primary mb-2">Reset Configuration</h4>
                <p className="font-body text-text-secondary mb-2">
                    Reset all configuration settings to their default values. This will clear all API keys 
                    and restore the application to its initial state.
                </p>
                <p className="font-small text-warning">
                    ⚠️ You will need to reconfigure your API keys after this operation.
                </p>
                </div>
                <Button
                variant="secondary"
                onClick={() => setShowResetConfigModal(true)}
                disabled={resetConfigMutation.isPending}
                >
                Reset Settings
                </Button>
            </div>

            {/* Success/Error Messages */}
            {resetConfigMutation.isSuccess && (
                <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-input">
                <p className="font-small text-success">
                    Configuration has been reset to defaults successfully.
                </p>
                </div>
            )}
            {resetConfigMutation.isError && (
                <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-input">
                <p className="font-small text-danger">
                    Failed to reset configuration: {resetConfigMutation.error?.message}
                </p>
                </div>
            )}
            </div>
        </div>
        </section>

        {/* Clear Data Confirmation Modal */}
        <ConfirmModal
        isOpen={showClearDataModal}
        onClose={() => setShowClearDataModal(false)}
        onConfirm={handleClearAllData}
        title="Clear All Data"
        message="Are you sure you want to delete all projects, collections, chat history, and analysis data? This action cannot be undone."
        confirmText="Delete All Data"
        cancelText="Cancel"
        variant="danger"
        />

        {/* Reset Configuration Confirmation Modal */}
        <ConfirmModal
        isOpen={showResetConfigModal}
        onClose={() => setShowResetConfigModal(false)}
        onConfirm={handleResetConfiguration}
        title="Reset Configuration"
        message="Are you sure you want to reset all settings to defaults? This will clear all your API keys and configuration. A backup will be created automatically."
        confirmText="Reset Settings"
        cancelText="Cancel"
        variant="warning"
        />

    </div>
  );
};

export default ConfigurationTab;