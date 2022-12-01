import discord
import asyncpg
import asyncio
from discord import Permissions
from discord.ext import commands


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # auto-role on member join
    @commands.Cog.listener("on_member_join")
    async def autorole(self, member: discord.Member):
        guild_roles = member.guild.roles
        try:
            self.bot.autorole_cache[member.guild.id]
        except KeyError:
            data = await self.bot.db.fetch('SELECT autorole FROM autoroles WHERE guild_id = $1', member.guild.id)
            if not data:
                return
            else:
                self.bot.autorole_cache[member.guild.id] = []  # creates cache
                for table in data:
                    self.bot.autorole_cache[member.guild.id] += [table["autorole"]]  # updates cache
                    # now I can use the cache
        for role in self.bot.autorole_cache[member.guild.id]:
            for guild_role in guild_roles:
                if role == guild_role.name:
                    await member.add_roles(guild_role)

    @commands.hybrid_command(description="Set a role that will be added when a member joins your server", with_app_command=True)
    @commands.guild_only()
    @commands.has_guild_permissions(manage_roles=True)
    async def add_autorole(self, ctx, role):
        guild_roles = ctx.guild.roles
        check = False
        for guild_role in guild_roles:
            if role == guild_role:
                check = True
                role = guild_role.name
            if role == guild_role.name:
                check = True
                break
        if not check:
            return await ctx.reply("That role does not exist.")
        try:
            ctx.bot.autorole_cache[ctx.guild.id] += [role]
        except KeyError:
            ctx.bot.autorole_cache[ctx.guild.id] = [role]
        await self.bot.db.execute('INSERT INTO autoroles (autorole, guild_id) VALUES ($1, $2)', role, ctx.guild.id)
        return await ctx.reply(f"{role} has been added as an autorole for {ctx.guild.name}")

    @commands.hybrid_command(description="View the list of autoroles for this server.", with_app_command=True)
    @commands.guild_only()
    @commands.has_guild_permissions(manage_roles=True)
    async def autorole_list(self, ctx):
        try:
            ctx.bot.autorole_cache[ctx.guild.id]
        except KeyError:
            data = await self.bot.db.fetch('SELECT autorole FROM autoroles WHERE guild_id = $1', ctx.guild.id)
            if not data:
                embed = discord.Embed(description=f"There are no autoroles set up for {ctx.guild.name}.",
                                      color=discord.Color.purple())
                return await ctx.reply(embed=embed)
            else:
                ctx.bot.autorole_cache[ctx.guild.id] = []  # creates cache
                for table in data:
                    ctx.bot.autorole_cache[ctx.guild.id] += [table["autorole"]]  # updates cache
                    # now I can use the cache
        autorole_list = ctx.bot.autorole_cache[ctx.guild.id]
        description = ""
        if len(autorole_list) > 0:
            for i in range(len(autorole_list)):
                description += f"**{i+1}.** {autorole_list[i]}\n"
            embed = discord.Embed(title="**__Autorole List__**", description=description, color=discord.Color.purple())
        else:
            embed = discord.Embed(description=f"There are no autoroles set up for {ctx.guild.name}.",
                                  color=discord.Color.purple())
        return await ctx.reply(embed=embed)


    @commands.hybrid_command(description="Remove a role that will be added when a member joins your server", with_app_command=True)
    @commands.guild_only()
    @commands.has_guild_permissions(manage_roles=True)
    async def remove_autorole(self, ctx, role):
        guild_roles = ctx.guild.roles
        check = False
        for guild_role in guild_roles:
            if role == guild_role:
                check = True
                role = guild_role.name
            if role == guild_role.name:
                check = True
                break
        if not check:
            return await ctx.reply("That role does not exist.")
        try:
            ctx.bot.autorole_cache[ctx.guild.id].remove(role)
        except KeyError:
            pass
        await self.bot.db.execute('DELETE FROM autoroles WHERE (autorole, guild_id) = ($1, $2)', role, ctx.guild.id)
        return await ctx.reply(f"{role} has been removed as an autorole for {ctx.guild.name}.")

    # welcome message
    @commands.Cog.listener("on_member_join")
    async def verification(self, member: discord.Member):
        guild_roles = member.guild.roles
        guild_channels = member.guild.channels
        verify_channel = await self.bot.db.fetchval('SELECT verify_channel FROM verify WHERE guild_id = $1',
                                                    member.guild.id)
        if not verify_channel:  # not in database
            pass
        else:
            unverified_role = None
            templist = ["Unverified", "unverified"]
            for role in guild_roles:
                if role.name in templist:
                    unverified_role = role
                    break
            if not unverified_role:
                unverified_role = await member.guild.create_role(name="Unverified",
                                                                 permissions=Permissions(view_channel=True))
                overwrites = {unverified_role: discord.PermissionOverwrite(view_channel=False)}
                templist = ["verification", "Verification", "rules", "Rules"]
                for channel in guild_channels:
                    if not channel.permissions_synced:
                        if channel.name not in templist:
                            await channel.edit(overwrites=overwrites)
            await member.add_roles(unverified_role)

    # WELCOME STUFF ############################################################################################
    @commands.Cog.listener("on_member_join")
    @commands.guild_only()
    async def welcome(self, member):
        try:
            self.bot.welcome_cache[member.guild.id]
        except KeyError:  # not cached
            data = await self.bot.db.fetchval('SELECT welcomeoff FROM welcome WHERE guild_id = $1', member.guild.id)
            if data:  # disabled
                return
        if member.guild.system_channel is not None:
            try:
                self.bot.welcome_msg_cache[member.guild.id]
            except KeyError:
                msg = await self.bot.db.fetchval('SELECT msg FROM welcome_msg WHERE guild_id = $1', member.guild.id)
                indexes = await self.bot.db.fetchval('SELECT indexes FROM welcome_msg WHERE guild_id = $1',
                                                     member.guild.id)
                embed = await self.bot.db.fetchval('SELECT embed FROM welcome_msg WHERE guild_id = $1', member.guild.id)
                title = await self.bot.db.fetchval('SELECT title FROM welcome_msg WHERE guild_id = $1', member.guild.id)
                image = await self.bot.db.fetchval('SELECT image FROM welcome_msg WHERE guild_id = $1', member.guild.id)
                if not msg:
                    msg = f'Hi {member.mention}! Welcome to {member.guild.name}!'
                    indexes = []
                else:
                    indexes = indexes.split()
            else:
                msg = self.bot.welcome_msg_cache[member.guild.id][0]
                indexes = self.bot.welcome_msg_cache[member.guild.id][1]
                embed = self.bot.welcome_msg_cache[member.guild.id][2]
                title = self.bot.welcome_msg_cache[member.guild.id][3]
                image = self.bot.welcome_msg_cache[member.guild.id][4]
                indexes = indexes.split()
            for i in range(len(indexes)):
                if indexes[i] == "index_mention":
                    indexes[i] = member.mention
                if indexes[i] == "index_guild":
                    indexes[i] = member.guild.name
                if indexes[i] == "index_name":
                    indexes[i] = f"{member.name}#{member.discriminator}"
            if len(indexes) == 1:
                description = msg % indexes[0]
            elif len(indexes) == 2:
                description = msg % (indexes[0], indexes[1])
            elif len(indexes) == 3:
                description = msg % (indexes[0], indexes[1], indexes[2])
            else:
                description = msg
            if embed == "True":
                if title == "None":
                    msg = discord.Embed(description=description, color=discord.Color.purple())
                else:
                    msg = discord.Embed(title=title, description=description, color=discord.Color.purple())
                if image != "None":
                    msg.set_image(url=image)
                return await member.guild.system_channel.send(embed=msg)
            else:
                return await member.guild.system_channel.send(description)


    @commands.hybrid_command(description="Make a custom welcome message.", with_app_command=True)
    @commands.guild_only()
    async def custom_welcome_embed(self, ctx):
        embed = discord.Embed(description="Please send the title of your embed below. Say None for no title. "
                                          "If you would like a text announcement use the `text_announce` command.",
                              color=discord.Color.purple())
        await ctx.reply(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        title = await self.bot.wait_for('message', check=check)
        title = title.content
        embed = discord.Embed(description="Please send the description of your embed below. "
                                          "\n"
                                          "\nSay membermention to mention the user that joined."
                                          "\nSay guildname for the server name"
                                          "\nSay membername to say the user's name and discriminator but not ping them.",
                              color=discord.Color.purple())
        await ctx.reply(embed=embed)
        description = await self.bot.wait_for('message', check=check)
        description = description.content
        embed = discord.Embed(
            description="Please send the url of your image for your embed below. Send None if you would like no image. If you would like a text announcement use the `text_announce` command.",
            color=discord.Color.purple())
        await ctx.reply(embed=embed)
        image = await self.bot.wait_for('message', check=check)
        image = image.content
        index_mention = None
        index_guild = None
        index_member = None
        if "membermention" in description:
            index_mention = description.find("membermention")
            description = description.replace("membermention", "%s")
        if "guildname" in description:
            index_guild = description.find("guildname")
            description = description.replace("guildname", "%s")
        if "membername" in description:
            index_member = description.find("membername")
            description = description.replace("membername", "%s")
        msg = description
        numbers = []
        indexes = ""
        if index_mention:
            numbers += [index_mention]
        if index_guild:
            numbers += [index_guild]
        if index_member:
            numbers += [index_member]
        for i in range(len(numbers)):
            if index_mention:
                if numbers[i] == index_mention:
                    indexes += "index_mention "
            if index_guild:
                if numbers[i] == index_guild:
                    indexes += "index_guild "
            if index_member:
                if numbers[i] == index_member:
                    indexes += "index_member "

        message = await self.bot.db.fetchval('SELECT msg FROM welcome_msg WHERE guild_id = $1', ctx.guild.id)
        if message:
            await self.bot.db.execute('UPDATE welcome_msg SET (msg, indexes, title, embed, image) = ($1, $2, $3, $4, $5) WHERE guild_id = $6', msg,
                                      indexes, title, "True", image, ctx.guild.id)
        else:
            await self.bot.db.execute('INSERT INTO welcome_msg (msg, indexes, guild_id, title, image, embed) VALUES ($1, $2, $3, $4, $5. $6)', msg,
                                      indexes, ctx.guild.id, title, image, "True")
        ctx.bot.welcome_msg_cache[ctx.guild.id] = [msg, indexes, "True", title, image]
        return await ctx.reply("The welcome message has been updated.")

    @commands.hybrid_command(description="Make a custom welcome message.", with_app_command=True)
    @commands.guild_only()
    async def custom_welcome(self, ctx):
        embed = discord.Embed(description="Please type your custom message."
                                          "\n"
                                          "\nSay membermention to mention the user that joined."
                                          "\nSay guildname for the server name"
                                          "\nSay membername to say the user's name and discriminator but not ping them.",
                              color=discord.Color.purple())
        await ctx.reply(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        msg = await self.bot.wait_for('message', check=check)
        msg = msg.content
        index_mention = None
        index_guild = None
        index_member = None
        if "membermention" in msg:
            index_mention = msg.find("membermention")
            msg = msg.replace("membermention", "%s")
        if "guildname" in msg:
            index_guild = msg.find("guildname")
            msg = msg.replace("guildname", "%s")
        if "membername" in msg:
            index_member = msg.find("membername")
            msg = msg.replace("membername", "%s")
        numbers = []
        indexes = ""
        if index_mention:
            numbers += [index_mention]
        if index_guild:
            numbers += [index_guild]
        if index_member:
            numbers += [index_member]
        for i in range(len(numbers)):
            if index_mention:
                if numbers[i] == index_mention:
                    indexes += "index_mention "
            if index_guild:
                if numbers[i] == index_guild:
                    indexes += "index_guild "
            if index_member:
                if numbers[i] == index_member:
                    indexes += "index_member "
        message = await self.bot.db.fetchval('SELECT msg FROM welcome_msg WHERE guild_id = $1', ctx.guild.id)
        if message:
            await self.bot.db.execute('UPDATE welcome_msg SET (msg, indexes, embed) = ($1, $2, $3) WHERE guild_id = $4', msg,
                                      indexes, "False", ctx.guild.id)
        else:
            await self.bot.db.execute('INSERT INTO welcome_msg (msg, indexes, guild_id, embed) VALUES ($1, $2, $3, $4)', msg,
                                      indexes, ctx.guild.id, "False")
        ctx.bot.welcome_msg_cache[ctx.guild.id] = [msg, indexes, "False", "None", "None"]
        return await ctx.reply("The welcome message has been updated.")

    @commands.hybrid_command(description="Enable or Disable welcome message", with_app_command=True)
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def toggle_welcome(self, ctx):
        try:
            self.bot.welcome_cache[ctx.guild.id]
        except KeyError:  # not cached
            data = await self.bot.db.fetchval('SELECT welcomeoff FROM welcome WHERE guild_id = $1', ctx.guild.id)
            if data:  # disabled
                await self.bot.db.execute('DELETE FROM welcome where guild_id = $1', ctx.guild.id)
                # enabled
                return await ctx.reply("The welcome message has been enabled")
            elif not data:  # enabled
                await self.bot.db.execute('INSERT INTO welcome (welcomeoff, guild_id) VALUES ($1, $2)', "True",
                                          ctx.guild.id)
                self.bot.welcome_cache[ctx.guild.id] = "True"
                # disabled
                return await ctx.reply("The welcome message has been disabled")
        else:
            del self.bot.welcome_cache[ctx.guild.id]
            await self.bot.db.execute('DELETE FROM welcome where guild_id = $1', ctx.guild.id)
            return await ctx.reply("The welcome message has been enabled")

    # GOODBYE STUFF ################################################################
    @commands.Cog.listener("on_member_remove")
    @commands.guild_only()
    async def goodbye(self, member):
        try:
            self.bot.goodbye_cache[member.guild.id]
        except KeyError:  # not cached
            data = await self.bot.db.fetchval('SELECT goodbyeoff FROM goodbye WHERE guild_id = $1', member.guild.id)
            if data:  # disabled
                return
        if member.guild.system_channel is not None:
            try:
                self.bot.goodbye_msg_cache[member.guild.id]
            except KeyError:
                msg = await self.bot.db.fetchval('SELECT msg FROM goodbye_msg WHERE guild_id = $1', member.guild.id)
                indexes = await self.bot.db.fetchval('SELECT indexes FROM goodbye_msg WHERE guild_id = $1',
                                                     member.guild.id)
                embed = await self.bot.db.fetchval('SELECT embed FROM goodbye_msg WHERE guild_id = $1', member.guild.id)
                title = await self.bot.db.fetchval('SELECT title FROM goodbye_msg WHERE guild_id = $1', member.guild.id)
                image = await self.bot.db.fetchval('SELECT image FROM goodbye_msg WHERE guild_id = $1', member.guild.id)
                if not msg:
                    msg = f'{member.mention} has left {member.guild.name}.'
                    indexes = []
                else:
                    indexes = indexes.split()
            else:
                msg = self.bot.goodbye_msg_cache[member.guild.id][0]
                title = self.bot.goodbye_msg_cache[member.guild.id][3]
                embed = self.bot.goodbye_msg_cache[member.guild.id][2]
                image = self.bot.goodbye_msg_cache[member.guild.id][4]
                indexes = self.bot.goodbye_msg_cache[member.guild.id][1]
                indexes = indexes.split()
            for i in range(len(indexes)):
                if indexes[i] == "index_mention":
                    indexes[i] = member.mention
                if indexes[i] == "index_guild":
                    indexes[i] = member.guild.name
                if indexes[i] == "index_name":
                    indexes[i] = f"{member.name}#{member.discriminator}"
            if len(indexes) == 1:
                description = msg % indexes[0]
            elif len(indexes) == 2:
                description = msg % (indexes[0], indexes[1])
            elif len(indexes) == 3:
                description = msg % (indexes[0], indexes[1], indexes[2])
            else:
                description = msg
            if embed == "True":
                if title == "None":
                    msg = discord.Embed(description=description, color=discord.Color.purple())
                else:
                    msg = discord.Embed(title=title, description=description, color=discord.Color.purple())
                if image != "None":
                    msg.set_image(url=image)
                return await member.guild.system_channel.send(embed=msg)
            else:
                return await member.guild.system_channel.send(description)

    @commands.hybrid_command(description="Make a custom goodbye message.", with_app_command=True)
    @commands.guild_only()
    async def custom_goodbye_embed(self, ctx):
        embed = discord.Embed(description="Please send the title of your embed below. Say None for no title. "
                                          "If you would like a text announcement use the `text_announce` command.",
                              color=discord.Color.purple())
        await ctx.reply(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        title = await self.bot.wait_for('message', check=check)
        title = title.content
        embed = discord.Embed(description="Please send the description of your embed below. "
                                          "\n"
                                          "\nSay membermention to mention the user that left."
                                          "\nSay guildname for the server name"
                                          "\nSay membername to say the user's name and discriminator but not ping them.",
                              color=discord.Color.purple())
        await ctx.reply(embed=embed)
        description = await self.bot.wait_for('message', check=check)
        description = description.content
        embed = discord.Embed(
            description="Please send the url of your image for your embed below. Send None if you would like no image. If you would like a text announcement use the `text_announce` command.",
            color=discord.Color.purple())
        await ctx.reply(embed=embed)
        image = await self.bot.wait_for('message', check=check)
        image = image.content
        index_mention = None
        index_guild = None
        index_member = None
        if "membermention" in description:
            index_mention = description.find("membermention")
            description = description.replace("membermention", "%s")
        if "guildname" in description:
            index_guild = description.find("guildname")
            description = description.replace("guildname", "%s")
        if "membername" in description:
            index_member = description.find("membername")
            description = description.replace("membername", "%s")
        msg = description
        numbers = []
        indexes = ""
        if index_mention:
            numbers += [index_mention]
        if index_guild:
            numbers += [index_guild]
        if index_member:
            numbers += [index_member]
        for i in range(len(numbers)):
            if index_mention:
                if numbers[i] == index_mention:
                    indexes += "index_mention "
            if index_guild:
                if numbers[i] == index_guild:
                    indexes += "index_guild "
            if index_member:
                if numbers[i] == index_member:
                    indexes += "index_member "
        message = await self.bot.db.fetchval('SELECT msg FROM goodbye_msg WHERE guild_id = $1', ctx.guild.id)
        if message:
            await self.bot.db.execute(
                'UPDATE goodbye_msg SET (msg, indexes, title, embed, image) = ($1, $2, $3, $4, $5) WHERE guild_id = $6',
                msg,
                indexes, title, "True", image, ctx.guild.id)
        else:
            await self.bot.db.execute(
                'INSERT INTO goodbye_msg (msg, indexes, guild_id, title, image, embed) VALUES ($1, $2, $3, $4, $5. $6)',
                msg,
                indexes, ctx.guild.id, title, image, "True")
        ctx.bot.goodbye_msg_cache[ctx.guild.id] = [msg, indexes, "True", title, image]
        return await ctx.reply("The goodbye message has been updated.")

    @commands.hybrid_command(description="Make a custom goodbye message.", with_app_command=True)
    @commands.guild_only()
    async def custom_goodbye(self, ctx):
        embed = discord.Embed(description="Please type your custom message."
                                          "\n"
                                          "\nSay membermention to mention the user that left."
                                          "\nSay guildname for the server name"
                                          "\nSay membername to say the user's name and discriminator but not ping them.",
                              color=discord.Color.purple())
        await ctx.reply(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        msg = await self.bot.wait_for('message', check=check)
        msg = msg.content
        index_mention = None
        index_guild = None
        index_member = None
        if "membermention" in msg:
            index_mention = msg.find("membermention")
            msg = msg.replace("membermention", "%s")
        if "guildname" in msg:
            index_guild = msg.find("guildname")
            msg = msg.replace("guildname", "%s")
        if "membername" in msg:
            index_member = msg.find("membername")
            msg = msg.replace("membername", "%s")
        numbers = []
        indexes = ""
        if index_mention:
            numbers += [index_mention]
        if index_guild:
            numbers += [index_guild]
        if index_member:
            numbers += [index_member]
        for i in range(len(numbers)):
            if index_mention:
                if numbers[i] == index_mention:
                    indexes += "index_mention "
            if index_guild:
                if numbers[i] == index_guild:
                    indexes += "index_guild "
            if index_member:
                if numbers[i] == index_member:
                    indexes += "index_member "

        message = await self.bot.db.fetchval('SELECT msg FROM goodbye_msg WHERE guild_id = $1', ctx.guild.id)
        if message:
            await self.bot.db.execute('UPDATE goodbye_msg SET (msg, indexes, embed) = ($1, $2, $3) WHERE guild_id = $4', msg,
                                      indexes, "False", ctx.guild.id)
        else:
            await self.bot.db.execute('INSERT INTO goodbye_msg (msg, indexes, guild_id, embed) VALUES ($1, $2, $3, $4)', msg,
                                      indexes, ctx.guild.id, "False")
        ctx.bot.goodbye_msg_cache[ctx.guild.id] = [msg, indexes, "False", "None", "None"]
        return await ctx.reply("The goodbye message has been updated.")


    @commands.hybrid_command(description="Enable or Disable goodbye message", with_app_command=True)
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def toggle_goodbye(self, ctx):
        try:
            self.bot.goodbye_cache[ctx.guild.id]
        except KeyError:  # not cached
            data = await self.bot.db.fetchval('SELECT goodbyeoff FROM goodbye WHERE guild_id = $1', ctx.guild.id)
            if data:  # disabled
                await self.bot.db.execute('DELETE FROM goodbye where guild_id = $1', ctx.guild.id)
                # enabled
                return await ctx.reply("The goodbye message has been enabled")
            elif not data:  # enabled
                await self.bot.db.execute('INSERT INTO goodbye (goodbyeoff, guild_id) VALUES ($1, $2)', "True",
                                          ctx.guild.id)
                self.bot.goodbye_cache[ctx.guild.id] = "True"
                return await ctx.reply("The goodbye message has been disabled")
                # disabled
        else:
            del self.bot.goodbye_cache[ctx.guild.id]
            await self.bot.db.execute('DELETE FROM goodbye where guild_id = $1', ctx.guild.id)
            return await ctx.reply("The goodbye message has been disabled")


async def setup(bot):
    await bot.add_cog(Welcome(bot))
