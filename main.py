import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
from config import token_API, user_id


help_text = """
/start - начало работы с ботом
/help - все команды бота
/files - выбор файла для скачивания
/reset - сбросить путь для скачивания файла
/back - вернуться в прошлую папку"""

start_text = """Данный бот предназначен для быстрого доступа к файлам на компьютере или сервере
Бот не может скачать файлы, чьё имя длиннее 30 символов"""
log_path = 'D:\\Проекты\\ТГ бот\\Логи.log'
bot_start_text = "Запуск бота"
directory = "C:\\Users\\User\\OneDrive\\Рабочий стол"
bot = Bot(token_API)
dp = Dispatcher(bot)

keyboards = []
kb = ReplyKeyboardMarkup(resize_keyboard=True)
kb.add('/help').insert('/start').add('/files').insert('/reset').add('/back')


def file_search():
    items = os.listdir(directory)
    files = [item for item in items if os.path.isfile(os.path.join(directory, item))]
    return files


def folder_search():
    items = os.listdir(directory)
    folders = [item for item in items if os.path.isdir(os.path.join(directory, item))]
    return folders


#  Запись в лог даты и времени запуска бота
def write_start_log():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, 'a') as file:
        file.write(f"[{timestamp}] {bot_start_text}\n")


def write_message_log(message):
    with open(log_path, 'a') as file:
        file.write(f"{message}\n")


async def on_startup(_):
    write_start_log()


#  Команды бота
@dp.message_handler(commands=['start'])
async def echo(message: types.Message):
    if message.from_user.id == user_id:
        await message.answer(text=start_text,
                             reply_markup=kb)
    else:
        await message.answer(text="Извините, у вас нет доступа к этой команде.")


@dp.message_handler(commands=['help'])
async def echo(message: types.Message):
    if message.from_user.id == user_id:
        await message.reply(text=help_text)
    else:
        await message.answer(text="Извините, у вас нет доступа к этой команде.")


@dp.message_handler(commands=['reset'])
async def echo(message: types.Message):
    if message.from_user.id == user_id:
        global directory
        directory = "C:\\Users\\User\\OneDrive\\Рабочий стол"
        await message.reply(text="Сброс пути выполнен. Текущая директория: " + directory)
    else:
        await message.answer(text="Извините, у вас нет доступа к этой команде.")


@dp.message_handler(commands=['back'])
async def echo(message: types.Message):
    if message.from_user.id == user_id:
        global directory
        path_components = directory.split(os.path.sep)
        shortened_path_components = path_components[:-1]
        directory = os.path.sep.join(shortened_path_components)
        formatted_directory = directory.replace(os.path.sep, '\\\\')
        await message.reply(text=f'Вернулись в прошлую папку: {formatted_directory}')
    else:
        await message.answer(text="Извините, у вас нет доступа к этой команде.")


@dp.message_handler(commands=['files'])
async def show_files(message: types.Message):
    if message.from_user.id == user_id:
        files = file_search()
        folders = folder_search()
        keyboard_files = InlineKeyboardMarkup()
        keyboard_folders = InlineKeyboardMarkup()

        if len(folders) != 0:
            for folder in folders:
                callback_data = f"folder_{folder[:30]}"
                folder_button = InlineKeyboardButton(folder, callback_data=callback_data)
                keyboard_folders.add(folder_button)
            await message.answer(text="Выберите папку:", reply_markup=keyboard_folders)

        if len(files) != 0:
            for file in files:
                callback_data = f"file_{file[:30]}"
                file_button = InlineKeyboardButton(file, callback_data=callback_data)
                keyboard_files.add(file_button)
            await message.answer(text="Выберите файл:", reply_markup=keyboard_files)
    else:
        await message.answer(text="Извините, у вас нет доступа к этой команде.")


#  Скачивание файла
@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('file_'))
async def handle_file_callback(callback_query: types.CallbackQuery):
    try:
        file_name = callback_query.data[len('file_'):]
        await bot.send_document(callback_query.from_user.id, document=open(os.path.join(directory, file_name), 'rb'))
    except Exception as e:
        await bot.send_message(callback_query.from_user.id, f"Имя файла слишком длинное: {e}")


#  Переход в следующую директорию
@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('folder_'))
async def handle_folder_callback(callback_query: types.CallbackQuery):
    folder_name = callback_query.data[len('folder_'):]
    global directory
    directory = os.path.join(directory, folder_name)

    files = file_search()
    folders = folder_search()
    keyboard_files = InlineKeyboardMarkup()
    keyboard_folders = InlineKeyboardMarkup()
    if len(files) != 0:
        for file in files:
            callback_data = f"file_{file[:30]}"
            file_button = InlineKeyboardButton(file, callback_data=callback_data)
            keyboard_files.add(file_button)
        await bot.send_message(callback_query.from_user.id, text="Выберите файл:",
                               reply_markup=keyboard_files)
    if len(folders) != 0:
        for folder in folders:
            callback_data = f"folder_{folder[:30]}"
            folder_button = InlineKeyboardButton(folder, callback_data=callback_data)
            keyboard_folders.add(folder_button)
        await bot.send_message(callback_query.from_user.id, text="Выберите папку:", reply_markup=keyboard_folders)


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
