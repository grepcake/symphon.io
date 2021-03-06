import requests
from bs4 import BeautifulSoup
import datetime
from compface.models import Concert, Composer
from django.http import HttpResponseRedirect


def get_month_concerts():
    try:
        return requests.get('https://www.meloman.ru/calendar/')
    except:
        print("Error while getting data from the Internet")


def get_concert(url):
    return requests.get('https://www.meloman.ru' + url)


months = {"Января": 1, "Февраля": 2, "Марта": 3, "Апреля": 4, "Мая": 5, "Июня": 6, "Июля": 7, "Августа": 8,
          "Сентября": 9, "Октября": 10, "Ноября": 11, "Декабря": 12}


def parse(request):
    month = BeautifulSoup(
        get_month_concerts().text, features='html.parser').findAll(
        'div', {'class': 'calendar-day'})
    for date in month:
        concerts = date.find_all('li', {'class': 'hall-entry'})
        day = int(date.find('p', {'class': 'day'}).text)
        month = months[date.find('p', {'class': 'month'}).text]
        for c in concerts:
            time = c.find('span', {'class': 'sans'}).text
            hour = int(time[:2])
            minute = int(time[-2:])
            place = c.find('div', {'class': 'hall-entry-head'}).text.strip()
            link = c.attrs['data-link']
            url = 'https://www.meloman.ru' + link
            concert_info = get_concert(link)
            soup = BeautifulSoup(concert_info.text, features='html.parser')
            tickets_url = soup.find('a', {'class': 'buy-tickets-online'})
            if tickets_url is not None:
                tickets_url = tickets_url.attrs['href']
            concerts = soup.find_all('h5', {'class': 'caps'})
            description = soup.title.string.split(':')[0]
            for comp in concerts:
                if comp.parent.find('h6', {'class': 'gray'}) is not None:
                    current_composer = comp.find('a')
                    if current_composer is not None:
                        composer_name = "".join(current_composer.text.strip().split())
                        if composer_name == 'И.С.Бах':
                            composer_name = 'Бах'
                        if composer_name == 'П.И.Чайковский':
                            composer_name = 'Чайковский'
                        result_set = Composer.objects.filter(
                            name=composer_name)
                        if len(result_set) != 1:
                            continue
                        composer = result_set[0]
                        start_time = datetime.datetime(2018, month, day, hour,
                                                       minute)
                        concert = Concert(
                            composer=composer,
                            start_time=start_time,
                            place=place,
                            url=url,
                            description=description,
                            buy_tickets_url=tickets_url)
                        concert.save()
    return HttpResponseRedirect('/')