#!/usr/bin/env python
# pylint: disable=C0116
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import requests
import json

import os
from dotenv import load_dotenv

load_dotenv()

from telegram import (
    Update,
    ForceReply,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)
from telegram.ext import (
    Updater,
    CommandHandler, 
    MessageHandler,
    Filters,
    CallbackContext,
    CallbackQueryHandler,
    ConversationHandler
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

CONTACT = range(1)

# Define a few command handlers. These usually take the two arguments update and context.
def start(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!' 
        '\n\nType /help to see what can i do'
    )

def button(update: Update, _: CallbackContext) -> None:
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    query.edit_message_text(text=f"Selected option: {query.data}")

def help_command(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Send /getotp to send OTP to your phone number')

def postOTP(phoneNumber):
    url = "https://cdn-api.co-vin.in/api/v2/auth/public/generateOTP"

    payload = json.dumps({
        "mobile": str(phoneNumber)
    })
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 Edg/90.0.818.51',
    'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)

    if(response.status_code == 200):
        message = "OTP sent successfully"
    else:
        message = "Error sending OTP"

    return message

def getotp(update: Update, _:CallbackContext) -> None:
    keyboard = [
        [KeyboardButton("Allow", request_contact = True)],
        [KeyboardButton("/cancel")],
    ]
    update.message.reply_text(
        'Please Allow to access your phone number.\n\n'
        'Then send your own contact',
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True),
    )

    return CONTACT

def contact(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    user_contact = update.message.contact
    phoneNumber = user_contact.phone_number
    update.message.reply_text(
        'Thanks',
        reply_markup=ReplyKeyboardRemove(),
    )
    message = postOTP(phoneNumber=phoneNumber)
    update.message.reply_text(message)
    return ConversationHandler.END

def cancel(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(os.getenv('TOKEN'))

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    #add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('getotp', getotp)],
        states={
            CONTACT: [
                MessageHandler(Filters.contact, contact),
                CommandHandler('cancel', cancel),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()