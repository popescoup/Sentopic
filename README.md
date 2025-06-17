# Sentopic - Reddit Analytics Tool

A comprehensive Reddit analytics tool with AI-powered insights. This project combines Reddit data collection, sentiment analysis, keyword tracking, and LLM-powered features for intelligent data exploration.

## Features

### Phase 1: Data Collection
- Collect posts and comments from Reddit using PRAW
- Configurable collection parameters (subreddit, sort method, limits)
- SQLite storage with comprehensive metadata
- Rate limiting and error handling

### Phase 2: Analytics Engine  
- Keyword extraction and tracking
- Sentiment analysis using VADER
- Co-occurrence detection and analysis
- Trend analysis over time
- Interactive CLI for data exploration

### Phase 3: LLM Integration (NEW)
- **AI-Powered Keyword Suggestions**: Describe your research goal and get relevant keywords automatically
- **Intelligent Analysis Summaries**: Get AI-generated insights that explain what your data means
- **Interactive Chat Agent**: Ask questions about your data using natural language
- **Semantic Search**: Find related content using AI embeddings, not just exact keywords
- **Multiple AI Providers**: Support for Anthropic Claude, OpenAI GPT, and local models

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Reddit API Credentials

1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Choose "script" as the app type
4. Note down your `client_id` (under the app name) and `client_secret`

### 3. Get LLM API Keys (Optional but Recommended)

**For Anthropic Claude:**
1. Visit https://console.anthropic.com/
2. Create an account and get your API key

**For OpenAI:**
1. Visit https://platform.openai.com/api-keys
2. Create an account and get your API key

### 4. Configure API Credentials

**⚠️ Important: Never commit your actual API credentials to version control!**

1. Copy the example configuration file:
   ```bash
   cp config.example.json config.json
   ```

2. Edit `config.json` with your actual credentials:
   ```json
   {
       "reddit": {
           "client_id": "YOUR_ACTUAL_CLIENT_ID",
           "client_secret": "YOUR_ACTUAL_CLIENT_SECRET",
           "user_agent": "Sentopic:v1.0 (by u/yourusername)"
       },
       "llm": {
           "enabled": true,
           "default_provider": "anthropic",
           "providers": {
               "anthropic": {
                   "api_key": "YOUR_ANTHROPIC_API_KEY",
                   "model": "claude-3-5-sonnet-20240620",
                   "max_tokens": 4000,
                   "temperature": 0.1
               },
               "openai": {
                   "api_key": "YOUR_OPENAI_API_KEY",
                   "model": "gpt-4o",
                   "max_tokens": 4000,
                   "temperature": 0.1
               }
           },
           "features": {
               "keyword_suggestion": true,
               "summarization": true,
               "rag_search": true,
               "chat_agent": true
           },
           "embeddings": {
               "provider": "openai",
               "model": "text-embedding-3-small",
               "storage": "sqlite"
           }
       }
   }
   ```

**Note**: The `config.json` file is included in `.gitignore` to protect your API credentials.

### 5. LLM Configuration Options

**Provider Options:**
- **anthropic**: Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Haiku
- **openai**: GPT-4o, GPT-4 Turbo, GPT-3.5 Turbo

**Embedding Options:**
- **openai**: Uses OpenAI's embedding models (requires OpenAI API key)
- **local**: Uses local sentence-transformer models (no API key needed, runs offline)

**Feature Toggles:**
- **keyword_suggestion**: AI suggests keywords based on your research description
- **summarization**: AI generates summaries of analysis results
- **rag_search**: Semantic search through your collected data
- **chat_agent**: Interactive AI chat for data exploration

## Usage

### Data Collection

**Interactive Collection:**
```bash
python main.py
```

**View Collection History:**
```bash
python main.py --list
```

### Analytics

**Run Analysis with AI Features:**
```bash
python main.py --analyze
```

**View Analysis Sessions:**
```bash
python main.py --sessions
```

**View Session Results:**
```bash
python main.py --results <session_id>
```

**View Trends Analysis:**
```bash
python main.py --trends <session_id>
```

