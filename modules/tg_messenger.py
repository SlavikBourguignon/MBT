import requests
import telegram
token = '6325523085:AAF9-l-dJYWZGj4nN9KfYLa2IHGn4MqEmz0'
channelId = '-1001808679036'


message = "python test"

bot = telegram.Bot(token = token)
bot.send_message(chat_id = channelId, text = message)

