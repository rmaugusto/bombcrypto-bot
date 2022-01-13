import yaml
import telebot
from threading import Thread

class TelegramNotification(object):
    def __init__(self, mainNotification, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.mainNotification = mainNotification

        self.bot = telebot.TeleBot(self.token, threaded=True)

        @self.bot.message_handler(commands=["screenshot"])
        def _process_command_screenshot(message):
            self.mainNotification.on_request_screenshot()

        @self.bot.message_handler(commands=["start"])
        def _process_command_start(message):
            self.send_text("""Bot commands available:

            /screenshot - Request screenshot.
            """)

        thread = Thread(target = self.infinity_polling)
        thread.start()

    def infinity_polling(self):
        self.bot.infinity_polling()

    def send_photo(self, photo_file_path):
        photo = open(photo_file_path, 'rb')
        self.bot.send_photo(self.chat_id, photo)
        photo.close()

    def send_text(self, message):
        try:
            self.bot.send_message(self.chat_id, message)
        except Exception as e:
            print(e)

class Notification(object):
    __instance = None


    @staticmethod 
    def getInstance():
        if Notification.__instance == None:
            Notification()
        return Notification.__instance

    def __init__(self):
        if Notification.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            Notification.__instance = self

        self.screenshot_callback = None       
        self.initialized = False
        self.telegram_notification = None            

        # Load config file.
        stream = open("config.yaml", 'r')
        c = yaml.safe_load(stream)

        if c.get('notification', {}).get('telegram', {}).get('token', '') not in ['', None]:
            self.telegram_notification = TelegramNotification(self, c['notification']['telegram']['token'], c['notification']['telegram']['chat_id'])
            self.level = c['notification']['level']
            self.initialized = True             


    def on_request_screenshot(self):
        if self.initialized and self.screenshot_callback:
            if self.telegram_notification:
                photo_file_path= self.screenshot_callback()
                self.telegram_notification.send_text('⬇️ Requesting screenshot..')
                self.telegram_notification.send_photo(photo_file_path)

    def send_text(self, message):
        if self.initialized:
            if self.telegram_notification:
                self.telegram_notification.send_text(message)

    def send_photo(self, photo_file_path):
        if self.initialized:
            if self.telegram_notification:
                self.telegram_notification.send_photo(photo_file_path)