### LLM Features (Phase 3)

**Test LLM Configuration:**
```bash
python main.py --test-llm
```

**Get AI Keyword Suggestions:**
```bash
python main.py --suggest-keywords "analyze iPhone battery complaints"
```

**Chat with Your Data:**
```bash
python main.py --chat <session_id>
```

**Help:**
```bash
python main.py --help
```

## Database Schema

The SQLite database (`sentopic.db`) contains tables for:

**Phase 1 - Collection:**
- **collections**: Collection configuration and metadata
- **posts**: Reddit posts with full metadata  
- **comments**: Reddit comments with hierarchy information

**Phase 2 - Analytics:**
- **analysis_sessions**: Analysis configuration and results
- **keyword_mentions**: Individual keyword occurrences with sentiment
- **keyword_stats**: Aggregated statistics per keyword
- **keyword_cooccurrences**: Keyword co-occurrence relationships

**Phase 3 - LLM:**
- **llm_summaries**: AI-generated analysis summaries
- **content_embeddings**: Vector embeddings for semantic search
- **chat_sessions**: AI chat conversation sessions
- **chat_messages**: Individual chat messages and AI responses

## AI-Powered Workflow

1. **Describe Your Research**: "I want to analyze sentiment about electric vehicle charging issues"

2. **Get AI Keyword Suggestions**: The AI suggests relevant keywords like "EV charging", "charging stations", "battery range", etc.

3. **Run Analysis**: Collect and analyze Reddit data for those keywords

4. **Get AI Summary**: Receive an intelligent summary explaining what the data reveals about your research question

5. **Interactive Exploration**: Chat with the AI to dig deeper, ask follow-up questions, and explore unexpected findings

6. **Semantic Search**: Find related discussions even when they don't use your exact keywords

## Comment Collection Strategy

- Collects up to N root comments per post (direct replies to the post)
- For each root comment, collects up to M replies  
- All comments must meet the minimum upvote threshold
- Preserves comment hierarchy with `parent_id` and `is_root` fields

## Rate Limiting & Cost Management

**Reddit API:**
- 1-second delay between requests
- Graceful error handling for API issues
- Progress bars show collection status

**LLM APIs:**
- Automatic retry logic with exponential backoff
- Token usage tracking and cost estimation
- Support for multiple providers with fallback
- Configurable rate limits and timeouts

## Security Notes

- API credentials are stored in `config.json` which is excluded from version control
- The database file (`sentopic.db`) is also excluded as it may contain user data
- Always keep your Reddit and LLM API credentials secure and never share them publicly
- LLM features can be disabled entirely by setting `"enabled": false` in the LLM config

## Cost Considerations

**LLM API Costs:**
- Anthropic Claude: ~$15-75 per 1M tokens depending on model
- OpenAI GPT: ~$2-60 per 1M tokens depending on model
- OpenAI Embeddings: ~$0.02-0.13 per 1M tokens depending on model

**Local Alternatives:**
- Use `"provider": "local"` for embeddings to avoid API costs
- Sentence-transformer models run locally without API calls
- Some features like summarization require cloud LLM APIs

## Troubleshooting

**LLM Not Working:**
```bash
# Test your LLM configuration
python main.py --test-llm

# Check if required packages are installed
pip install anthropic openai sentence-transformers
```

**Reddit API Issues:**
- Verify your Reddit API credentials in `config.json`
- Check if your Reddit app is configured as "script" type
- Ensure your user agent string is descriptive

**Performance:**
- For large datasets, consider using local embeddings instead of OpenAI
- Semantic search performance depends on the number of stored embeddings
- Use collection filtering to limit analysis scope

## Integration with Future Phases

This Phase 3 implementation is designed to integrate seamlessly with:
- **Phase 4**: FastAPI backend will import these modules directly for web interface
- **Advanced Analytics**: LLM-powered trend prediction and anomaly detection
- **Visualization**: AI-generated insights for data visualization components

The modular architecture ensures all LLM features can be easily disabled or swapped out while maintaining full compatibility with the existing analytics workflow.