from aiogram import F, Bot, Dispatcher, types
import asyncio, logging, os
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile
from aiogram.utils.media_group import MediaGroupBuilder

import get_weather, create_figures
from datetime import datetime

# Обязательное к заполнению!
bot_key = 'PUT KEY' # Telegram API key
weather_key = 'PUT KEY' # OpenWeather API key
admin_username = '@ergle_manul' # ник в Telegram тех. админа

logging.basicConfig(level=logging.INFO)
bot = Bot(bot_key)
dp = Dispatcher()

""" Хранилища данных, получаемые от пользователя """
# Первый город
waiting_first_city = False
first_city_name = ''
first_city_key = 0
# Второй город
waiting_second_city = False
second_city_name = ''
second_city_key = 0
# Экстра города
count_cities = 0
list_cities_name = []
list_cities_key = []
# Прогноз
forecast_day = 0

async def message_error(message: types.Message, err):
    """ Отправляет пользователю информацию об ошибке """
    await message.answer(
        f'||{str(err).replace(".", "\\.")}|| '
        f'\n\nУпс\\! Что\\-то пошло не так\\.\\.\\. Напишите пожалуйста {admin_username.replace('_', '\\_')} '
        f'и покажите ему это сообщение\\.',
        parse_mode=ParseMode.MARKDOWN_V2
    )
    await message.answer(
        f'К сожалению, вам скорее всего придется сделать запрос заново с помощью ранее использованной команды. Приносим извинения за неудобства.')

@dp.message(F.text == '/start')
async def start_message(message: types.Message):
    """ Выводит приветственное сообщение пользователю.
    Сообщение хранится в messages/start.txt. """
    try:
        with open('messages/start.txt', encoding='utf-8') as f:
            text = f.read()
    except Exception as err: # Ошибка, если файл не найден или что-то другое
        await message_error(message, err)
    else:
        await message.answer(text, parse_mode=ParseMode.HTML)

@dp.message(F.text == '/info')
async def info_message(message: types.Message):
    """ Выводит информационное сообщение пользователю.
    Сообщение хранится в messages/info.txt. """
    try:
        with open('messages/info.txt', encoding='utf-8') as f:
            text = f.read()
            text_message = f'{text}'.format(admin_username=admin_username)
    except Exception as err: # Ошибка, если файл не найден или что-то другое
        await message_error(message, err)
    else:
        await message.answer(text_message, parse_mode=ParseMode.HTML)

@dp.message(F.text == '/weather')
async def weather_hello_message(message: types.Message):
    global waiting_first_city, first_city_name, first_city_key, waiting_second_city, second_city_name
    global second_city_key, count_cities, list_cities_key, list_cities_name, forecast_day
    # Опустошение всех данных при использовании команды /weather
    waiting_first_city = False
    first_city_name = ''
    first_city_key = 0
    waiting_second_city = False
    second_city_name = ''
    second_city_key = 0
    count_cities = 0
    list_cities_name = []
    list_cities_key = []
    forecast_day = 0

    # Вывод сообщения
    try:
        with open('messages/weather_1_first_city.txt', encoding='utf-8') as f:
            text = f.read()
            text_message = f'{text}'.format(admin_username=admin_username)
    except Exception as err: # Ошибка, если файл не найден или что-то другое
        await message_error(message, err)
    else:
        await message.answer(text_message, parse_mode=ParseMode.HTML)
        waiting_first_city = True

