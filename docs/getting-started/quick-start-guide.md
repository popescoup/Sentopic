# Sentopic Quick Start Guide

## Welcome to Sentopic

Sentopic transforms Reddit discussions into actionable business intelligence. This guide will get you from installation to your first insights in about 30 minutes.

---

## Your First 30 Minutes

### Step 1: Configure API Access (5 minutes)

Before collecting data, you need to set up your Reddit API credentials and optionally configure AI features.

#### Reddit API Setup (Required)

1. **Create a Reddit App**
   - Visit [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps) and sign in
   - Click **"create another app..."**
   - Fill out the form:
     - **Name**: Any name (e.g., "Sentopic Research")
     - **App type**: Select **"script"** (important!)
     - **Redirect URI**: `http://localhost`
   - Click **"create app"**

2. **Gather Your Credentials**
   - **Client ID**: String under your app name
   - **Client Secret**: Longer string labeled "secret"
   - **User Agent**: Create in format `AppName/1.0 by /u/YourUsername`

3. **Enter in Sentopic**
   - Open Sentopic → **Settings** (gear icon)
   - Navigate to **Configuration** tab
   - Enter your Reddit credentials
   - Click **"Test Reddit Connection"** to verify

#### AI Provider Setup (Recommended)

For keyword suggestions, analysis summaries, and the chat assistant:

