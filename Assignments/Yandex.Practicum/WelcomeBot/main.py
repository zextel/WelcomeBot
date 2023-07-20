from WelcomeBot import WelcomeBot
from helpers.keys import TELEGRAM_BOT_API_KEY

if __name__ == '__main__':
    wb = WelcomeBot(TELEGRAM_BOT_API_KEY)
    wb.start()
