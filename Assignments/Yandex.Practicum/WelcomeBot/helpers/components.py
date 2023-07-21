from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

from helpers import constants

MENU_START_KB = ReplyKeyboardMarkup(
    [[constants.CMD_START_MENU_PHOTO],
     [constants.CMD_START_MENU_STORY],
     [constants.CMD_START_MENU_VOICE],
     [constants.CMD_START_MENU_VCHAT]],
    resize_keyboard=True,
    one_time_keyboard=True
)

MENU_PHOTO_KB = InlineKeyboardMarkup(
    [[InlineKeyboardButton(constants.CMD_PHOTO_SELFIE_TEXT, callback_data="PHOTO_1")],
     [InlineKeyboardButton(constants.CMD_PHOTO_SCHOOL_TEXT, callback_data="PHOTO_2")],
     [InlineKeyboardButton(constants.CMD_BACK, callback_data="BACK")]]
)

MENU_VOICE_KB = InlineKeyboardMarkup(
    [[InlineKeyboardButton(constants.CMD_VOICE_GRAND_GPT, callback_data="VOICE_1")],
     [InlineKeyboardButton(constants.CMD_VOICE_SQL_NOSQL, callback_data="VOICE_2")],
     [InlineKeyboardButton(constants.CMD_VOICE_HEARTBREAK, callback_data="VOICE_3")],
     [InlineKeyboardButton(constants.CMD_BACK, callback_data="BACK")]]
)

BACK_TO_MENU = InlineKeyboardMarkup(
    [[InlineKeyboardButton(constants.CMD_BACK, callback_data="BACK")]]
)
