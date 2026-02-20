import os, logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from anthropic import Anthropic

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
chat_histories = {}
SYSTEM_PROMPT = "Ты умный AI-ассистент. Отвечай на языке пользователя, чётко и по делу."

async def start(update, context):
    chat_histories[update.effective_user.id] = []
    await update.message.reply_text("👋 Привет! Я AI-бот. Задай любой вопрос!\n\n/clear — очистить историю")

async def clear(update, context):
    chat_histories[update.effective_user.id] = []
    await update.message.reply_text("🧹 История очищена!")

async def handle_message(update, context):
    user_id = update.effective_user.id
    if user_id not in chat_histories:
        chat_histories[user_id] = []
    chat_histories[user_id].append({"role": "user", "content": update.message.text})
    if len(chat_histories[user_id]) > 20:
        chat_histories[user_id] = chat_histories[user_id][-20:]
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=chat_histories[user_id]
        )
        reply = response.content[0].text
        chat_histories[user_id].append({"role": "assistant", "content": reply})
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text("⚠️ Ошибка, попробуй ещё раз.")

def main():
    app = ApplicationBuilder().token(os.environ["TELEGRAM_BOT_TOKEN"]).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
