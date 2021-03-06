import datetime

from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render, redirect

from django.contrib.auth.models import User
from django.contrib.auth import login
from .models import Profile
from .models import MALE, FEMALE, NON_DISCLOSED

from .vk_api import get_authorization_url, get_auth_info, get_bdate_and_sex


def request_token(request):
    user = request.user
    if user.is_authenticated:
        return HttpResponseRedirect('/')
    url = get_authorization_url()
    return redirect(url)


def receive_token(request):
    if request.user.is_authenticated or request.method != 'GET':
        return HttpResponseNotFound()
    code = request.GET.get('code')
    if code is None:
        return HttpResponseNotFound()
    data = get_auth_info(code)
    token = data.get('access_token')
    expires_in = data.get('expires_in')
    vk_id = data.get('user_id')
    email = data.get('email')
    assert token is not None
    assert expires_in is not None
    assert vk_id is not None
    if email is None:
        return render(request, 'failure.html', {'reason': 'Пожалуйста, укажите e-mail в настройках Вашей страницы '
                                                          'ВКонтакте'})
    bdate, sex, fn, ln = get_bdate_and_sex(token, vk_id)
    if bdate is None:
        return render(request, 'failure.html', {'reason': 'Пожалуйста, укажите возраст в настройках Вашей страницы '
                                                          'ВКонтакте'})
    if sex is None:
        sex = 0
    try:
        result_set = User.objects.get(username=vk_id)
        login(request, result_set)
        return HttpResponseRedirect('/')
    except User.DoesNotExist:
        pass
    age = make_age(bdate)
    gender = make_gender(sex)
    user = User(username=vk_id, email=email, first_name=fn, last_name=ln)
    user.save()
    profile = Profile(user=user, vk_id=vk_id, age=age, gender=gender)
    profile.save()
    login(request, user)
    return render(request, 'index.html')


def make_age(bdate):  # format of bdate is D.M.YYYY
    day, month, year = map(int, bdate.split('.'))
    date = datetime.date(year, month, day)
    today = datetime.date.today()
    delta = datetime.timedelta() + today - date
    return int(delta.days // 365.2425)


def make_gender(sex):
    if sex == 0:
        return NON_DISCLOSED
    elif sex == 1:
        return FEMALE
    elif sex == 2:
        return MALE
    else:
        assert False, 'unknown sex: ' % sex
