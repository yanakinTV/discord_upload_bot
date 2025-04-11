@echo off
REM スクリプト開始
echo === GitHub Push Script (.env は除外) ===

REM .env を除いて変更されたファイルを全て add
for /f "delims=" %%f in ('git status --porcelain ^| findstr /v ".env"') do (
    for /f "tokens=2 delims= " %%a in ("%%f") do git add "%%a"
)

REM コミット（時間を含めると分かりやすいです）
setlocal enabledelayedexpansion
for /f %%a in ('powershell -Command "Get-Date -Format yyyy-MM-dd_HH-mm-ss"') do set timestamp=%%a
git commit -m "Auto commit at !timestamp!"

REM プッシュ
git push origin main

echo === 完了しました ===
pause
