import os
import threading
import nest_asyncio
from flask import Flask
import discord
from discord.ext import commands
from google import genai

# 非同期イベントループのネスト（干渉防止）を許可
nest_asyncio.apply()

# --- 1. Webサーバー設定 ---
app = Flask(__name__)

@app.route('/')
def home():
    return "539 Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# バックグラウンドでWebサーバーを動かす
threading.Thread(target=run_web).start()


# --- 2. DiscordとGeminiの設定 ---
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

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

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    print('【539神】起動完了！Discordで話しかけてみてください。')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    is_mentioned = bot.user.mentioned_in(message)
    is_kw1 = "539" in message.content
    is_kw2 = "神" in message.content

    if is_mentioned or is_kw1 or is_kw2:
        print(f'メッセージ受信: {message.content}')
        try:
            clean_content = message.content.replace(f'<@{bot.user.id}>', '').strip()
            user_input = clean_content if clean_content else "こんにちは"

            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=user_input,
                config={'system_instruction': SYSTEM_INSTRUCTION}
            )
            await message.reply(response.text)
            print('返信完了！')
        except Exception as e:
            print(f'送信時エラー詳細: {e}')

# ボットを起動
bot.run(DISCORD_TOKEN)
