from telebot import TeleBot

from config.config import Config
from utils.format import sanitize_output
from utils.logger import Logger


def post_to_channel(text):
    Logger.logger.info('Posting message to Telegram Announcement channel')
    try:
        bot = TeleBot(Config.TG_BOT_TOKEN)
        bot.send_message(chat_id=Config.ANNOUNCEMENT_CHANNEL_ID, text=sanitize_output(text), parse_mode='MarkdownV2')
    except Exception as e:
        Logger.logger.error(f'Failed to post message: {text} || {e}')
