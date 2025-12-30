import discord
from discord.ext import commands, tasks
import os
from datetime import datetime, time
import pytz
from dotenv import load_dotenv
from scraper import (
    scrape_all_sources,
    scrape_bleeping_computer,
    scrape_wired_security,
    scrape_ars_technica_security,
    scrape_krebs_security,
    scrape_darknet_diaries
)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Store settings
last_episode_title = None
darknet_notification_channel_id = None
daily_news_channel_id = None
user_timezone = pytz.timezone('America/Chicago')  # Kansas City timezone

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    check_darknet_diaries.start()
    daily_news_digest.start()

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
        articles = scrape_bleeping_computer()
    elif source == 'wired':
        await ctx.send('Fetching news from WIRED...')
        articles = scrape_wired_security()
    elif source == 'ars':
        await ctx.send('Fetching news from Ars Technica...')
        articles = scrape_ars_technica_security()
    elif source == 'krebs':
        await ctx.send('Fetching news from Krebs on Security...')
        articles = scrape_krebs_security()
    else:
        await ctx.send('Invalid source! Use: all, bleeping, wired, ars, or krebs')
        return
    
    if not articles:
        await ctx.send('Couldn\'t fetch news right now. Try again later!')
        return
    
    for article in articles:
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
    
    await ctx.send(f'Found {len(articles)} articles!')

@bot.command(name='darknet')
async def get_darknet(ctx):
    """Check latest Darknet Diaries episodes"""
    await ctx.send('🎧 Fetching latest Darknet Diaries episodes...')
    
    episodes = scrape_darknet_diaries()
    
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
    global darknet_notification_channel_id, last_episode_title
    
    darknet_notification_channel_id = ctx.channel.id
    
    episodes = scrape_darknet_diaries()
    if episodes:
        last_episode_title = episodes[0]['title']
        await ctx.send(f'I will notify this channel when new Darknet Diaries episodes are released!\n'
                      f'Latest episode: {last_episode_title}')
    else:
        await ctx.send('Watching enabled, but couldn\'t fetch current episode.')

@bot.command(name='unwatch_darknet')
async def unwatch_darknet(ctx):
    """Stop receiving Darknet Diaries notifications"""
    global darknet_notification_channel_id
    darknet_notification_channel_id = None
    await ctx.send('Darknet Diaries notifications disabled.')

@bot.command(name='daily_news')
async def setup_daily_news(ctx):
    """Enable daily news digest at 8:00 AM and 3:15 PM in this channel"""
    global daily_news_channel_id
    daily_news_channel_id = ctx.channel.id
    await ctx.send('Daily news digest enabled!\n'
                   'You\'ll receive 1 article from each source at:\n'
                   '• 8:00 AM\n'
                   '• 3:15 PM\n'
                   '(Central Time)')

@bot.command(name='stop_daily_news')
async def stop_daily_news(ctx):
    """Disable daily news digest"""
    global daily_news_channel_id
    daily_news_channel_id = None
    await ctx.send('Daily news digest disabled.')

@tasks.loop(hours=6)
async def check_darknet_diaries():
    """Check for new Darknet Diaries episodes every 6 hours"""
    global last_episode_title, darknet_notification_channel_id
    
    if darknet_notification_channel_id is None:
        return
    
    print("Checking for new Darknet Diaries episodes...")
    episodes = scrape_darknet_diaries()
    
    if not episodes:
        return
    
    latest_episode = episodes[0]
    
    if last_episode_title is None:
        last_episode_title = latest_episode['title']
        return
    
    if latest_episode['title'] != last_episode_title:
        print(f"New episode detected: {latest_episode['title']}")
        last_episode_title = latest_episode['title']
        
        channel = bot.get_channel(darknet_notification_channel_id)
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
            
            await channel.send("@everyone")
            await channel.send(embed=embed)

@tasks.loop(minutes=1)  # Check every minute
async def daily_news_digest():
    """Send daily news digest at 8:00 AM and 3:15 PM"""
    global daily_news_channel_id
    
    if daily_news_channel_id is None:
        return
    
    now = datetime.now(user_timezone)
    current_time = now.time()
    
    # Check if it's 8:00 AM or 3:15 PM (with 1 minute tolerance)
    morning_time = time(8, 0)
    afternoon_time = time(15, 10)
    
    # Only trigger once per minute at the exact time
    if (current_time.hour == morning_time.hour and current_time.minute == morning_time.minute) or \
       (current_time.hour == afternoon_time.hour and current_time.minute == afternoon_time.minute):
        
        print(f"Sending daily news digest at {current_time}")
        channel = bot.get_channel(daily_news_channel_id)
        
        if channel:
            await channel.send('**@InconceivableNate, Here is your Daily Cybersecurity News Digest**')
            
            # Get 1 article from each source 
            sources = [
                ('Bleeping Computer', scrape_bleeping_computer, 0xFF6B6B),
                ('WIRED', scrape_wired_security, 0x000000),
                ('Ars Technica', scrape_ars_technica_security, 0xFF4F00),
                ('Krebs on Security', scrape_krebs_security, 0x0066CC)
            ]
            
            total_articles = 0
            
            for source_name, scraper_func, color in sources:
                articles = scraper_func()
                if articles:
                    article = articles[0]  # Get first article
                    embed = discord.Embed(
                        title=article['title'],
                        url=article['link'],
                        description=article['description'],
                        color=color
                    )
                    embed.set_footer(text=f"Source: {article['source']}")
                    await channel.send(embed=embed)
                    total_articles += 1
                else:
                    await channel.send(f'Could not fetch from {source_name}')
            
            await channel.send(f'Daily digest complete! {total_articles} articles delivered.')

@bot.command(name='ping')
async def ping(ctx):
    """Test command"""
    await ctx.send('Pong! Bot is online.')

@bot.command(name='help_news')
async def help_news(ctx):
    """Show news command help"""
    help_text = """
    **Cybersecurity News Bot Commands:**
    
    **News Commands:**
    `!news` or `!news all` - Get news from all sources
    `!news bleeping` - Bleeping Computer
    `!news wired` - WIRED Security
    `!news ars` - Ars Technica
    `!news krebs` - Krebs on Security
    
    **Daily News Digest:**
    `!daily_news` - Get 1 article from each source at 8:00 AM & 3:15 PM
    `!stop_daily_news` - Stop daily digest
    
    **Darknet Diaries:**
    `!darknet` - Check latest episodes
    `!watch_darknet` - Get notified of new episodes
    `!unwatch_darknet` - Stop notifications
    
    **Other:**
    `!ping` - Check if bot is online
    """
    await ctx.send(help_text)

bot.run(TOKEN)