@dp.message()
async def message_processing(message: types.Message):
    """ Обработка сообщений без команд """
    global waiting_first_city, waiting_second_city, first_city_name, count_cities
    # Если вводится 1 город
    if waiting_first_city:
        global first_city_key
        first_city_name = message.text

        """ Код обрабатывает ситуацию, если город не был найден.
        Если город не найден, то он сообщает об этом пользователю.
        Если город найден, то выводит сообщение с просьбой ввести второй город.
        Сообщение находится в messages/weather_2_second_city.txt. """
        try:
            first_city_key = get_weather.get_key_by_city(weather_key, first_city_name)
        except IndexError: # Город не найден
            waiting_first_city = False
            await message.answer(
                f'Город <i>{first_city_name}</i> не был найден...\nПроверьте корректность его написания.',
                parse_mode=ParseMode.HTML
            )
        else:
            waiting_first_city = False

            # Просьба ввести второй город
            try:
                with open('messages/weather_2_second_city.txt', encoding='utf-8') as f:
                    text = f.read()
            except Exception as err:
                await message_error(message, err)
            else:
                await message.answer(text, parse_mode=ParseMode.HTML)
                waiting_second_city = True

    # Если вводится 2 город
    elif waiting_second_city:
        global second_city_key, second_city_name
        second_city_name = message.text

        """ 
        Код обрабатывает ситуацию, если город не был найден.
        Если город не найден, то он сообщает об этом пользователю.
        Если город найден, то выводит сообщение с предложением добавить доп. города.
        Сообщение находится в messages/weather_3_1_extra_cities.txt.
        """
        try:
            second_city_key = get_weather.get_key_by_city(weather_key, second_city_name)
        except IndexError:  # Город не найден
            waiting_second_city = False
            await message.answer(
                f'Город <i>{second_city_name}</i> не был найден...\nПроверьте корректность его написания.',
                parse_mode=ParseMode.HTML
            )
        except Exception as err:
            waiting_second_city = False
            await message_error(message, err)
        else:
            waiting_second_city = False
            # Инлайн-клавиатура добавления промежуточных городов
            yes_button = types.InlineKeyboardButton(text='Да', callback_data='yes_button')
            no_button = types.InlineKeyboardButton(text='Нет', callback_data='no_button')
            inline_keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[yes_button, no_button]])

            # Вывод сообщения пользователю
            try:
                with open('messages/weather_3_1_extra_cities.txt', encoding='utf-8') as f:
                    text = f.read()
                    text_message = f'{text}'.format(first_city_name=first_city_name, second_city_name=second_city_name)
            except Exception as err:
                await message_error(message, err)
            else:
                await message.answer(text_message, parse_mode=ParseMode.HTML, reply_markup=inline_keyboard)

    # Если вводятся промежуточные города
    elif count_cities > 0:
        global list_cities_name, list_cities_key
        try:
            city_key = get_weather.get_key_by_city(weather_key, message.text)
        except IndexError:
            count_cities = 0
            await message.answer(
                f'Город <i>{message.text}</i> не был найден...\nПроверьте корректность его написания.',
                parse_mode=ParseMode.HTML
            )
            await message.answer('К сожалению, вам придется сделать запрос заново с помощью команды /weather. Приносим извинения за неудобства.')
        except Exception as err:
            count_cities = 0
            await message_error(message, err)
        else:
            list_cities_name.append(message.text)
            list_cities_key.append(city_key)
            count_cities -= 1

            if count_cities > 0:
                await message.answer('Введите следующий город:')
            else:
                inline_keyboard = types.InlineKeyboardMarkup(
                    inline_keyboard=[[types.InlineKeyboardButton(text='Продолжить!', callback_data='choice_day')]]
                )
                text_message = '<b>Список промежуточных городов:</b>\n'
                for city in list_cities_name:
                    text_message += f'{city}\n'
                text_message += '\nНажмите на кнопку ниже, чтобы продолжить.'
                await message.answer(text_message, reply_markup=inline_keyboard, parse_mode=ParseMode.HTML)

@dp.callback_query(F.data == 'yes_button')
async def extra_cities_count(callback_query: types.CallbackQuery):
    """ Функция обрабатывает запрос и предлагает пользователю выбрать
    число промежуточных городов. Сообщение находится по пути messages/weather_3_2_count_cities.txt """

    # Иналайн-клавиатура с вариантами
    city_0 = types.InlineKeyboardButton(text='Отмена', callback_data='no_button')
    city_1 = types.InlineKeyboardButton(text='1', callback_data='city_1')
    city_2 = types.InlineKeyboardButton(text='2', callback_data='city_2')
    city_3 = types.InlineKeyboardButton(text='3', callback_data='city_3')
    city_4 = types.InlineKeyboardButton(text='4', callback_data='city_4')
    inline_keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[[city_1, city_2], [city_3, city_4], [city_0]]
    )

    # Вывод сообщения
    try:
        with open('messages/weather_3_2_count_cities.txt', encoding='utf-8') as f:
            text = f.read()
    except Exception as err:
        await message_error(callback_query.message, err)

    else:
        await callback_query.message.answer(text, reply_markup=inline_keyboard)

""" Обработка полученного ответа от выбора добавления промежуточных городов """
@dp.callback_query(F.data.in_(['city_1', 'city_2', 'city_3', 'city_4']))
async def extra_cities_processing(callback: types.CallbackQuery):
    global count_cities

    # Обработка выбранного варианта
    count_cities = int(callback.data[-1])

    # Отправка сообщения пользователю
    await callback.message.answer('Введите первый город:')


