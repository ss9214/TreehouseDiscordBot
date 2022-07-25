import os
import discord
from discord.ext import commands
import random
from random import randint
import easy_pil
from easy_pil import *

level_cache = {(0000000000, 000000000): [1, 0, "blue"]}


class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["lvllb", "lvl_lb", "lvl_leaderboard", "level_lb", "lb"], description="Check out the leaderboard for your server!")
    @commands.guild_only()
    async def leaderboard(self, ctx):
        data = await self.bot.db.fetch('SELECT level,xp,user_id FROM leveling WHERE guild_id = $1 ORDER BY level DESC, xp DESC LIMIT 10', ctx.guild.id)
        if data:
            em = discord.Embed(title="__**Leveling Leaderboard**__", color=discord.Color.purple())
            count = 0
            for table in data:
                count += 1
                user = self.bot.get_user(table['user_id'])
                if not user:
                    user = "Not in server"
                em.add_field(name=f"{count}. {user}", value=f"Level - **{table['level']}** | XP - **{table['xp']}**", inline=False)
            return await ctx.send(embed=em)
        return await ctx.send("There are no users to store in the leaderboard.")

    @commands.command(aliases=["r", "Rank", "R"], description="Check your rank or someone else's rank.")
    @commands.guild_only()
    async def rank(self, ctx, member: discord.Member = None):
        colors = {"red": ("#580f0f", "#c01f1f"), "orange": ("#63340f", "#c96719"), "yellow": ("#494511", "#f1c40f"), "green": ("#114712", "#15a018"),
                  "blue": ("#0c3a4e", "#1d99d0"), "purple": ("#4d2d7c", "#9674c9"), "pink": ("#651569", "#a618ad"), "black_white": ("#242424", "#c5c5c5")}
        if member:
            user = member.id
        else:
            user = ctx.author.id
        try:  # check if cached
            level_cache[(user, ctx.guild.id)]
        except KeyError:  # not cached
            data = await self.bot.db.fetchval('SELECT user_id FROM leveling WHERE (user_id, guild_id) = ($1, $2)', user, ctx.guild.id)
            if not data:  # not in database
                await self.bot.db.execute('INSERT INTO leveling (user_id, level, xp, card_color, guild_id) VALUES ($1, 1, 0, $3, $2)', user, ctx.guild.id, "blue")
                xp = 0
                level = 1
                color = "blue"
                level_cache[(user, ctx.guild.id)] = [1, 0, "blue"]
            else:  # in database
                xp = await self.bot.db.fetchval('SELECT xp FROM leveling WHERE (user_id, guild_id) = ($1, $2)', user, ctx.guild.id)
                level = await self.bot.db.fetchval('SELECT level FROM leveling WHERE (user_id, guild_id) = ($1, $2)', user, ctx.guild.id)
                color = await self.bot.db.fetchval('SELECT card_color FROM leveling WHERE (user_id, guild_id) = ($1, $2)', user, ctx.guild.id)
                level_cache[(user, ctx.guild.id)] = [level, xp, color]
        else:  # if cached
            level = level_cache[(user, ctx.guild.id)][0]
            xp = level_cache[(user, ctx.guild.id)][1]
            color = level_cache[(user, ctx.guild.id)][2]

        next_level_xp = (level * 10) ** 2
        percent_next = round((xp / next_level_xp) * 100, 2)
        card_colors = ""
        for key in colors.keys():
            if key == color:
                card_colors = colors[key]
                break
        background = Editor(Canvas((900, 300), color=card_colors[0]))
        if not member:
            user = ctx.author
        else:
            user = member
        pfp = await load_image_async(str(user.avatar.url))
        pf = Editor(pfp).resize((150, 150)).circle_image()

        poppins = Font.poppins(size=45)
        small_poppins = Font.poppins(size=35)
        card_right_shape = [(650, 0), (750, 300), (900, 300), (900, 0)]
        background.polygon(card_right_shape, color=card_colors[1])
        background.paste(pf, (30, 30))

        background.rectangle((30, 220), width=650, height=40, color="#FFFFFF", radius=12)
        background.bar((30, 220), max_width=650, height=40, percentage=percent_next, color=card_colors[1], radius=12)
        background.text((200, 40), f"{user.name}#{user.discriminator}", font=poppins, color="#FFFFFF")

        background.rectangle((200, 100), width=350, height=2, fill="#FFFFFF")
        background.text((200, 130), f"Level - {level} | XP - {xp}/{next_level_xp} | {percent_next}%", font=small_poppins, color="#FFFFFF")

        file = discord.File(fp=background.image_bytes, filename="card.png")
        await ctx.send(file=file)

    @commands.Cog.listener("on_message")
    async def increaseXP(self, message):
        if message.author.bot:
            return
        else:
            ints = [1]
            try:  # check if cached
                level_cache[(message.author.id, message.guild.id)]
            except KeyError:  # not cached
                data = await self.bot.db.fetchval('SELECT user_id FROM leveling WHERE (user_id, guild_id) = ($1, $2)', message.author.id, message.guild.id)
                if not data:  # not in database
                    await self.bot.db.execute('INSERT INTO leveling (user_id, level, xp, card_color, guild_id) VALUES ($1, 1, 0, $2, $3)',
                                              message.author.id, "blue", message.guild.id)
                    xp = 0
                    level = 1
                    level_cache[(message.author.id, message.guild.id)] = [1, 0, "blue"]
                    color = "blue"
                else:
                    xp = await self.bot.db.fetchval('SELECT xp FROM leveling WHERE (user_id, guild_id) = ($1, $2)', message.author.id, message.guild.id)
                    level = await self.bot.db.fetchval('SELECT level FROM leveling WHERE (user_id, guild_id) = ($1, $2)',
                                                       message.author.id, message.guild.id)
                    color = await self.bot.db.fetchval('SELECT card_color FROM leveling WHERE (user_id, guild_id) = ($1, $2)',
                                                       message.author.id, message.guild.id)
                    level_cache[(message.author.id, message.guild.id)] = [level, xp, color]
            else:  # if cached
                xp = level_cache[(message.author.id, message.guild.id)][1]
                level = level_cache[(message.author.id, message.guild.id)][0]
                color = level_cache[(message.author.id, message.guild.id)][2]
            # actually increasing the level now that we have current xp and current level
            if randint(1, 2) in ints:
                xp += 1
                if xp == (level * 10) ** 2:
                    level += 1
            await self.bot.db.execute('UPDATE leveling SET (xp, level) = ($1, $2) WHERE (user_id, guild_id) = ($3, $4)', xp, level,
                                      message.author.id, message.guild.id)
            level_cache[(message.author.id, message.guild.id)] = [level, xp, color]

    @commands.command(description="Check available card colors")
    @commands.guild_only()
    async def card_colors(self, ctx):
        colors = ["red", "orange", "yellow", "green", "blue", "purple", "pink", "black_white"]
        msg = ""
        for i in range(len(colors)):
            msg += f"**{i+1}. **{colors[i]}\n"
        await ctx.send(msg)

    @commands.command(aliases=["ccc"], description="Change the color of your !rank card.")
    @commands.guild_only()
    async def change_card_color(self, ctx, color):
        try:  # check if cached
            level_cache[(ctx.author.id, ctx.guild.id)]
        except KeyError:  # not cached
            data = await self.bot.db.fetchval('SELECT user_id FROM leveling WHERE (user_id, guild_id) = ($1, $2)', ctx.author.id, ctx.guild.id)
            if not data:  # not in database
                await self.bot.db.execute(
                    'INSERT INTO leveling (user_id, level, xp, card_color, guild_id) VALUES ($1, 1, 0, $2, $3)',
                    ctx.author.id, "blue", ctx.guild.id)
                level_cache[(message.author.id, ctx.guild.id)] = [1, 0, "blue"]
        # now that it's in the database and cache we can proceed
        colors = ["red", "orange", "yellow", "green", "blue", "purple", "pink", "black_white"]
        if color in colors:
            await self.bot.db.execute('UPDATE leveling SET card_color = $1 WHERE (user_id, guild_id) = ($2, $3)', color, ctx.author.id, ctx.guild.id)
            level_cache[(ctx.author.id, ctx.guild.id)][2] = color
            return await ctx.send(f"Your card color has been set to {color}.")
        else:
            return await ctx.send(f"Please choose a color in the following list: {colors}")


async def setup(bot):
    await bot.add_cog(Levels(bot))
