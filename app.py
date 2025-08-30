import datetime
import pytz
import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, StickerSendMessage
from dotenv import load_dotenv

load_dotenv(override=True)

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ["ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["CHANNEL_SECRET"])


@app.route("/")
def index():
    return "You call index()"


@app.route("/callback", methods=["POST"])
def callback():
    """Messaging APIからの呼び出し関数"""
    # LINEがリクエストの改ざんを防ぐために付与する署名を取得
    signature = request.headers["X-Line-Signature"]
    # リクエストの内容をテキストで取得
    body = request.get_data(as_text=True)
    # ログに出力
    app.logger.info("Request body: " + body)

    try:
        # signature と body を比較することで、リクエストがLINEから送信されたものであることを検証
        handler.handle(body, signature)
    except InvalidSignatureError:
        # クライアントからのリクエストに誤りがあったことを示すエラーを返す
        abort(400)
    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    dt = datetime.datetime.now(pytz.timezone("Asia/Tokyo"))
    reply_greeting = ""
    if 10 > dt.hour >= 2:
        reply_greeting = "おはよう！"
    elif 18 > dt.hour >= 10:
        reply_greeting = "こんにちは！"
    elif (24 > dt.hour >= 18) and (2 > dt.hour >= 0):
        reply_greeting = "こんばんは！"

    reply_conetnts = f"ただいまの東京の時刻は、「{dt.hour}時 {dt.minute}分」です"

    sticker_message = StickerSendMessage(
        package_id="446", sticker_id="1988"  # スタンプパッケージID  # スタンプID
    )

    line_bot_api.reply_message(
        event.reply_token,
        [TextSendMessage(text=reply_greeting), TextSendMessage(text=reply_conetnts), sticker_message],
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
