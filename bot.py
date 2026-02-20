import os, logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])
chat_histories = {}
SYSTEM_PROMPT = "Ты умный AI-ассистент. Отвечай на языке пользователя, чётко и по делу."

async def start(update, context):
    chat_histories[update.effective_user.id] = []
    await update.message.reply_text("👋 Привет! Я Твоя Вселенная. Задай любой вопрос!\n\n/clear — очистить историю")

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
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, *chat_histories[user_id]],
            max_tokens=1024, temperature=0.7
        )
        reply = response.choices[0].message.content
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
