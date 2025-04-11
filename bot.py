import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

# .env を読み込む
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
FLASK_BASE_URL = os.getenv("FLASK_BASE_URL")  # 例: http://localhost:5000/upload
GUILD_ID = int(os.getenv("DISCORD_GUILD_ID"))  # サーバーID（intで取得）

# Bot クライアント設定
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
guild = discord.Object(id=GUILD_ID)  # コマンドを同期する対象サーバー

# 起動時イベント
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync(guild=guild)  # 対象サーバーにスラッシュコマンド同期
        print(f"🌐 Synced {len(synced)} commands to guild {GUILD_ID}")
    except Exception as e:
        print(f"❌ Sync failed: {e}")

# /upload コマンド定義（ギルド限定）
@bot.tree.command(name="upload", description="自分専用のアップロードURLを取得します", guild=guild)
async def upload(interaction: discord.Interaction):
    user_id = interaction.user.id
    upload_url = f"{FLASK_BASE_URL}/{user_id}"
    await interaction.response.send_message(
        f"📄 アップロードはこちらからどうぞ:\n{upload_url}",
        ephemeral=True  # 他の人には見えないように
    )

# Bot起動
bot.run(TOKEN)
