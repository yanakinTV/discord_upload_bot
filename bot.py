# bot.py
import os
import discord
from discord.ext import commands, tasks
from discord import app_commands
from dotenv import load_dotenv
from asyncio import Queue

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
FLASK_BASE_URL = os.getenv("FLASK_BASE_URL")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

user_channel_map = {}
video_queue = Queue()

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🌐 Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"❌ Sync failed: {e}")
    send_loop.start()

@bot.tree.command(name="upload", description="自分専用のアップロードURLを取得します")
async def upload(interaction: discord.Interaction):
    user_id = interaction.user.id
    channel_id = interaction.channel_id
    user_channel_map[str(user_id)] = channel_id

    upload_url = f"{FLASK_BASE_URL}/{user_id}"
    await interaction.response.send_message(
        f"📤 アップロードはこちらからどうぞ:\n{upload_url}",
        ephemeral=True
    )

async def enqueue_video(user_id: int, file_url: str):
    await video_queue.put((user_id, file_url))

@tasks.loop(seconds=2)
async def send_loop():
    while not video_queue.empty():
        user_id, file_url = await video_queue.get()
        channel_id = user_channel_map.get(str(user_id))
        if channel_id:
            channel = bot.get_channel(channel_id)
            if channel:
                await channel.send(f"📽️ アップロード完了: {file_url}")
            else:
                print("⚠️ チャンネルが見つかりません")
        else:
            print("⚠️ チャンネルIDが記録されていません")

bot.run(TOKEN)
