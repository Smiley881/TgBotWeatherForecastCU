import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

def create_plots(id_user, all_metrics, forecast_day, list_cities):
    """ Строит линейный графики прогноза погоды по городам """
    # График температур
    plt.figure(figsize=(8, 5))
    for city, metric in enumerate(all_metrics):
        plt.plot(np.arange(0, forecast_day + 1, 1), metric['temp'], label=list_cities[city])
    plt.title('График температур в каждом городе')
    plt.xlabel('День')
    plt.xticks(np.arange(0, forecast_day + 1, 1))
    plt.ylabel('Температура (в °С)')
    plt.legend(loc='best')
    plt.grid()
    plt.savefig(f'figures/{id_user}_temp_{datetime.today().date()}.png')

    # График влажности
    plt.figure(figsize=(8, 5))
    for city, metric in enumerate(all_metrics):
        plt.plot(np.arange(0, forecast_day + 1, 1), metric['hum'], label=list_cities[city])
    plt.title('График влажности в каждом городе')
    plt.xlabel('День')
    plt.xticks(np.arange(0, forecast_day + 1, 1))
    plt.ylabel('Влажность (в %)')
    plt.legend(loc='best')
    plt.grid()
    plt.savefig(f'figures/{id_user}_hum_{datetime.today().date()}.png')

    # График ветра
    plt.figure(figsize=(8, 5))
    for city, metric in enumerate(all_metrics):
        plt.plot(np.arange(0, forecast_day + 1, 1), metric['speed_wind'], label=list_cities[city])
    plt.title('График скорости ветра в каждом городе')
    plt.xlabel('День')
    plt.xticks(np.arange(0, forecast_day + 1, 1))
    plt.ylabel('Скорость ветра (в км/ч)')
    plt.legend(loc='best')
    plt.grid()
    plt.savefig(f'figures/{id_user}_wind_{datetime.today().date()}.png')

    # График дождей, если они хоть где-то есть
    if sum([sum(i['rain']) for i in all_metrics]) > 0:
        plt.figure(figsize=(8, 5))
        for city, metric in enumerate(all_metrics):
            plt.plot(np.arange(0, forecast_day + 1, 1), metric['rain'], label=list_cities[city])
        plt.title('График выпадения осадков в виде дождей\nв каждом городе')
        plt.xlabel('День')
        plt.xticks(np.arange(0, forecast_day + 1, 1))
        plt.ylabel('Количество осадков (в мм)')
        plt.legend(loc='best')
        plt.grid()
        plt.savefig(f'figures/{id_user}_rain_{datetime.today().date()}.png')

    # График снега если хоть где-то есть
    if sum([sum(i['snow']) for i in all_metrics]) > 1.5:
        plt.figure(figsize=(8, 5))
        for city, metric in enumerate(all_metrics):
            plt.plot(np.arange(0, forecast_day + 1, 1), metric['snow'], label=list_cities[city])
        plt.title('График выпадения осадков в виде\nснега в каждом городе')
        plt.xlabel('День')
        plt.xticks(np.arange(0, forecast_day + 1, 1))
        plt.ylabel('Количество осадков (в см)')
        plt.legend(loc='best')
        plt.grid()
        plt.savefig(f'figures/{id_user}_snow_{datetime.today().date()}.png')

def create_bars(id_user, all_metrics, list_cities):
    """ Строит столбчатые диаграммы прогноза погоды по городам """
    # График температуры
    list_temp = [city['temp'][0] for city in all_metrics]
    plt.bar(list_cities, list_temp)
    plt.title('График температур в каждом городе')
    plt.xlabel('Город')
    plt.ylabel('Температура (в °С)')
    plt.grid(axis='y')
    plt.savefig(f'figures/{id_user}_temp_{datetime.today().date()}.png')

    # График влажности
    list_hum = [city['hum'][0] for city in all_metrics]
    plt.bar(list_cities, list_hum)
    plt.title('График влажности в каждом городе')
    plt.xlabel('Город')
    plt.ylabel('Влажность (в %)')
    plt.grid(axis='y')
    plt.savefig(f'figures/{id_user}_hum_{datetime.today().date()}.png')

    # График скорости ветра
    list_wind = [city['speed_wind'][0] for city in all_metrics]
    plt.bar(list_cities, list_wind)
    plt.title('График скорости ветра в каждом городе')
    plt.xlabel('Город')
    plt.ylabel('Скорость ветра (в км/ч)')
    plt.grid(axis='y')
    plt.savefig(f'figures/{id_user}_wind_{datetime.today().date()}.png')

    # График дождей если хоть где-то есть
    if sum([sum(i['rain']) for i in all_metrics]) > 0:
        list_rain = [city['rain'][0] for city in all_metrics]
        plt.bar(list_cities, list_rain)
        plt.title('График выпадения осадков в виде\nдождей в каждом городе')
        plt.xlabel('Город')
        plt.ylabel('Количество осадков (в мм)')
        plt.grid(axis='y')
        plt.savefig(f'figures/{id_user}_rain_{datetime.today().date()}.png')

    # График снега если хоть где-то есть
    if sum([sum(i['snow']) for i in all_metrics]) > 1.5:
        list_snow = [city['snow'][0] for city in all_metrics]
        plt.bar(list_cities, list_snow)
        plt.title('График выпадения осадков в виде\nснега в каждом городе')
        plt.xlabel('Город')
        plt.ylabel('Количество осадков (в см)')
        plt.grid(axis='y')
        plt.savefig(f'figures/{id_user}_snow_{datetime.today().date()}.png')