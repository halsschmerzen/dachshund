import discord
from discord.ext import commands
import os
from scraper import query_listings, read_banned_keywords, run_search
from dotenv import load_dotenv
import asyncio
import uuid

'''
As of 7th October 2024, this Bot is still in very early development. It works for the most part, but has many bugs
and needs drastic improvement. I do not recommend using this bot as of now.
'''

'''
TODO:
1. **Configuration Management**:
   - Implement a configuration file (e.g., JSON, YAML, or .env) to allow users to configure:
     - Bot token
     - Command prefix
     - Default scraper settings (price, interval, duration)
     - Banned keywords file path
     - Any other customizable options

2. **Error Handling**:
   - Improve error handling for failed API calls during scraping.
   - Provide user-friendly error messages in Discord when something goes wrong.

3. **Logging**:
   - Integrate a logging system to log important events, errors, and information for easier debugging and monitoring.
   - Consider using Python's `logging` module for better log management.

4. **User Permissions**:
   - Add more granular permission checks to ensure only authorized users can start or stop scrapers.

5. **Code Optimization**:
   - Refactor repetitive code to improve maintainability (e.g., channel creation and deletion).
   - Consider using async/await for more efficient handling of I/O operations.

6. **Testing**:
   - Write unit tests and integration tests to ensure bot reliability and functionality.

7. **Documentation**:
   - Create detailed documentation for developers on how to set up and use the bot.
   - Include instructions for contributing to the project.

8. **Features**:
   - Add more scraper functionalities, such as:
     - Support for multiple queries in a single command.
     - Alerts for specific keyword matches in listings.
     - Option to filter listings based on additional parameters.

9. **User Feedback**:
   - Implement feedback mechanisms to allow users to report issues or suggest improvements directly in Discord.

10. **Deployment**:
    - Create scripts or Docker containers to simplify deployment in different environments (local, cloud, etc.).
'''


intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

load_dotenv()
bot_token = os.getenv('BOT_TOKEN')

scraper_tasks = {}  # Dictionary to store scraper tasks and channels

@bot.event
async def on_ready():
    """
    Event that triggers when the bot has connected to Discord and is ready.
    It logs the bot's username and syncs the command tree with Discord.
    """
    print(f'Logged in as {bot.user}')
    synced = await bot.tree.sync()
    print(f'Synced {len(synced)} commands')

@bot.tree.command()
async def start_scraper(ctx, query: str, price: int, interval: int, duration: int = None, users: discord.User = None):
    """
    Starts a scraper that queries listings based on the given parameters.
    A private text channel is created for the user to receive updates.
    
    Parameters:
    - ctx: The context of the command invocation.
    - query: The search query for the scraper.
    - price: The maximum price for the listings.
    - interval: The time interval for checking listings.
    - duration: Optional; how long the scraper should run.
    - users: Optional; a specific user to grant access to the channel.
    """
    curr_dir = os.path.dirname(__file__)
    banned_keywords = read_banned_keywords(os.path.join(curr_dir, '../resources/banned_keywords.txt'))
    print(banned_keywords)

    unique_id = str(uuid.uuid4())[:4]  # Shortened UUID

    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.user: discord.PermissionOverwrite(read_messages=True),
        ctx.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }

    if users:
        overwrites[users] = discord.PermissionOverwrite(read_messages=True)

    channel_name = f'{unique_id}-scraper-{query}'

    if len(channel_name) > 25:
        print(f'Channel creation failed! Name too long, using a shorter name.')
        channel_name = f'{unique_id}-scraper-{query[:22]}'

    scraper_channel = await ctx.guild.create_text_channel(channel_name, overwrites=overwrites)
    print(f"Channel created: {scraper_channel.name}")

    async def send_to_discord(message):
        """
        Sends a message to the specified Discord channel.

        Parameters:
        - message: The message to send to the channel.
        """
        if scraper_channel:  
            print(f'Sending message: {message}')
            await scraper_channel.send(f'{ctx.user.mention} {message}')
        else:
            print('Error: scraper_channel is None')

    if duration is None:
        duration = 3600  # Default to 1 hour

    scraper_task = asyncio.create_task(run_search(query, price, interval, duration, banned_keywords, send_to_discord))

    scraper_tasks[unique_id] = (scraper_task, scraper_channel)
    await ctx.response.send_message(f'Scraper started! Listings will be sent to {scraper_channel.mention}')

    if duration:  
        await asyncio.sleep(duration)
        if scraper_channel:
            await scraper_channel.delete()
            print(f'Scraping duration has ended. {scraper_channel.name} has been deleted.')
            await ctx.followup.send(f'Scraping ended. Channel {scraper_channel.name} has been deleted.')
            scraper_tasks.pop(unique_id, None)  

@bot.tree.command()
async def stop_scraper(ctx, unique_id: str):
    """
    Stops a running scraper based on the unique ID or stops all scrapers if 'all' is specified.
    Deletes the associated channel when stopping.

    Parameters:
    - ctx: The context of the command invocation.
    - unique_id: The unique ID of the scraper to stop, or 'all' to stop all scrapers.
    """
    if unique_id == "all":  
        stopped_count = 0
        for unique_id, (scraper_task, scraper_channel) in list(scraper_tasks.items()):
            if scraper_task and not scraper_task.done():
                scraper_task.cancel()
                if scraper_channel:
                    await scraper_channel.delete()
                    print(f'Channel {scraper_channel.name} with ID {unique_id} was deleted. Scraping stopped.')
                    stopped_count += 1
                scraper_tasks.pop(unique_id, None)

        await ctx.response.send_message(f'All scrapers stopped! Deleted {stopped_count} channels.')
    else:
        scraper_task, scraper_channel = scraper_tasks.get(unique_id, (None, None))

        if scraper_task and not scraper_task.done():
            scraper_task.cancel()

            if scraper_channel:  
                await scraper_channel.delete()  
                await ctx.response.send_message(f'Scraper stopped! The channel {scraper_channel.name} has been deleted.')
                print(f'Channel with the ID {unique_id} was deleted. Scraping stopped.')
                scraper_tasks.pop(unique_id, None)  
            else:
                await ctx.response.send_message('The channel for scraping no longer exists.')
        else:
            await ctx.response.send_message('Invalid ID or the scraper is not running!')

@stop_scraper.autocomplete('unique_id')
async def autocomplete_scraper_id(interaction: discord.Interaction, current: str):
    """
    Provides autocomplete suggestions for the unique IDs of active scrapers or the option to stop all scrapers.

    Parameters:
    - interaction: The interaction that triggered the autocomplete.
    - current: The current input string for the autocomplete.
    """
    options = [
        discord.app_commands.Choice(name=unique_id, value=unique_id) 
        for unique_id in scraper_tasks.keys()
    ]
    
    options.append(discord.app_commands.Choice(name="Stop all scrapers", value="all"))

    return [option for option in options if current.lower() in option.name.lower()][:25]

bot.run(bot_token)
