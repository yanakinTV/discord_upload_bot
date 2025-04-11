import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
FLASK_BASE_URL = os.getenv("FLASK_BASE_URL")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# 一時的にユーザーIDとチャンネルIDを記録する辞書
user_channel_map = {}

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🌐 Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"❌ Sync failed: {e}")

@bot.tree.command(name="upload", description="自分専用のアップロードURLを取得します")
async def upload(interaction: discord.Interaction):
    user_id = interaction.user.id
    channel_id = interaction.channel_id
    user_channel_map[str(user_id)] = channel_id

    upload_url = f"{FLASK_BASE_URL}/upload/{user_id}"
    await interaction.response.send_message(
        f"📤 アップロードはこちらからどうぞ:\n{upload_url}",
        ephemeral=True
    )

# Flask 側から呼び出される非同期関数
async def send_video_url(user_id: int, video_url: str):
    channel_id = user_channel_map.get(str(user_id))
    if channel_id:
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(f"📽️ アップロード完了: {video_url}")
        else:
            print("⚠️ チャンネルが見つかりません")
    else:
        print("⚠️ チャンネルIDが記録されていません")

bot.run(TOKEN)
