import discord
from discord.ext import commands, tasks
import os
from datetime import datetime, time, timedelta
import pytz
import json
from dotenv import load_dotenv
from scraper import (
    scrape_all_sources,
    scrape_bleeping_computer,
    scrape_wired_security,
    scrape_ars_technica_security,
    scrape_krebs_security,
    scrape_darknet_diaries,
    scrape_with_retry
)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Global settings
USER_ID = 'YOUR_USER_ID_HERE'  # Replace with your Discord user ID
user_timezone = pytz.timezone('America/Chicago')

# File to store persistent data
SETTINGS_FILE = 'bot_settings.json'

# Default settings structure
default_settings = {
    'last_episode_title': None,
    'darknet_channel_id': None,
    'daily_news_channel_id': None,
    'user_keywords': [],
    'sent_articles': {},
    'notification_times': ['08:00', '15:15'],
    'weekly_articles': [],
    'notify_user': True  # Whether to tag user on notifications
}

def load_settings():
    """Load settings from file"""
    try:
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return default_settings.copy()

def save_settings(settings):
    """Save settings to file"""
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)

# Load settings on startup
settings = load_settings()

def is_article_new(article_link):
    """Check if article hasn't been sent in last 24 hours"""
    current_time = datetime.now().isoformat()
    
    # Clean old articles (older than 24 hours)
    cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
    settings['sent_articles'] = {
        link: timestamp 
        for link, timestamp in settings['sent_articles'].items() 
        if timestamp > cutoff
    }
    
    # Check if article is new
    if article_link in settings['sent_articles']:
        return False
    
    settings['sent_articles'][article_link] = current_time
    save_settings(settings)
    return True

def matches_keywords(article, keywords):
    """Check if article matches user keywords"""
    if not keywords:
        return True
    text = (article['title'] + ' ' + article['description']).lower()
    return any(keyword.lower() in text for keyword in keywords)

def filter_articles(articles):
    """Filter articles by keywords and duplicates"""
    filtered = []
    for article in articles:
        if is_article_new(article['link']) and matches_keywords(article, settings['user_keywords']):
            filtered.append(article)
    return filtered

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f"Settings loaded: {len(settings['sent_articles'])} articles tracked")
    print(f"Keywords: {settings['user_keywords']}")
    check_darknet_diaries.start()
    daily_news_digest.start()
    weekly_summary.start()

@bot.command(name='news')
async def get_news(ctx, source: str = 'all'):
    """
    Fetch cybersecurity news
    Usage: !news [all|bleeping|wired|ars|krebs]
    """
    source = source.lower()
    
    if source == 'all':
        await ctx.send('Fetching news from all sources...')
        articles = scrape_all_sources()
    elif source == 'bleeping':
        await ctx.send('Fetching news from Bleeping Computer...')
        articles = scrape_with_retry(scrape_bleeping_computer)
    elif source == 'wired':
        await ctx.send('Fetching news from WIRED...')
        articles = scrape_with_retry(scrape_wired_security)
    elif source == 'ars':
        await ctx.send('Fetching news from Ars Technica...')
        articles = scrape_with_retry(scrape_ars_technica_security)
    elif source == 'krebs':
        await ctx.send('Fetching news from Krebs on Security...')
        articles = scrape_with_retry(scrape_krebs_security)
    else:
        await ctx.send('Invalid source! Use: all, bleeping, wired, ars, or krebs')
        return
    
    if not articles:
        await ctx.send('Couldn\'t fetch news right now. Try again later!')
        return
    
    # Filter articles
    filtered = filter_articles(articles)
    
    if not filtered:
        await ctx.send('No new articles matching your filters.')
        return
    
    for article in filtered:
        colors = {
            'Bleeping Computer': 0xFF6B6B,
            'WIRED': 0x000000,
            'Ars Technica': 0xFF4F00,
            'Krebs on Security': 0x0066CC
        }
        color = colors.get(article['source'], 0x5865F2)
        
        embed = discord.Embed(
            title=article['title'],
            url=article['link'],
            description=article['description'],
            color=color
        )
        embed.set_footer(text=f"Source: {article['source']}")
        await ctx.send(embed=embed)
    
    await ctx.send(f'Found {len(filtered)} new articles!')

