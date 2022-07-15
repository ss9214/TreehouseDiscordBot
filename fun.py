import discord
from discord.ext import commands
import random
import os


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["ym"], help="Responds with an offensive yo mama joke.")
    @commands.guild_only()
    async def yomama(self, ctx):
        yo_mama_quotes = [
            "yo mama so fat, when she fell I didn't laugh, but the sidewalk cracked up.",
            'yo mama so fat, when she skips a meal, the stock market drops.',
            'yo mama so fat, it took me two buses and a train to get to her good side.',
            'yo mama so fat, when she goes camping, the bears hide their food.',
            "yo mama so fat, if she buys a fur coat, a whole species will become extinct.",
            "yo mama so fat, she stepped on a scale and it said: 'To be continued.'",
            "yo mama so fat, I swerved to miss her in my car and ran out of gas.",
            "yo mama so fat, she was overthrown by a small militia group, and now she's known as the Republic of Yo Mama."
        ]

        response = random.choice(yo_mama_quotes)
        await ctx.send(response)

    @commands.command(help="Run this command for a good chuckle")
    @commands.guild_only()
    async def rr(self, ctx, *args):
        await ctx.send('https://tenor.com/view/rick-astly-rick-rolled-gif-22755440')

    @commands.command(help="Slap a friend.")
    @commands.guild_only()
    async def slap(self, ctx, *args):
        slap_gifs = ['https://cdn.discordapp.com/attachments/995847174854291526/996248072407486526/IMG_2334.gif',
                     'https://cdn.discordapp.com/attachments/995847174854291526/996248007089602600/IMG_2333.gif',
                     'https://cdn.discordapp.com/attachments/995847174854291526/996247897656000533/IMG_2332.gif']
        response = random.choice(slap_gifs)
        await ctx.send(response)

    @commands.command(help="Slap a friend.")
    @commands.guild_only()
    async def hug(self, ctx, *args):
        hug_gifs = ['https://cdn.discordapp.com/attachments/995847174854291526/996248363328614480/IMG_2338.gif',
                    'https://cdn.discordapp.com/attachments/995847174854291526/996248206281277550/IMG_2335.gif',
                    'https://cdn.discordapp.com/attachments/995847174854291526/996248285285208087/IMG_2337.gif']
        response = random.choice(hug_gifs)
        await ctx.send(response)

    @commands.command(help="Slap a friend.")
    @commands.guild_only()
    async def kiss(self, ctx, *args):
        kiss_gifs = ['https://cdn.discordapp.com/attachments/995847174854291526/996247560136171632/IMG_2331.gif',
                     'https://cdn.discordapp.com/attachments/995847174854291526/996247521976385607/IMG_2330.gif',
                     'https://cdn.discordapp.com/attachments/995847174854291526/996247359858163843/IMG_2329.gif']
        response = random.choice(kiss_gifs)
        await ctx.send(response)


async def setup(bot):
    await bot.add_cog(Fun(bot))
