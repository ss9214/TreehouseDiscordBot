import discord
from discord.ext import commands
from random import randint

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener("on_message")
    @commands.guild_only()
    async def msg_to_money(self, message):
        if message.author.bot:
            return
        else:
            ints = [1, 2]
            await self.open_account(message.author.id)
            wallet = await self.bot.db.fetchval('SELECT wallet FROM users WHERE user_id = $1', message.author.id)
            if randint(1, 10) in ints:
                wallet += 1
                await self.bot.db.execute('UPDATE users SET wallet = $1 WHERE user_id = $2', wallet, message.author.id)
                self.bot.user_cache[message.author.id][0] = wallet
            else:
                return

    @commands.hybrid_command(aliases=["daily", "dl"], description="Claim your daily login reward!",with_app_command=True)
    @commands.guild_only()
    @commands.cooldown(1, 60 * 60 * 24, commands.BucketType.user)
    async def daily_login(self, ctx):
        await self.open_account(ctx.author.id)
        await self.update(ctx.author.id, 1000, 0, 0, 0)
        return await ctx.reply("$1000 has been added to your balance.")

    @daily_login.error
    async def daily_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            cooldown = round(error.retry_after / 3600)
            if cooldown < 1:
                cooldown = round(error.retry_after / 60)
                if cooldown < 1:
                    cooldown = round(error.retry_after)
                    return await ctx.reply(
                        f":no_entry: You are still on cooldown. Please check back in {cooldown} seconds")
                return await ctx.reply(f":no_entry: You are still on cooldown. Please check back in {cooldown} minutes")
            return await ctx.reply(f":no_entry: You are still on cooldown. Please check back in {cooldown} hours")
        else:
            raise error

    @commands.hybrid_command(aliases=["weekly", "wl"], description="Claim your weekly login reward!",with_app_command=True)
    @commands.guild_only()
    @commands.cooldown(1, 60 * 60 * 24 * 7, commands.BucketType.user)
    async def weekly_login(self, ctx):
        await self.open_account(ctx.author.id)
        await self.update(ctx.author.id, 10000, 0, 0, 0)
        return await ctx.reply("$10000 has been added to your balance.")

    @weekly_login.error
    async def weekly_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            cooldown = round(error.retry_after / (3600 * 24))
            if cooldown < 1:
                cooldown = round(error.retry_after / 3600)
                if cooldown < 1:
                    cooldown = round(error.retry_after / 60)
                    if cooldown < 1:
                        cooldown = round(error.retry_after)
                        return await ctx.send(
                            f":no_entry: You are still on cooldown. Please check back in {cooldown} seconds")
                    return await ctx.send(
                        f":no_entry: You are still on cooldown. Please check back in {cooldown} minutes")
                return await ctx.send(f":no_entry: You are still on cooldown. Please check back in {cooldown} hours")
            return await ctx.send(f":no_entry: You are still on cooldown. Please check back in {cooldown} days")

    async def open_account(self, user_id):
        try:
            self.bot.user_cache[user_id]
        except KeyError:  # not cached
            # bank, wins, losses
            in_db = await self.bot.db.fetchrow('SELECT wallet, bank, wins, losses FROM users WHERE user_id = $1',
                                               user_id)
            wal = await self.bot.db.fetchval('SELECT wallet FROM users WHERE user_id = $1', user_id)
            bank = await self.bot.db.fetchval('SELECT bank FROM users WHERE user_id = $1', user_id)
            wins = await self.bot.db.fetchval('SELECT wins FROM users WHERE user_id = $1', user_id)
            losses = await self.bot.db.fetchval('SELECT losses FROM users WHERE user_id = $1', user_id)
            if not in_db:
                self.bot.user_cache[user_id] = [100, 100, 0, 0]
                await self.bot.db.execute(
                    'INSERT INTO users (wallet, bank, wins, losses, user_id) VALUES (100, 100, 0, 0, $1)', user_id)
            else:
                self.bot.user_cache[user_id] = [wal, bank, wins, losses]
        else:
            return False

    @commands.hybrid_command(aliases=["bal"], description="Check your balance.", with_app_command=True)
    @commands.guild_only()
    async def balance(self, ctx):
        await self.open_account(ctx.author.id)
        wallet_amt = ctx.bot.user_cache[ctx.author.id][0]
        bank_amt = ctx.bot.user_cache[ctx.author.id][1]
        em = discord.Embed(title=f"{ctx.author.name}'s Balance", color=discord.Color.blue())
        em.add_field(name="Wallet Balance: ", value=f'${wallet_amt}')
        em.add_field(name="Bank Balance: ", value=f'${bank_amt}')
        await ctx.reply(embed=em)

    @commands.hybrid_command(aliases=["prof", "pf"], description="Check your profile.", with_app_command=True)
    @commands.guild_only()
    async def profile(self, ctx):
        await self.open_account(ctx.author.id)
        wallet_amt = ctx.bot.user_cache[ctx.author.id][0]
        bank_amt = ctx.bot.user_cache[ctx.author.id][1]
        win_amt = ctx.bot.user_cache[ctx.author.id][2]
        loss_amt = ctx.bot.user_cache[ctx.author.id][3]
        em = discord.Embed(title=f"{ctx.author.name}'s Profile", color=discord.Color.blue())
        em.add_field(name=f"Wallet Balance: ", value=f'${wallet_amt}')
        em.add_field(name=f"Bank Balance: ", value=f'${bank_amt}')
        em.add_field(name=f"Win count: ", value=f'{win_amt} wins')
        em.add_field(name=f"Loss Count: ", value=f'{loss_amt} losses')
        await ctx.reply(embed=em)

    async def update(self, user_id, wallet_amt, bank_amt, wins, losses):
        self.bot.user_cache[user_id][0] += wallet_amt
        self.bot.user_cache[user_id][1] += bank_amt
        self.bot.user_cache[user_id][2] += wins
        self.bot.user_cache[user_id][3] += losses
        await self.bot.db.execute('UPDATE users SET (wallet, bank, wins, losses) = ($1, $2, $3, $4) WHERE user_id = $5',
                                  self.bot.user_cache[user_id][0], self.bot.user_cache[user_id][1],
                                  self.bot.user_cache[user_id][2], self.bot.user_cache[user_id][3], user_id)


async def setup(bot):
    await bot.add_cog(Economy(bot))
