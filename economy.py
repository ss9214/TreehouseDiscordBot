import os
import discord
from discord.ext import commands
from random import randint
import random

user_cache = {00000000000000: [0, 0, 0, 0]}


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
                user_cache[message.author.id][0] = wallet
            else:
                return

    async def open_account(self, user_id):
        try:
            user_cache[user_id]
        except KeyError:  # not cached
            # bank, wins, losses
            in_db = await self.bot.db.fetchrow('SELECT wallet, bank, wins, losses FROM users WHERE user_id = $1', user_id)
            wal = await self.bot.db.fetchval('SELECT wallet FROM users WHERE user_id = $1', user_id)
            bank = await self.bot.db.fetchval('SELECT bank FROM users WHERE user_id = $1', user_id)
            wins = await self.bot.db.fetchval('SELECT wins FROM users WHERE user_id = $1', user_id)
            losses = await self.bot.db.fetchval('SELECT losses FROM users WHERE user_id = $1', user_id)
            if not in_db:
                user_cache[user_id] = [100, 100, 0, 0]
                await self.bot.db.execute('INSERT INTO users (wallet, bank, wins, losses, user_id) VALUES (100, 100, 0, 0, $1)', user_id)
            else:
                user_cache[user_id] = [wal, bank, wins, losses]
        else:
            return False

    @commands.command(aliases=["bal"])
    @commands.guild_only()
    async def balance(self, ctx):
        await self.open_account(ctx.author.id)
        wallet_amt = user_cache[ctx.author.id][0]
        bank_amt = user_cache[ctx.author.id][1]
        em = discord.Embed(title=f"{ctx.author.name}'s Balance", color=discord.Color.blue())
        em.add_field(name="Wallet Balance: ", value=f'${wallet_amt}')
        em.add_field(name="Bank Balance: ", value=f'${bank_amt}')
        await ctx.send(embed=em)

    @commands.command(aliases=["prof"])
    @commands.guild_only()
    async def profile(self, ctx):
        await self.open_account(ctx.author.id)
        wallet_amt = user_cache[ctx.author.id][0]
        bank_amt = user_cache[ctx.author.id][1]
        win_amt = user_cache[ctx.author.id][2]
        loss_amt = user_cache[ctx.author.id][3]
        em = discord.Embed(title=f"{ctx.author.name}'s Profile", color=discord.Color.blue())
        em.add_field(name=f"Wallet Balance: ", value=f'${wallet_amt}')
        em.add_field(name=f"Bank Balance: ", value=f'${bank_amt}')
        em.add_field(name=f"Win count: ", value=f'{win_amt} wins')
        em.add_field(name=f"Loss Count: ", value=f'{loss_amt} losses')
        await ctx.send(embed=em)

    @commands.command(aliases=["cf"], help="Do a gamble coinflip")
    @commands.guild_only()
    async def coinflip(self, ctx, choice=None, bet_amount: int = None):
        await self.open_account(ctx.author.id)
        options = ["h", "t", "heads", "tails", "Heads", "Tails", "head", "tail", "Head", "Tail"]
        if not choice and not bet_amount:
            return await ctx.send("Please include which side you are guessing and the bet amount.")
        elif bet_amount > user_cache[ctx.author.id][0]:
            return await ctx.send("You don't have enough money to gamble. L")
        elif bet_amount < 50:
            return await ctx.send("Please bet at least $50!")
        if choice in options:
            if choice == "h" or choice == "H" or choice == "heads":
                choice = "Heads"
            else:
                choice = "Tails"
            sides = ["Heads", "Tails"]
            response = random.choice(sides)
            await self.open_account(ctx.author.id)
            if response == choice:
                await self.update(ctx.author.id, bet_amount, 0, 1, 0)
                await ctx.send(
                    f'Result: {response}\nHorray! You flipped {choice}! You were correct so you gained ${bet_amount}!\nYour balance is now ${user_cache[ctx.author.id][0]}!')
            elif response != choice:
                await self.update(ctx.author.id, (-1 * bet_amount), 0, 0, 1)
                await ctx.send(
                    f'Result: {response}\nAwwww! You flipped {choice}! You were wrong so you lost ${bet_amount}!\nYour balance is now ${user_cache[ctx.author.id][0]}!')
        else:
            return await ctx.send(f"Acceptable entries for heads and tails include: {options}")

    @commands.command(aliases=["dr"], help="Gamble and see if you roll higher or lower than the bot")
    @commands.guild_only()
    async def dieroll(self, ctx, lower_or_higher=None, bet_amount: int = None):
        await self.open_account(ctx.author.id)
        choice = lower_or_higher
        options = ["l", "L", "low", "Low", "lower", "Lower", "h", "H", "high", "High", "higher", "Higher"]
        if not choice:
            return await ctx.send(
                "Please choose if you will roll higher or lower than the bot and how much you are gambling.")
        elif bet_amount > user_cache[ctx.author.id][0]:
            return await ctx.send("You don't have enough money to gamble. L")
        elif bet_amount < 50:
            return await ctx.send("Please bet at least $50!")
        if choice in options:
            lower_options = ["l", "L", "low", "Low", "lower", "Lower"]
            if choice in lower_options:
                choice = "Lower"
            else:
                choice = "Higher"
            bot_roll = randint(1, 20)
            your_roll = randint(1, 20)
            await ctx.send(f"The bot's roll is {bot_roll}")
            await ctx.send(f"Your roll is {your_roll}")
            if your_roll > bot_roll:
                result = "Higher"
            else:
                result = "Lower"
            if result == choice:
                await self.update(ctx.author.id, bet_amount, 0, 1, 0)
                await ctx.send(f"You guessed {choice}, which was correct! "
                               f"You gained ${bet_amount}!\nYour balance is now ${user_cache[ctx.author.id][0]}!")
            elif result != choice:
                await self.update(ctx.author.id, (-1 * bet_amount), 0, 0, 1)
                await ctx.send(f"You guessed {choice}, which was wrong. "
                               f"You lost ${bet_amount}!\nYour balance is now ${user_cache[ctx.author.id][0]}!")
        else:
            return await ctx.send(f"Acceptable entries for higher and lower include: {options}")

    async def update(self, user_id, wallet_amt, bank_amt, wins, losses):
        user_cache[user_id][0] += wallet_amt
        user_cache[user_id][1] += bank_amt
        user_cache[user_id][2] += wins
        user_cache[user_id][3] += losses
        await self.bot.db.execute('UPDATE users SET (wallet, bank, wins, losses) = ($1, $2, $3, $4) WHERE user_id = $5',
                                  user_cache[user_id][0], user_cache[user_id][1],
                                  user_cache[user_id][2], user_cache[user_id][3], user_id)


async def setup(bot):
    await bot.add_cog(Economy(bot))
