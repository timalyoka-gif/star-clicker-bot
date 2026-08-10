import time
import threading
import telebot
from telebot import types

# Твой токен бота
BOT_TOKEN = "8629186084:AAGKVgKJtfeENFNgI81d-g4IJklYetJ9_k0"
bot = telebot.TeleBot(BOT_TOKEN)

# Новая ссылка на твое мини-приложение на Vercel
WEB_APP_URL = "https://star-clicker-by-sulik-2.vercel.app/"

# ID чата или канала, куда будет приходить автоматическая рассылка
# (Можешь указать ID своего канала, например "@my_channel", или оставить свой Telegram ID)
AUTO_CHAT_ID = "ТВОЙ_CHAT_ID_ИЛИ_КАНАЛ"


# Функция автоматической рассылки сообщений со ссылкой
def send_scheduled_message():
    text = (
        "🔥 **Daily Update from Star Clicker!**\n\n"
        "Don't forget to collect your daily gifts, open cases, and level up your clicks!\n"
        f"👉 Play now: {WEB_APP_URL}"
    )
    try:
        # Отправляем только если заменен стандартный текст получателя
        if AUTO_CHAT_ID != "ТВОЙ_CHAT_ID_ИЛИ_КАНАЛ":
            bot.send_message(AUTO_CHAT_ID, text, parse_mode="Markdown")
            print("Автоматическое сообщение отправлено!")
    except Exception as e:
        print(f"Ошибка авто-отправки: {e}")


# Фоновый поток для планировщика
def schedule_worker():
    import schedule
    # Настраиваем отправку каждый день в 12:00 дня
    schedule.every().day.at("12:00").do(send_scheduled_message)

    while True:
        schedule.run_pending()
        time.sleep(1)


# Запускаем фоновый поток планировщика
threading.Thread(target=schedule_worker, daemon=True).start()


@bot.message_handler(commands=['start'])
def start_command(message):
    user_name = message.from_user.first_name

    # Приветствие
    welcome_text = (
        f"⭐ **Hello, {user_name}! Welcome to Star Clicker!**\n\n"
        f"Tap stars, open daily gifts, use promo codes and enjoy the game created <b>by SULIK</b>!\n\n"
        f"Choose an option below:"
    )

    # Клавиатура с кнопками
    markup = types.InlineKeyboardMarkup(row_width=1)

    # Кнопка запуска мини-приложения (Web App)
    web_app_info = types.WebAppInfo(url=WEB_APP_URL)
    btn_play = types.InlineKeyboardButton("✨ Play Star Clicker", web_app=web_app_info)

    # Кнопки для доната через Telegram Stars (XTR)
    btn_support_15 = types.InlineKeyboardButton("⭐ Support Author (15 Stars)", callback_data="donate_15")
    btn_support_30 = types.InlineKeyboardButton("⭐ Support Author (30 Stars)", callback_data="donate_30")

    markup.add(btn_play, btn_support_15, btn_support_30)

    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode="HTML",
        reply_markup=markup
    )


# Обработка нажатия на кнопки поддержки автора (выставление инвойса на звезды)
@bot.callback_query_handler(func=lambda call: call.data in ["donate_15", "donate_30"])
def handle_donation(call):
    chat_id = call.message.chat.id

    if call.data == "donate_15":
        amount = 15
        title = "Support SULIK (15 Stars)"
        description = "Official author support via Telegram Stars."
        payload = "support_15_stars"
    else:
        amount = 30
        title = "Support SULIK (30 Stars)"
        description = "Mega author support via Telegram Stars."
        payload = "support_30_stars"

    # Цены для Telegram Stars (валюта XTR)
    prices = [types.LabeledPrice(label=title, amount=amount)]

    bot.send_invoice(
        chat_id=chat_id,
        title=title,
        description=description,
        invoice_payload=payload,
        provider_token="",  # Для Telegram Stars всегда оставляем пустую строку!
        currency="XTR",  # Официальная валюта Telegram Stars
        prices=prices,
        start_parameter="support-author"
    )


# Обязательный этап перед оплатой
@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout_handler(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


# Обработка успешной оплаты
@bot.message_handler(content_types=['successful_payment'])
def success_payment_handler(message):
    payment = message.successful_payment
    amount_paid = payment.total_amount  # Сумма звезд

    bot.send_message(
        message.chat.id,
        f"🎉 **Thank you so much!**\nPayment of {amount_paid} Telegram Stars was successful. Your support means a lot to SULIK!",
        parse_mode="Markdown"
    )


if __name__ == '__main__':
    print("🤖 Bot by SULIK is successfully running and waiting for messages...")
    bot.infinity_polling()

