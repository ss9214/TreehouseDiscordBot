import os
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(description="Setup the verification system for your server. ", with_app_command=True)
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
            ctx.bot.verify_cache[ctx.guild.id]
        except KeyError:  # not cached
            db_verify_channel = await self.bot.db.fetchval('SELECT verify_channel FROM verify WHERE guild_id = $1',
                                                           ctx.guild.id)
            if not db_verify_channel:  # not in db
                await self.bot.db.execute('INSERT INTO verify (guild_id, verify_channel) VALUES ($1, $2)', ctx.guild.id,
                                          verify_channel.id)
                ctx.bot.verify_cache[ctx.guild.id] = verify_channel.id
            else:  # in db
                await self.bot.db.execute('UPDATE verify SET verify_channel = $1 WHERE guild_id = $2',
                                          verify_channel.id, ctx.guild.id)
                ctx.bot.verify_cache[ctx.guild.id] = verify_channel.id

        db_verify_channel = await self.bot.db.fetchval('SELECT verify_channel FROM verify WHERE guild_id = $1',
                                                       ctx.guild.id)
        if verify_channel.id == db_verify_channel:
            return await ctx.send("You already have a verification system setup in this channel.")
        else:
            await verify_channel.send(embed=em)

    @commands.hybrid_command(description="Reset a user's player data. Must have administrator permissions.", with_app_command=True)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def reset_user(self, ctx, user):
        if not user:
            return ctx.send("Please include a user's ID to reset their data")
        else:
            await self.bot.db.execute(
                'UPDATE users SET (wallet, bank, wins, losses) = (1000, 100, 0, 0) WHERE user_id = $1', user)

    @reset_user.error
    async def reset_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.send(":no_entry: You do not have permission to reset this user.")
        else:
            raise error

    # set prefix
    @commands.hybrid_command(aliases=['setpre'], description="Change the prefix of the server.", with_app_command=True)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def setprefix(self, ctx, new_prefix):
        guild = await self.bot.db.fetchval('SELECT guild_id FROM guilds WHERE guild_id = $1', ctx.guild.id)
        if guild:  # if guild is not in database
            await self.bot.db.execute('UPDATE guilds SET prefix = $1 WHERE guild_id = $2', new_prefix, ctx.guild.id)
        else:  # if guild is in database
            await self.bot.db.execute('INSERT INTO guilds (guild_id, prefix) VALUES ($1, $2)', ctx.guild.id, new_prefix)
        ctx.bot.cache[ctx.guild.id] = new_prefix
        await ctx.send(f"The prefix has been updated to {ctx.bot.cache[ctx.guild.id]}")

    @commands.hybrid_command(aliases=["enable"], description="Enable a command", with_app_command=True)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def enable_command(self, ctx, command):
        cmd = self.bot.get_command(command)

        if not cmd:
            return await ctx.send("That command does not exist.")
        elif ctx.command == cmd:
            return await ctx.send("You cannot disable this command.")
        else:
            cmd.enabled = True
            await self.bot.db.execute('DELETE FROM disabled WHERE (guild_id, command_name) = ($1, $2)', ctx.guild.id,
                                      cmd.qualified_name)
            try:
                ctx.bot.disabled_cache[ctx.guild.id]
            except KeyError:
                pass
            else:
                for i in range(len(ctx.bot.disabled_cache[ctx.guild.id])):
                    if ctx.bot.disabled_cache[ctx.guild.id][i] == cmd.qualified_name:
                        ctx.bot.disabled_cache[ctx.guild.id].remove(cmd.qualified_name)
            embed = discord.Embed(description="This command is now enabled.", color=discord.Color.purple())
            return await ctx.send(embed=embed)


    @commands.hybrid_command(aliases=["disable"], description="Disable a command", with_app_command=True)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def disable_command(self, ctx, command):
        cmd = self.bot.get_command(command)

        if not cmd:
            return await ctx.send("That command does not exist.")
        elif ctx.command == cmd:
            return await ctx.send("You cannot disable this command.")
        else:
            await self.bot.db.execute('INSERT INTO disabled (guild_id, command_name) VALUES ($1, $2)', ctx.guild.id,
                                      cmd.qualified_name)
            try:
                ctx.bot.disabled_cache[ctx.guild.id] += [cmd.qualified_name]
            except KeyError:
                ctx.bot.disabled_cache[ctx.guild.id] = [cmd.qualified_name]
            embed = discord.Embed(description="This command is now disabled.", color=discord.Color.purple())
            return await ctx.send(embed=embed)



async def setup(bot):
    await bot.add_cog(Admin(bot))
