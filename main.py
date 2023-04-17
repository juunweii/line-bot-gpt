from fastapi import FastAPI
import os
import openai
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from fastapi import FastAPI, Request, Form, status
from fastapi.responses import JSONResponse


app = FastAPI()
line_bot_api = LineBotApi(os.environ.get('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET'))
openai.api_key = os.environ.get('OPENAI_API_KEY')


@app.post("/callback")
async def callback(request: Request):
    # Get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # Get request body as text
    body = await request.body()

    # Handle webhook body
    try:
        handler.handle(body.decode('utf-8'), signature)
    except InvalidSignatureError:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": "Invalid signature."})

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    response = get_gpt_response(text)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response))


def get_gpt_response(prompt):
    model_engine = "GPT-3.5-turbo"
    completions = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.5,
    )

    message = completions.choices[0].text
    return message.strip()
