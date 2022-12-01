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
# caches
pre_cache = {"00000000000000": "a"}
afk_cache = {0000000000: [False, "cuz I am"]}
giveaway_cache = {000000000: "False"}
birthday_cache = {(0000000000, 0000000000000): [9, 21]}
verify_cache = {0000000000: 00000000}  # guild_id, channel_id
color_cache = {000000000: ["white", "yellow"]}
level_cache = {(0000000000, 000000000): [1, 0, "blue"]}
user_cache = {00000000000000: [0, 0, 0, 0]}
banned_words_cache = {0000000000000: ["hi", "bye"]}  # guild_id, banned words
welcome_cache = {00000000000: "True"}
disabled_cache = {00000000000: ["command1", "command2"]}
activity = discord.Game(name="your mother | Thelp")
goodbye_cache = {00000000000: "True"}
welcome_msg_cache = {00000000000: ["msg", "indexes", "embed", "title", "image"]}
goodbye_msg_cache = {00000000000: ["msg", "indexes", "embed", "title", "image"]}
autorole_cache = {0000000000: ["rolename1", "rolename2"]}
sticky_cache = {(0000000000, 0000000000): [["sticky_name", "msg", "None"]]}


# metaclass
class MyCogs(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=get_prefix,
                         intents=intents, 
                         activity=activity, 
                         status=discord.Status.online)
        self.initial_extensions = ['cogs.admin',
                              'cogs.moderation',
                              'cogs.utility',
                              'cogs.stickiesandannouncements',
                              'cogs.welcome',
                              'cogs.colors',
                              'cogs.music',
                              'cogs.economy',
                              'cogs.leveling',
                              'cogs.fun',
                              'cogs.antispam',
                              'cogs.games']
    async def setup_hook(self):
        for extension in self.initial_extensions:
            await self.load_extension(extension)
        await bot.tree.sync()
    
    async def close(self):
        await super().close()
        await self.session.close()


# get current prefix
async def get_prefix(bot, message):
    try:
        prefix = pre_cache[message.guild.id]
    except KeyError:  # not cached
        guild = await bot.db.fetchval('SELECT guild_id FROM guilds WHERE guild_id = $1', message.guild.id)
        if guild:  # in database
            prefix = await bot.db.fetchval('SELECT prefix FROM guilds WHERE guild_id = $1', message.guild.id)
            pre_cache[message.guild.id] = prefix
        else:
            prefix = DEFAULT_PREFIX
    else:  # cached
        if pre_cache[message.guild.id] is None:
            prefix = DEFAULT_PREFIX
    return commands.when_mentioned_or(prefix)(bot, message)


bot = MyCogs()


# checking if commands are enabled or disabled per server
@bot.check
async def disabled_command(ctx):
    try:
        for command in disabled_cache[ctx.guild.id]:
            if command == ctx.command.qualified_name:
                raise commands.DisabledCommand
    except KeyError:  # not cached
        disabled = await bot.db.fetchval("SELECT command_name FROM disabled WHERE (guild_id, command_name) = ($1, $2)",
                                         ctx.guild.id, ctx.command.qualified_name)
        if not disabled:
            return True
        else:
            raise commands.DisabledCommand

    else:
        return True


@bot.listen()
async def on_command_error(ctx, error):
    if isinstance(error, commands.DisabledCommand):
        embed = discord.Embed(description="This command is disabled.", color=discord.Color.purple())
        return await ctx.send(embed=embed)
    elif isinstance(error, commands.errors.MissingPermissions):
        embed = discord.Embed(description="You do not have the required permissions for this command. :no_entry:",
                              color=discord.Color.purple())
        return await ctx.send(embed=embed)
    elif isinstance(error, commands.errors.MemberNotFound):
        embed = discord.Embed(description="Member not found. Please try again.", color=discord.Color.purple())
        return await ctx.send(embed=embed)
    elif isinstance(error, commands.errors.ChannelNotFound):
        embed = discord.Embed(description="Channel not found. Please try again.", color=discord.Color.purple())
        return await ctx.send(embed=embed)
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        embed = discord.Embed(
            description="You are missing a required argument, please do '<@995715935287648348> help' for help.",
            color=discord.Color.purple())
        return await ctx.send(embed=embed)
    else:
        raise error


