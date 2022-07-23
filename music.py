import discord
import os
from discord.ext import commands
import wavelink


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # create node
    @commands.Cog.listener()
    async def node_connect(self):
        await self.bot.wait_until_ready()
        # await wavelink.NodePool.create_node(bot=self.bot, host='lavalink.oops.wtf', port=443, password='www.freelavalink.ga',
        #                                     https=True)
        await wavelink.NodePool.create_node(bot=self.bot, host='lavalink.kapes.eu', port=2222, password='lavalinkplay', https=False)

    # log in
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.loop.create_task(self.node_connect())

    # ready node
    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        print(f"Node {node.identifier} is ready!")

    # play a song command
    @commands.command(description="Play a song in a voice channel through YouTube.")
    @commands.guild_only()
    async def play(self, ctx, *, search: wavelink.YouTubeTrack):
        if search is None:
            await ctx.send("Please include a song to play")
            return
        if ctx.author.voice is None:
            return await ctx.send("Please join a voice channel to run this command.")
        else:
            voice_channel = ctx.author.voice.channel
            voice = ctx.voice_client
        if not ctx.voice_client:
            vc: wavelink.Player = await voice_channel.connect(cls=wavelink.Player)
        elif not ctx.author.voice.channel == ctx.me.voice.channel:
            return await ctx.send("We must be in the same voice channel to play a song")
        else:
            vc: wavelink.Player = voice

        if not vc.is_playing():
            await vc.play(search)
            duration = str(int(search.duration / 60)) + ":"
            if int(search.duration % 60) == 0:
                duration += "00"
            elif 0 < int(search.duration % 60) < 10:
                duration += "0"
                duration += str(int(search.duration % 60))
            else:
                duration += str(int(search.duration % 60))
            await ctx.send(f"**Now Playing**: {search.title} **{duration}**")
        else:
            await vc.queue.put_wait(search)
            duration = str(int(search.duration / 60)) + ":"
            if int(search.duration % 60) == 0:
                duration += "00"
            elif 0 < int(search.duration % 60) < 10:
                duration += "0"
                duration += str(int(search.duration % 60))
            else:
                duration += str(int(search.duration % 60))
            await ctx.send(f"**Added song to queue:** {search.title} **{duration}**")

        vc.ctx = ctx
        setattr(vc, "loop", False)

    # plays next song after current song ends
    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track: wavelink.Track, reason):
        ctx = player.ctx
        vc: player = ctx.voice_client

        if vc.loop:
            return await vc.play(track)
        if vc.queue.is_empty:
            return await vc.disconnect()

        next_song = vc.queue.get()
        await vc.play(next_song)
        duration = str(int(next_song.duration / 60)) + ":"
        if int(next_song.duration % 60) == 0:
            duration += "00"
        elif 0 < int(next_song.duration % 60) < 10:
            duration += "0"
            duration += str(int(next_song.duration % 60))
        else:
            duration += str(int(next_song.duration % 60))
        await ctx.send(f'**Now Playing**: {next_song.title} **{duration}**')

    # leave channel command
    @commands.command(description="Makes the bot leave the voice channel.")
    @commands.guild_only()
    async def leave(self, ctx):
        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)
        if not ctx.voice_client:
            return await ctx.send("The bot is not in a voice channel.")
        elif not ctx.author.voice:
            return await ctx.send("Please join a voice channel to run this command.")
        elif not ctx.author.voice.channel == ctx.me.voice.channel:
            return await ctx.send("We must be in the same voice channel for me to leave.")
        if not player.is_connected():
            await ctx.send("The bot is not connected to a voice channel.")
        else:
            await player.disconnect()
            await ctx.send("The bot has been disconnected.")

    # pause song command
    @commands.command(description="Pause a song that is currently playing.")
    @commands.guild_only()
    async def pause(self, ctx):
        if not ctx.voice_client:
            return await ctx.send("The bot is not in a voice channel.")
        elif not ctx.author.voice:
            return await ctx.send("Please join a voice channel to run this command.")
        elif not ctx.author.voice.channel == ctx.me.voice.channel:
            return await ctx.send("We must be in the same voice channel to pause a song.")
        else:
            vc: wavelink.Player = ctx.voice_client
        if vc.is_playing():
            await vc.pause()
            await ctx.send("The song has been paused.")
        else:
            await ctx.send("There is no audio playing.")

    # resume song command
    @commands.command(aliases=["res"], description="Resume a song that is currently paused.")
    @commands.guild_only()
    async def resume(self, ctx):
        if not ctx.voice_client:
            return await ctx.send("The bot is not in a voice channel.")
        elif not ctx.author.voice:
            return await ctx.send("Please join a voice channel to run this command.")
        elif not ctx.author.voice.channel == ctx.me.voice.channel:
            return await ctx.send("We must be in the same voice channel to resume a song.")
        else:
            vc: wavelink.Player = ctx.voice_client
        if vc.is_paused():
            await vc.resume()
            await ctx.send("The song has been resumed.")
        else:
            await ctx.send("The audio is not currently paused.")

    # toggle loop on or off
    @commands.command(description="Toggle loop on/off for the current song.")
    @commands.guild_only()
    async def loop(self, ctx):
        if not ctx.voice_client:
            return await ctx.send("The bot is not in a voice channel.")
        elif not ctx.author.voice:
            return await ctx.send("Please join a voice channel to run this command.")
        elif not ctx.author.voice.channel == ctx.me.voice.channel:
            return await ctx.send("We must be in the same voice channel to loop a song.")
        else:
            vc: wavelink.Player = ctx.voice_client

        if vc.loop is False:
            setattr(vc, "loop", True)
            return await ctx.send("Loop is toggled on for the current song.")
        else:
            setattr(vc, "loop", False)
            return await ctx.send("Loop is toggled off.")

    # look at queue command
    @commands.command(description="View the current queue.")
    @commands.guild_only()
    async def queue(self, ctx):
        if not ctx.voice_client:
            return await ctx.send("The bot is not in a voice channel.")
        elif not ctx.author.voice:
            return await ctx.send("Please join a voice channel to run this command.")
        elif not ctx.author.voice.channel == ctx.me.voice.channel:
            return await ctx.send("We must be in the same voice channel for me to leave.")
        else:
            vc: wavelink.Player = ctx.voice_client
        if vc.queue.is_empty:
            return await ctx.send("The queue is empty.")
        else:
            for i in range(len(vc.queue)):
                duration = str(int(vc.queue[i].duration / 60)) + ":"
                if int(vc.queue[i].duration % 60) == 0:
                    duration += "00"
                elif 0 < int(vc.queue[i].duration % 60) < 10:
                    duration += "0"
                    duration += str(int(vc.queue[i].duration % 60))
                else:
                    duration += str(int(vc.queue[i].duration % 60))
                await ctx.send(f'**{i + 1}.)** {vc.queue[i]} **{duration}**')

    # skip command
    @commands.command(description="Play the next song in queue")
    @commands.guild_only()
    async def skip(self, ctx):
        if not ctx.voice_client:
            return await ctx.send("The bot is not in a voice channel.")
        elif not ctx.author.voice:
            return await ctx.send("Please join a voice channel to run this command.")
        elif not ctx.author.voice.channel == ctx.me.voice.channel:
            return await ctx.send("We must be in the same voice channel for me to skip this song.")
        else:
            vc: wavelink.Player = ctx.voice_client
        if vc.queue.is_empty:
            return await ctx.send("There is nothing in the queue.")
        else:
            if vc.loop is True:
                setattr(vc, "loop", False)
            await vc.stop()

    @commands.command(aliases=["nowp"], description="Check what song is currently playing")
    @commands.guild_only()
    async def nowplaying(self, ctx):
        if not ctx.voice_client:
            return await ctx.send("The bot is not in a voice channel.")
        else:
            vc: wavelink.Player = ctx.voice_client
        if vc.is_playing() or vc.is_paused():
            duration = str(int(vc.source.duration / 60)) + ":"
            if int(vc.source.duration % 60) == 0:
                duration += "00"
            elif 0 < int(vc.source.duration % 60) < 10:
                duration += "0"
                duration += str(int(vc.source.duration % 60))
            else:
                duration += str(int(vc.source.duration % 60))
            await ctx.send(
                f"The bot is playing {vc.source.title} **{duration}** in channel {ctx.me.voice.channel.mention}")
        else:
            await ctx.send("The bot is currently not playing any audio.")

    @commands.command(aliases=["nextp"], description="Check what song is playing next")
    @commands.guild_only()
    async def nextplaying(self, ctx):
        if not ctx.voice_client:
            return await ctx.send("The bot is not in a voice channel.")
        else:
            vc: wavelink.Player = ctx.voice_client
        if not vc.queue.is_empty:
            next_song = vc.queue.get()
            duration = str(int(next_song.duration / 60)) + ":"
            if int(next_song.duration % 60) == 0:
                duration += "00"
            elif 0 < int(next_song.duration % 60) < 10:
                duration += "0"
                duration += str(int(next_song.duration % 60))
            else:
                duration += str(int(next_song.duration % 60))
            await ctx.send(
                f"The bot is next playing {next_song.title} **{duration}** in channel {ctx.me.voice.channel.mention}")
        elif vc.queue.is_empty is True:
            return await ctx.send("There is nothing in queue.")


async def setup(bot):
    await bot.add_cog(Music(bot))

