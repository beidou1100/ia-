import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# 定义状态
LANGUAGE, CHAT = range(2)

BOT_TOKEN = os.getenv("BOT_TOKEN")

# 欢迎消息，中英文
welcome_text = {
    "zh": "欢迎使用高级机器人！请选择语言。",
    "en": "Welcome to the advanced bot! Please choose a language.",
}

# 帮助信息
help_text = {
    "zh": "这是帮助信息。发送 /start 重新开始。",
    "en": "This is help info. Send /start to restart.",
}

# 语言选择键盘
language_keyboard = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("中文 🇨🇳", callback_data="lang_zh")],
        [InlineKeyboardButton("English 🇺🇸", callback_data="lang_en")],
    ]
)

# 聊天状态键盘
chat_keyboard = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("结束对话", callback_data="end_chat")],
    ]
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(welcome_text["zh"], reply_markup=language_keyboard)
    return LANGUAGE

async def language_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    lang = query.data.split("_")[1]
    context.user_data["lang"] = lang
    await query.edit_message_text(
        f"{'你选择了中文' if lang == 'zh' else 'You chose English'}. 请开始对话吧！",
        reply_markup=chat_keyboard,
    )
    return CHAT

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get("lang", "zh")
    user_text = update.message.text
    # 简单回显，并加点内容
    if lang == "zh":
        reply = f"你说：{user_text}，机器人正在处理你的请求..."
    else:
        reply = f"You said: {user_text}, the bot is processing your request..."
    await update.message.reply_text(reply, reply_markup=chat_keyboard)
    return CHAT

async def end_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "zh")
    goodbye = "对话结束，欢迎随时再来！" if lang == "zh" else "Conversation ended, welcome back anytime!"
    await query.edit_message_text(goodbye)
    return ConversationHandler.END

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "zh")
    await update.message.reply_text(help_text.get(lang, help_text["zh"]))

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("已取消。发送 /start 重新开始。")
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANGUAGE: [CallbackQueryHandler(language_choice, pattern="^lang_")],
            CHAT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, chat),
                CallbackQueryHandler(end_chat, pattern="^end_chat$"),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel), CommandHandler("help", help_command)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("help", help_command))

    print("高级机器人已启动，等待消息...")
    app.run_polling()

if __name__ == "__main__":
    main()
