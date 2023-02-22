import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from google_module.google_module import check_1_url, check_2_url
import random
import time, json
from threading import Thread
from datetime import date
from aiogram.exceptions import AiogramError, TelegramForbiddenError

# Чтение конфига
with open("config.json", "r") as read_file:
    config = json.load(read_file)

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# Объект бота
bot = Bot(token=config["TG_TOKEN"])
# Пришлось создать отдельный объект бота для второго потока
bt = Bot(token=config["TG_TOKEN"])
# Диспетчер
dp = Dispatcher()

# Хэндлер на команду /start
@dp.message(commands=["start"])
async def cmd_start(message: types.Message):
    print(message.chat.id)
    await message.answer(f"Привет! Я всё ещё работую.\nПроверка таблиц: {th.is_alive()}")

# Приём стикеров
@dp.message(content_types=["sticker"])
async def ctikc(message: types.Message):
    print(message.sticker.file_id)

# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)


# Если вдруг ошибки, что б сообщение точно отправилось
# Может остановить поток
async def sending_messages(id:int,text:str):
    while True:
        try:
            await bt.send_message(id, text)
            break
        except TelegramForbiddenError as e:
            print(e)
            break
        except  AiogramError as e:
            print(e)
            await asyncio.sleep(20)


# Просмотр изменений в таблицах
async def get_updates():
    '''
    Получаем таблицу, проверяем, изменилось ли там что-то
    '''  
    while True:
        
        try:
            if config["URL_FOR_TABLE_1"] == "" or config["LAST_LINE_1"] == "" or config["CHAT_FOR_URL_1"] == "":
                raise Exception("Отсутствует первая ссылка")
            
            ### Смотрим первую таблицу
            resp = check_1_url(config["URL_FOR_TABLE_1"], config["LAST_LINE_1"])
            
            # Если появились новые строки для извещения
            if resp["texts_to_send"] != []:            
                # Отсылаем пользователю все тексты
                tasks = [asyncio.ensure_future(sending_messages(config["CHAT_FOR_URL_1"], i)) for i in resp["texts_to_send"]]
                await asyncio.wait(tasks)
            
            # Выгружаем информацию о последней строке
            if resp["last_line"] != config["LAST_LINE_1"]:
                config["LAST_LINE_1"] = resp["last_line"]
                with open("config.json", "w") as write_file:
                    json.dump(config, write_file, indent=4)
        
        except BaseException as e:
            print(e)            
            
        try:
            if config["URL_FOR_TABLE_2"] == "" or config["LAST_LINE_2"] == "" or config["CHAT_FOR_URL_2"] == "":
                raise Exception("Отсутствует вторая ссылка")
            
            ### Смотрим вторую таблицу
            resp = check_2_url(config["URL_FOR_TABLE_2"], config["LAST_LINE_2"])
            
            # Если появились новые строки для извещения
            if resp["texts_to_send"] != []:
                # Смотрим, извещали ли об этом сегодня
                today = str(date.today())
                if today != config["DATE_URL_2"]:
                    # Если не извещали, что шлём стикер
                    config["DATE_URL_2"] = today
                    await bt.send_sticker(config["CHAT_FOR_URL_2"], random.choice(config["MONEY_STICKERS"]))

                # Отсылаем пользователю все тексты
                tasks = [asyncio.ensure_future(sending_messages(config["CHAT_FOR_URL_2"], i)) for i in resp["texts_to_send"]]
                await asyncio.wait(tasks)

            # Выгружаем информацию о последней строке
            if resp["last_line"] != config["LAST_LINE_2"]:
                config["LAST_LINE_2"] = resp["last_line"]
                with open("config.json", "w") as write_file:
                    json.dump(config, write_file, indent=4)

        except BaseException as e:
            print(e)
        # Раз в 30 минут обновление
        print(1800 - time.time() % 1800)
        await asyncio.sleep(1800 - time.time() % 1800)


def sec_thread_start():
    asyncio.run(get_updates())


if __name__ == "__main__":
    # Запуск запросов в таблицу
    th = Thread(target=sec_thread_start, daemon=True)#, args=(i, ))
    th.start()
    # Запуск тг бота
    asyncio.run(main())