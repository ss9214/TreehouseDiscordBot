import os
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Reset a user's player data. Must have administrator permissions.")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def reset_user(self, ctx, user):
        if not user:
            return ctx.send("Please include a user's ID to reset their data")
        else:
            await self.bot.db.execute('UPDATE users SET (wallet, bank, wins, losses) = (1000, 100, 0, 0) WHERE user_id = $1', user)

    @reset_user.error
    async def reset_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.send(":no_entry: You do not have permission to reset this user.")
        else:
            raise error

    # set prefix
    @commands.command(aliases=['setpre'], description="Change the prefix of the server.")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def setprefix(self, ctx, new_prefix):
        guild = await self.bot.db.fetchval('SELECT guild_id FROM guilds WHERE guild_id = $1', ctx.guild.id)
        if guild:  # if guild is not in database
            await self.bot.db.execute('UPDATE guilds SET prefix = $1 WHERE guild_id = $2', new_prefix, ctx.guild.id)
        else:  # if guild is in dat!seabase
            await self.bot.db.execute('INSERT INTO guilds (guild_id, prefix) VALUES ($1, $2)', ctx.guild.id, new_prefix)
        ctx.bot.cache[ctx.guild.id] = new_prefix
        await ctx.send(f"The prefix has been updated to {ctx.bot.cache[ctx.guild.id]}")

    @setprefix.error
    async def setpre_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.send(":no_entry: You do not have permission to set the prefix.")
        else:
            raise error


async def setup(bot):
    await bot.add_cog(Admin(bot))
