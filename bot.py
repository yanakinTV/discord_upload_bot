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

# ユーザーIDとチャンネルIDを保存する関数
def save_channel_map(user_id, channel_id):
    lines = {}
    if os.path.exists("channel_map.txt"):
        with open("channel_map.txt", "r", encoding="utf-8") as f:
            for line in f:
                uid, cid = line.strip().split(":")
                lines[uid] = cid

    lines[str(user_id)] = str(channel_id)

    with open("channel_map.txt", "w", encoding="utf-8") as f:
        for uid, cid in lines.items():
            f.write(f"{uid}:{cid}\n")

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

    save_channel_map(user_id, channel_id)  # ファイルに記録

    upload_url = f"{FLASK_BASE_URL}/{user_id}"
    await interaction.response.send_message(
        f"📤 アップロードはこちらからどうぞ:\n{upload_url}",
        ephemeral=True
    )

# Flaskから呼び出される関数（例: 動画アップ完了後）
async def send_video_url(user_id: int, video_url: str):
    channel_id = None
    if os.path.exists("channel_map.txt"):
        with open("channel_map.txt", "r", encoding="utf-8") as f:
            for line in f:
                uid, cid = line.strip().split(":")
                if uid == str(user_id):
                    channel_id = int(cid)
                    break

    if channel_id:
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(f"📽️ アップロード完了: {video_url}")
        else:
            print("⚠️ チャンネルが見つかりません")
    else:
        print("⚠️ チャンネルIDが記録されていません")

# 起動
bot.run(TOKEN)