import os
import discord
from discord.ext import commands
import random
import datetime
from datetime import timedelta
import asyncio
banned_words_cache = {0000000000000: ["hi", "bye"]}  # guild_id, banned words


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener('on_message')
    @commands.guild_only()
    async def automod(self, message, *args):
        if message.author.bot:
            return
        try:
            banned_words_cache[message.guild.id]
        except KeyError:  # not cached
            data = await self.bot.db.fetch('SELECT banned_word FROM automod WHERE guild_id = $1', message.guild.id)
            if not data:  # not in db (doesn't exist)
                return
            else:
                banned_words_cache[message.guild.id] = []
                for table in data:
                    banned_words_cache[message.guild.id] += [table['banned_word']]  # now it is cached
        word_list = banned_words_cache[message.guild.id]
        for word in word_list:
            if word in message.content:
                await message.delete()
                return await message.author.send(f"{word} is banned from {message.guild.name}. Please refrain from using it in your speech.")

    @commands.command(description="Remove a word from the banned words list.")
    @commands.has_guild_permissions(administrator=True)
    async def remove_banned_word(self, ctx, remove_word):
        try:
            banned_words_cache[ctx.guild.id]
        except KeyError:  # not cached
            await self.bot.db.execute('DELETE FROM automod where (guild_id, banned_word) = ($1, $2)', ctx.guild.id,
                                      remove_word)
        else:  # cached
            await self.bot.db.execute('DELETE FROM automod where (guild_id, banned_word) = ($1, $2)', ctx.guild.id,
                                      remove_word)
            words_list = banned_words_cache[ctx.guild.id]
            for word in words_list:
                if word == remove_word:
                    words_list.remove(word)
        await ctx.send(f"||{remove_word}|| has been removed from the banned_words_list.")

    @commands.command(description="Add a word to the banned words list.")
    @commands.has_guild_permissions(administrator=True)
    async def add_banned_word(self, ctx, word):
        try:
            banned_words_cache[ctx.guild.id]
        except KeyError:  # not cached
            banned_words_cache[ctx.guild.id] = [word]
        else:  # cached
            banned_words_cache[ctx.guild.id] += [word]
        await self.bot.db.execute('INSERT INTO automod (guild_id, banned_word) VALUES ($1, $2)', ctx.guild.id, word)
        return await ctx.send(f"||{word}|| has been added to the banned words list")

    @commands.command(aliases= ["bwl"], description="Check the list of banned words")
    @commands.has_guild_permissions(moderate_members=True)
    async def banned_words_list(self, ctx):
        try:
            banned_words_cache[ctx.guild.id]
        except KeyError:  # not cached
            data = await self.bot.db.fetch('SELECT banned_word FROM automod WHERE guild_id = $1', ctx.guild.id)
            if not data:  # not in db (doesn't exist)
                return await ctx.send(f"{ctx.guild.name} does not have a banned words list.")
            else:
                banned_words_cache[ctx.guild.id] = []
                for table in data:
                    banned_words_cache[ctx.guild.id] += [table['banned_word']]  # now it is cached

        words_list = banned_words_cache[ctx.guild.id]
        em = discord.Embed(title=f"__**Banned Words List for {ctx.guild.name}**__", color=discord.Color.purple())
        em.add_field(name=f"__Words__", value="\n".join(words_list), inline=False)
        return await ctx.send(embed=em)

    @commands.command(description="Timeout someone.")
    @commands.has_guild_permissions(moderate_members=True)
    @commands.guild_only()
    async def mute(self, ctx, user: discord.Member, time=None):
        if not user:
            return await ctx.send("Please include a user to timeout.")
        if not time:
            time = "1d"
            new_time = 60*60*24
        else:
            time_period = time[-1]
            new_time = time[:-1]
            try:
                new_time = int(new_time)
            except ValueError:
                return await ctx.send("Time must be an integer. Format: (Time)(s/m/h/d/w).\nFor example: 10h")
            else:
                if time_period == "m":
                    new_time = new_time*60
                elif time_period == "h":
                    new_time = new_time*60*60
                elif time_period == "d":
                    new_time = new_time*60*60*24
                elif time_period == "w":
                    new_time = new_time*60*60*24*7
                else:
                    return await ctx.send("Time period must be s/m/h/d/w.\nFor example: 10h")
        await user.timeout(timedelta(seconds=new_time))
        return await ctx.send(f"{user.name}#{user.discriminator} has been muted for {time}.")

    @mute.error
    async def mute_error(self, ctx, error):
        if isinstance(error, commands.errors.MemberNotFound):
            await ctx.send("Member not found. Please try again.")

    @commands.command(description="Ban someone.")
    @commands.has_guild_permissions(ban_members=True)
    @commands.guild_only()
    async def ban(self, ctx, user: discord.Member, time=None, *, reason=None):
        new_time = None
        if not user:
            return await ctx.send("Please include a user to ban.")
        if not time:
            pass
        else:
            time_period = time[-1]
            new_time = time[:-1]
            try:
                new_time = int(new_time)
            except ValueError:
                return await ctx.send("Time must be an integer. Format: (Time)(s/m/h/d/w).\nFor example: 10h")
            else:
                if time_period == "m":
                    new_time = new_time * 60
                elif time_period == "h":
                    new_time = new_time * 60 * 60
                elif time_period == "d":
                    new_time = new_time * 60 * 60 * 24
                elif time_period == "w":
                    new_time = new_time * 60 * 60 * 24 * 7
                else:
                    return await ctx.send("Time period must be s/m/h/d/w.\nFor example: 10h")
        await user.ban(delete_message_days=1, reason=reason)
        if new_time:
            await asyncio.sleep(new_time)
            await user.unban()
            await user.send(f"You have been banned from {ctx.guild.name} for {time} for reason: {reason}")
        else:
            await user.send(f"You have been banned from {ctx.guild.name} forever for reason: {reason}")
        if time:
            return await ctx.send(f"{user.name}#{user.discriminator} has been banned for {time}.")
        else:
            return await ctx.send(f"{user.name}#{user.discriminator} has been banned.")

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.errors.MemberNotFound):
            await ctx.send("Member not found. Please try again.")

    @commands.command(description="Kick someone.")
    @commands.has_guild_permissions(kick_members=True)
    @commands.guild_only()
    async def kick(self, ctx, user: discord.Member, *, reason=None):
        if not user:
            return await ctx.send("Please include a user to kick.")
        if reason:
            await user.send(f"You have been kicked from {ctx.guild.name} for reason: {reason}")
        else:
            await user.send(f"You have been kicked from {ctx.guild.name} for no given reason.")
        await ctx.send(f"{user.name}#{user.discriminator} has been kicked.")
        await user.kick(reason=reason)

    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.errors.MemberNotFound):
            await ctx.send("Member not found. Please try again.")

    @commands.command(description="Clear an amount of messages.")
    @commands.has_guild_permissions(manage_messages=True)
    @commands.guild_only()
    async def clear(self, ctx, message_count=None):
        if not message_count:
            return await ctx.send("Please include how many messages you want to delete.")
        try:
            int(message_count)
        except ValueError:
            return await ctx.send("The amount of messages you are deleting must be a number lmao.")
        else:
            await ctx.channel.purge(limit=int(message_count))
            msg = await ctx.send(f"{message_count} messages have been cleared")
            await asyncio.sleep(5)
            await msg.delete()

    @commands.command(description="Set a slowmode for a channel.")
    @commands.has_guild_permissions(manage_channels=True)
    @commands.guild_only()
    async def slowmode_on(self, ctx, seconds=None):
        if not seconds:
            return await ctx.send("Please include how long the slowmode should be.")
        try:
            int(seconds)
        except ValueError:
            return await ctx.send("The slowmode must be a number lmao.")
        else:
            await ctx.channel.edit(slowmode_delay=seconds)
            await ctx.send(f"The slowmode delay has been set in this channel to {seconds} seconds!")

    @commands.command(description="Turn off slowmode for a channel.")
    @commands.has_guild_permissions(manage_channels=True)
    @commands.guild_only()
    async def slowmode_off(self, ctx):
        await ctx.channel.edit(slowmode_delay=0)
        await ctx.send(f"The slowmode delay in this channel has been turned off!")

    @commands.command(description=" Use this command to lock a channel")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send(f'**<#{ctx.channel.id}> has been locked**')

    @commands.command(description=" Use this command to unlock a channel")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await ctx.send(f'**<#{ctx.channel.id}> has been unlocked**')


async def setup(bot):
    await bot.add_cog(Moderation(bot))
