import os
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions

color_cache = {000000000: ["white", "yellow"]}


class Colors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["addc", "ac"], description="Create a color for the server. Must have administrator permissions.")
    @commands.has_permissions(manage_roles=True)
    @commands.guild_only()
    async def create_color(self, ctx, hex_code, name):
        if "#" not in hex_code:
            return await ctx.send("Hex code must have a hashtag.")
        guild_roles = ctx.guild.roles
        for i in range(len(guild_roles)):
            if name == guild_roles[i].name:
                return await ctx.send("There is already a role in this server with that name. Please choose a different name.")
        try:
            color_cache[ctx.guild.id]
        except KeyError:  # not cached
            color_list = await self.bot.db.fetchval('SELECT color_list FROM colors WHERE guild_id = $1', ctx.guild.id)
            if not color_list:  # not in database
                await self.bot.db.execute('INSERT INTO colors (guild_id, color_list) VALUES ($1, $2)', ctx.guild.id,
                                          name)
                color_cache[ctx.guild.id] = []  # creating cache
                color_cache[ctx.guild.id] += [name]  # updating cache
                await ctx.guild.create_role(name=name, color=discord.Color.from_str(hex_code))
                return await ctx.send(f"{name} has been successfully added!")
            else:  # in database but not cached
                await self.bot.db.execute('UPDATE colors SET color_list = $1 WHERE guild_id = $2',
                                          f' {color_list} {name}', ctx.guild.id)
                color_list = await self.bot.db.fetchval('SELECT color_list FROM colors WHERE guild_id = $1',
                                                        ctx.guild.id)
                if " " in color_list:
                    colors = color_list.split()
                else:
                    colors = color_list
                color_cache[ctx.guild.id] = []
                for i in range(len(colors)):
                    color_cache[ctx.guild.id] += [colors[i]]  # updates cache
                await ctx.guild.create_role(name=name, color=discord.Color.from_str(hex_code))
                return await ctx.send(f"{name} has been successfully added!")
        else:  # if cached and dbed
            color_cache[ctx.guild.id] += [name]
            color_list = await self.bot.db.fetchval('SELECT color_list FROM colors WHERE guild_id = $1', ctx.guild.id)
            await self.bot.db.execute('UPDATE colors SET color_list = $1 WHERE guild_id = $2', f' {color_list} {name},',
                                      ctx.guild.id)
            await ctx.guild.create_role(name=name, color=discord.Color.from_str(hex_code))
            return await ctx.send(f"{name} has been successfully added!")

    @create_color.error
    async def create_color_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.send(":no_entry: You do not have permission to create roles.")
        else:
            raise error

    @commands.command(aliases=["setc", "sc"], description="Set your color role.")
    @commands.guild_only()
    async def set_color(self, ctx, color):
        your_roles = ctx.author.roles
        try:
            color_cache[ctx.guild.id]
        except KeyError:  # not cached
            your_roles = ctx.author.roles
            color_list = await self.bot.db.fetchval('SELECT color_list FROM colors WHERE guild_id = $1', ctx.guild.id)
            if not color_list:  # not in database
                return await ctx.send("Your server has not set up the color system")
            else:  # in database
                color_list = await self.bot.db.fetchval('SELECT color_list FROM colors WHERE guild_id = $1',
                                                        ctx.guild.id)  # gets the colors
                if "" in color_list:
                    colors = color_list.split()
                else:
                    colors = color_list
                color_cache[ctx.guild.id] = []  # creates cache
                for i in range(len(colors)):
                    color_cache[ctx.guild.id] += colors[i]  # updates cache
                if color in color_cache[ctx.guild.id]:
                    roles = ctx.guild.roles
                    for k in range(len(color_cache[ctx.guild.id])):
                        for j in range(len(your_roles)):
                            if your_roles[j].name == color_cache[ctx.guild.id][k]:
                                await ctx.author.remove_roles(your_roles[j])
                    for i in range(len(roles)):
                        if roles[i].name == color:
                            await ctx.author.add_roles(roles[i])
                            return await ctx.send(f"Your color is now {color}")
        else:  # cached
            if color in color_cache[ctx.guild.id]:
                roles = ctx.guild.roles
                for k in range(len(color_cache[ctx.guild.id])):
                    for j in range(len(your_roles)):
                        if your_roles[j].name == color_cache[ctx.guild.id][k]:
                            await ctx.author.remove_roles(your_roles[j])
                for i in range(len(roles)):
                    if roles[i].name == color:
                        await ctx.author.add_roles(roles[i])
                        return await ctx.send(f"Your color is now {color}")

    @commands.command(aliases=["remc", "rc"], description="Remove a color role that you have.")
    @commands.guild_only()
    async def remove_color(self, ctx, color):
        your_roles = ctx.author.roles
        for i in range(len(your_roles)):
            if color == your_roles[i].name:
                return await ctx.author.remove_roles(your_roles[i])
        return await ctx.send("You have no role with that color name.")


async def setup(bot):
    await bot.add_cog(Colors(bot))
