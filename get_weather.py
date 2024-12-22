import requests, json
from datetime import datetime

def get_key_by_city(api_key, city):
    """ Ищет ключ города по названию, с помощью которого будем получать прогноз """
    res = requests.get('http://dataservice.accuweather.com/locations/v1/cities/search', params={
        'apikey': api_key,
        'q': city,
        'language': 'ru-ru'
    }).json()
    return f'{res[0]["Key"]}'

def get_forecast(api_key, city_key):
    """ Записывает в json-файл прогноз погоды на 5 дней на основе ключа города """
    res = requests.get(f'http://dataservice.accuweather.com/forecasts/v1/daily/5day/{city_key}', params={
        'apikey': api_key,
        'language': 'ru-ru',
        'details': True,
        'metric': True
    }).json()

    with open(f'data/forecast_{city_key}_{datetime.today().date()}.json', 'w') as file:
        json.dump(res, file)

def check_bad_weather(city_key, day_forecast):
    """ Оценивает погоду в точке назначения и возвращает советы,
    погодные значения и уровень неблагоприятности погоды """
    # Чтение файла с погодой
    with open(f'data/forecast_{city_key}_{datetime.today().date()}.json') as file:
        content = json.load(file)

    # Вывод погодных метрик и сохранение в словаре
    temp_min = [content['DailyForecasts'][day]['Temperature']['Minimum']['Value'] for day in range(day_forecast+1)]
    temp_max = [content['DailyForecasts'][day]['Temperature']['Maximum']['Value'] for day in range(day_forecast+1)]
    temp_avg = [(t_max + t_min) / 2 for t_max, t_min in zip(temp_max, temp_min)]
    hum_avg = [content['DailyForecasts'][day]['Day']['RelativeHumidity']['Maximum'] for day in range(day_forecast+1)]
    speed_wind = [content['DailyForecasts'][day]['Day']['Wind']['Speed']['Value'] for day in range(day_forecast+1)]
    rain_mm = [content['DailyForecasts'][day]['Day']['Rain']['Value'] for day in range(day_forecast+1)]
    snow_cm = [content['DailyForecasts'][day]['Day']['Snow']['Value'] for day in range(day_forecast+1)]

    metrics = {
        'temp': temp_avg,
        'hum': hum_avg,
        'speed_wind': speed_wind,
        'rain': rain_mm,
        'snow': snow_cm
    }

    advices = set()

    # Оценка температуры
    for temp in temp_avg:
        if temp <= -35 or temp >= 40:
            advices.add('• В один из дней будет экстремальный показатель температуры!\n')
        elif -35 < temp <= -20:
            advices.add('• В один из дней будут заморозки. Одевайте очень теплые пуховики.\n')
        elif -20 < temp <= -5:
            advices.add('• В один из дней в городе будет холодно.\n')
        elif 31 > temp >= 25:
            advices.add('• В один из дней будет слегка жарковато. Одевайтесь посвободнее.\n')
        elif 40 > temp >= 31:
            advices.add('• В один из дней в городе будет стоять сильная жара. Не забудьте мини-вентиляторы и головные уборы.\n')

    # Оценка влажности
    for hum in hum_avg:
        if 70 < hum < 90:
            advices.add('• В один из дней влажность будет чуть выше нормы.\n')
        elif hum >= 90:
            advices.add('• В один из дней влажность будет значительно выше нормы.\n')
        elif 15 <= hum< 30:
            advices.add('• В один из дней влажность будет немного ниже нормы.\n')
        elif hum < 15:
            advices.add('• В один из дней влажность будет значительно ниже нормы.\n')

    # Оценка скорости ветра
    for wind in speed_wind:
        if 30 <= wind < 50:
            advices.add('• В один из дней скорость ветра будет слегка повышена. Придержите свои шляпы!\n')
        elif 50 <= wind < 70:
            advices.add('• В один из дней скорость ветра будет значительно выше нормы! Будьте осторожны!\n')
        elif wind >= 70:
            advices.add('• Штормовой ветер! Будьте бдительны и держитесь безопасных мест.\n')

    # Оценки снежных осадков
    for snow in snow_cm:
        if 0 < snow < 19:
            advices.add('• В один из дней в городе будет наблюдаться легкий снегопад.\n')
        elif 19 <= snow < 30:
            advices.add('• В один из дней будет сильный снегопад.\n')
        elif 30 <= snow < 50:
            advices.add('• Прогнозируется обильный снегопад! Одевайтесь теплее!\n')
        elif snow > 50:
            advices.add('• Ожидается снежный ураган!\n')

    # Оценка дождей
    for rain in rain_mm:
        if 0 < rain < 15:
            advices.add('• В один из дней в городе будет пасмурная погода, возможен дождь.\n')
        elif 15 <= rain < 50:
            advices.add('• В один из дней прогнозируется сильный дождь. Не забудьте взять с собой дождевики.\n')
        elif rain > 50:
            advices.add('• Ожидается очень сильный ливень.\n')

    return advices, metrics
