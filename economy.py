import os
import discord
from discord.ext import commands
from random import randint
import random
import asyncio

user_cache = {00000000000000: [0, 0, 0, 0]}


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Challenge someone to a connect4 game for money", aliases=["con4"])
    @commands.guild_only()
    async def connect4(self, ctx, player: discord.Member = None, money=None):
        con4_board = []
        for i in range(42):
            con4_board += [":black_circle:"]
        await self.open_account(player.id)
        await self.open_account(ctx.author.id)
        if not player:
            return await ctx.send(
                "Please include who you are challenging at a game of connect4 and if applicable, the money you would like to wager.")
        if money:
            if money > user_cache[ctx.author.id][0]:
                return await ctx.send(f"{ctx.author.mention} doesn't have enough money to gamble. L")
            elif money > user_cache[player.id][0]:
                return await ctx.send(f"{player.mention} doesn't have enough money to gamble. L")
            msg = await ctx.send(
                f"{player.mention},{ctx.author.mention} has challenged you to a game of connect4 for ${money}.\n React below to accept or deny.")
        else:
            msg = await ctx.send(
                f"{player.mention},{ctx.author.mention} has challenged you to a game of connect4 for fun (no gambling).\n React below to accept or deny.")
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")

        def check(reaction, user):
            return user == player and str(reaction.emoji) in ["✅", "❌"]

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
            if str(reaction.emoji) == "✅":
                await ctx.send(
                    f"{player.mention} has accepted {ctx.author.mention}'s challenge! The game will start momentarily.")

            elif str(reaction.emoji) == "❌":
                return await ctx.send(f"{player.mention} has denied {ctx.author.mention}'s challenge!")
        except asyncio.TimeoutError:
            return await ctx.send(f"{player.mention} took too long to respond.")
        else:
            emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣"]
            emojistring = ""
            for i in range(len(emojis)):
                emojistring += emojis[i]
            msg = ""
            templist = [7, 14, 21, 28, 35]
            for i in range(len(con4_board)):
                if i in templist:
                    msg += f"\n{con4_board[i]}"
                else:
                    msg += con4_board[i]
            board = await ctx.send(f'{msg}\n\n{emojistring}')
            for emoji in emojis:
                await board.add_reaction(emoji)
            turn = 1
            while self.con4checkWin(ctx.author.mention, player.mention, con4_board) == ":black_circle:" and turn <= 42:
                if turn % 2 != 0:
                    turn_msg = await ctx.send(f"It is {ctx.author.mention}'s turn.")
                elif turn % 2 == 0:
                    turn_msg = await ctx.send(f"It is {player.mention}'s turn.")
                else:
                    turn_msg = None

                def check(reaction, user):
                    if turn % 2 != 0:
                        return (user == ctx.author) and str(reaction.emoji) in emojis
                    elif turn % 2 == 0:
                        return (user == player) and str(reaction.emoji) in emojis

                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
                except asyncio.TimeoutError:
                    if turn % 2 != 0:
                        await ctx.send(f"{ctx.author.mention} took too long to respond, so {player.mention} wins!")
                    elif turn % 2 == 0:
                        await ctx.send(f"{player.mention} took too long to respond, so {ctx.author.mention} wins!")
                    if money:
                        await self.open_account(ctx.author.id)
                        await self.open_account(player.id)
                        if turn % 2 == 0:
                            await self.update(ctx.author.id, money, 0, 0, 0)
                            await self.update(player.id, (money * -1), 0, 0, 0)
                        elif turn % 2 != 0:
                            await self.update(player.id, money, 0, 0, 0)
                            await self.update(ctx.author.id, (money * -1), 0, 0, 0)
                    return
                else:
                    con4_board, emojis = self.con4makeMove(reaction.emoji, emojis, turn, con4_board)
                    turn += 1
                    await turn_msg.delete()
                    await board.delete()
                    emojistring = ""
                    for i in range(len(emojis)):
                        emojistring += emojis[i]
                    msg = ""
                    templist = [7, 14, 21, 28, 35]
                    for i in range(len(con4_board)):
                        if i in templist:
                            msg += f"\n{con4_board[i]}"
                        else:
                            msg += con4_board[i]
                    board = await ctx.send(f'{msg}\n\n{emojistring}')
                    for emoji in emojis:
                        await board.add_reaction(emoji)
            else:
                if turn == 43:
                    await ctx.send("You tied so no one wins :sob:")
                else:
                    await ctx.send(f"{self.con4checkWin(ctx.author.mention, player.mention, con4_board)} has won! Congratulations!")
                    if money:
                        user_id = self.con4checkWin(ctx.author.id, player.id, con4_board)
                        await self.open_account(ctx.author.id)
                        await self.open_account(player.id)
                        if user_id == ctx.author.id:
                            await self.update(ctx.author.id, money, 0, 0, 0)
                            await self.update(player.id, (money * -1), 0, 0, 0)
                        elif user_id == player.id:
                            await self.update(player.id, money, 0, 0, 0)
                            await self.update(ctx.author.id, (money * -1), 0, 0, 0)

    def con4makeMove(self, emoji, emojis, turn, board):
        emoji_list = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
        for index in range(len(emoji_list)):
            if emoji_list[index] == emoji:
                if turn % 2 != 0:
                    if board[index+35] == ":black_circle:":
                        board[index+35] = ":red_circle:"
                    elif board[index+28] == ":black_circle:":
                        board[index+28] = ":red_circle:"
                    elif board[index+21] == ":black_circle:":
                        board[index+21] = ":red_circle:"
                    elif board[index+14] == ":black_circle:":
                        board[index+14] = ":red_circle:"
                    elif board[index+7] == ":black_circle:":
                        board[index+7] = ":red_circle:"
                    else:
                        board[index] = ":red_circle:"
                elif turn % 2 == 0:
                    if board[index+35] == ":black_circle:":
                        board[index+35] = ":yellow_circle:"
                    elif board[index+28] == ":black_circle:":
                        board[index+28] = ":yellow_circle:"
                    elif board[index+21] == ":black_circle:":
                        board[index+21] = ":yellow_circle:"
                    elif board[index+14] == ":black_circle:":
                        board[index+14] = ":yellow_circle:"
                    elif board[index+7] == ":black_circle:":
                        board[index+7] = ":yellow_circle:"
                    else:
                        board[index] = ":yellow_circle:"
                for i in range(7):
                    templist = [board[i], board[i + 7], board[i + 14], board[i + 21], board[i + 28], board[i + 35]]
                    if ":black_circle:" in templist:
                        pass
                    else:
                        emojis.remove(emoji)
                return board, emojis

    def con4checkWin(self, player1, player2, board):
        # horizontal
        horizontallist = []
        for i in range(4, 7):
            horizontallist += [i, i+7, i+14, i+21, i+28, i+35]
        for i in range(len(board)):
            if i in horizontallist:
                pass
            else:
                lineH = self.con4checkDirection(i, i + 1, i + 2, i + 3, player1, player2, board)
                if lineH != ":black_circle:":
                    return lineH
        # vertical
        vertlist = []
        for i in range(21, 42):
            vertlist += [i]
        for i in range(len(board)):
            if i in vertlist:
                pass
            else:
                lineV = self.con4checkDirection(i, i + 7, i + 14, i + 21, player1, player2, board)
                if lineV != ":black_circle:":
                    return lineV
        # diagonal down left
        diaglistdownleft = []
        for i in range(2):
            diaglistdownleft += [i, i + 7, i + 14, i + 21, i + 28, i + 35]
        for i in range(21, 42):
            if i in diaglistdownleft:
                pass
            else:
                diaglistdownleft += [i]

        for i in range(len(board)):
            if i in diaglistdownleft:
                pass
            else:
                lineDL = self.con4checkDirection(i, i + 6, i + 12, i + 18, player1, player2, board)
                if lineDL != ":black_circle:":
                    return lineDL

        # diagonal down right
        diaglistdownright = []
        for i in range(4, 7):
            diaglistdownright += [i, i + 7, i + 14, i + 21, i + 28, i + 35]
        for i in range(21, 42):
            if i in diaglistdownright:
                pass
            else:
                diaglistdownright += [i]

        for i in range(len(board)):
            if i in diaglistdownright:
                pass
            else:
                lineDR = self.con4checkDirection(i, i + 8, i + 16, i + 24, player1, player2, board)
                if lineDR != ":black_circle:":
                    return lineDR
        return ":black_circle:"

    def con4checkDirection(self, pos1, pos2, pos3, pos4, player1, player2, board):
        if (board[pos1] == board[pos2] == board[pos3] == board[pos4]) and (board[pos4] != ":black_circle:"):
            if board[pos1] == ":red_circle:":
                return player1
            elif board[pos1] == ":yellow_circle:":
                return player2
        else:
            return ":black_circle:"

    @commands.command(description="Challenge someone to a tictactoe game for money")
    @commands.guild_only()
    async def tictactoe(self, ctx, player: discord.Member = None, money=None):
        tictactoe_board = [":white_large_square:", ":white_large_square:", ":white_large_square:",
                           ":white_large_square:", ":white_large_square:", ":white_large_square:",
                           ":white_large_square:", ":white_large_square:", ":white_large_square:"]
        await self.open_account(player.id)
        await self.open_account(ctx.author.id)
        if not player:
            return await ctx.send(
                "Please include who you are challenging at a game of tic-tac-toe and if applicable, the money you would like to wager.")
        if money:
            if money > user_cache[ctx.author.id][0]:
                return await ctx.send(f"{ctx.author.mention} doesn't have enough money to gamble. L")
            elif money > user_cache[player.id][0]:
                return await ctx.send(f"{player.mention} doesn't have enough money to gamble. L")
            msg = await ctx.send(
                f"{player.mention},{ctx.author.mention} has challenged you to a game of tictactoe for ${money}.\n React below to accept or deny.")
        else:
            msg = await ctx.send(
                f"{player.mention},{ctx.author.mention} has challenged you to a game of tictactoe for fun (no gambling).\n React below to accept or deny.")
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")

        def check(reaction, user):
            return user == player and str(reaction.emoji) in ["✅", "❌"]

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
            if str(reaction.emoji) == "✅":
                await ctx.send(
                    f"{player.mention} has accepted {ctx.author.mention}'s challenge! The game will start momentarily.")

            elif str(reaction.emoji) == "❌":
                return await ctx.send(f"{player.mention} has denied {ctx.author.mention}'s challenge!")
        except asyncio.TimeoutError:
            return await ctx.send(f"{player.mention} took too long to respond.")
        else:

            board = await ctx.send(f'{tictactoe_board[0]} {tictactoe_board[1]} {tictactoe_board[2]}\n'
                                   f'{tictactoe_board[3]} {tictactoe_board[4]} {tictactoe_board[5]}\n'
                                   f'{tictactoe_board[6]} {tictactoe_board[7]} {tictactoe_board[8]}')
            emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
            for emoji in emojis:
                await board.add_reaction(emoji)
            turn = 1
            while self.checkWin(ctx.author.mention, player.mention,
                                tictactoe_board) == ":white_large_square:" and turn <= 9:
                if turn % 2 != 0:
                    turn_msg = await ctx.send(f"It is {ctx.author.mention}'s turn.")
                elif turn % 2 == 0:
                    turn_msg = await ctx.send(f"It is {player.mention}'s turn.")
                else:
                    turn_msg = None

                def check(reaction, user):
                    if turn % 2 != 0:
                        return (user == ctx.author) and str(reaction.emoji) in emojis
                    elif turn % 2 == 0:
                        return (user == player) and str(reaction.emoji) in emojis

                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
                except asyncio.TimeoutError:
                    if turn % 2 != 0:
                        await ctx.send(f"{ctx.author.mention} took too long to respond, so {player.mention} wins!")
                    elif turn % 2 == 0:
                        await ctx.send(f"{player.mention} took too long to respond, so {ctx.author.mention} wins!")
                    if money:
                        await self.open_account(ctx.author.id)
                        await self.open_account(player.id)
                        if turn % 2 == 0:
                            await self.update(ctx.author.id, money, 0, 0, 0)
                            await self.update(player.id, (money * -1), 0, 0, 0)
                        elif turn % 2 != 0:
                            await self.update(player.id, money, 0, 0, 0)
                            await self.update(ctx.author.id, (money * -1), 0, 0, 0)
                    return
                else:
                    tictactoe_board, emojis = self.makeMove(reaction.emoji, emojis, turn, tictactoe_board)
                    turn += 1
                    await turn_msg.delete()
                    await board.delete()
                    board = await ctx.send(f'{tictactoe_board[0]} {tictactoe_board[1]} {tictactoe_board[2]}\n'
                                           f'{tictactoe_board[3]} {tictactoe_board[4]} {tictactoe_board[5]}\n'
                                           f'{tictactoe_board[6]} {tictactoe_board[7]} {tictactoe_board[8]}')
                    for emoji in emojis:
                        await board.add_reaction(emoji)
            else:
                if turn == 10:
                    await ctx.send("You tied so no one wins :sob:")
                else:
                    await ctx.send(
                        f"{self.checkWin(ctx.author.mention, player.mention, tictactoe_board)} has won! Congratulations!")
                    if money:
                        user_id = self.checkWin(ctx.author.id, player.id, tictactoe_board)
                        await self.open_account(ctx.author.id)
                        await self.open_account(player.id)
                        if user_id == ctx.author.id:
                            await self.update(ctx.author.id, money, 0, 0, 0)
                            await self.update(player.id, (money * -1), 0, 0, 0)
                        elif user_id == player.id:
                            await self.update(player.id, money, 0, 0, 0)
                            await self.update(ctx.author.id, (money * -1), 0, 0, 0)

    def makeMove(self, emoji, emojis, turn, board):
        emoji_list = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
        for index in range(len(emoji_list)):
            if emoji_list[index] == emoji:
                if turn % 2 != 0:
                    board[index] = ":regional_indicator_x:"
                elif turn % 2 == 0:
                    board[index] = ":regional_indicator_o:"
                emojis.remove(emoji)
                return board, emojis

    def checkWin(self, player1, player2, board):
        # horizontal
        lineHOne = self.checkDirection(0, 1, 2, player1, player2, board)
        if lineHOne != ":white_large_square:":
            return lineHOne
        lineHTwo = self.checkDirection(3, 4, 5, player1, player2, board)
        if lineHTwo != ":white_large_square:":
            return lineHTwo
        lineHThree = self.checkDirection(6, 7, 8, player1, player2, board)
        if lineHThree != ":white_large_square:":
            return lineHThree
        # vertical
        lineVOne = self.checkDirection(0, 3, 6, player1, player2, board)
        if lineVOne != ":white_large_square:":
            return lineVOne
        lineVTwo = self.checkDirection(1, 4, 7, player1, player2, board)
        if lineVTwo != ":white_large_square:":
            return lineVTwo
        lineVThree = self.checkDirection(2, 5, 8, player1, player2, board)
        if lineVThree != ":white_large_square:":
            return lineVThree
        # diagonal
        lineDOne = self.checkDirection(0, 4, 8, player1, player2, board)
        if lineDOne != ":white_large_square:":
            return lineDOne
        lineDTwo = self.checkDirection(2, 4, 6, player1, player2, board)
        if lineDTwo != ":white_large_square:":
            return lineDTwo
        return ":white_large_square:"

    def checkDirection(self, pos1, pos2, pos3, player1, player2, board):
        if (board[pos1] == board[pos2] == board[pos3]) and (board[pos3] != ":white_large_square:"):
            if board[pos1] == ":regional_indicator_x:":
                return player1
            elif board[pos1] == ":regional_indicator_o:":
                return player2
        else:
            return ":white_large_square:"

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

    @commands.command(aliases=["daily", "dl"], description="Claim your daily login reward!")
    @commands.guild_only()
    @commands.cooldown(1, 60 * 60 * 24, commands.BucketType.user)
    async def daily_login(self, ctx):
        await self.open_account(ctx.author.id)
        await self.update(ctx.author.id, 1000, 0, 0, 0)
        return await ctx.send("$1000 has been added to your balance.")

    @daily_login.error
    async def daily_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            cooldown = round(error.retry_after / 3600)
            if cooldown < 1:
                cooldown = round(error.retry_after / 60)
                if cooldown < 1:
                    cooldown = round(error.retry_after)
                    return await ctx.send(
                        f":no_entry: You are still on cooldown. Please check back in {cooldown} seconds")
                return await ctx.send(f":no_entry: You are still on cooldown. Please check back in {cooldown} minutes")
            return await ctx.send(f":no_entry: You are still on cooldown. Please check back in {cooldown} hours")
        else:
            raise error

    @commands.command(aliases=["weekly", "wl"], description="Claim your weekly login reward!")
    @commands.guild_only()
    @commands.cooldown(1, 60 * 60 * 24 * 7, commands.BucketType.user)
    async def weekly_login(self, ctx):
        await self.open_account(ctx.author.id)
        await self.update(ctx.author.id, 10000, 0, 0, 0)
        return await ctx.send("$10000 has been added to your balance.")

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
            user_cache[user_id]
        except KeyError:  # not cached
            # bank, wins, losses
            in_db = await self.bot.db.fetchrow('SELECT wallet, bank, wins, losses FROM users WHERE user_id = $1',
                                               user_id)
            wal = await self.bot.db.fetchval('SELECT wallet FROM users WHERE user_id = $1', user_id)
            bank = await self.bot.db.fetchval('SELECT bank FROM users WHERE user_id = $1', user_id)
            wins = await self.bot.db.fetchval('SELECT wins FROM users WHERE user_id = $1', user_id)
            losses = await self.bot.db.fetchval('SELECT losses FROM users WHERE user_id = $1', user_id)
            if not in_db:
                user_cache[user_id] = [100, 100, 0, 0]
                await self.bot.db.execute(
                    'INSERT INTO users (wallet, bank, wins, losses, user_id) VALUES (100, 100, 0, 0, $1)', user_id)
            else:
                user_cache[user_id] = [wal, bank, wins, losses]
        else:
            return False

    @commands.command(aliases=["bal"], description="Check your balance.")
    @commands.guild_only()
    async def balance(self, ctx):
        await self.open_account(ctx.author.id)
        wallet_amt = user_cache[ctx.author.id][0]
        bank_amt = user_cache[ctx.author.id][1]
        em = discord.Embed(title=f"{ctx.author.name}'s Balance", color=discord.Color.blue())
        em.add_field(name="Wallet Balance: ", value=f'${wallet_amt}')
        em.add_field(name="Bank Balance: ", value=f'${bank_amt}')
        await ctx.send(embed=em)

    @commands.command(aliases=["prof"], description="Check your profile.")
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

    @commands.command(aliases=["cf"], description="Do a gamble coinflip.")
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

    @commands.command(aliases=["dr"], description="Gamble and see if you roll higher or lower than the bot.")
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
