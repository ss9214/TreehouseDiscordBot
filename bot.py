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

##################### prefix stuff #################################
cache = {995741045851689010: "!"}


# get current prefix
async def get_prefix(bot, message):
    for key, value in cache.items():
        try:
            prefix = cache[key]
        except KeyError:  # not cached
            prefix = await bot.db.fetchval('SELECT prefix FROM guilds WHERE guild_id = $1', message.guild.id)
            if prefix is None:
                prefix = DEFAULT_PREFIX
                cache[message.guild.id] = prefix
        else:  # cached
            if prefix is None:
                prefix = DEFAULT_PREFIX
        return commands.when_mentioned_or(prefix)(bot, message)


################################ Main Code #####################################################
class MyCogs(commands.Bot):
    async def setup_hook(self):
        initial_extensions = ['cogs.music',
                              'cogs.fun',
                              'cogs.economy',
                              'cogs.admin',
                              'cogs.exp']
        for extension in initial_extensions:
            await self.load_extension(extension)


# set prefix
bot = MyCogs(command_prefix=get_prefix, intents=intents)


# change prefix
@bot.command(aliases=['setpre'], help="Change the prefix of the server.")
@commands.has_permissions(administrator=True)
async def setprefix(ctx, new_prefix):
    await bot.db.execute('UPDATE guilds SET prefix = $1 WHERE guild_id = $2', new_prefix, ctx.guild.id)
    cache[ctx.guild.id] = new_prefix
    await ctx.send("Prefix Updated")


# check prefix
@bot.command(aliases=['pre'], help="Check what the current prefix of this server is.")
@commands.guild_only()
async def prefix(ctx):
    for key in cache.keys():
        try:
            ctx.guild.id = key
        except KeyError:  # not cached
            await ctx.send("The prefix of this server is !")
        else:  # cached
            await ctx.send(f"The prefix of this server is {cache[ctx.guild.id]}")


################################ Main Code #####################################################
class MyCogs(commands.Bot):
    async def setup_hook(self):
        initial_extensions = ['cogs.music',
                              'cogs.fun']
        for extension in initial_extensions:
            await self.load_extension(extension)


bot = MyCogs(command_prefix=get_prefix, intents=intents)
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


################################# Create Database #############################################
logging.basicConfig(level=logging.INFO)


async def main():
    async with aiohttp.ClientSession() as ahttp, \
            asyncpg.create_pool(dsn='postgres://postgres:postgres@localhost:5432/TreehouseBot') as db_pool:
        bot.ahttp = ahttp
        bot.db = db_pool
        await bot.start(TOKEN)


asyncio.run(main())

