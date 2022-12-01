import os
import discord
from discord.ext import commands
import random
from random import randint
import asyncio
from discord import app_commands

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # @commands.hybrid_command(description="Challenge people to a game of poker.", with_app_command=True)
    # @commands.guild_only()
    # async def poker(self, ctx, min_bet_amount):
    #     card_names = ["Diamonds", "Hearts", "Spades", "Clubs"]
    #     card_numbers = [2, 3, 4, 5, 6, 7, 8, 9, "Jack", "Queen", "King", "Ace"]
    #     cards = []
    #     for card_number in card_numbers:
    #         for card_name in card_names:
    #             cards += f"{card_number} of {card_name}"
    #
    #     embed = discord.Embed(title="Poker Challenge!",
    #                           description=f"React below if you would like to participate in a game of poker!"
    #                                       f"\nThe minimum bet amount is {min_bet_amount}. "
    #                                       f"\nYou have 30 seconds to react!")
    #     msg = await ctx.reply(embed=embed)
    #     await asyncio.sleep(30)
    #     reactions = msg.reactions
    #     players = [user async for user in reactions[0].users()]
    #     if len(players) <= 2:
    #         return await ctx.reply("You must have at least 3 players to play a game of poker.")
    #     player_mentions = []
    #     for i in range(len(players)):
    #         player_mentions += [f"{i + 1}. {players[i].mention}"]
    #     embed = discord.Embed(title="The poker game has started!", description='**__Players:__**\n' + player_mentions.join("\n")
    #                           + f"**Minimum Bet Amount:** {min_bet_amount}")
    #     await ctx.reply(embed=embed)
    #     embed = discord.Embed(description="Each player has successfully placed their starting bets in the pot.")
    #     await ctx.reply(embed=embed)
    #     player = players[0]
    #     game = discord.Embed(title="Poker Game of Texas Hold'em", description=f"Turn: {player.mention}\nRound: 1")
    #     player_hands = {}
    #     for player in players:
    #         player_hands[player.id] = []
    #     for key in player_hands.keys():
    #         random_card = randint(0, len(cards))
    #         player_hands[key] += [cards[random_card]]
    #         del cards[random_card]
    #         random_card = randint(0, len(cards))
    #         player_hands[key] += [cards[random_card]]
    #         del cards[random_card]
    #
    # async def poker_move(self, first_turn, channel, player, players):
    #     current_player = ""
    #     if player == players[len(players) - 1]:
    #         current_player = "last player"
    #     moves = ["check", "raise", "fold", "call"]
    #     if first_turn:
    #         embed = discord.Embed(description=f"{player.mention}, how much will you make the initial bet amount?")
    #     else:
    #         embed = discord.Embed(description=f"{player.mention}, what will be your move: check, raise, fold, or call?")
    #     await channel.reply(embed=embed)
    #
    #     def check(m):
    #         return m.author == player and m.channel == channel.channel
    #
    #     while True:
    #         msg = await self.bot.wait_for('message', check=check)
    #         move = msg.content
    #         if first_turn:
    #             try:
    #                 int(move)
    #             except ValueError:
    #                 pass
    #             else:
    #                 break
    #         elif move in moves:
    #             break
    #     if first_turn:
    #         return move
    #     else:
    #         if move == "check":
    #             return "check"
    #         if move == "raise":
    #             embed = discord.Embed(description=f"{player.mention}, how much are you going to raise by?")
    #             await ctx.reply(embed=embed)
    #
    #             def check(m):
    #                 return m.author == player and m.channel == channel.channel
    #
    #             while True:
    #                 msg = await self.bot.wait_for('message', check=check)
    #                 raise_amt = msg.content
    #                 try:
    #                     int(raise_amt)
    #                 except ValueError:
    #                     await ctx.reply("Your response must be a number.")
    #                 else:
    #                     break
    #             return "raise" and int(raise_amt)
    #         if move == "fold":
    #             return "fold" and player
    #
    #
    # async def check_poker_win(self, players):
    #     poker_hands = ["Royal Flush", "Straight Flush", "Four of a Kind", "Full House", "Flush", "Straight",
    #                    "Three of a Kind",
    #                    "Two Pair", "One Pair", "High Card"]

    @commands.hybrid_command(description="Challenge someone to a connect4 game for an optional amount of money",
                      aliases=["con4"], with_app_command=True)
    @commands.guild_only()
    async def connect4(self, ctx, player: discord.Member = None, optional_money=None):
        con4_board = []
        for i in range(42):
            con4_board += [":black_circle:"]
        await self.open_account(player.id)
        await self.open_account(ctx.author.id)
        if not player:
            return await ctx.reply(
                "Please include who you are challenging at a game of connect4 and if applicable, the money you would like to wager.")
        if optional_money:
            if optional_money > ctx.bot.user_cache[ctx.author.id][0]:
                return await ctx.reply(f"{ctx.author.mention} doesn't have enough money to gamble. L")
            elif optional_money > ctx.bot.user_cache[player.id][0]:
                return await ctx.reply(f"{player.mention} doesn't have enough money to gamble. L")
            msg = await ctx.send(
                f"{player.mention},{ctx.author.mention} has challenged you to a game of connect4 for ${optional_money}.\n React below to accept or deny.")
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
                    if optional_money:
                        await self.open_account(ctx.author.id)
                        await self.open_account(player.id)
                        if turn % 2 == 0:
                            await self.update(ctx.author.id, optional_money, 0, 0, 0)
                            await self.update(player.id, (optional_money * -1), 0, 0, 0)
                        elif turn % 2 != 0:
                            await self.update(player.id, optional_money, 0, 0, 0)
                            await self.update(ctx.author.id, (optional_money * -1), 0, 0, 0)
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
                    await ctx.send(
                        f"{self.con4checkWin(ctx.author.mention, player.mention, con4_board)} has won! Congratulations!")
                    if optional_money:
                        user_id = self.con4checkWin(ctx.author.id, player.id, con4_board)
                        await self.open_account(ctx.author.id)
                        await self.open_account(player.id)
                        if user_id == ctx.author.id:
                            await self.update(ctx.author.id, optional_money, 0, 0, 0)
                            await self.update(player.id, (optional_money * -1), 0, 0, 0)
                        elif user_id == player.id:
                            await self.update(player.id, optional_money, 0, 0, 0)
                            await self.update(ctx.author.id, (optional_money * -1), 0, 0, 0)

    async def con4makeMove(self, emoji, emojis, turn, board):
        emoji_list = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
        for index in range(len(emoji_list)):
            if emoji_list[index] == emoji:
                if turn % 2 != 0:
                    if board[index + 35] == ":black_circle:":
                        board[index + 35] = ":red_circle:"
                    elif board[index + 28] == ":black_circle:":
                        board[index + 28] = ":red_circle:"
                    elif board[index + 21] == ":black_circle:":
                        board[index + 21] = ":red_circle:"
                    elif board[index + 14] == ":black_circle:":
                        board[index + 14] = ":red_circle:"
                    elif board[index + 7] == ":black_circle:":
                        board[index + 7] = ":red_circle:"
                    else:
                        board[index] = ":red_circle:"
                elif turn % 2 == 0:
                    if board[index + 35] == ":black_circle:":
                        board[index + 35] = ":yellow_circle:"
                    elif board[index + 28] == ":black_circle:":
                        board[index + 28] = ":yellow_circle:"
                    elif board[index + 21] == ":black_circle:":
                        board[index + 21] = ":yellow_circle:"
                    elif board[index + 14] == ":black_circle:":
                        board[index + 14] = ":yellow_circle:"
                    elif board[index + 7] == ":black_circle:":
                        board[index + 7] = ":yellow_circle:"
                    else:
                        board[index] = ":yellow_circle:"
                for i in range(7):
                    templist = [board[i], board[i + 7], board[i + 14], board[i + 21], board[i + 28], board[i + 35]]
                    if ":black_circle:" in templist:
                        pass
                    else:
                        emojis.remove(emoji)
                return board, emojis

    async def con4checkWin(self, player1, player2, board):
        # horizontal
        horizontallist = []
        for i in range(4, 7):
            horizontallist += [i, i + 7, i + 14, i + 21, i + 28, i + 35]
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

    @commands.hybrid_command(description="Challenge someone to a tictactoe game for an optional amount of money", with_app_command=True)
    @commands.guild_only()
    async def tictactoe(self, ctx, player: discord.Member = None, optional_money=None):
        tictactoe_board = [":white_large_square:", ":white_large_square:", ":white_large_square:",
                           ":white_large_square:", ":white_large_square:", ":white_large_square:",
                           ":white_large_square:", ":white_large_square:", ":white_large_square:"]
        await self.open_account(player.id)
        await self.open_account(ctx.author.id)
        if not player:
            return await ctx.reply(
                "Please include who you are challenging at a game of tic-tac-toe and if applicable, the optional_money you would like to wager.")
        if optional_money:
            if optional_money > ctx.bot.user_cache[ctx.author.id][0]:
                return await ctx.reply(f"{ctx.author.mention} doesn't have enough money to gamble. L")
            elif optional_money > ctx.bot.user_cache[player.id][0]:
                return await ctx.reply(f"{player.mention} doesn't have enough money to gamble. L")
            msg = await ctx.send(
                f"{player.mention},{ctx.author.mention} has challenged you to a game of tictactoe for ${optional_money}.\n React below to accept or deny.")
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
                    if optional_money:
                        await self.open_account(ctx.author.id)
                        await self.open_account(player.id)
                        if turn % 2 == 0:
                            await self.update(ctx.author.id, optional_money, 0, 0, 0)
                            await self.update(player.id, (optional_money * -1), 0, 0, 0)
                        elif turn % 2 != 0:
                            await self.update(player.id, optional_money, 0, 0, 0)
                            await self.update(ctx.author.id, (optional_money * -1), 0, 0, 0)
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
                    if optional_money:
                        user_id = self.checkWin(ctx.author.id, player.id, tictactoe_board)
                        await self.open_account(ctx.author.id)
                        await self.open_account(player.id)
                        if user_id == ctx.author.id:
                            await self.update(ctx.author.id, optional_money, 0, 0, 0)
                            await self.update(player.id, (optional_money * -1), 0, 0, 0)
                        elif user_id == player.id:
                            await self.update(player.id, optional_money, 0, 0, 0)
                            await self.update(ctx.author.id, (optional_money * -1), 0, 0, 0)

    async def makeMove(self, emoji, emojis, turn, board):
        emoji_list = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
        for index in range(len(emoji_list)):
            if emoji_list[index] == emoji:
                if turn % 2 != 0:
                    board[index] = ":regional_indicator_x:"
                elif turn % 2 == 0:
                    board[index] = ":regional_indicator_o:"
                emojis.remove(emoji)
                return board, emojis

    async def checkWin(self, player1, player2, board):
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

    @app_commands.command(description="Do a gamble coinflip.")
    @app_commands.choices(choices=[
        app_commands.Choice(name="Heads", value="Heads"),
        app_commands.Choice(name="Tails", value="Tails")
        ])
    @app_commands.guild_only()
    async def coinflip(self, interaction:discord.Interaction, choices: app_commands.Choice[str], bet_amount: int) -> None:
        await self.open_account(interaction.user.id)
        if bet_amount > self.bot.user_cache[interaction.user.id][0]:
            return await interaction.response.send_message("You don't have enough money to gamble. L")
        elif bet_amount < 50:
            return await interaction.response.send_message("Please bet at least $50!")
        if choices.value=="Heads":
            choice = "Heads"
        elif choices.value=="Heads":
            choice = "Tails"
        sides = ["Heads", "Tails"]
        response = random.choice(sides)
        await self.open_account(interaction.user.id)
        if response == choice:
            await self.update(interaction.user.id, bet_amount, 0, 1, 0)
            await interaction.response.send_message(
                f'Result: {response}\nHorray! You flipped {choice}! You were correct so you gained ${bet_amount}!\nYour balance is now ${self.bot.user_cache[interaction.user.id][0]}!')
        elif response != choice:
            await self.update(interaction.user.id, (-1 * bet_amount), 0, 0, 1)
            await interaction.response.send_message(
                f'Result: {response}\nAwwww! You flipped {choice}! You were wrong so you lost ${bet_amount}!\nYour balance is now ${self.bot.user_cache[interaction.user.id][0]}!')

    @app_commands.command(description="Gamble and see if you roll higher or lower than the bot.")
    @app_commands.choices(choices=[
        app_commands.Choice(name="Higher", value="Higher"),
        app_commands.Choice(name="Lower", value="Lower")
        ])
    @commands.guild_only()
    async def dieroll(self, interaction:discord.Interaction, choices: app_commands.Choice[str], bet_amount: int):
        await self.open_account(interaction.user.id)  
        if bet_amount > self.bot.user_cache[interaction.user.id][0]:
            return await interaction.response.send_message("You don't have enough money to gamble. L")
        elif bet_amount < 50:
            return await interaction.response.send_message("Please bet at least $50!")
        if choices.value == "Lower":
            choice = "Lower"
        elif choices.value== "Higher":
            choice = "Higher"
        bot_roll = randint(1, 6)
        your_roll = randint(1, 6)
        while bot_roll == your_roll:
            bot_roll = randint(1, 6)
            your_roll = randint(1, 6)
        if your_roll > bot_roll:
            result = "Higher"
        elif your_roll < bot_roll:
            result = "Lower"

        bot_roll = f"The bot's roll is {bot_roll}"
        await interaction.response.send_message(embed=  discord.Embed(description= bot_roll, color=discord.Color.purple()))
        await asyncio.sleep(1)
        your_roll = f"Your roll is {your_roll}"
        await interaction.edit_original_message(embed=  discord.Embed(description= bot_roll + "\n" + your_roll + "\n", color=discord.Color.purple()))
        await asyncio.sleep(1)

        
        if result == choice:
            await self.update(interaction.user.id, bet_amount, 0, 1, 0)
            result = f"You guessed {choice}, which was correct! You gained ${bet_amount}!\nYour balance is now ${self.bot.user_cache[interaction.user.id][0]}!"
        elif result != choice:
            await self.update(interaction.user.id, (-1 * bet_amount), 0, 0, 1)
            result = f"You guessed {choice}, which was wrong. You lost ${bet_amount}!\nYour balance is now ${self.bot.user_cache[interaction.user.id][0]}!"
        return await interaction.edit_original_message(embed=  discord.Embed(description = bot_roll + "\n" + your_roll + "\n" + result, color=discord.Color.purple()))
    
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

    async def update(self, user_id, wallet_amt, bank_amt, wins, losses):
        self.bot.user_cache[user_id][0] += wallet_amt
        self.bot.user_cache[user_id][1] += bank_amt
        self.bot.user_cache[user_id][2] += wins
        self.bot.user_cache[user_id][3] += losses
        await self.bot.db.execute('UPDATE users SET (wallet, bank, wins, losses) = ($1, $2, $3, $4) WHERE user_id = $5',
                                  self.bot.user_cache[user_id][0], self.bot.user_cache[user_id][1],
                                  self.bot.user_cache[user_id][2], self.bot.user_cache[user_id][3], user_id)


async def setup(bot):
    await bot.add_cog(Games(bot))