############################## HELP ###########################################################
class MyHelpCommand(commands.HelpCommand):

    def __init__(self):
        super().__init__()

    async def send_bot_help(self, mapping):
        channel = self.get_destination()
        try:
            prefix = pre_cache[channel.guild.id]
        except KeyError:  # not pre_cached
            prefix = await bot.db.fetchval('SELECT prefix FROM guilds WHERE guild_id = $1', channel.guild.id)
            if not prefix:
                prefix = "T"
        cogs = []
        embeds = []
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
                if cog_name == "Admin":
                    page = "1"
                    emoji = ':gear:'
                    cogs += [f"**Page {page}:** {cog_name} {emoji}"]
                    embed1 = discord.Embed(title=f'**Page {page} :** __{cog_name}__  {emoji}',
                                           description=f"\n".join(command_signatures),
                                           color=discord.Color.purple())
                    embeds += [embed1]
                elif cog_name == "Moderation":
                    page = "2"
                    emoji = '<:ban:998413036425596978>'
                    cogs += [f"**Page {page}:** {cog_name} {emoji}"]
                    embed2 = discord.Embed(title=f'**Page {page} :** __{cog_name}__  {emoji}',
                                           description=f"\n".join(command_signatures),
                                           color=discord.Color.purple())
                    embeds += [embed2]
                elif cog_name == "Utility":
                    page = "3"
                    emoji = ':straight_ruler:'
                    cogs += [f"**Page {page}:** {cog_name} {emoji}"]
                    embed3 = discord.Embed(title=f'**Page {page} :** __{cog_name}__  {emoji}',
                                           description=f"\n".join(command_signatures),
                                           color=discord.Color.purple())
                    embeds += [embed3]
                elif cog_name == "StickiesAndAnnouncements":
                    page = "4"
                    cog_name = "Stickies and Announcements"
                    emoji = ':mega:   :notepad_spiral:'
                    cogs += [f"**Page {page}:** {cog_name} {emoji}"]
                    embed4 = discord.Embed(title=f'**Page {page} :** __{cog_name}__  {emoji}',
                                           description=f"\n".join(command_signatures),
                                           color=discord.Color.purple())
                    embeds += [embed4]
                elif cog_name == "Welcome":
                    page = "5"
                    emoji = '<:welcome:1001181138469007401>'
                    cogs += [f"**Page {page}:** {cog_name} {emoji}"]
                    embed5 = discord.Embed(title=f'**Page {page} :** __{cog_name}__  {emoji}',
                                           description=f"\n".join(command_signatures),
                                           color=discord.Color.purple())
                    embeds += [embed5]
                elif cog_name == "Colors":
                    page = "6"
                    emoji = ':art:'
                    cogs += [f"**Page {page}:** {cog_name} {emoji}"]
                    embed6 = discord.Embed(title=f'**Page {page} :** __{cog_name}__  {emoji}',
                                           description=f"\n".join(command_signatures),
                                           color=discord.Color.purple())
                    embeds += [embed6]
                elif cog_name == "Music":
                    page = "7"
                    emoji = '<:musicnotes:996810296956026910>'
                    cogs += [f"**Page {page}:** {cog_name} {emoji}"]
                    embed7 = discord.Embed(title=f'**Page {page} :** __{cog_name}__  {emoji}',
                                           description=f"\n".join(command_signatures),
                                           color=discord.Color.purple())
                    embeds += [embed7]
                elif cog_name == "Economy":
                    page = "8"
                    emoji = '<:money:996812142021976186>'
                    cogs += [f"**Page {page} :** {cog_name} {emoji}"]
                    embed8 = discord.Embed(title=f'**Page {page}:** __{cog_name}__  {emoji}',
                                           description=f"\n".join(command_signatures),
                                           color=discord.Color.purple())
                    embeds += [embed8]
                elif cog_name == "Fun":
                    emoji = ':tada:'
                    page = '10'
                    cogs += [f"**Page {page} :** {cog_name} {emoji}"]
                    embed10 = discord.Embed(title=f'**Page {page}:** __{cog_name}__  {emoji}',
                                            description=f"\n".join(command_signatures),
                                            color=discord.Color.purple())
                    embeds += [embed10]
                elif cog_name == "Levels":
                    page = "9"
                    emoji = ':star_struck:'
                    cogs += [f"**Page {page} :** {cog_name} {emoji}"]
                    embed9 = discord.Embed(title=f'**Page {page}:** __{cog_name}__  {emoji}',
                                           description=f"\n".join(command_signatures),
                                           color=discord.Color.purple())
                    embeds += [embed9]
                elif cog_name == "Games":
                    page = "11"
                    emoji = ':game_die:'
                    cogs += [f"**Page {page} :** {cog_name} {emoji}"]
                    embed11 = discord.Embed(title=f'**Page {page}:** __{cog_name}__  {emoji}',
                                            description=f"\n".join(command_signatures),
                                            color=discord.Color.purple())
                    embeds += [embed11]

        embed0 = discord.Embed(
            title="**Help Page:**",
            description="**Do '<@995715935287648348> prefix' if you forgot the prefix of your server.**\n\n" + "\n".join(cogs), color=discord.Color.purple())
        embeds.insert(0, embed0)
        msg = await channel.send(embed=embed0)
        emojis = ["◀", "▶", "<:DigitalZero:1004594806779023505>",
                  "<:DigitalNumber1:1004591294863130734>", "<:DigitalNumberTwo:1004591655631982612>",
                  "<:DigitalThree:1004591709553967154>", "<:DigitalFour:1004591767150145606>",
                  "<:DigitalFive:1004591813065191524>", "<:DigitalSix:1004591856652390420>",
                  "<:DigitalSeven:1004591904391974993>", "<:DigitalEight:1004592050269847642>",
                  "<:DigitalNine:1004592099439689768>", "<:DigitalTen:1004593737621577728>",
                  "<:DigitalEleven:1004592560653746226>"]
        curpage = 0
        for emoji in emojis:
            await msg.add_reaction(emoji)
        while True:
            def check(reaction, user):
                return str(reaction.emoji) in emojis and user != bot.user
            try:
                reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
            except asyncio.TimeoutError:
                break
            else:
                await msg.remove_reaction(reaction.emoji, user)
                for i in range(len(emojis)):
                    if emojis[i] == str(reaction.emoji):
                        if i > 1:
                            msg = await msg.edit(embed=embeds[i - 2])
                            curpage = i - 2
                        else:
                            if i == 0:
                                if curpage > 0:
                                    curpage = curpage - 1
                                    msg = await msg.edit(embed=embeds[curpage])
                            if i == 1:
                                if curpage < 11:
                                    curpage = curpage + 1
                                    msg = await msg.edit(embed=embeds[curpage])


# redefining caches
bot.help_command = MyHelpCommand()
bot.pre_cache = pre_cache
bot.verify_cache = verify_cache
bot.afk_cache = afk_cache
bot.giveaway_cache = giveaway_cache
bot.birthday_cache = birthday_cache
bot.color_cache = color_cache
bot.level_cache = level_cache
bot.user_cache = user_cache
bot.banned_words_cache = banned_words_cache
bot.disabled_cache = disabled_cache
bot.welcome_cache = welcome_cache
bot.welcome_msg_cache = welcome_msg_cache
bot.goodbye_cache = goodbye_cache
bot.goodbye_msg_cache = goodbye_msg_cache
bot.autorole_cache = autorole_cache
bot.sticky_cache = sticky_cache


# Log in text
@bot.event
async def on_ready():
    print("Logged in as: " + bot.user.name)
    

################################# Create Database #############################################
logging.basicConfig(level=logging.INFO)


async def main():
    async with aiohttp.ClientSession() as ahttp, \
            asyncpg.create_pool(dsn='postgres://postgres:postgres@localhost:5432/TreehouseBot') as db_pool:
        bot.ahttp = ahttp
        bot.db = db_pool
        await bot.start(TOKEN)


asyncio.run(main())

