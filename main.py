import datetime
import discord
from discord import file
from discord import message
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
from discord.ext import tasks



load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

LOG_CHANNEL_ID = 1509371635172643020
GENERAL_CHANNEL_ID = 1509365569500086392

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')


@bot.event
async def on_member_join(member):
    await member.send(f'Welcome to the server, {member.name}!')
    print(f'{member.name} has joined the server.')


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    blocked_words = ['fuck', 'shit', 'bitch', 'asshole', 'damn', 'bastard', 'dick', 'pussy', 'cunt', 'slut', 'test']

    user_message = message.content.lower().split()

    if any(word in user_message for word in blocked_words):
        await message.delete()
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        await log_channel.send(f"{message.author.mention} said \"{message.content}\" in {message.channel.mention} // BLOCKED")
        
        with open('log.txt', 'a') as file:                      #message logger
            file.write(f"{message.author.mention} said \"{message.content}\" in {message.channel.mention} on {datetime.datetime.now()} // BLOCKED\n")

        try:
            await message.author.send(f"{message.author.name}, please refrain from using inappropriate language.")
        except:
            print("user has disabled direct messages")
            await message.channel.send(f"{message.author.mention}, please refrain from using inappropriate language.")

    else:
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        await log_channel.send(f"{message.author.mention} said \"{message.content}\" in {message.channel.mention}")

        with open('log.txt', 'a') as file:                      #message logger
            file.write(f"{message.author.mention} said \"{message.content}\" in {message.channel.mention} on {datetime.datetime.now()}\n")

    await bot.process_commands(message)



@tasks.loop(minutes=15)
async def moderation_cleanup():
    blocked_words = {'fuck','shit','bitch','asshole','damn','bastard','dick','pussy','cunt','slut'}

    now = datetime.datetime.utcnow()
    cutoff = now - datetime.timedelta(minutes=15)

    for channel in bot.get_all_channels():
        if isinstance(channel, discord.TextChannel):
            async for msg in channel.history(limit=200):
                if msg.created_at < cutoff:
                    break

                content_words = msg.content.lower().split()
                if any(word in blocked_words for word in content_words):
                    try:
                        await msg.delete()
                        log_channel = bot.get_channel(LOG_CHANNEL_ID)
                        await log_channel.send(
                            f"{msg.author.mention} said \"{msg.content}\" in {msg.channel.mention} // AUTO-DELETED (15‑min scan)"
                        )
                    except:
                        pass






@bot.event
async def on_presence_update(before, after):
    # We only care if their status changed, not if they just changed games
    if before.status == discord.Status.offline and after.status == discord.Status.online:
        # Check if their new status is 'online'
        if after.status == discord.Status.online:
            print(f"{after.name} has just logged on!")
            
            #Send a notification to general channel
            GENERAL_CHANNEL = bot.get_channel(GENERAL_CHANNEL_ID)
            if GENERAL_CHANNEL:
                await GENERAL_CHANNEL.send(f" **{after.name}** is now online!")
            
            with open('log.txt', 'a') as file:                      #message logger
                file.write(f"{after.name} logged in on {datetime.datetime.now()}\n")


        
@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello, {ctx.author.mention}!")


@bot.command()
async def anounceviddone(ctx, *, video_url):
    GENERAL_CHANNEL = bot.get_channel(GENERAL_CHANNEL_ID)  

    if GENERAL_CHANNEL:
        await GENERAL_CHANNEL.send(f"New video announcement: {video_url}")



@bot.command()
async def anouncevidsoon(ctx, *, videotitle, topic, ETA, give_or_take):
    GENERAL_CHANNEL = bot.get_channel(GENERAL_CHANNEL_ID)  

    if GENERAL_CHANNEL:
        await GENERAL_CHANNEL.send(f"New video announcement: {videotitle} - Topic: {topic} - ETA: {ETA}, give or take: {give_or_take}")



@bot.command()
async def generate_sentence(ctx, *, length):
    # Placeholder implementation - replace with actual sentence generation logic
    await ctx.send("Here's a generated sentence!")

@bot.command()
async def deleteall(ctx):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if ctx.author.guild_permissions.administrator:
        await ctx.channel.purge()
        await ctx.send(f"All messages deleted in {ctx.channel.mention}", delete_after=5)
        await log_channel.send(f"{ctx.author.mention} deleted all messages in {ctx.channel.mention}")
    else:
        await ctx.send("You do not have permission to use this command.", delete_after=5)

@bot.command()
async def kick(ctx, member: discord.Member, *, reason=None):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if ctx.author.guild_permissions.kick_members:
        await member.kick(reason=reason)
        await ctx.send(f"{member.mention} has been kicked from the server.")
        await log_channel.send(f"{ctx.author.mention} kicked {member.mention} from the server.")
    else:
        await ctx.send("You do not have permission to use this command.", delete_after=5)


@bot.command()
async def c_help(ctx):
    help_message = """
    **Available Commands:**
     `!hello`: Greets the user.
     `!anounceviddone <video_url>`: Announces a new video with the provided URL.
     `!anouncevidsoon <videotitle> <topic> <ETA> <give_or_take>`: Announces an upcoming video with details.
     `!generate_sentence <length>`: Generates a sentence of the specified length.
     `!deleteall`: Deletes all messages in the current channel (Admin only).
     `!kick <member> [reason]`: Kicks a member from the server (Admin only).
    """
    await ctx.send(help_message, delete_after=10)





bot.run(token, log_handler=handler, log_level=logging.DEBUG)