@bot.command(name='darknet')
async def get_darknet(ctx):
    """Check latest Darknet Diaries episodes"""
    await ctx.send('Fetching latest Darknet Diaries episodes...')
    
    episodes = scrape_with_retry(scrape_darknet_diaries)
    
    if not episodes:
        await ctx.send('Couldn\'t fetch episodes right now. Try again later!')
        return
    
    for episode in episodes:
        embed = discord.Embed(
            title=f"🎙️ {episode['title']}",
            url=episode['link'],
            description=episode['description'],
            color=0x1DB954
        )
        if episode.get('date'):
            embed.add_field(name="Released", value=episode['date'], inline=True)
        embed.set_footer(text="Darknet Diaries by Jack Rhysider")
        await ctx.send(embed=embed)
    
    await ctx.send(f'Found {len(episodes)} episodes!')

@bot.command(name='watch_darknet')
async def watch_darknet(ctx):
    """Set this channel to receive notifications for new Darknet Diaries episodes"""
    settings['darknet_channel_id'] = ctx.channel.id
    
    episodes = scrape_with_retry(scrape_darknet_diaries)
    if episodes:
        settings['last_episode_title'] = episodes[0]['title']
        save_settings(settings)
        await ctx.send(f'I will notify this channel when new Darknet Diaries episodes are released!\n'
                      f'Latest episode: {episodes[0]["title"]}')
    else:
        await ctx.send('Watching enabled, but couldn\'t fetch current episode.')

@bot.command(name='unwatch_darknet')
async def unwatch_darknet(ctx):
    """Stop receiving Darknet Diaries notifications"""
    settings['darknet_channel_id'] = None
    save_settings(settings)
    await ctx.send('Darknet Diaries notifications disabled.')

@bot.command(name='daily_news')
async def setup_daily_news(ctx):
    """Enable daily news digest in this channel"""
    settings['daily_news_channel_id'] = ctx.channel.id
    save_settings(settings)
    times = ' and '.join(settings['notification_times'])
    await ctx.send(f'Daily news digest enabled!\n'
                   f'You\'ll receive 1 article from each source at: {times}\n'
                   f'(Central Time)')

@bot.command(name='stop_daily_news')
async def stop_daily_news(ctx):
    """Disable daily news digest"""
    settings['daily_news_channel_id'] = None
    save_settings(settings)
    await ctx.send('Daily news digest disabled.')

@bot.command(name='set_keywords')
async def set_keywords(ctx, *keywords):
    """
    Filter news by keywords
    Example: !set_keywords ransomware breach vulnerability
    Use !set_keywords clear to remove all filters
    """
    if keywords and keywords[0].lower() == 'clear':
        settings['user_keywords'] = []
        save_settings(settings)
        await ctx.send('Keyword filters cleared. You\'ll receive all news.')
    elif keywords:
        settings['user_keywords'] = list(keywords)
        save_settings(settings)
        await ctx.send(f'Filtering news for keywords: {", ".join(keywords)}')
    else:
        if settings['user_keywords']:
            await ctx.send(f'Current keywords: {", ".join(settings["user_keywords"])}')
        else:
            await ctx.send('No keyword filters set. Use: !set_keywords ransomware breach')

@bot.command(name='show_keywords')
async def show_keywords(ctx):
    """Show current keyword filters"""
    if settings['user_keywords']:
        await ctx.send(f'Current keyword filters: {", ".join(settings["user_keywords"])}')
    else:
        await ctx.send('No keyword filters active. All news will be shown.')

@bot.command(name='notify_me')
async def toggle_notifications(ctx):
    """Toggle whether you get tagged (@mentioned) on scheduled notifications"""
    settings['notify_user'] = not settings['notify_user']
    save_settings(settings)
    
    if settings['notify_user']:
        await ctx.send('You will be tagged on scheduled notifications (you\'ll get push notifications)')
    else:
        await ctx.send('Tag notifications disabled (you won\'t get pinged, but messages will still be sent)')

