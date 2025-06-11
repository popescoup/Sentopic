# Sentopic - Phase 1: Reddit Data Collection

Phase 1 of the Sentopic Reddit analytics tool. This component handles collecting posts and comments from Reddit and storing them in a SQLite database.

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

### 3. Configure API Credentials

**⚠️ Important: Never commit your actual API credentials to version control!**

1. Copy the example configuration file:
   ```bash
   cp config.example.json config.json
   ```

2. Edit `config.json` with your actual Reddit API credentials:
   ```json
   {
       "reddit": {
           "client_id": "YOUR_ACTUAL_CLIENT_ID",
           "client_secret": "YOUR_ACTUAL_CLIENT_SECRET",
           "user_agent": "Sentopic:v1.0 (by u/yourusername)"
       }
   }
   ```

Replace:
- `YOUR_ACTUAL_CLIENT_ID` with your Reddit app's client ID
- `YOUR_ACTUAL_CLIENT_SECRET` with your Reddit app's client secret  
- `yourusername` with your Reddit username

**Note**: The `config.json` file is included in `.gitignore` to protect your API credentials. Only the `config.example.json` template is tracked in version control.

## Usage

### Interactive Collection

Run the main script to start an interactive collection:

```bash
python main.py
```

You'll be prompted to enter:
- **Subreddit**: Name without "r/" (e.g., "technology")
- **Sort Method**: hot, new, rising, top, or controversial
- **Time Period**: For top/controversial only (hour, day, week, month, year, all)
- **Posts Count**: Number of posts to collect
- **Root Comments**: Maximum root comments per post
- **Replies per Root**: Maximum replies per root comment  
- **Min Upvotes**: Minimum upvotes required for comments

### View Collection History

```bash
python main.py --list
```

### Help

```bash
python main.py --help
```

## Database Schema

The SQLite database (`sentopic.db`) contains three tables:

- **collections**: Collection configuration and metadata
- **posts**: Reddit posts with full metadata
- **comments**: Reddit comments with hierarchy information

## Comment Collection Strategy

- Collects up to N root comments per post (direct replies to the post)
- For each root comment, collects up to M replies  
- All comments must meet the minimum upvote threshold
- Preserves comment hierarchy with `parent_id` and `is_root` fields

## Rate Limiting

The collector includes built-in rate limiting to respect Reddit's API limits:
- 1-second delay between requests
- Graceful error handling for API issues
- Progress bars show collection status

## Security Notes

- API credentials are stored in `config.json` which is excluded from version control
- The database file (`sentopic.db`) is also excluded as it may contain user data
- Always keep your Reddit API credentials secure and never share them publicly

## Integration with Future Phases

This Phase 1 code is designed to integrate seamlessly with:
- **Phase 2**: Analytics engine will use the collected data for keyword extraction and sentiment analysis
- **Phase 3**: LLM integration will work with the stored text content
- **Phase 4**: FastAPI backend will import these modules directly

The database schema and collection IDs are designed to support the full analytics workflow described in your project specification.