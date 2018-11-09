import requests
from bs4 import BeautifulSoup
import datetime
from compface.models import Concert, Composer


def get_html():
    try:
        return requests.get('https://www.meloman.ru/calendar/')
    except:
        print("Error while getting data from the Internet")


def parse_concert(url):
    concertr = requests.get('https://www.meloman.ru' + url)
    return BeautifulSoup(
        concertr.text, features='html.parser').find_all(
            'h5', {'class': 'caps'})


def parse():
    month = BeautifulSoup(
        get_html().text, features='html.parser').findAll(
            'div', {'class': 'calendar-day'})
    for day in month:
        concerts = day.find_all('li', {'class': 'hall-entry'})
        dayo = int(day.find('p', {'class': 'day'}).text)
        date = day.find('p', {'class': 'month'}).text
        if date == 'Января':
            month = 1
        elif date == 'Февраля':
            month = 2
        elif date == 'Марта':
            month = 3
        elif date == 'Апреля':
            month = 4
        elif date == 'Мая':
            month = 5
        elif date == 'Июня':
            month = 6
        elif date == 'Июля':
            month = 7
        elif date == 'Августа':
            month = 8
        elif date == 'Сентября':
            month = 9
        elif date == 'Октября':
            month = 10
        elif date == 'Ноября':
            month = 11
        elif date == 'Декабря':
            month = 12
        for c in concerts:
            d = c.find('span', {'class': 'sans'}).text
            hour = int(d[:2])
            minute = int(d[-2:])
            place = c.find('div', {'class': 'hall-entry-head'}).text.strip()
            link = c.attrs['data-link']
            url = 'https://www.meloman.ru' + link
            for comp in parse_concert(link):
                if comp.parent.find('h6', {'class': 'gray'}) is not None:
                    composer = comp.find('a')
                    if composer is not None:
                        composer_name = "".join(composer.text.strip().split())
                        result_set = Composer.objects.filter(
                            name=composer_name)
                        if len(result_set != 1):
                            continue
                        composer_id = result_set[0].id
                        start_time = datetime.datetime(2018, month, dayo, hour,
                                                       minute)
                        concert = Concert(
                            composer=composer_id,
                            start_time=start_time,
                            place=place,
                            url=url)
                        concert.save()
