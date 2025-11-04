# Sentopic Installation Guide - Windows

## System Requirements

- **Operating System**: Windows 10 or Windows 11 (64-bit)
- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 1GB available disk space
- **Internet Connection**: Required for initial setup and Reddit data collection

---

## Installation Steps

### Step 1: Download the Installer

Download `Sentopic-1.0.0.exe` from your purchase confirmation email or customer download portal.

### Step 2: Run the Installer

1. **Locate the downloaded installer** in your Downloads folder
2. **Double-click** `Sentopic-1.0.0.exe` to launch the installer

### Step 3: Handle Windows Security Warning

Windows will show a security warning because the app is not currently code-signed by Microsoft.

**Windows SmartScreen Warning:**

When you run the installer, Windows SmartScreen will display: **"Windows protected your PC"**

**To proceed:**

1. Click **"More info"** (small text link in the warning dialog)
2. A new button will appear: **"Run anyway"**
3. Click **"Run anyway"** to continue installation

This is a standard Windows security measure for unsigned applications. Your app is safe - Windows simply doesn't recognize the publisher yet.

### Step 4: Complete Installation Wizard

1. The Sentopic installer will launch
2. Click **"Next"** to begin installation
3. Choose your installation location (default is recommended: `C:\Program Files\Sentopic`)
4. Review installation settings
5. Click **"Install"** to begin installation
6. Wait for installation to complete (typically 30-60 seconds)
7. Click **"Finish"** to close the installer

**Shortcuts Created:**
- Desktop shortcut: **Sentopic**
- Start Menu entry: **Sentopic**

### Step 5: First Launch

1. Double-click the **Sentopic** desktop shortcut, or launch from Start Menu
2. If Windows Defender shows another SmartScreen warning, repeat the "More info" → "Run anyway" process
3. The application will launch and initialize (may take 10-15 seconds on first launch)

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

### Windows SmartScreen Keeps Blocking the App

If you continue to see SmartScreen warnings after installation:

1. **Temporary solution**: Always use "More info" → "Run anyway"
2. **Permanent solution**: Add Sentopic to Windows Defender exclusions:
   - Open **Windows Security** (search in Start Menu)
   - Go to **Virus & threat protection**
   - Click **Manage settings** under "Virus & threat protection settings"
   - Scroll down to **Exclusions** and click **Add or remove exclusions**
   - Click **Add an exclusion** → **Folder**
   - Navigate to and select: `C:\Program Files\Sentopic`
   - Sentopic will no longer trigger SmartScreen warnings

### Antivirus Software Blocking Sentopic

Some antivirus programs may flag Sentopic as suspicious (false positive):

**Symptoms:**
- Installation fails or is blocked
- Application won't launch
- Features don't work properly

**Solution:**
1. Add Sentopic to your antivirus exclusion/whitelist
2. Location to whitelist: `C:\Program Files\Sentopic`
3. Specific file to whitelist: `C:\Program Files\Sentopic\python-backend\sentopic.exe`

Each antivirus is different - consult your antivirus documentation for adding exclusions.

### "Cannot connect to backend server"

If Sentopic's frontend loads but shows connection errors:

1. **Check port conflicts**: Sentopic uses ports 8000-8020. Close other applications that might use these ports
2. **Firewall issues**: 
   - Open **Windows Defender Firewall** (search in Start Menu)
   - Click **Allow an app through firewall**
   - Click **Change settings** (requires admin)
   - Click **Allow another app**
   - Browse to `C:\Program Files\Sentopic\Sentopic.exe` and add it
   - Ensure both **Private** and **Public** checkboxes are checked
3. **Restart the application**: Completely close Sentopic (check system tray) and relaunch

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

1. Check **Event Viewer** (search in Start Menu → Windows Logs → Application) for error messages
2. Verify you have sufficient disk space (1GB+)
3. Try running as Administrator (right-click Sentopic shortcut → "Run as administrator")
4. Uninstall and reinstall Sentopic
5. Restart your computer and try again

### Performance Issues

If Sentopic runs slowly:

- Close unnecessary applications to free up RAM
- Start with smaller collections (500 posts) before scaling up
- Reduce the number of keywords in your projects
- Check Windows Task Manager for high CPU/memory usage

### Port Conflicts with Other Software

If Sentopic reports that all ports are in use:

**Common conflicting software:**
- Local web development servers (XAMPP, WAMP, local Node.js servers)
- Other analytics or database tools
- Corporate VPN or security software

**Solutions:**
1. Temporarily close other applications using ports 8000-9020
2. Check Task Manager for processes using network connections
3. Use Command Prompt to find what's using a port:
```
   netstat -ano | findstr :8000
```
4. Restart your computer to clear stuck port bindings

---

## Uninstalling Sentopic

### Remove Application

1. Open **Settings** → **Apps** → **Apps & features**
2. Find **Sentopic** in the list
3. Click **Uninstall**
4. Follow the uninstaller wizard
5. Click **Finish** when complete

**Alternative method:**
1. Open **Control Panel** → **Programs** → **Uninstall a program**
2. Find **Sentopic** in the list
3. Click **Uninstall**

### Remove User Data (Optional)

The uninstaller preserves your data by default. If you want to completely remove all Sentopic data:

1. Open **File Explorer**
2. Navigate to: `C:\Users\[YourUsername]\AppData\Roaming\Sentopic`
3. Delete the entire **Sentopic** folder

**What's stored here:**
- `sentopic.db` - Your projects and collections database
- `config.json` - Your API credentials and settings
- `logs/` - Application logs

**Note**: Your projects, collections, and settings will be permanently deleted. Only do this if you're sure you want to remove all data.

---

## Getting Help

### Support Resources

- **Email Support**: support@sentopic.io
- **In-App Help**: Click Settings → Help for detailed documentation
- **Response Time**: We respond to support emails within 24-48 hours

### When Contacting Support

Please include:

- Windows version (Settings → System → About)
- Sentopic version (visible in Settings → About)
- Description of the issue
- Steps to reproduce the problem
- Any error messages (exact text or screenshots)
- What you've already tried to fix it

### Privacy Note

Sentopic stores all data locally on your Windows PC. Your Reddit data, API credentials, and analysis results are never sent to Sentopic servers. AI features send only the necessary text to your chosen AI provider (Anthropic or OpenAI) according to their respective privacy policies.

---

## Next Steps

Once installed and configured:

1. Review the **Quick Start Guide** in Settings → Help
2. Start with a focused research question
3. Collect data from 1-2 relevant subreddits
4. Create your first analysis project
5. Explore the AI chat assistant for deeper insights

Welcome to Sentopic - we're excited to see what insights you'll discover!