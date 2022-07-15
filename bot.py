# bot.py
# imports
import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
import asyncpg
import asyncio
import aiohttp
import logging


load_dotenv()

# token and guild
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
DEFAULT_PREFIX = '!'
# intents
intents = discord.Intents.all()
cache = {"00000000000000": "!"}
activity = discord.Game(name="ur mom")


# metaclass
class MyCogs(commands.Bot):
    async def setup_hook(self):
        initial_extensions = ['cogs.music',
                              'cogs.fun',
                              'cogs.economy',
                              'cogs.admin',
                              'cogs.leveling',
                              'cogs.utility',
                              'cogs.antispam',
                              'cogs.colors']
        for extension in initial_extensions:
            await self.load_extension(extension)


# get current prefix
async def get_prefix(bot, message):
    try:
        prefix = cache[message.guild.id]
    except KeyError:  # not cached
        guild = await bot.db.fetchval('SELECT guild_id FROM guilds WHERE guild_id = $1', message.guild.id)
        if guild:  # in database
            prefix = await bot.db.fetchval('SELECT prefix FROM guilds WHERE guild_id = $1', message.guild.id)
            cache[message.guild.id] = prefix
        else:
            prefix = DEFAULT_PREFIX
    else:  # cached
        if cache[message.guild.id] is None:
            prefix = DEFAULT_PREFIX
    return commands.when_mentioned_or(prefix)(bot, message)


bot = MyCogs(get_prefix, intents=intents, activity=activity, status=discord.Status.idle)
bot.cache = cache
spam_dict = {0000000000: ["word", "word", "word", "word"]}


# Log in text
@bot.event
async def on_ready():
    print("Logged in as: " + bot.user.name)


# welcome message
@bot.event
async def on_member_join(member):
    guild = member.guild
    if guild.system_channel is not None:
        await guild.system_channel.send(
            f'Hi {member.mention}! Welcome to {guild.name}!'
        )


############################## HELP ###########################################################
class MyHelp(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Help")
        for cog, commands in mapping.items():
            command_signatures = [self.get_command_signature(c) for c in commands]
            if command_signatures:
                cog_name = getattr(cog, "qualified_name", "No Category")
                emoji = ""
                if cog_name == "Music":
                    emoji = '<:musicnotes:996810296956026910>'
                elif cog_name == "Fun":
                    emoji = ':tada:'
                elif cog_name == "Economy":
                    emoji = '<:money:996812142021976186>'
                elif cog_name == "Admin":
                    emoji = ':gear:'
                elif cog_name == "Leveling":
                    emoji = ':star_struck:'
                elif cog_name == "Utility":
                    emoji = ':straight_ruler:'
                elif cog_name == "Colors":
                    emoji = ':art:'
                embed.add_field(name=f'__{cog_name}__  {emoji}', value="\n".join(command_signatures), inline=True)
        channel = self.get_destination()
        await channel.send(embed=embed)


bot.help_command = MyHelp()

################################# Create Database #############################################
logging.basicConfig(level=logging.INFO)


async def main():
    async with aiohttp.ClientSession() as ahttp, \
            asyncpg.create_pool(dsn='postgres://postgres:postgres@localhost:5432/TreehouseBot') as db_pool:
        bot.ahttp = ahttp
        bot.db = db_pool
        await bot.start(TOKEN)


asyncio.run(main())
