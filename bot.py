import os
import random
import time
from datetime import datetime

import aiocron
import aiohttp
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if BOT_TOKEN is None:
    print("BOT_TOKEN is not set in the environment variables!")
    exit(1)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="$", intents=intents)

library_channel_id = None
cron_task = None


@bot.event
async def on_ready():
    print(
        f"{bot.user} has connected to Discord! Version {discord.__version__}"
    )
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(e)


async def get_image_urls_from_channel(channel_id):
    image_urls = []
    channel = bot.get_channel(channel_id)
    if channel is None:
        return image_urls
    # may be slow for large channels because it fetches all messages
    async for message in channel.history(limit=None):
        for attachment in message.attachments:
            if attachment.filename.lower().endswith((".png", ".jpg", ".jpeg")):
                image_urls.append(attachment.url)
    return image_urls


async def change_icon(guild):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(f"{timestamp} Changing icon for {guild.name}...")
    if library_channel_id is not None:
        image_urls = await get_image_urls_from_channel(library_channel_id)
        if image_urls:
            rand_image_url = random.choice(image_urls)
            async with aiohttp.ClientSession() as session:
                async with session.get(rand_image_url) as resp:
                    if resp.status == 200:
                        icon = await resp.read()
                        await guild.edit(icon=icon)
                        library_channel = bot.get_channel(library_channel_id)
                        await library_channel.send(
                            f"Icon changed to {rand_image_url} at {timestamp}"
                        )
        else:
            print("No images found in library channel!")


@bot.hybrid_command()
async def set_library_channel(ctx, channel_id: str):
    global library_channel_id
    library_channel_id = int(channel_id)
    images = await get_image_urls_from_channel(library_channel_id)
    await ctx.send(
        f"Library channel set to {channel_id}, found {len(images)} images."
    )


@bot.hybrid_command()
async def start(ctx, cron_syntax: str):
    global cron_task
    if library_channel_id is None:
        await ctx.send("Library channel is not set!")
        return

    if cron_task is None:
        cron_task = aiocron.crontab(
            cron_syntax, func=change_icon, args=(ctx.guild,)
        )
        await ctx.send(
            f"Icon change loop started with cron syntax: {cron_syntax}"
        )
    else:
        await ctx.send("Icon change loop is already running!")


@bot.hybrid_command()
async def stop(ctx):
    global cron_task
    if cron_task is not None:
        cron_task.stop()
        cron_task = None
        await ctx.send("Icon change loop stopped!")
    else:
        await ctx.send("No icon change loop is running!")


@bot.hybrid_command()
async def change_icon_now(ctx):
    if library_channel_id is None:
        await ctx.send("Library channel is not set!")
        return

    await change_icon(ctx.guild)

    if ctx.interaction:
        await ctx.interaction.response.send_message(
            "Icon changed immediately!"
        )
    else:
        await ctx.send("Icon changed immediately!")


@bot.hybrid_command()
async def next_icon_change(ctx):
    global cron_task
    if cron_task is None:
        await ctx.send("Icon change loop is not running!")
        return

    next_time = await cron_task.next(datetime.now())
    await ctx.send(f"Next icon change is scheduled for: {next_time}")


bot.run(BOT_TOKEN)
