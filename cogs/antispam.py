import os
import discord
from discord.ext import commands
from datetime import timedelta
import datetime
import asyncio


class AntiSpam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cd_mapping = commands.CooldownMapping.from_cooldown(6, 5, commands.BucketType.member)

    @commands.Cog.listener("on_message")
    async def spam_check(self, message):
        bucket = self.cd_mapping.get_bucket(message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            await message.author.timeout(timedelta(seconds=5))
            if message.author.is_timed_out():
                await message.author.send(f"You have been muted for 5 seconds in {message.guild.name} for spamming.")
                await asyncio.sleep(1)
        else:
            return


async def setup(bot):
    await bot.add_cog(AntiSpam(bot))
