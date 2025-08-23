/**
 * Configuration Tab Component
 * Reddit API and LLM provider configuration forms
 */

import React, { useState, useEffect } from 'react';
import Input from '@/components/ui/Input';
import Button from '@/components/ui/Button';
import ConnectionTest from './ConnectionTest';
import { useUpdateRedditConfig, useUpdateLLMConfig, useTestConnections } from '@/hooks/useSettings';
import type { RedditConfigUpdate, LLMConfigUpdate, ConfigurationStatus } from '@/types/api';

interface ConfigurationTabProps {
  /** Current configuration status */
  configStatus?: ConfigurationStatus;
  /** Whether configuration status is loading */
  statusLoading: boolean;
  /** Function to call when configuration is saved */
  onSave?: () => void;
}

export const ConfigurationTab: React.FC<ConfigurationTabProps> = ({
  configStatus,
  statusLoading,
  onSave
}) => {
  // Form state for Reddit configuration
  const [redditConfig, setRedditConfig] = useState<RedditConfigUpdate>({
    client_id: '',
    client_secret: '',
    user_agent: 'Sentopic:v1.0 (by u/yourusername)'
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

  // Mutation hooks
  const updateRedditMutation = useUpdateRedditConfig();
  const updateLLMMutation = useUpdateLLMConfig();
  const testConnectionsMutation = useTestConnections();

  // Initialize form with current configuration status
  useEffect(() => {
    if (configStatus?.llm) {
      setLLMConfig(prev => ({
        ...prev,
        enabled: configStatus.llm.enabled,
        features: {
          ...prev.features,
          ...configStatus.llm.features
        }
      }));
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

          <div className="relative">
            <Input
              label="Client Secret"
              type={showPasswords.reddit_client_secret ? "text" : "password"}
              value={redditConfig.client_secret}
              onChange={(e) => setRedditConfig(prev => ({ ...prev, client_secret: e.target.value }))}
              placeholder="Your Reddit API Client Secret"
              fullWidth
              required
              endIcon={
                <button
                  type="button"
                  onClick={() => togglePasswordVisibility('reddit_client_secret')}
                  className="text-text-tertiary hover:text-text-primary"
                >
                  {showPasswords.reddit_client_secret ? '👁️' : '🙈'}
                </button>
              }
            />
          </div>

          <Input
            label="User Agent"
            type="text"
            value={redditConfig.user_agent}
            onChange={(e) => setRedditConfig(prev => ({ ...prev, user_agent: e.target.value }))}
            placeholder="Sentopic:v1.0 (by u/yourusername)"
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
          {/* Enable/Disable LLM */}
          <div className="flex items-center space-x-3">
            <input
              type="checkbox"
              id="llm-enabled"
              checked={llmConfig.enabled}
              onChange={(e) => setLLMConfig(prev => ({ ...prev, enabled: e.target.checked }))}
              className="rounded border-border-secondary focus:border-accent focus:ring-accent"
            />
            <label htmlFor="llm-enabled" className="font-medium text-text-primary">
              Enable AI Features
            </label>
          </div>

          {llmConfig.enabled && (
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
                  <option value="openai">OpenAI (GPT)</option>
                </select>
              </div>

              {/* Anthropic Configuration */}
              <div className="bg-panel border border-border-primary rounded-default p-4">
                <h4 className="font-medium text-text-primary mb-3">Anthropic (Claude)</h4>
                <div className="space-y-3">
                  <div className="relative">
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
                      endIcon={
                        <button
                          type="button"
                          onClick={() => togglePasswordVisibility('anthropic_api_key')}
                          className="text-text-tertiary hover:text-text-primary"
                        >
                          {showPasswords.anthropic_api_key ? '👁️' : '🙈'}
                        </button>
                      }
                    />
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
                    fullWidth
                  />
                </div>
              </div>

              {/* OpenAI Configuration */}
              <div className="bg-panel border border-border-primary rounded-default p-4">
                <h4 className="font-medium text-text-primary mb-3">OpenAI (GPT)</h4>
                <div className="space-y-3">
                  <div className="relative">
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
                      endIcon={
                        <button
                          type="button"
                          onClick={() => togglePasswordVisibility('openai_api_key')}
                          className="text-text-tertiary hover:text-text-primary"
                        >
                          {showPasswords.openai_api_key ? '👁️' : '🙈'}
                        </button>
                      }
                    />
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
                    fullWidth
                  />
                </div>
              </div>

              {/* Feature Configuration */}
              <div>
                <label className="block font-medium text-text-primary mb-3">AI Features</label>
                <div className="grid grid-cols-2 gap-3">
                  {Object.entries(llmConfig.features!).map(([feature, enabled]) => (
                    <div key={feature} className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id={`feature-${feature}`}
                        checked={enabled}
                        onChange={(e) => setLLMConfig(prev => ({
                          ...prev,
                          features: {
                            ...prev.features!,
                            [feature]: e.target.checked
                          }
                        }))}
                        className="rounded border-border-secondary focus:border-accent focus:ring-accent"
                      />
                      <label htmlFor={`feature-${feature}`} className="text-sm text-text-secondary capitalize">
                        {feature.replace('_', ' ')}
                      </label>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}

          <div className="flex justify-end">
            <Button
              type="submit"
              variant="primary"
              loading={updateLLMMutation.isPending}
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

        <div className="space-y-4">
          <ConnectionTest
            label="Reddit API"
            isConfigured={configStatus?.reddit.configured || false}
            isConnected={configStatus?.reddit.connected || false}
            error={configStatus?.reddit.error}
            isTesting={testConnectionsMutation.isPending}
            onTest={handleTestAllConnections}
          />

          {configStatus?.llm.enabled && Object.entries(configStatus.llm.providers).map(([provider, status]) => (
            <ConnectionTest
              key={provider}
              label={`${provider.charAt(0).toUpperCase() + provider.slice(1)} API`}
              isConfigured={status.configured}
              isConnected={status.connected}
              error={status.error}
              isTesting={testConnectionsMutation.isPending}
              onTest={handleTestAllConnections}
            />
          ))}
        </div>
      </section>
    </div>
  );
};

export default ConfigurationTab;