@bot.command(name='set_times')
async def set_notification_times(ctx, time1: str, time2: str = None):
    """
    Set custom notification times (24-hour format)
    Example: !set_times 09:00 17:30
    Example: !set_times 08:00 (for single daily notification)
    """
    try:
        # Validate time format
        datetime.strptime(time1, '%H:%M')
        times = [time1]
        
        if time2:
            datetime.strptime(time2, '%H:%M')
            times.append(time2)
        
        settings['notification_times'] = times
        save_settings(settings)
        
        times_str = ' and '.join(times)
        await ctx.send(f' Notification times set to: {times_str} (Central Time)')
    except ValueError:
        await ctx.send('Invalid time format. Use HH:MM (24-hour format)\nExample: !set_times 09:00 17:30')

@bot.command(name='stats')
async def show_stats(ctx):
    """Show bot statistics"""
    total_tracked = len(settings['sent_articles'])
    keywords = len(settings['user_keywords'])
    
    embed = discord.Embed(
        title="Bot Statistics",
        color=0x5865F2
    )
    embed.add_field(name="Articles Tracked (24h)", value=str(total_tracked), inline=True)
    embed.add_field(name="Active Keywords", value=str(keywords), inline=True)
    embed.add_field(name="Notification Times", value=', '.join(settings['notification_times']), inline=False)
    embed.add_field(name="Tag on Notify", value="Yes" if settings['notify_user'] else "🔕 No", inline=True)
    
    if settings['user_keywords']:
        embed.add_field(name="Keywords", value=', '.join(settings['user_keywords']), inline=False)
    
    await ctx.send(embed=embed)

@tasks.loop(hours=6)
async def check_darknet_diaries():
    """Check for new Darknet Diaries episodes every 6 hours"""
    if settings['darknet_channel_id'] is None:
        return
    
    print("Checking for new Darknet Diaries episodes...")
    episodes = scrape_with_retry(scrape_darknet_diaries)
    
    if not episodes:
        return
    
    latest_episode = episodes[0]
    
    if settings['last_episode_title'] is None:
        settings['last_episode_title'] = latest_episode['title']
        save_settings(settings)
        return
    
    if latest_episode['title'] != settings['last_episode_title']:
        print(f"New episode detected: {latest_episode['title']}")
        settings['last_episode_title'] = latest_episode['title']
        save_settings(settings)
        
        channel = bot.get_channel(settings['darknet_channel_id'])
        if channel:
            embed = discord.Embed(
                title=f"NEW DARKNET DIARIES EPISODE!",
                description=f"**{latest_episode['title']}**",
                url=latest_episode['link'],
                color=0xFF0000
            )
            embed.add_field(
                name="Description",
                value=latest_episode['description'],
                inline=False
            )
            if latest_episode.get('date'):
                embed.add_field(name="Released", value=latest_episode['date'], inline=True)
            embed.set_footer(text="Darknet Diaries by Jack Rhysider")
            
            if settings['notify_user']:
                await channel.send(f"<@{USER_ID}>")
            await channel.send(embed=embed)

