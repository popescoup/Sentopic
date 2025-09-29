# Sentopic Installation Guide - macOS

## System Requirements

- **Operating System**: macOS 10.15 (Catalina) or later
- **Architecture**: Intel Mac or Apple Silicon (M1/M2/M3)
- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 1GB available disk space
- **Internet Connection**: Required for initial setup and Reddit data collection

---

## Installation Steps

### Step 1: Download the Installer

Download `Sentopic-1.0.0-mac.dmg` from your purchase confirmation email or customer download portal.

### Step 2: Mount and Install

1. **Locate the downloaded DMG file** in your Downloads folder
2. **Double-click** `Sentopic-1.0.0-mac.dmg` to mount it
3. A Finder window will open showing the Sentopic application
4. **Drag Sentopic.app** to the Applications folder shortcut
5. Wait for the copy to complete
6. **Eject the DMG** by clicking the eject button next to "Sentopic" in Finder sidebar

### Step 3: First Launch

macOS will show security warnings when launching Sentopic for the first time because the app is not currently code-signed by Apple.

**Initial Launch Method:**

1. Open your **Applications** folder
2. **Right-click** (or Control+click) on **Sentopic.app**
3. Select **"Open"** from the context menu
4. A security dialog will appear saying "Sentopic cannot be opened because it is from an unidentified developer"
5. Click **"Open"** in the dialog
6. The application will launch and initialize

