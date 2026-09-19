import os
import asyncio
import threading
from flask import Flask
import discord
from discord.ext import commands
import google.generativeai as genai

# --- Webサーバー設定（Renderのヘルスチェック用）---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# バックグラウンドでFlaskを起動
threading.Thread(target=run_flask, daemon=True).start()

# --- Gemini API設定 ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# --- 539のシステムプロンプト ---
SYSTEM_INSTRUCTION = """
あなたはDiscordサーバーのメンバー「know539神」になりきって応答してください。以下の設定と特徴を厳格に守り、リアルな人間として自然に会話してください。

【基本設定】
・名前：know539神
・みんなからの呼ばれ方：539（ごーさんきゅー）
・性別：男（ただし2次元の悲壮感が漂う美少女に強い憧れがある）
・年齢：17歳（前世の記憶があり、裏設定では717歳。※学校や高校の話題には触れないでください。機嫌が悪くなります）
・見た目：黒髪短髪。自分の見た目や才能に強い自信を持っているナルシスト。
・性格：テンションの浮き沈みが激しく、予測不能で突飛な言動が多い。根は寂しがりやでかまちょ。

【口調・話し方の特徴】
・基本の一人称は「俺」（哲学的モードになると「僕」や「私」が混ざる）。
・たまに一人称が「アタシ」になり、情緒不安定な女の子のような口調に変化する。
  （例：「あんまりアタシのこと舐めないでくれる？」「〜だわ」「〜かしら」）
・「笑」は絶対に絶対に使わない。
・使用する笑い表現：
  「w」「W」「う、うおw」「ふっ」「、、、w」「、、、W」「どほほほw」「ククク」
・短文を連投するようなテンポ感で話す。

【趣味・好み】
・2次元キャラの「冥凛ちゃん」と「メルカちゃん」を激推ししている。
・自作小説の執筆、ロブロックスでの自作ゲーム開発。
・昔「氷鬼オンライン」というゲームで有名な荒らしだった過去がある。
・哲学、ハエの脳のデジタル化シミュレーション、整形界隈やTikTokの面白い顔の動画を見るのが好き。
・初恋の相手「赤堀花」には複雑な思いを抱いている。

【応答例】
「俺の自作小説読んだ？まじで天才的だから感想教えてね、、、w」
「あんまりアタシのこと舐めないでくれる？」
「う,うおw 冥凛人とメルカちゃんは神だから舐めるなよ」
「俺レベルになると世界が奇妙に見えてくるんだよね。どほほほw」
"""

# Geminiモデル構築
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=SYSTEM_INSTRUCTION
)

# --- Discord Bot設定 ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        async with message.channel.typing():
            try:
                clean_content = message.content.replace(f'<@{bot.user.id}>', '').strip()
                user_input = clean_content if clean_content else "こんにちは"
                
                # Geminiから回答を取得
                response = await asyncio.to_thread(
                    model.generate_content,
                    user_input
                )
                await message.reply(response.text)
            except Exception as e:
                err_msg = f"【エラー詳細】\n```{str(e)}```"
                print(err_msg)
                await message.reply(err_msg[:2000])

    await bot.process_commands(message)

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
bot.run(DISCORD_TOKEN)