@tasks.loop(minutes=1)
async def daily_news_digest():
    """Send daily news digest at configured times"""
    if settings['daily_news_channel_id'] is None:
        return
    
    now = datetime.now(user_timezone)
    current_time = now.strftime('%H:%M')
    
    # Check if current time matches any notification time
    if current_time in settings['notification_times']:
        print(f"Sending daily news digest at {current_time}")
        channel = bot.get_channel(settings['daily_news_channel_id'])
        
        if channel:
            # Tag user if enabled
            if settings['notify_user']:
                await channel.send(f'<@{USER_ID}>**Daily Cybersecurity News Digest**')
            else:
                await channel.send(f'**Daily Cybersecurity News Digest**')
            
            sources = [
                ('Bleeping Computer', scrape_bleeping_computer, 0xFF6B6B),
                ('WIRED', scrape_wired_security, 0x000000),
                ('Ars Technica', scrape_ars_technica_security, 0xFF4F00),
                ('Krebs on Security', scrape_krebs_security, 0x0066CC)
            ]
            
            total_articles = 0
            
            for source_name, scraper_func, color in sources:
                articles = scrape_with_retry(scraper_func)
                
                if articles:
                    # Filter and get first new article
                    filtered = filter_articles(articles)
                    
                    if filtered:
                        article = filtered[0]
                        embed = discord.Embed(
                            title=article['title'],
                            url=article['link'],
                            description=article['description'],
                            color=color
                        )
                        embed.set_footer(text=f"Source: {article['source']}")
                        await channel.send(embed=embed)
                        total_articles += 1
                        
                        # Store for weekly summary
                        settings['weekly_articles'].append({
                            'article': article,
                            'timestamp': datetime.now().isoformat()
                        })
                    else:
                        await channel.send(f'{source_name}: No new articles matching your filters')
                else:
                    await channel.send(f'Could not fetch from {source_name}')
            
            save_settings(settings)
            await channel.send(f'Daily digest complete! {total_articles} articles delivered.')

@tasks.loop(hours=24)
async def weekly_summary():
    """Send weekly summary every Sunday"""
    now = datetime.now(user_timezone)
    
    # Check if it's Sunday at 10:00 AM
    if now.weekday() == 6 and now.hour == 10 and now.minute == 0:
        if settings['daily_news_channel_id'] is None:
            return
        
        print("Sending weekly summary...")
        channel = bot.get_channel(settings['daily_news_channel_id'])
        
        if channel and settings['weekly_articles']:
            # Tag user if enabled
            if settings['notify_user']:
                await channel.send(f'<@{USER_ID}>**Weekly Cybersecurity Summary**')
            else:
                await channel.send(f'**Weekly Cybersecurity Summary**')
            
            # Count articles by source
            source_counts = {}
            for entry in settings['weekly_articles']:
                source = entry['article']['source']
                source_counts[source] = source_counts.get(source, 0) + 1
            
            embed = discord.Embed(
                title="📈 This Week in Cybersecurity",
                description=f"You received {len(settings['weekly_articles'])} articles this week",
                color=0x5865F2
            )
            
            for source, count in source_counts.items():
                embed.add_field(name=source, value=f"{count} articles", inline=True)
            
            embed.set_footer(text="Stay informed, stay secure!")
            await channel.send(embed=embed)
            
            # Clear weekly articles
            settings['weekly_articles'] = []
            save_settings(settings)

@bot.command(name='ping')
async def ping(ctx):
    """Test command"""
    await ctx.send('Pong! Bot is online.')

@bot.command(name='help_news')
async def help_news(ctx):
    """Show all available commands"""
    help_text = """
    **Cybersecurity News Bot - Command List**
    
    **News Commands:**
    `!news` or `!news all` - Get news from all sources
    `!news bleeping` - Bleeping Computer
    `!news wired` - WIRED Security
    `!news ars` - Ars Technica
    `!news krebs` - Krebs on Security
    
    **Daily Digest:**
    `!daily_news` - Enable daily digest in this channel
    `!stop_daily_news` - Stop daily digest
    `!set_times HH:MM HH:MM` - Set custom notification times
    
    **Keyword Filtering:**
    `!set_keywords word1 word2 word3` - Filter news by keywords
    `!show_keywords` - Show active keywords
    `!set_keywords clear` - Remove all filters
    
    **Notification Settings:**
    `!notify_me` - Toggle @ mentions on/off for scheduled notifications
    
    **Darknet Diaries:**
    `!darknet` - Check latest episodes
    `!watch_darknet` - Get notified of new episodes
    `!unwatch_darknet` - Stop notifications
    
    **Other:**
    `!stats` - Show bot statistics
    `!ping` - Check if bot is online
    
    **Features:**
    • Duplicate prevention (24h)
    • Keyword filtering
    • Retry on failures
    • Weekly summaries (Sundays at 10 AM)
    • Customizable notification times
    """
    await ctx.send(help_text)

bot.run(TOKEN)
