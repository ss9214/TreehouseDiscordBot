import os
import discord
from discord.ext import commands
import random
import datetime
import asyncio

afk_cache = {0000000000: [False, "cuz I am"]}
giveaway_cache = {000000000: "False"}
birthday_cache = {(0000000000, 0000000000000): [9, 21]}
verify_cache = {0000000000: 00000000}  # guild_id, channel_id


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Setup the verification system for your server. ")
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def set_verification(self, ctx):
        prefix = await self.bot.db.fetchval('SELECT prefix FROM guilds WHERE guild_id = $1', ctx.guild.id)
        if not prefix:
            prefix = "T"
        em = discord.Embed(title="Verification!!", description=f"Please type {prefix}verify below to become verified.")
        guild_channels = ctx.guild.channels
        templist = ["verify", "verification"]
        verify_channel = None
        for channel in guild_channels:
            if channel.name in templist:
                verify_channel = channel
                break
        if not verify_channel:
            verify_channel = await ctx.guild.create_text_channel("verification")
        try:
            verify_cache[ctx.guild.id]
        except KeyError:  # not cached
            db_verify_channel = await self.bot.db.fetchval('SELECT verify_channel FROM verify WHERE guild_id = $1',
                                                           ctx.guild.id)
            if not db_verify_channel:  # not in db
                await self.bot.db.execute('INSERT INTO verify (guild_id, verify_channel) VALUES ($1, $2)', ctx.guild.id,
                                          verify_channel.id)
                verify_cache[ctx.guild.id] = verify_channel.id
            else:  # in db
                await self.bot.db.execute('UPDATE verify SET verify_channel = $1 WHERE guild_id = $2',
                                          verify_channel.id, ctx.guild.id)
                verify_cache[ctx.guild.id] = verify_channel.id

        db_verify_channel = await self.bot.db.fetchval('SELECT verify_channel FROM verify WHERE guild_id = $1',
                                                       ctx.guild.id)
        if verify_channel.id == db_verify_channel:
            return await ctx.send("You already have a verification system setup in this channel.")
        else:
            await verify_channel.send(embed=em)

    @commands.command(description="Verify youself if you aren't already verified.")
    @commands.guild_only()
    async def verify(self, ctx):
        author_roles = ctx.author.roles
        try:
            verify_cache[ctx.guild.id]
        except KeyError:  # not cached
            verify_channel = await self.bot.db.fetchval('SELECT verify_channel FROM verify WHERE guild_id = $1',
                                                        ctx.guild.id)
            if not verify_channel:  # not in database
                msg = await ctx.send("Verification is not setup in this server. Please contact staff.")
                await asyncio.sleep(6)
                return await msg.delete()
            else:  # in database
                if ctx.channel.id != verify_channel:
                    return await ctx.send("You are not in the correct channel to use this command")
                elif ctx.channel.id == verify_channel:
                    pass
        templist = ["unverified", "Unverified"]
        for role in author_roles:
            if role.name in templist:
                await ctx.author.remove_roles(role)
                msg = await ctx.send("You are now verified.")
                await asyncio.sleep(4)
                return await msg.delete()

        msg = await ctx.send("You are already verified.")
        await asyncio.sleep(4)
        return await msg.delete()

    async def check_for_birthday(self):
        await self.wait_until_ready()
        now = datetime.datetime.now()
        nowmonth = now.month
        nowday = now.day

        while not self.is_closed():
            datamonth = await self.bot.db.fetchval('SELECT month FROM Giveaway WHERE (month,day) = ($1, $2)', nowmonth,
                                                   nowday)
            dataday = await self.bot.db.fetchval('SELECT day FROM Giveaway WHERE (month,day) = ($1, $2)', nowmonth,
                                                 nowday)
            if datamonth and dataday:
                try:
                    await bot.get_user(member).send("Happy birthday!")
                except:
                    pass
                success = False
                index = 0
                while not success:
                    try:
                        await guild.channels[index].send(f"Happy birthday to <@{member.id}!")
                    except discord.Forbidden:
                        index += 1
                    except AttributeError:
                        index += 1
                    except IndexError:
                        pass
                    else:
                        success = True
            await asyncio.sleep(60 * 60 * 24)

    @commands.command(description="Set your birthday!")
    @commands.guild_only()
    async def setbirthday(self, ctx, bday=None):
        member = ctx.author.id
        guild = ctx.guild.id
        if not bday:
            return await ctx.send("Please include your birthday. Please use format: !setbirthday 9/7.")
        list = bday.split("/")
        try:
            int(list[0])
        except TypeError:
            await ctx.send("Invalid date. Please use format: !setbirthday 9/7.")
            return
        try:
            int(list[1])
        except TypeError:
            return await ctx.send("Invalid date. Please use format: !setbirthday 9/7.")
        list[0] = int(list[0])
        list[1] = int(list[1])
        if list[0] > 13 or list[0] < 1:
            await ctx.send("Invalid date. Please use format: !setbirthday 9/7.")
            return
        else:
            pass

        if list[0] in (1, 3, 5, 7, 8, 10, 12):
            if list[1] > 31 or list[1] < 1:
                await ctx.send("Invalid date. Please use format: !setbirthday 9/7.")
                return
            else:
                pass
        elif list[0] in (4, 6, 9, 11):
            if list[1] > 30 or list[1] < 1:
                await ctx.send("Invalid date. Please use format: !setbirthday 9/7.")
                return
        elif list[0] == 2:
            if list[1] > 29 or list[1] < 1:
                await ctx.send("Invalid date. Please use format: !setbirthday 9/7.")
                return
            else:
                pass
        else:
            await ctx.send("Invalid date. Please use format: !setbirthday 9/7.")
            return
        list = bday.split("/")
        month = int(list[0])
        day = int(list[1])
        try:
            birthday_cache[(member, guild)]
        except KeyError:  # not cached
            datauser = await self.bot.db.fetchval('SELECT user_id FROM birthdays WHERE (user_id, guild_id) = ($1, $2)',
                                                  member, guild)
            if not datauser:  # not in database
                await self.bot.db.execute(
                    'INSERT INTO birthdays (user_id, guild_id, month, day) VALUES ($1, $2, $3, $4)', member, guild,
                    month, day)
                birthday_cache[(member, guild)] = [month, day]
            elif datauser:
                await self.bot.db.execute(
                    'UPDATE birthdays SET (month, day) = ($1, $2) WHERE (guild_id, user_id) = ($3, $4)', month, day,
                    guild, member)
                birthday_cache[(member, guild)] = [month, day]
        else:  # cached
            birthday_cache[(member, guild)] = [month, day]
            await self.bot.db.execute(
                'UPDATE birthdays SET (month, day) = ($1, $2) WHERE (guild_id, user_id) = ($3, $4)', month, day,
                guild, member)
        return await ctx.send(f"Your birthday has been set to {month}/{day}")

    @commands.command(description="Host a giveaway! Time is in hours!")
    @commands.guild_only()
    async def giveaway(self, ctx, item: str = None, time=None):
        if not time:
            return await ctx.send(
                "Please include the time in hours and the item you are giving away.\nFormat: !giveaway <prize> <time>")
        try:
            time = int(time)
        except ValueError:
            return await ctx.send("Time must be a number lmao\nFormat: !giveaway <prize> <time>")
        else:
            embed = discord.Embed(title=f"{ctx.author.name}#{ctx.author.discriminator} is hosting a giveaway!",
                                  color=discord.Color.purple())
            embed.add_field(name="Prize:", value=item)
            embed.add_field(name="Ends:", value=f"{time} hours from now!")
            embed.set_footer(text="React below to enter!")
            msg = await ctx.send(embed=embed)
            await msg.add_reaction("🎉")
            try:
                giveaway_cache[ctx.guild.id]
            except KeyError:  # not cached
                data = await self.bot.db.fetchval('SELECT giveaway FROM Giveaway WHERE guild_id = $1', ctx.guild.id)
                if data == "True":  # in database as true
                    return await ctx.send("You already have an active giveaway. Please try again when it is over.")
                elif data == "False":  # in database as false
                    await self.bot.db.fetchval('UPDATE Giveaway SET giveaway = $1 WHERE guild_id = $2', "True",
                                               ctx.guild.id)
                    giveaway_cache[ctx.guild.id] = "True"
                else:  # not in database
                    await self.bot.db.fetchval('INSERT INTO Giveaway (giveaway, guild_id) VALUES ($1, $2)', "True",
                                               ctx.guild.id)
                    giveaway_cache[ctx.guild.id] = "True"
            # now it is cached
            await asyncio.sleep(time * 3600)
            giveaway_cache[ctx.guild.id] = "False"
            new_msg = await ctx.channel.fetch_message(msg.id)
            reactions = new_msg.reactions
            users = [user async for user in reactions[0].users()]
            winner = random.choice(users)
            while winner == self.bot.user:
                winner = random.choice(users)
            await ctx.send(f"Congratulations {winner.mention}! You have won {item}!")

    @commands.command(aliases=['pre'], description="Check what the current prefix of this server is.")
    @commands.guild_only()
    async def prefix(self, ctx):
        try:
            ctx.bot.cache[ctx.guild.id]
        except KeyError:  # not cached
            prefix = await self.bot.db.fetchval('SELECT prefix FROM guilds WHERE guild_id = $1', ctx.guild.id)
            if not prefix:  # if guild is not in database
                await ctx.send("The prefix of this server is !")
            else:
                await ctx.send(f"The prefix of this server is {prefix}")
        else:  # cached
            await ctx.send(f"The prefix of this server is {ctx.bot.cache[ctx.guild.id]}")

    @commands.Cog.listener("on_message")
    @commands.guild_only()
    async def afk_ping(self, message, *args):
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
    @commands.command(description="Set yourself as afk.")
    @commands.guild_only()
    async def afk(self, ctx, *, reason=None):

        try:
            afk_cache[ctx.author.id]
        except KeyError:  # not in cache
            in_db = await self.bot.db.fetchval('SELECT user_id FROM afk WHERE user_id = $1', ctx.author.id)
            if not in_db:
                if reason:
                    await self.bot.db.execute('INSERT INTO afk (user_id, afk, reason) VALUES ($1, $2, $3)',
                                              ctx.author.id, True,
                                              reason)
                    afk_cache[ctx.author.id] = [True, reason]
                    return await ctx.send("You are now afk.")
                else:
                    return await ctx.send("Give a reason.")
            else:
                afk = await self.bot.db.fetchval('SELECT afk FROM afk WHERE user_id = $1', ctx.author.id)
                if afk:
                    return
                elif not afk:
                    if reason:
                        await self.bot.db.execute('UPDATE afk SET (afk, reason) = ($1, $2) WHERE user_id = $3',
                                                  True, reason, ctx.author.id)
                        return await ctx.send("You are now afk.")
                    else:
                        return await ctx.send("Give a reason.")

        else:  # in cache
            if afk_cache[ctx.author.id][0]:
                return
            elif not afk_cache[ctx.author.id][0]:
                if reason:
                    afk_cache[ctx.author.id] = [True, reason]
                    return await ctx.send("You are now afk.")
                else:
                    return await ctx.send("Give a reason.")

    @commands.command()
    @commands.guild_only()
    async def servers(self, ctx):
        await ctx.send(f"{ctx.author.mention}, I'm in {len(self.bot.guilds)} servers!")


async def setup(bot):
    await bot.add_cog(Utility(bot))
