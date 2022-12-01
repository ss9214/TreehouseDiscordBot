import os
import discord
from discord.ext import commands,tasks
import random
import datetime
import asyncio
import asyncpg


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # self.birthday_check_loop.add_exception_type(asyncpg.PostgresConnectionError)
        # self.birthday_check_loop.start()

    
    @commands.hybrid_command(description="See what users have a given role.", with_app_command=True)
    @commands.guild_only()
    async def hasrole(self, ctx, role_name):
        guild_roles = ctx.guild.roles
        members = ctx.guild.members
        guild_role = None
        for role in guild_roles:
            if role.name == role_name:
                guild_role = role
        if not guild_role:
            return await ctx.reply(f"{role_name} is not the name of a role in {ctx.guild.name}")
        users = ""
        user_count = 0
        real_user_count = 0
        for member in members:
            member_roles = member.roles
            for role in member_roles:
                if role == guild_role:
                    user_count += 1
                    real_user_count += 1
                    users += f"{member.name}#{member.discriminator}\n"
                    if user_count == 30:
                        user_count = 0
        if users != "":
            users += f"\nUser count: {real_user_count}"
        else:
            embed = discord.Embed(description="There are no users with the given role.", color=discord.Color.purple())
            return await ctx.reply(embed=embed)
        embed = discord.Embed(title=f"__Users with {role_name} role__", description=users, color=discord.Color.purple())
        return await ctx.reply(embed=embed)

    @commands.hybrid_command(description="Verify youself if you aren't already verified.", with_app_command=True)
    @commands.guild_only()
    async def verify(self, ctx):
        author_roles = ctx.author.roles
        try:
            ctx.bot.verify_cache[ctx.guild.id]
        except KeyError:  # not cached
            verify_channel = await self.bot.db.fetchval('SELECT verify_channel FROM verify WHERE guild_id = $1',
                                                        ctx.guild.id)
            if not verify_channel:  # not in database
                msg = await ctx.reply("Verification is not setup in this server. Please contact staff.")
                await asyncio.sleep(6)
                await ctx.message.delete()
                return await msg.delete()
            else:  # in database
                if ctx.channel.id != verify_channel:
                    msg = await ctx.reply("You are not in the correct channel to use this command")
                    await asyncio.sleep(4)
                    await ctx.message.delete()
                    return await msg.delete()
                elif ctx.channel.id == verify_channel:
                    pass
        templist = ["unverified", "Unverified"]
        for role in author_roles:
            if role.name in templist:
                await ctx.author.remove_roles(role)
                msg = await ctx.reply("You are now verified.")
                await asyncio.sleep(4)
                await ctx.message.delete()
                return await msg.delete()

        msg = await ctx.reply("You are already verified.")
        await asyncio.sleep(4)
        await ctx.message.delete()
        return await msg.delete()

    # @tasks.loop(minutes=1.0)
    # async def birthday_check_loop(self):
    #     now = datetime.datetime.now().strftime("%H:%M")
    #     if now == "00:00":
    #         for guild in self.bot.guilds:
    #             for member in guild.members:
    #                 self.check_for_birthday(member, guild)
    
    # @birthday_check_loop.before_loop
    # async def before_birthday_check_loop(self):
    #     await self.bot.wait_until_ready()

    # async def check_for_birthday(self, member, guild):
    #     now = datetime.datetime.now()
    #     nowmonth = now.month
    #     nowday = now.day

    #     while not self.is_closed():
    #         datamonth = await self.bot.db.fetchval('SELECT month FROM Giveaway WHERE (month,day) = ($1, $2)', nowmonth,
    #                                                nowday)
    #         dataday = await self.bot.db.fetchval('SELECT day FROM Giveaway WHERE (month,day) = ($1, $2)', nowmonth,
    #                                              nowday)
    #         if datamonth and dataday:
    #             try:
    #                 await self.bot.get_user(member).send("Happy birthday!")
    #             except:
    #                 pass
    #             success = False
    #             index = 0
    #             while not success:
    #                 try:
    #                     await guild.channels[index].send(f"Happy birthday to <@{member.id}!")
    #                 except discord.Forbidden:
    #                     index += 1
    #                 except AttributeError:
    #                     index += 1
    #                 except IndexError:
    #                     pass
    #                 else:
    #                     success = True
    #         await asyncio.sleep(60 * 60 * 24)

    # @commands.hybrid_command(description="Set your birthday!", with_app_command=True)
    # @commands.guild_only()
    # async def setbirthday(self, ctx, bday=None):
    #     member = ctx.author.id
    #     guild = ctx.guild.id
    #     if not bday:
    #         return await ctx.reply("Please include your birthday. Please use format: !setbirthday 9/7.")
    #     list = bday.split("/")
    #     try:
    #         int(list[0])
    #     except TypeError:
    #         await ctx.reply("Invalid date. Please use format: !setbirthday 9/7.")
    #         return
    #     try:
    #         int(list[1])
    #     except TypeError:
    #         return await ctx.reply("Invalid date. Please use format: !setbirthday 9/7.")
    #     list[0] = int(list[0])
    #     list[1] = int(list[1])
    #     if list[0] > 13 or list[0] < 1:
    #         await ctx.reply("Invalid date. Please use format: !setbirthday 9/7.")
    #         return
    #     else:
    #         pass

    #     if list[0] in (1, 3, 5, 7, 8, 10, 12):
    #         if list[1] > 31 or list[1] < 1:
    #             await ctx.reply("Invalid date. Please use format: !setbirthday 9/7.")
    #             return
    #         else:
    #             pass
    #     elif list[0] in (4, 6, 9, 11):
    #         if list[1] > 30 or list[1] < 1:
    #             await ctx.reply("Invalid date. Please use format: !setbirthday 9/7.")
    #             return
    #     elif list[0] == 2:
    #         if list[1] > 29 or list[1] < 1:
    #             await ctx.reply("Invalid date. Please use format: !setbirthday 9/7.")
    #             return
    #         else:
    #             pass
    #     else:
    #         await ctx.reply("Invalid date. Please use format: !setbirthday 9/7.")
    #         return
    #     list = bday.split("/")
    #     month = int(list[0])
    #     day = int(list[1])
    #     try:
    #         ctx.bot.birthday_cache[(member, guild)]
    #     except KeyError:  # not cached
    #         datauser = await self.bot.db.fetchval('SELECT user_id FROM birthdays WHERE (user_id, guild_id) = ($1, $2)',
    #                                               member, guild)
    #         if not datauser:  # not in database
    #             await self.bot.db.execute(
    #                 'INSERT INTO birthdays (user_id, guild_id, month, day) VALUES ($1, $2, $3, $4)', member, guild,
    #                 month, day)
    #             ctx.bot.birthday_cache[(member, guild)] = [month, day]
    #         elif datauser:
    #             await self.bot.db.execute(
    #                 'UPDATE birthdays SET (month, day) = ($1, $2) WHERE (guild_id, user_id) = ($3, $4)', month, day,
    #                 guild, member)
    #             ctx.bot.birthday_cache[(member, guild)] = [month, day]
    #     else:  # cached
    #         ctx.bot.birthday_cache[(member, guild)] = [month, day]
    #         await self.bot.db.execute(
    #             'UPDATE birthdays SET (month, day) = ($1, $2) WHERE (guild_id, user_id) = ($3, $4)', month, day,
    #             guild, member)
    #     return await ctx.reply(f"Your birthday has been set to {month}/{day}")

    # @commands.command(description="Host a giveaway! Time is in hours!")
    # @commands.guild_only()
    # async def giveaway(self, ctx, item: str = None, time=None):
    #     if not time:
    #         return await ctx.send(
    #             "Please include the time in hours and the item you are giving away.\nFormat: !giveaway <prize> <time>")
    #     try:
    #         time = int(time)
    #     except ValueError:
    #         return await ctx.send("Time must be a number lmao\nFormat: !giveaway <prize> <time>")
    #     else:
    #         embed = discord.Embed(title=f"{ctx.author.name}#{ctx.author.discriminator} is hosting a giveaway!",
    #                               color=discord.Color.purple())
    #         embed.add_field(name="Prize:", value=item)
    #         embed.add_field(name="Ends:", value=f"{time} hours from now!")
    #         embed.set_footer(text="React below to enter!")
    #         msg = await ctx.send(embed=embed)
    #         await msg.add_reaction("🎉")
    #         try:
    #             ctx.bot.giveaway_cache[ctx.guild.id]
    #         except KeyError:  # not cached
    #             data = await self.bot.db.fetchval('SELECT giveaway FROM Giveaway WHERE guild_id = $1', ctx.guild.id)
    #             if data == "True":  # in database as true
    #                 return await ctx.send("You already have an active giveaway. Please try again when it is over.")
    #             elif data == "False":  # in database as false
    #                 await self.bot.db.fetchval('UPDATE Giveaway SET giveaway = $1 WHERE guild_id = $2', "True",
    #                                            ctx.guild.id)
    #                 ctx.bot.giveaway_cache[ctx.guild.id] = "True"
    #             else:  # not in database
    #                 await self.bot.db.fetchval('INSERT INTO Giveaway (giveaway, guild_id) VALUES ($1, $2)', "True",
    #                                            ctx.guild.id)
    #                 ctx.bot.giveaway_cache[ctx.guild.id] = "True"
    #         # now it is cached
    #         await asyncio.sleep(time * 3600)
    #         ctx.bot.giveaway_cache[ctx.guild.id] = "False"
    #         new_msg = await ctx.channel.fetch_message(msg.id)
    #         reactions = new_msg.reactions
    #         users = [user async for user in reactions[0].users()]
    #         winner = random.choice(users)
    #         while winner == self.bot.user:
    #             winner = random.choice(users)
    #         await ctx.send(f"Congratulations {winner.mention}! You have won {item}!")

    @commands.hybrid_command(aliases=['pre'], description="Check what the current prefix of this server is.", with_app_command=True)
    @commands.guild_only()
    async def prefix(self, ctx):
        try:
            ctx.bot.cache[ctx.guild.id]
        except KeyError:  # not cached
            prefix = await self.bot.db.fetchval('SELECT prefix FROM guilds WHERE guild_id = $1', ctx.guild.id)
            if not prefix:  # if guild is not in database
                await ctx.reply("The prefix of this server is T")
            else:
                await ctx.reply(f"The prefix of this server is {prefix}")
        else:  # cached
            await ctx.reply(f"The prefix of this server is {ctx.bot.cache[ctx.guild.id]}")

    @commands.Cog.listener("on_message")
    @commands.guild_only()
    async def afk_ping(self, message):
        if message.author.bot:
            return
        data = await self.bot.db.fetchval('SELECT afk FROM afk WHERE user_id = $1', message.author.id)
        if data:
            await message.channel.send(f"{message.author.mention}: Welcome back from your afk!")
            await self.bot.db.execute('UPDATE afk SET afk = $1 WHERE user_id = $2', False, message.author.id)
        if message.mentions:
            for mention in message.mentions:
                reason = await self.bot.db.fetchval('SELECT reason FROM afk where user_id = $1', mention.id)
                afk = await self.bot.db.fetchval('SELECT afk FROM afk WHERE user_id = $1', mention.id)
                if afk is True:
                    return await message.channel.send(f"{mention} is afk for reason: {reason}")
                else:
                    return

    # afk command
    @commands.hybrid_command(description="Set yourself as afk.", with_app_command=True)
    @commands.guild_only()
    async def afk(self, ctx, reason=None):
        try:
            ctx.bot.afk_cache[ctx.author.id]
        except KeyError:  # not in cache
            in_db = await self.bot.db.fetchval('SELECT user_id FROM afk WHERE user_id = $1', ctx.author.id)
            if not in_db:
                if reason:
                    await self.bot.db.execute('INSERT INTO afk (user_id, afk, reason) VALUES ($1, $2, $3)',
                                              ctx.author.id, True,
                                              reason)
                    ctx.bot.afk_cache[ctx.author.id] = [True, reason]
                    return await ctx.reply("You are now afk.")
                else:
                    return await ctx.reply("Give a reason.")
            else:
                afk = await self.bot.db.fetchval('SELECT afk FROM afk WHERE user_id = $1', ctx.author.id)
                if afk:
                    return
                elif not afk:
                    if reason:
                        await self.bot.db.execute('UPDATE afk SET (afk, reason) = ($1, $2) WHERE user_id = $3',
                                                  True, reason, ctx.author.id)
                        return await ctx.reply("You are now afk.")
                    else:
                        return await ctx.reply("Give a reason.")

        else:  # in cache
            if ctx.bot.afk_cache[ctx.author.id][0]:
                return
            elif not ctx.bot.afk_cache[ctx.author.id][0]:
                if reason:
                    ctx.bot.afk_cache[ctx.author.id] = [True, reason]
                    return await ctx.reply("You are now afk.")
                else:
                    return await ctx.reply("Give a reason.")

    @commands.hybrid_command(description="Check how many servers the bot is in.", with_app_command=True)
    @commands.guild_only()
    async def servers(self, ctx):
        await ctx.reply(f"{ctx.author.mention}, I'm in {len(self.bot.guilds)} servers!")

    # @commands.hybrid_command(description="Set up reaction roles in your server.", with_app_command=True)
    # @commands.guild_only()
    # async def reaction_role(self, ctx):
    #     def check(m):
    #         return m.author == ctx.author and m.channel == ctx.channel
    #     await ctx.reply(f"Please provide the message id for the message you are adding reaction roles for.")
    #     msg = await self.bot.wait_for('message', check=check)
    #     msg = msg.content
    #     channel_id = None
    #     try:
    #         msg = int(msg)
    #     except ValueError:
    #         return await ctx.reply(embed=discord.Embed(description="That is not a valid message id.", color=discord.Color.purple()))
    #     for channel in ctx.guild.channels:
    #         if channel.id == msg.channel.id:
    #             channel_id = channel.id
    #             break
    #     if not channel_id:
    #         return await ctx.reply(embed=discord.Embed(description="That is not a valid message id.", color=discord.Color.purple()))
    #     while True:
    #         await ctx.reply(embed=discord.Embed(description="Please provide a role ID. Say 'done' if you're done."))
    #         try:
    #             role_id = await self.bot.wait_for('message', check=check)
    #         except asyncio.TimeoutError:
    #             msg = await ctx.reply(embed=discord.Embed(description="You have timed out."))
    #             await asyncio.sleep(5)
    #             await msg.delete()
    #         await ctx.reply(embed=discord.Embed(description="Please provide the reaction for the role. Say 'done' if you're done."))
    #         try:
    #             reaction = await self.bot.wait_for('message', check=check)
    #         except asyncio.TimeoutError:
    #             timeout_msg = await ctx.reply(embed=discord.Embed(description="You have timed out."))
    #             await asyncio.sleep(5)
    #             await timeout_msg.delete()
        

async def setup(bot):
    await bot.add_cog(Utility(bot))
