from discord.ext import commands
import random
from discord import app_commands
import discord

class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="poop",with_app_command=True, description="poop.")
    async def charlie_is_stupid(self, ctx: commands.Context):
        await ctx.reply("I just pooped really hard.")

    @app_commands.command(description="Responds with an offensive yo mama joke.")
    async def yomama(self, interaction: discord.Interaction) -> None:
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
        await interaction.response.send_message(response)

    @commands.hybrid_command(name="rr", description="Run this command for a good chuckle.", with_app_command=True)
    async def rr(self, ctx: commands.Context):
        await ctx.reply('https://tenor.com/view/rick-astly-rick-rolled-gif-22755440')

    @commands.hybrid_command(name="slap", description="Slap a friend.", with_app_command=True)
    async def slap(self, ctx: commands.Context):
        slap_gifs = ['https://cdn.discordapp.com/attachments/995847174854291526/996248072407486526/IMG_2334.gif',
                     'https://cdn.discordapp.com/attachments/995847174854291526/996248007089602600/IMG_2333.gif',
                     'https://cdn.discordapp.com/attachments/995847174854291526/996247897656000533/IMG_2332.gif']
        response = random.choice(slap_gifs)
        await ctx.reply(response)

    @commands.hybrid_command(description="Hug a friend.", with_app_command=True)
    async def hug(self, ctx: commands.Context):
        hug_gifs = ['https://cdn.discordapp.com/attachments/995847174854291526/996248363328614480/IMG_2338.gif',
                    'https://cdn.discordapp.com/attachments/995847174854291526/996248206281277550/IMG_2335.gif',
                    'https://cdn.discordapp.com/attachments/995847174854291526/996248285285208087/IMG_2337.gif']
        response = random.choice(hug_gifs)
        await ctx.reply(response)

    @commands.hybrid_command(description="Kiss a friend.", with_app_command=True)
    async def kiss(self, ctx: commands.Context):
        kiss_gifs = ['https://cdn.discordapp.com/attachments/995847174854291526/996247560136171632/IMG_2331.gif',
                     'https://cdn.discordapp.com/attachments/995847174854291526/996247521976385607/IMG_2330.gif',
                     'https://cdn.discordapp.com/attachments/995847174854291526/996247359858163843/IMG_2329.gif']
        response = random.choice(kiss_gifs)
        await ctx.reply(response)


async def setup(bot):
    await bot.add_cog(Fun(bot))
