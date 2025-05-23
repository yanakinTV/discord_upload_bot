import os
import uuid
import asyncio
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import boto3

import bot  # bot.enqueue_video を呼ぶだけ

load_dotenv()
app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

R2_BUCKET = os.getenv("R2_BUCKET")
R2_ENDPOINT = os.getenv("R2_ENDPOINT")
R2_ACCESS_KEY = os.getenv("R2_ACCESS_KEY")
R2_SECRET_KEY = os.getenv("R2_SECRET_KEY")
R2_PUBLIC_URL = os.getenv("R2_PUBLIC_URL")

s3 = boto3.client(
    "s3",
    endpoint_url=R2_ENDPOINT,
    aws_access_key_id=R2_ACCESS_KEY,
    aws_secret_access_key=R2_SECRET_KEY
)

@app.route("/upload/<int:user_id>", methods=["GET", "POST"])
def upload_file(user_id):
    if request.method == "POST":
        if "file" not in request.files:
            return render_template("error.html", message="ファイルが見つかりません")
        file = request.files["file"]
        if file.filename == "":
            return render_template("error.html", message="ファイルが選択されていません")

        filename = secure_filename(file.filename)
        local_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(local_path)

        key = f"uploads/{uuid.uuid4()}_{filename}"
        s3.upload_file(local_path, R2_BUCKET, key)

        file_url = f"{R2_PUBLIC_URL}/{key}"

        # 非同期キューに渡す（Render でも安全）
        asyncio.run(bot.enqueue_video(user_id, file_url))

        return render_template("complete.html", file_url=file_url, user_id=user_id)

    return render_template("upload.html", user_id=user_id)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
