import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
from easy_pil import *

class Colors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(aliases=["addc", "ac"], with_app_command=True, description="Create a color for the server. Must have 'manage roles' permission.")
    @commands.has_permissions(manage_roles=True)
    @commands.guild_only()
    async def create_color(self, ctx, hex_code, name):
        if not hex_code:
            return await ctx.reply("You must include the hex_code and the name of the role.\n Tcreate_color #FFFFFF white")
        if "#" not in hex_code:
            return await ctx.reply("Hex code must have a hashtag.")
        guild_roles = ctx.guild.roles
        for i in range(len(guild_roles)):
            if name == guild_roles[i].name:
                return await ctx.reply(
                    "There is already a role in this server with that name. Please choose a different name.")
        try:
            ctx.bot.color_cache[ctx.guild.id]
        except KeyError:  # not cached
            data = await self.bot.db.fetch('SELECT color_list FROM colors WHERE guild_id = $1', ctx.guild.id)
            await self.bot.db.execute('INSERT INTO colors (guild_id, color_list) VALUES ($1, $2)', ctx.guild.id,
                                      name)
            ctx.bot.color_cache[ctx.guild.id] = []  # creating cache
            if not data:
                ctx.bot.color_cache[ctx.guild.id] += [name]  # updating cache
            else:
                for table in data:
                    ctx.bot.color_cache[ctx.guild.id] += [table['color_list']]  # now it is cached
                ctx.bot.color_cache[ctx.guild.id] += [name]
            await ctx.guild.create_role(name=name, color=discord.Color.from_str(hex_code))
            return await ctx.reply(f"{name} has been successfully added!")

        else:  # if cached and dbed
            ctx.bot.color_cache[ctx.guild.id] += [name]
            await self.bot.db.execute('INSERT INTO colors (guild_id, color_list) VALUES ($1, $2)', ctx.guild.id,
                                      name)
            await ctx.guild.create_role(name=name, color=discord.Color.from_str(hex_code))
            return await ctx.reply(f"{name} has been successfully added!")

    @create_color.error
    async def create_color_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.reply(":no_entry: You do not have permission to create roles.")
        else:
            raise error

    @commands.hybrid_command(aliases=["colors", "cl"], description="Check the list of color roles.", with_app_command=True)
    @commands.guild_only()
    async def color_list(self, ctx):
        try:
            ctx.bot.color_cache[ctx.guild.id]
        except KeyError:  # not cached
            color_list = await self.bot.db.fetch('SELECT color_list FROM colors WHERE guild_id = $1', ctx.guild.id)
            ctx.bot.color_cache[ctx.guild.id] = []  # creating cache
            if not color_list:  # no colors in db
                return await ctx.reply("Your server has not set up the color system.")
            else:  # in db
                colors = []
                ctx.bot.color_cache[ctx.guild.id] = []  # creates cache
                for table in color_list:
                    ctx.bot.color_cache[ctx.guild.id] += [table['color_list']]  # now it is cached
                    colors += [table['color_list']]
                guild_roles = ctx.guild.roles
                for color in colors:
                    inside = False
                    for role in guild_roles:
                        if color == role.name:
                            inside = True
                    if not inside:
                        await self.bot.db.execute('DELETE FROM colors WHERE (guild_id, color_list) = ($1, $2)',
                                                  ctx.guild.id, color)
                        for color2 in ctx.bot.color_cache[ctx.guild.id]:
                            if color2 == color:
                                ctx.bot.color_cache[ctx.guild.id].remove(color2)

        colors = ctx.bot.color_cache[ctx.guild.id]
        if len(colors) % 2 == 0:
            size2 = 150 * (len(colors) - 2) + 50
        else:
            size2 = 150 * (len(colors) - 1) + 50
        background = Editor(Canvas((1500, size2), color="#111111"))
        font = Font.montserrat(size=60, variant="bold")
        roles = ctx.guild.roles
        for i in range(len(colors)):
            for role in roles:
                if role.name == colors[i]:
                    if i % 2 == 0:
                        background.text((50, i * 100 + 40), f"{i + 1}. {role.name}", font=font,
                                        color=f"{role.color}")
                    else:
                        background.text((800, (i - 1) * 100 + 40), f"{i + 1}. {role.name}", font=font,
                                        color=f"{role.color}")
        file = discord.File(fp=background.image_bytes, filename="colors.png")
        await ctx.reply(file=file)

    @commands.hybrid_command(aliases=["setc", "sc"], description="Set your color role.", with_app_command=True)
    @commands.guild_only()
    async def set_color(self, ctx, color):
        your_roles = ctx.author.roles
        try:
            ctx.bot.color_cache[ctx.guild.id]
        except KeyError:  # not cached
            your_roles = ctx.author.roles
            color_list = await self.bot.db.fetch('SELECT color_list FROM colors WHERE guild_id = $1', ctx.guild.id)
            if not color_list:  # not in database
                return await ctx.reply("Your server has not set up the color system")
            else:  # in database
                ctx.bot.color_cache[ctx.guild.id] = []  # creates cache
                for table in color_list:
                    ctx.bot.color_cache[ctx.guild.id] += [table["color_list"]]  # updates cache
        # now cached
        try:
            choice = int(color)
        except ValueError:
            if color in ctx.bot.color_cache[ctx.guild.id]:
                roles = ctx.guild.roles
                for k in range(len(ctx.bot.color_cache[ctx.guild.id])):
                    for j in range(len(your_roles)):
                        if your_roles[j].name == ctx.bot.color_cache[ctx.guild.id][k]:
                            await ctx.author.remove_roles(your_roles[j])
                for i in range(len(roles)):
                    if roles[i].name == color:
                        await ctx.author.add_roles(roles[i])
                        return await ctx.reply(f"Your color is now {color}")
            else:
                return await ctx.reply("That color doesn't exist.")
        else:
            roles = ctx.guild.roles
            color = ctx.bot.color_cache[ctx.guild.id][(choice - 1)]
            for k in range(len(ctx.bot.color_cache[ctx.guild.id])):
                for j in range(len(your_roles)):
                    if your_roles[j].name == ctx.bot.color_cache[ctx.guild.id][k]:
                        await ctx.author.remove_roles(your_roles[j])
            for i in range(len(roles)):
                if roles[i].name == color:
                    await ctx.author.add_roles(roles[i])
                    return await ctx.reply(f"Your color is now {color}")


    @commands.hybrid_command(aliases=["remc", "rc"], description="Remove a color role that you have.", with_app_command=True)
    @commands.guild_only()
    async def remove_color(self, ctx, color):
        your_roles = ctx.author.roles
        for i in range(len(your_roles)):
            if color == your_roles[i].name:
                return await ctx.author.remove_roles(your_roles[i])
        return await ctx.reply("You have no role with that color name.")


async def setup(bot):
    await bot.add_cog(Colors(bot))
