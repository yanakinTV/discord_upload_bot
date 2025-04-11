# app.py
import os
from flask import Flask, request, render_template, redirect, url_for, flash
import boto3
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# .env読み込み
load_dotenv()

# Flaskアプリ設定
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "default_secret_key")

# Cloudflare R2の設定
R2_ENDPOINT = os.getenv("R2_ENDPOINT")
R2_ACCESS_KEY = os.getenv("R2_ACCESS_KEY")
R2_SECRET_KEY = os.getenv("R2_SECRET_KEY")
R2_BUCKET = os.getenv("R2_BUCKET")
R2_PUBLIC_URL = os.getenv("R2_PUBLIC_URL")

# boto3 S3 client
s3 = boto3.client(
    's3',
    endpoint_url=R2_ENDPOINT,
    aws_access_key_id=R2_ACCESS_KEY,
    aws_secret_access_key=R2_SECRET_KEY
)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/upload/<upload_id>", methods=["GET", "POST"])
def upload_file(upload_id):
    if request.method == "POST":
        if 'file' not in request.files:
            flash("No file part")
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash("No selected file")
            return redirect(request.url)

        filename = secure_filename(file.filename)
        local_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(local_path)

        try:
            s3.upload_file(local_path, R2_BUCKET, filename)
            public_url = f"{R2_PUBLIC_URL}/{filename}"
            os.remove(local_path)
            return render_template("complete.html", url=public_url, upload_id=upload_id)
        except Exception as e:
            flash(f"Upload failed: {str(e)}")
            return redirect(request.url)

    return render_template("upload.html", upload_id=upload_id)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
