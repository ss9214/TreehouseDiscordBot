import os
import discord
from discord.ext import commands
import random
afk_cache = {0000000000: [False, "cuz I am"]}


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # check prefix
    @commands.command(aliases=['pre'], help="Check what the current prefix of this server is.")
    @commands.guild_only()
    async def prefix(self, ctx):
        try:
            ctx.bot.cache[ctx.guild.id]
        except KeyError:  # not cached
            prefix = await self.bot.db.fetchval('SELECT guild_id FROM guilds WHERE guild_id = $1', ctx.guild.id)
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
    @commands.command(help="Set yourself as afk.")
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


async def setup(bot):
    await bot.add_cog(Utility(bot))
