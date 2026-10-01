import os
from flask import Flask
import threading

# 1. 簡易的なFlaskサーバーを作る（Renderに「生きてます」と伝えるため）
app = Flask('')

@app.route('/')
def home():
    return "I am alive!"

def run_flask():
    # Renderが指定するポート番号を取得して起動
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

# 2. Flaskサーバーを別スレッドで裏側で動かす
def keep_alive():
    t = threading.Thread(target=run_flask)
    t.start()

if __name__ == "__main__":
    # Flaskを裏で起動してから、Discord Botを動かす
    keep_alive()
    # ここにあなたのDiscord Botの起動コード（bot.run(...) など）を書く