**Alternative Method (if right-click doesn't work):**

1. Try to open Sentopic normally (double-click)
2. If blocked, go to **System Preferences → Security & Privacy**
3. Click the **"Open Anyway"** button next to the Sentopic warning
4. Confirm by clicking **"Open"** in the dialog

**For Future Launches:**

After the first successful launch, you can open Sentopic normally by double-clicking - macOS will remember your permission.

---

## Initial Configuration

### Reddit API Setup (Required)

Sentopic requires Reddit API credentials to collect data. Follow these steps to create your credentials:

#### Creating a Reddit App

1. Visit [https://www.reddit.com/prefs/apps](https://www.reddit.com/prefs/apps) and sign in with your Reddit account
2. Scroll to the bottom and click **"create another app..."** or **"are you a developer? create an app..."**
3. Fill out the form:
   - **Name**: Any name you choose (e.g., "Sentopic Research Tool")
   - **App type**: Select **"script"** (IMPORTANT: Must be "script", not "web app")
   - **Description**: Optional (e.g., "Reddit analytics for business research")
   - **About URL**: Leave blank
   - **Redirect URI**: Enter `http://localhost` (required, even though it won't be used)
   - **Permissions**: Leave default selections
4. Click **"create app"**

#### Locating Your Credentials

After creating your app, you'll see it listed on the page:

- **Client ID**: The string directly under your app's name (looks like random characters, e.g., `abc123DEF456`)
- **Client Secret**: The longer string labeled "secret"
- **User Agent**: You need to create this yourself in the format: `AppName/1.0 by /u/YourRedditUsername`

Example User Agent: `SentopicResearch/1.0 by /u/john_researcher`

#### Entering Credentials in Sentopic

1. Launch Sentopic
2. Click the **Settings** icon (gear) in the top-right corner
3. Navigate to the **Configuration** tab
4. Under **Reddit API Configuration**, enter:
   - **Client ID**: Your client ID from Reddit
   - **Client Secret**: Your client secret from Reddit  
   - **User Agent**: Your custom user agent string
5. Click **"Test Reddit Connection"** to verify your credentials work
6. If successful, you'll see a green success message

### AI Provider Setup (Optional but Recommended)

AI features enhance Sentopic with keyword suggestions, analysis summaries, and the interactive chat assistant.

#### Anthropic (Claude) Setup

1. Visit [https://console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys)
2. Create an account or sign in
3. Add billing information (pay-as-you-go)
4. Generate a new API key
5. In Sentopic Settings → Configuration → LLM Provider:
   - Select **"Anthropic"** as provider
   - Paste your API key
   - Click **"Test Anthropic Connection"**

#### OpenAI (GPT) Setup

1. Visit [https://platform.openai.com/settings/organization/api-keys](https://platform.openai.com/settings/organization/api-keys)
2. Create an account or sign in
3. Add billing information (pay-as-you-go)
4. Generate a new API key
5. In Sentopic Settings → Configuration → LLM Provider:
   - Select **"OpenAI"** as provider
   - Paste your API key
   - Click **"Test OpenAI Connection"**

**Note**: You only need to configure one AI provider, not both. Choose based on your preference or existing accounts.

---

## Getting Started

After configuration is complete:

1. **Create Your First Collection**
   - Click **"Collection Manager"** in the header
   - Select subreddits relevant to your research
   - Configure collection parameters (posts, comments, time period)
   - Start the collection and monitor progress

2. **Create Your First Project**
   - Return to the main dashboard
   - Click **"New Project"**
   - Define your research question
   - Select keywords (or use AI suggestions)
   - Choose your collections
   - Start analysis

3. **Explore Results**
   - View sentiment analysis and keyword insights
   - Ask questions using the AI assistant
   - Explore trends and co-occurrences
   - Export findings for your team

For detailed usage guidance, click the **Help** button in Sentopic's settings menu.

---

## Troubleshooting

### "Sentopic is damaged and can't be opened"

This security message sometimes appears on macOS. Run this Terminal command to fix it:

```bash
sudo xattr -rd com.apple.quarantine /Applications/Sentopic.app
```

Enter your Mac password when prompted, then try launching Sentopic again.

### "Cannot connect to backend server"

If Sentopic's frontend loads but shows connection errors:

1. **Check port conflicts**: Sentopic uses ports 8000-8020. Close other applications that might use these ports
2. **Firewall issues**: Add Sentopic to your firewall's allowed applications in System Preferences → Security & Privacy → Firewall
3. **Restart the application**: Completely quit Sentopic (Cmd+Q) and relaunch

### Reddit API Connection Fails

If the Reddit connection test fails:

- Verify your **app type is "script"** (not "web app") on Reddit
- Double-check Client ID and Client Secret for typos or extra spaces
- Ensure your User Agent follows the format: `AppName/Version by /u/username`
- Check that your Reddit account is in good standing

### AI Features Not Working

- Verify you've entered a valid API key in Settings
- Check that your AI provider account has billing configured
- Test the connection using the "Test Connection" button
- Ensure you have available credits/usage quota

### Application Won't Start

1. Check **Console.app** (Applications → Utilities → Console) for error messages
2. Verify you have sufficient disk space (1GB+)
3. Try moving Sentopic.app to Trash, emptying Trash, and reinstalling
4. Restart your Mac and try again

### Performance Issues

If Sentopic runs slowly:

- Close unnecessary applications to free up RAM
- Start with smaller collections (500 posts) before scaling up
- Reduce the number of keywords in your projects
- Clear browser cache if using any web components

---

## Uninstalling Sentopic

### Remove Application

1. Open your **Applications** folder
2. Drag **Sentopic.app** to the Trash
3. Empty Trash

### Remove User Data (Optional)

If you want to completely remove all Sentopic data:

```bash
# Remove application support files
rm -rf ~/Library/Application\ Support/Sentopic

# Remove preferences
rm ~/Library/Preferences/com.sentopic.desktop.plist

# Remove logs
rm -rf ~/Library/Logs/Sentopic
```

**Note**: Your projects, collections, and settings will be permanently deleted. Only do this if you're sure you want to remove all data.

---

## Getting Help

### Support Resources

- **Email Support**: support@sentopic.io
- **In-App Help**: Click Settings → Help for detailed documentation
- **Response Time**: We respond to support emails within 24-48 hours

### When Contacting Support

Please include:

- macOS version (Apple menu → About This Mac)
- Sentopic version (visible in Settings → About)
- Description of the issue
- Steps to reproduce the problem
- Any error messages (exact text or screenshots)
- What you've already tried to fix it

### Privacy Note

Sentopic stores all data locally on your Mac. Your Reddit data, API credentials, and analysis results are never sent to Sentopic servers. AI features send only the necessary text to your chosen AI provider (Anthropic or OpenAI) according to their respective privacy policies.

---

## Next Steps

Once installed and configured:

1. Review the **Quick Start Guide** in Settings → Help
2. Start with a focused research question
3. Collect data from 1-2 relevant subreddits
4. Create your first analysis project
5. Explore the AI chat assistant for deeper insights

Welcome to Sentopic - we're excited to see what insights you'll discover!