**Choose One:**
- **Anthropic**: [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys)
- **OpenAI**: [platform.openai.com/settings/organization/api-keys](https://platform.openai.com/settings/organization/api-keys)

Create an account, add billing, generate an API key, then enter it in **Settings → Configuration → LLM Provider**.

---

### Step 2: Create Your First Collection (10 minutes)

Collections gather Reddit posts and comments for analysis. Let's start with a focused example.

#### Recommended First Collection

**Goal**: Collect recent technology discussions to understand trends and sentiment

**Parameters:**
- **Subreddit**: r/technology
- **Sort Method**: Top
- **Time Period**: Year
- **Posts**: 100
- **Root Comments**: 5 per post
- **Replies**: 3 per root comment
- **Min Upvotes**: 10

**Why these parameters?**
- Small enough to complete quickly (~5 minutes)
- Large enough to provide meaningful insights
- Quality filter ensures substantive discussions

#### Creating the Collection

1. Click **"Collection Manager"** in the header
2. Click **"New Collection"**
3. Enter the parameters above
4. Click **"Start Collection"**
5. Monitor progress in real-time

**What's happening**: Sentopic is querying Reddit's API to gather posts and their comment threads. The API has rate limits, so larger collections take longer.

---

### Step 3: Create Your First Project (10 minutes)

Projects analyze your collections to answer specific research questions.

#### Example Project: Technology Trends Analysis

**Research Question**: "What technology trends are people most excited or concerned about?"

**Recommended Keywords**:
- AI
- machine learning
- privacy
- security
- cloud computing

**Why these keywords?**
- Focused yet meaningful scope
- Likely to appear in tech discussions
- Capture different aspects (innovation, concerns, infrastructure)

#### Creating the Project

1. Return to **Projects Dashboard**
2. Click **"New Project"**
3. Enter your research question
4. Add your keywords (or use **"AI Suggest Keywords"** for ideas)
5. Select your r/technology collection
6. Configure options:
   - **Partial Matching**: Enable (captures variations like "AI-powered", "privacy-focused")
   - **Context Window**: 100 words (balanced view)
   - **Generate Summary**: Enable (requires AI provider)
7. Click **"Create Project"**

**Analysis time**: About 15 seconds for 100 posts with 5 keywords

---

### Step 4: Explore Your Results (5 minutes)

Once analysis completes, explore your findings:

#### Understanding the Dashboard

**Keyword Overview**
- Total mentions across all keywords
- Distribution by keyword
- Click to see detailed breakdown per keyword

**Keyword Relationships**
- Shows which keywords appear together
- Network visualization of connections
- Identifies themes and associations
- Click edges to explore discussions containing both keywords

**Keyword Trends**
- How mention frequency changes over time
- Rising (↗), stable (→), or falling (↘) indicators
- Multiple keyword comparison

**Recent Discussions**
- Sample posts and comments containing your keywords
- Highlighted keywords in context
- Sentiment scores for each mention
- Click **"Explore All Mentions"** to filter and search

**AI Summary** (if enabled)
- Business-focused analysis of findings
- Key themes and patterns
- Pain points and opportunities
- Competitive insights

#### Using the AI Chat Assistant

Ask natural language questions about your data:
- "What are the main concerns about AI in these discussions?"
- "Which keywords have the most negative sentiment?"
- "What themes appear with 'privacy' mentions?"
- "Compare sentiment between 'AI' and 'machine learning'"

The assistant searches your data and provides evidence-based answers.

---

## Key Concepts

### Collections vs Projects

**Collections** = Raw data from Reddit
- Gather posts and comments from specific subreddits
- Reusable across multiple projects
- Think of them as your research library

**Projects** = Analysis and insights
- Apply keywords to collections
- Generate sentiment scores and relationships
- Answer specific research questions
- Can use multiple collections

### Sentiment Scores

Sentopic analyzes the emotional tone of each keyword mention:

- **+0.3 to +1.0**: Positive (praise, satisfaction, recommendations)
- **-0.3 to +0.3**: Neutral (factual, mixed, balanced)
- **-0.3 to -1.0**: Negative (criticism, complaints, concerns)

**Business interpretation**:
- Highly positive (+0.7+): Strong advocacy, feature requests
- Neutral: Factual discussions, comparisons
- Highly negative (-0.7+): Major pain points, urgent issues

### Keyword Strategy

**Start Focused, Then Expand**

Good first project: 3-5 specific keywords
- AI, machine learning, privacy

Avoid: 15+ broad keywords
- technology, computer, internet, software, hardware... (too generic)

**Why?** Focused keywords produce clearer insights. Use findings from one project to inform the next - this is an iterative research process.

### Iterative Research Methodology

Effective analysis involves multiple projects that build on each other:

1. **Initial exploration**: Broad keywords, discover patterns
2. **Analyze co-occurrences**: Find unexpected keyword relationships
3. **Drill deeper**: Create targeted follow-up projects
4. **Refine understanding**: Iterate based on findings

**Example progression**:
- Project 1: General tech sentiment (5 keywords)
- Discovery: "AI" and "privacy" frequently co-occur with negative sentiment
- Project 2: Focus on AI privacy concerns (targeted keywords)
- Discovery: Specific concern around facial recognition
- Project 3: Deep dive into facial recognition discussions

---

## Common Beginner Mistakes

### ❌ Too Many Broad Keywords
**Problem**: "technology, software, internet, computer, device, digital, online, app, program..."
- Overwhelming results
- Diluted insights
- Processing takes longer

**Solution**: Start with 3-5 focused keywords relevant to your specific question

### ❌ Collecting Too Much Data Initially
**Problem**: First collection = 5 subreddits × 1000 posts each
- Takes hours to collect
- Long wait before you can experiment
- May hit API rate limits

**Solution**: Start small (100-500 posts), validate your approach, then scale up

### ❌ Wrong Subreddit Selection
**Problem**: Analyzing gaming sentiment using r/technology instead of gaming subreddits
- Irrelevant discussions
- Low keyword match rate
- Wasted collection time

**Solution**: Choose subreddits where your target audience actually discusses your topics

### ❌ Ignoring Context Windows
**Problem**: Setting context window to 20 words
- Too narrow for understanding
- Misses important surrounding context
- Less accurate sentiment analysis

**Solution**: Use 80-120 words for balanced context that captures full meaning

### ❌ Not Reading Actual Examples
**Problem**: Only looking at aggregate statistics
- Miss nuance and context
- Can't validate AI insights
- Overlook important patterns

**Solution**: Always review sample discussions to validate findings

---

## Success Checklist

After your first 30 minutes, you should have:

- ✅ Reddit API configured and tested
- ✅ AI provider configured (optional but recommended)
- ✅ One completed collection with real data
- ✅ One analyzed project with results
- ✅ Understanding of sentiment scores and insights
- ✅ Explored keyword relationships and trends
- ✅ Used the AI chat assistant to ask questions

---

## Next Steps

### Expand Your Research

1. **Create Additional Collections**
   - Try different subreddits relevant to your domain
   - Experiment with time periods (month, year, all-time)
   - Compare different sorting methods (hot, top, new)

2. **Refine Your Keywords**
   - Use co-occurrence findings to discover new relevant terms
   - Create follow-up projects targeting specific themes
   - Compare sentiment across different keyword variations

3. **Leverage AI Features**
   - Use keyword suggestions for new research angles
   - Ask the chat assistant complex analytical questions
   - Generate summaries for stakeholder reports

### Best Practices

**Collection Strategy**
- Start with 1-2 subreddits per collection
- Use consistent time periods within a project to avoid bias
- Set reasonable minimum upvote thresholds (10-50) to filter quality

**Keyword Selection**
- Mix brand terms (product names) with category terms (industry keywords)
- Include both positive and negative sentiment terms
- Test different variations (singular/plural, abbreviations)

**Analysis Approach**
- Create focused projects that answer specific questions
- Iterate based on findings - each project informs the next
- Cross-reference findings with other data sources
- Always validate AI insights by reading actual discussions

---

## Getting Help

### In-App Resources
- **Settings → Help**: Comprehensive feature documentation
- **AI Chat Assistant**: Ask questions about your specific data
- **Tooltips**: Hover over labels for contextual guidance

### Support
- **Email**: support@sentopic.io
- **Documentation**: sentopic.io/docs
- **Response Time**: 24-48 hours for technical support

### Recommended Learning Path

1. Complete this quick start (30 minutes)
2. Create 2-3 practice projects to get comfortable
3. Review **Settings → Help** for advanced features
4. Start your real research with focused questions

---

## Example Research Questions

To inspire your first projects:

**Product Research**
- "What features do users want in project management tools?"
- "What are the main complaints about food delivery apps?"
- "How do people compare iPhone vs Android in 2024?"

**Market Intelligence**
- "What concerns do people have about electric vehicles?"
- "What's the sentiment around remote work policies?"
- "How do gamers feel about subscription-based gaming?"

**Trend Analysis**
- "What AI applications are people most excited about?"
- "What privacy concerns are people discussing?"
- "What new technologies are gaining traction?"

**Competitive Analysis**
- "How do users compare Slack vs Microsoft Teams?"
- "What do people say about [competitor] customer service?"
- "What makes users switch from [product A] to [product B]?"

---

## Tips for Success

1. **Be Specific**: Focused research questions yield clearer insights than vague explorations
2. **Start Small**: 100-500 posts is enough to validate your approach before scaling
3. **Iterate Often**: Create multiple small projects rather than one massive analysis
4. **Read Examples**: Always review actual discussions to validate aggregate findings
5. **Use AI Wisely**: AI suggestions are helpful starting points, not definitive answers
6. **Trust the Process**: Meaningful insights emerge from iterative refinement, not first attempts

---

Welcome to Sentopic! We're excited to see what insights you'll discover. If you have questions or feedback, reach out to support@sentopic.io.