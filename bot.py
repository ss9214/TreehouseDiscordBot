# bot.py
# imports
# run bot with python Desktop\\Python\\DiscordBot\\bot.py in command prompt
import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
import asyncpg
import asyncio
import aiohttp
import logging
from discord import Permissions

load_dotenv()

# token and guild
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
DEFAULT_PREFIX = 'T'
# intents
intents = discord.Intents.all()
cache = {"00000000000000": "a"}
activity = discord.Game(name="ur mom | Thelp")


# metaclass
class MyCogs(commands.Bot):
    async def setup_hook(self):
        initial_extensions = ['cogs.admin',
                              'cogs.moderation',
                              'cogs.utility',
                              'cogs.music',
                              'cogs.economy',
                              'cogs.fun',
                              'cogs.colors',
                              'cogs.leveling',
                              'cogs.antispam',
                              'cogs.giustaff']
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


bot = MyCogs(get_prefix, intents=intents, activity=activity, status=discord.Status.online)


############################## HELP ###########################################################
class MyHelpCommand(commands.HelpCommand):

    def __init__(self):
        super().__init__()

    async def send_bot_help(self, mapping):
        em = discord.Embed(title="Help",
                           description=f"**Do '<@995715935287648348> prefix' if you forgot the prefix of your server.**",
                           color=discord.Color.purple())
        channel = self.get_destination()
        try:
            prefix = cache[channel.guild.id]
        except KeyError:  # not cached
            prefix = await bot.db.fetchval('SELECT prefix FROM guilds WHERE guild_id = $1', channel.guild.id)
            if not prefix:
                prefix = "T"
        for cog, commands in mapping.items():
            command_signatures = [command.name for command in commands]
            for i in range(len(command_signatures)):
                string_a = bot.get_command(command_signatures[i]).signature
                string_b = string_a.replace("=None", "")
                string_c = string_b.replace("[", "<")
                string_d = string_c.replace("]", ">")
                command = command_signatures[i]
                command_signatures[i] = "**" + prefix + command_signatures[i] + "**"
                command_signatures[i] += f' {string_d} - {bot.get_command(command).description}'
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
                elif cog_name == "Levels":
                    emoji = ':star_struck:'
                elif cog_name == "Utility":
                    emoji = ':straight_ruler:'
                elif cog_name == "Colors":
                    emoji = ':art:'
                elif cog_name == "Moderation":
                    emoji = '<:ban:998413036425596978>'
                if cog_name != "No Category" and cog_name != "Giustaff":
                    em.add_field(name=f'__{cog_name}__  {emoji}', value=f"\n".join(command_signatures), inline=False)
        await channel.send(embed=em)


bot.help_command = MyHelpCommand()
bot.cache = cache


# Log in text
@bot.event
async def on_ready():
    print("Logged in as: " + bot.user.name)


# welcome message
@bot.event
async def on_member_join(member):
    guild = member.guild
    guild_roles = guild.roles
    guild_channels = guild.channels
    verify_channel = await bot.db.fetchval('SELECT verify_channel FROM verify WHERE guild_id = $1',
                                           guild.id)
    if not verify_channel:  # not in database
        pass
    else:
        unverified_role = None
        templist = ["Unverified", "unverified"]
        for role in guild_roles:
            if role.name in templist:
                unverified_role = role
                break
        if not unverified_role:
            unverified_role = await guild.create_role(name="Unverified", permissions=Permissions(view_channel=True))
            overwrites = {unverified_role: discord.PermissionOverwrite(view_channel=False)}
            templist = ["verification", "Verification", "rules", "Rules"]
            for channel in guild_channels:
                if not channel.permissions_synced:
                    if channel.name not in templist:
                        await channel.edit(overwrites=overwrites)
        await member.add_roles(unverified_role)
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
bg_task = loop.create_task(self.check_for_birthday())
