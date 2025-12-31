Cybersecurity News Discord Bot
A powerful Discord bot that aggregates cybersecurity news from multiple trusted sources, provides AI-powered summaries, and sends scheduled notifications. Built with Python and powered by Groq AI.
Features
News Aggregation

Multi-Source Scraping: Automatically pulls news from:

Bleeping Computer
WIRED Security
Ars Technica
Krebs on Security
Darknet Diaries (podcast episodes)



AI-Powered Summaries

Generate intelligent summaries of top cybersecurity articles
Powered by Groq's Llama 3.1 70B model
Highlights critical threats, trends, and action items
Customizable article count (default: 10)

Smart Filtering

Duplicate Prevention: Tracks articles sent in the last 24 hours
Keyword Filtering: Only receive news matching your interests
Source Selection: Query specific sources or all at once

Scheduled Notifications

Daily Digest: Automated news delivery at custom times
Weekly Summary: Sunday recap of articles received
Darknet Diaries Alerts: Get notified when new episodes drop
Customizable Times: Set your own notification schedule
Toggle Mentions: Control push notifications on/off

Reliability

Automatic retry logic for failed scrapers
Error handling for all background tasks
Persistent settings across restarts
Graceful reconnection handling

Installation
Prerequisites

Python 3.8 or higher
Discord account with Developer Mode enabled
Groq API account (free tier available)

Step 1: Clone the Repository
git clone https://github.com/pasketticode4dayz/cybersecurity-news-bot.git
cd cybersecurity-news-bot
Step 2: Install Dependencies
pip install -r requirements.txt
Or install manually:
pip install discord.py python-dotenv requests beautifulsoup4 pytz groq
Step 3: Set Up Discord Bot

Go to Discord Developer Portal
Click "New Application" and give it a name
Go to the "Bot" tab and click "Add Bot"
Under "Privileged Gateway Intents", enable:

Message Content Intent


Click "Reset Token" and copy your bot token
Go to "OAuth2" → "URL Generator"

Select scope: bot
Select permissions: Send Messages, Embed Links, Read Message History, View Channels


Copy the generated URL and open it to invite the bot to your server

Step 4: Get Groq API Key

Go to Groq Console
Sign up for a free account
Navigate to "API Keys"
Create a new API key and copy it

Step 5: Configure Environment Variables
Create a .env file in the project root:
DISCORD_TOKEN=your_discord_bot_token_here
GROQ_API_KEY=your_groq_api_key_here
Step 6: Get Your Discord User ID

Step 7: Run the Bot
python3 bot.py
You should see: [BotName] has connected to Discord!
Commands
News Commands
CommandDescription!news or !news allGet news from all sources!news bleepingGet news from Bleeping Computer!news wiredGet news from WIRED Security!news arsGet news from Ars Technica!news krebsGet news from Krebs on Security
AI Summary
CommandDescription!ai_summaryGenerate AI summary of top 10 articles!ai_summary 15Summarize specific number of articles
Daily Digest
CommandDescription!daily_newsEnable daily digest in current channel!stop_daily_newsDisable daily digest!set_times HH:MM HH:MMSet custom notification times (24-hour format)
Keyword Filtering
CommandDescription!set_keywords word1 word2Filter news by keywords!show_keywordsShow active keyword filters!set_keywords clearRemove all filters
Notification Settings
CommandDescription!notify_meToggle @ mentions on/off for notifications
Darknet Diaries
CommandDescription!darknetCheck latest episodes!watch_darknetGet notified of new episodes in current channel!unwatch_darknetStop episode notifications
Other
CommandDescription!statsShow bot statistics and settings!pingCheck if bot is online!help_newsShow all available commands
Usage Examples
Get News from All Sources
!news
Get AI Summary
!ai_summary
Analyzes top 10 articles and provides executive summary with threats, trends, and action items.
Set Up Daily Digest
!daily_news
!set_times 08:00 15:30
Receive 1 article from each source at 8:00 AM and 3:30 PM daily.
Filter by Keywords
!set_keywords ransomware breach malware
Only receive articles mentioning ransomware, breach, or malware.
Watch Darknet Diaries
!watch_darknet
Get notified in current channel when new episodes are released.
Project Structure
cybersecurity-news-bot/
├── bot.py                 # Main bot code with commands and tasks
├── scraper.py            # Web scraping functions for all sources
├── .env                  # Environment variables (not in repo)
├── bot_settings.json     # Persistent settings (auto-generated)
├── requirements.txt      # Python dependencies
└── README.md            # This file
Configuration
Default Settings

Notification Times: 8:00 AM and 3:15 PM (Central Time)
Duplicate Prevention: 24 hours
Weekly Summary: Sundays at 10:00 AM
Darknet Check: Every 6 hours
User Mentions: Enabled by default

Customization
All settings are stored in bot_settings.json and persist across restarts:

Notification times
Keyword filters
Sent articles tracking
Channel IDs
User preferences

Technical Details
News Sources

Bleeping Computer: General cybersecurity news
WIRED Security: In-depth security journalism
Ars Technica: Technical analysis and research
Krebs on Security: Security investigations and analysis
Darknet Diaries: Security podcast by Jack Rhysider

AI Model

Provider: Groq
Model: Llama 3.1 70B Versatile
Temperature: 0.7 (balanced creativity)
Max Tokens: 1000
Free Tier: 30 requests/minute

Background Tasks

check_darknet_diaries: Every 6 hours
daily_news_digest: Every minute (checks for scheduled times)
weekly_summary: Every hour (triggers Sunday 10 AM)

Troubleshooting
Bot Not Responding to Commands

Ensure "Message Content Intent" is enabled in Discord Developer Portal
Restart the bot after enabling intents
Check that bot has proper permissions in the channel

Scraper Errors

Sites may change their HTML structure - update selectors in scraper.py
Check your internet connection
Verify no rate limiting from news sites

AI Summary Not Working

Verify GROQ_API_KEY is set in .env
Check Groq API rate limits (30/min on free tier)
Ensure you have an active internet connection

Missing Notifications

Verify USER_ID is set correctly in bot.py
Check that notification times are in 24-hour format (HH:MM)
Ensure !daily_news is enabled in a channel

Rate Limits & Costs
Groq API (Free Tier)

30 requests per minute
Sufficient for personal use
No credit card required

Discord API

No costs
Standard rate limits apply (handled by discord.py)

Web Scraping

Respectful scraping with retries
No API keys needed for news sources

Contributing
Contributions are welcome! Feel free to:

Add new news sources
Improve scraping reliability
Add new features
Fix bugs
Improve documentation

Please open an issue or pull request on GitHub.
Future Enhancements
Potential features to add:

 RSS feed fallback for reliability
 More news sources (The Hacker News, SecurityWeek, etc.)
 Sentiment analysis of articles
 Threat level indicators
 Export summaries to PDF
 Multi-user support with individual settings
 Web dashboard for configuration

License
MIT License - feel free to use and modify for your needs.
Acknowledgments

News sources: Bleeping Computer, WIRED, Ars Technica, Krebs on Security
Darknet Diaries by Jack Rhysider
Powered by Groq AI
Built with discord.py

Support
For issues or questions:

Open a GitHub issue
Check existing issues for solutions
Review the troubleshooting section


Note: This bot is for personal/educational use. Please respect the terms of service of all news sources and APIs used.
