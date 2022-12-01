import discord
from discord.ext import commands
import asyncio


class StickiesAndAnnouncements(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(description="Create a sticky text announcement.", with_app_command=True)
    @commands.guild_only()
    @commands.has_guild_permissions(manage_messages=True)
    async def sticky_create_text(self, ctx, sticky_name, channel: discord.TextChannel):
        em = discord.Embed(
            description="Please send your sticky message below. If you would like an embed use the 'sticky_create_embed' command",
            color=discord.Color.purple())
        await ctx.reply(embed=em)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        msg = await self.bot.wait_for('message', check=check)
        msg = msg.content
        data = await self.bot.db.fetchval('SELECT sticky_name FROM stickies WHERE '
                                          '(guild_id, channel_id) = ($1,$2)', ctx.guild.id, ctx.channel.id)
        if data == sticky_name:
            embed = discord.Embed(
                description="You already have a sticky message by this name, so please change the name.",
                color=discord.Color.purple())
            return await ctx.reply(embed=embed)
        if data:
            em = discord.Embed(
                description="You can only have 1 sticky message per channel, are your sure would like to replace it?"
                            "\n"
                            "Type 'Confirm' to continue, otherwise type anything else to quit.",
                color=discord.Color.purple())
            await ctx.reply(embed=em)
            msg = await self.bot.wait_for('message', check=check)
            msg = msg.content
            if msg == "Confirm":
                await self.bot.db.execute(
                    'UPDATE stickies SET (sticky_name, message, last_sticky_id) '
                    '= ($1, $2, $3) WHERE (channel_id, guild_id) = ($4, $5)', sticky_name, msg, "None", channel.id,
                    ctx.guild.id)
            else:
                em = discord.Embed(description="You have successfully quit.", color=discord.Color.purple())
                return await ctx.reply(embed=em)
        else:
            await self.bot.db.execute(
                'INSERT INTO stickies (sticky_name, channel_id, message, guild_id, last_sticky_id) '
                'VALUES ($1, $2, $3, $4, $5)', sticky_name, channel.id, msg, ctx.guild.id, "None")
        ctx.bot.sticky_cache[(ctx.guild.id, channel.id)] = [sticky_name, msg, "None"]
        embed = discord.Embed(description=f"{sticky_name} has been added as a sticky message in {channel.name}",
                              color=discord.Color.purple())
        return await ctx.reply(embed=embed)

    @commands.hybrid_command(
        description="Remove a sticky message. Do the `sticky_list` command to see what stickies are in your server.", with_app_command=True)
    @commands.guild_only()
    @commands.has_guild_permissions(manage_messages=True)
    async def sticky_remove(self, ctx):
        em = discord.Embed(description="What is the name of the sticky message you would like to remove?")
        await ctx.reply(embed=em)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        msg = await self.bot.wait_for('message', check=check)
        msg = msg.content
        for channel in ctx.guild.channels:
            check = False
            try:
                if ctx.bot.sticky_cache[(ctx.guild.id, channel.id)][0] == msg:
                    check = True
                    del ctx.bot.sticky_cache[(ctx.guild.id, channel.id)]
                    await self.bot.db.execute(
                        'DELETE FROM stickies WHERE (channel_id, sticky_name, guild_id) = ($1, $2, $3)', channel.id,
                        msg,
                        ctx.guild.id)
            except KeyError:
                data = await self.bot.db.fetchval('SELECT channel_id FROM stickies WHERE '
                                                  '(channel_id, sticky_name, guild_id) = ($1, $2, $3)', channel.id, msg,
                                                  ctx.guild.id)
                if data:
                    await self.bot.db.execute('DELETE FROM stickies WHERE '
                                              '(channel_id, sticky_name, guild_id) = ($1, $2, $3)', channel.id, msg,
                                              ctx.guild.id)
                    check = True
        if check:
            embed = discord.Embed(
                description=f"You have successfully removed the sticky message '{msg}' from your server.",
                color=discord.Color.purple())
        else:
            embed = discord.Embed(description="There is no sticky message by that name.",
                                  color=discord.Color.purple())
        return await ctx.reply(embed=embed)

    @commands.hybrid_command(description="Look at the list of sticky messages for this server.", with_app_command=True)
    async def sticky_list(self, ctx):
        channel_list = []
        sticky_name_list = []
        try:
            self.bot.sticky_cache[(ctx.guild.id, ctx.channel.id)]
        except KeyError:  # not cached
            data = await self.bot.db.fetch('SELECT channel_id, sticky_name FROM stickies WHERE '
                                           'guild_id = $1', ctx.guild.id)
            for table in data:
                channel_list += [table["channel_id"]]
                sticky_name_list += [table["sticky_name"]]
        else:
            for channel in channel_list:
                sticky_name_list += [self.bot.sticky_cache[(ctx.guild.id, channel)][0]]
        msg = ""
        for i in range(len(channel_list)):
            msg += f"**{i + 1}. **Sticky: {sticky_name_list[i]}; Channel: <#{channel_list[i]}>\n"
        embed = discord.Embed(title=f"**__Sticky List in {ctx.guild.name}__**",
                              description=msg, color=discord.Color.purple())
        if len(channel_list) == 0:
            embed = discord.Embed(description="There are no stickies set up in this server.",
                                  color=discord.Color.purple())
        return await ctx.reply(embed=embed)

    @commands.Cog.listener('on_message')
    async def sticky_message(self, message):
        if message.author.bot:
            return
        try:
            self.bot.sticky_cache[(message.guild.id, message.channel.id)]
        except KeyError:  # not cached
            sticky_message = await self.bot.db.fetchval('SELECT message FROM stickies WHERE '
                                                        '(guild_id, channel_id) = ($1,$2)', message.guild.id,
                                                        message.channel.id)
            sticky_name = await self.bot.db.fetchval('SELECT sticky_name FROM stickies WHERE '
                                                     '(guild_id, channel_id) = ($1,$2)', message.guild.id,
                                                     message.channel.id)
            last_sticky = await self.bot.db.fetchval('SELECT last_sticky_id FROM stickies WHERE '
                                                     '(guild_id, channel_id) = ($1,$2)', message.guild.id,
                                                     message.channel.id)
            if sticky_message:
                self.bot.sticky_cache[(message.guild.id, message.channel.id)] = [sticky_name, sticky_message,
                                                                                 last_sticky]
            else:
                return
        sticky_message = self.bot.sticky_cache[(message.guild.id, message.channel.id)][1]
        last_sticky = self.bot.sticky_cache[(message.guild.id, message.channel.id)][2]
        if sticky_message:
            if last_sticky != "None":
                int(last_sticky)
                last_sticky = await message.channel.fetch_message(last_sticky)
                await asyncio.sleep(10)
                await last_sticky.delete()
            msg = await message.channel.send(sticky_message)
            self.bot.sticky_cache[(message.guild.id, message.channel.id)][2] = msg.id
            await self.bot.db.execute(
                'UPDATE stickies SET last_sticky_id = $1 WHERE '
                '(channel_id, guild_id) = ($2, $3)', str(msg.id), message.channel.id,
                message.guild.id)
        else:
            return

    @commands.hybrid_command(description="Send a text announcement.", with_app_command=True)
    @commands.guild_only()
    @commands.has_guild_permissions(manage_messages=True)
    async def text_announce(self, ctx, channel: discord.TextChannel):
        await ctx.reply(
            "Please send your announcement below. If you would like an embed use the `embed_announce` command")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        msg = await self.bot.wait_for('message', check=check)
        msg = msg.content
        await channel.send(msg)

    @commands.hybrid_command(description="Send an embed announcement.", with_app_command=True)
    @commands.guild_only()
    @commands.has_guild_permissions(manage_messages=True)
    async def embed_announce(self, ctx, channel: discord.TextChannel):
        em = discord.Embed(
            description="Please send the title of your embed below. Say None for no title. If you would like a text announcement use the `text_announce` command.",
            color=discord.Color.purple())
        await ctx.reply(embed=em)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        title = await self.bot.wait_for('message', check=check)
        title = title.content
        em = discord.Embed(
            description="Please send the content of your embed below. If you would like a text announcement use the `text_announce` command.",
            color=discord.Color.purple())
        await ctx.reply(embed=em)
        content = await self.bot.wait_for('message', check=check)
        content = content.content
        em = discord.Embed(
            description="Please send the url of your image for your embed below. Send None if you would like no image. If you would like a text announcement use the `text_announce` command.",
            color=discord.Color.purple())
        await ctx.reply(embed=em)
        image = await self.bot.wait_for('message', check=check)
        image = image.content
        if title == "None":
            embed = discord.Embed(description=content, color=discord.Color.purple())
        else:
            embed = discord.Embed(title=title, description=content, color=discord.Color.purple())
        if image != "None":
            embed.set_image(url=image)
        await channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(StickiesAndAnnouncements(bot))
