import os
import random
import time
from datetime import datetime

import aiocron
import aiohttp
import discord
import pytz
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

log_channel_id = None
library_channel_id = None
cron_task = None
loop_timezone = None


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
    if log_channel_id is None:
        print(
            f"{timestamp} Error when executing function change_icon :"
            " log_channel not defined"
        )
        return
    if library_channel_id is not None:
        image_urls = await get_image_urls_from_channel(library_channel_id)
        if image_urls:
            rand_image_url = random.choice(image_urls)
            async with aiohttp.ClientSession() as session:
                async with session.get(rand_image_url) as resp:
                    if resp.status == 200:
                        icon = await resp.read()
                        await guild.edit(icon=icon)
                        log_channel = bot.get_channel(log_channel_id)
                        await log_channel.send(
                            f"Icon changed to {rand_image_url} at {timestamp}"
                        )
        else:
            print(f"{timestamp} No images found in library channel!")


@bot.hybrid_command()
async def set_library_channel(ctx, channel_id: str):
    global library_channel_id
    library_channel_id = int(channel_id)
    images = await get_image_urls_from_channel(library_channel_id)
    await ctx.send(
        f"Library channel set to {channel_id}, found {len(images)} images."
    )


@bot.hybrid_command()
async def set_log_channel(ctx, channel_id: str):
    global log_channel_id
    log_channel_id = int(channel_id)
    await ctx.send(f"Log channel set to {channel_id}.")


@bot.hybrid_command()
async def start(ctx, cron_syntax: str, timezone: str = None):
    global cron_task, loop_timezone
    if library_channel_id is None:
        await ctx.send("Library channel is not set!")
        return

    if log_channel_id is None:
        await ctx.send("Log channel is not set!")
        return

    try:
        # Convert the timezone string to a proper timezone object
        if timezone is not None:
            loop_timezone = pytz.timezone(timezone)
        else:
            loop_timezone = pytz.UTC  # Default to UTC if no timezone specified
            
        if cron_task is None:
            cron_task = aiocron.crontab(
                cron_syntax, func=change_icon, args=(ctx.guild,), tz=loop_timezone
            )
            await ctx.send(
                f"Icon change loop started with cron syntax: `{cron_syntax}` and"
                f" timezone: {loop_timezone}"
            )
        else:
            await ctx.send("Icon change loop is already running!")
            
    except pytz.exceptions.UnknownTimeZoneError:
        await ctx.send(f"Unknown timezone: {timezone}")
        return


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

    if log_channel_id is None:
        await ctx.send("Log channel is not set!")
        return

    await change_icon(ctx.guild)

    try:
        if ctx.interaction and not ctx.interaction.response.is_done():
            await ctx.interaction.response.send_message(
                "Icon changed immediately!"
            )
        else:
            await ctx.send("Icon changed immediately!")
    except discord.errors.NotFound:
        await ctx.send("Icon changed immediately!")


@bot.hybrid_command()
async def next_icon_change(ctx):
    global cron_task
    if cron_task is None:
        await ctx.send("Icon change loop is not running!")
        return

    next_time = await cron_task.next(datetime.now(loop_timezone))
    await ctx.send(f"Next icon change is scheduled for: {next_time}")


@bot.event
async def on_error(event, *args, **kwargs):
    print(f"An error occurred: {event}")
    print(args)
    print(kwargs)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandInvokeError):
        await ctx.send("There was an error executing the command.")
    else:
        await ctx.send("An error occurred.")
    print(f"An error occurred: {error}")


@bot.event
async def on_disconnect():
    print("Bot disconnected! Attempting to reconnect...")


@bot.event
async def on_resumed():
    print("Bot resumed connection!")


bot.run(BOT_TOKEN)