@dp.callback_query(F.data.in_(['no_button', 'choice_day']))
async def choice_forecast_day(callback_query: types.CallbackQuery):
    """ Функция позволяет выбрать количество дней для прогноза.
    Сообщение, которое выводится пользователю, находится в messages/weather_4_choice_day.txt """
    # Создание инлайн-клавиатуры
    day_0 = types.InlineKeyboardButton(text='В текущий день', callback_data='day_0')
    day_1 = types.InlineKeyboardButton(text='Завтра', callback_data='day_1')
    day_2 = types.InlineKeyboardButton(text='Послезавтра', callback_data='day_2')
    day_3 = types.InlineKeyboardButton(text='Через 3 дня', callback_data='day_3')
    day_4 = types.InlineKeyboardButton(text='Через 4 дня', callback_data='day_4')
    inline_keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[day_0, day_1], [day_2, day_3], [day_4]])

    # Вывод сообщения
    try:
        with open('messages/weather_4_choice_day.txt', encoding='utf-8') as f:
            text = f.read()
            text_message = f'{text}'.format(first_city_name=first_city_name, second_city_name=second_city_name)
    except Exception as err:
        await message_error(callback_query.message, err)
    else:
        await callback_query.message.answer(text_message, reply_markup=inline_keyboard, parse_mode=ParseMode.HTML)

@dp.callback_query(F.data.in_(['day_0', 'day_1', 'day_2', 'day_3', 'day_4']))
async def get_weather_forecast(callback: types.CallbackQuery):
    global forecast_day
    # Получаем id пользователя для названия графиков
    id_user = callback.from_user.id

    # Передаем значение в forecast_day
    forecast_day = int(callback.data[-1])

    # Обновляем список городов на основе наличия промежуточных городов
    list_cities = {first_city_key: first_city_name}
    for city_key, city_name in zip(list_cities_key, list_cities_name):
        list_cities[city_key] = city_name
    list_cities[second_city_key] = second_city_name

    # Получаем прогноз по каждому городу
    for city_key in list_cities.keys():
        get_weather.get_forecast(weather_key, city_key)

    # Получаем метрики и ревизию
    all_metrics = []
    all_advices = {}
    for city_key in list_cities.keys():
        advices, metrics = get_weather.check_bad_weather(city_key, forecast_day)
        all_metrics.append(metrics)
        all_advices[city_key] = '\n'.join(list(advices))

    # Если прогноз на несколько дней, то строим линейный график
    if forecast_day > 0:
        create_figures.create_plots(id_user, all_metrics, forecast_day, list(list_cities.values()))
    else: # иначе столбчатый график
        # Что-то здесь не так, не разобрался в чем дело
        # create_figures.create_bars(id_user, all_metrics, list(list_cities.values()))
        create_figures.create_plots(id_user, all_metrics, forecast_day, list(list_cities.values()))

    # Подготовка ответа
    text_message = 'Основные метрики погодных условий ты можешь наблюдать на графиках выше.\n\nПредупреждения:\n'
    if len(all_advices) == 0:
        text_message += 'Отсутствуют'
    else:
        for city_key, advices in all_advices.items():
            if city_key == first_city_key:
                continue
            else:
                text_message += f'{list_cities[city_key]}:\n{advices}\n'
    text_message += 'Для создания нового запроса, напиши /weather.'

    # Подготовка к отправке графиков
    media = MediaGroupBuilder(caption=text_message)
    media.add_photo(media=FSInputFile(f'figures/{id_user}_temp_{datetime.today().date()}.png'))
    media.add_photo(media=FSInputFile(f'figures/{id_user}_hum_{datetime.today().date()}.png'))
    media.add_photo(media=FSInputFile(f'figures/{id_user}_wind_{datetime.today().date()}.png'))
    if os.path.exists(f'figures/{id_user}_rain_{datetime.today().date()}.png'):
        media.add_photo(media=FSInputFile(f'figures/{id_user}_rain_{datetime.today().date()}.png'))
    if os.path.exists(f'figures/{id_user}_snow_{datetime.today().date()}.png'):
        media.add_photo(media=FSInputFile(f'figures/{id_user}_snow_{datetime.today().date()}.png'))

    # Отправка результата
    await callback.message.answer_media_group(media.build())

    # Очищение графиков
    os.remove(f'figures/{id_user}_temp_{datetime.today().date()}.png')
    os.remove(f'figures/{id_user}_hum_{datetime.today().date()}.png')
    os.remove(f'figures/{id_user}_wind_{datetime.today().date()}.png')
    if os.path.exists(f'figures/{id_user}_rain_{datetime.today().date()}.png'):
        os.remove(f'figures/{id_user}_rain_{datetime.today().date()}.png')

    if os.path.exists(f'figures/{id_user}_snow_{datetime.today().date()}.png'):
        os.remove(f'figures/{id_user}_snow_{datetime.today().date()}.png')


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
