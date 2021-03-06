from datetime import datetime

from django.http import HttpRequest, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render, redirect
from .forms import PhotoForm

from PIL import Image

from .recognize import recognize_image, recognize_url_image
from .models import Concert, Composer, Composition, Compilation

import math


def index(request):
    photo_form = PhotoForm()
    return render(request, 'index.html', {'form': photo_form})


def recognize(request):
    if request.method != "POST":
        return redirect('/')
    photo_form = PhotoForm(request.POST, request.FILES)
    result_set = None
    if not photo_form.is_valid():
        return render(request, 'failure.html', {
            'reason':
            'Не получилось обработать фотографию, попробуйте снова'
        })
    if 'photo' in request.FILES:
        image_field = photo_form.cleaned_data['photo']
        image = Image.open(image_field)
        result_set = recognize_image(image)
    elif 'data' in photo_form.cleaned_data:
        result_set = recognize_url_image(photo_form.cleaned_data['data'])

    if not result_set:
        return render(request, 'failure.html',
                      {'reason': ' Мы не нашли лиц на вашем изображении.'})
    elif len(result_set) > 1:
        # TODO maybe choose one composer?
        return render(
            request, 'failure.html', {
                'reason':
                'На вашей фотографии _слишком_ много композиторов (больше одного)!'
            })
    else:
        if result_set == [-1]:
            return render(
                request, 'failure.html',
                {'reason': 'На этом изображении нет известных композиторов.'})
        composer_id = result_set[0]
        # TODO: maybe check that composer_id exists in the database
        return HttpResponseRedirect('composer/%s' % composer_id)


def composer(request, composer_id):
    try:
        comp = Composer.objects.get(pk=composer_id)
    except Composer.DoesNotExist:
        return HttpResponseNotFound()
    compositions = Composition.objects.filter(author=comp)
    return render(
        request, 'composer.html', {
            'name': comp.name,
            'first_name': comp.first_name,
            'patronymic': comp.patronymic,
            'biography': comp.bio,
            'photo': comp.photo,
            'compositions': compositions
        })


def affiche(request, composer_id):
    concerts = Concert.objects.filter(composer=composer_id)
    return render(request, 'affiche.html', {'concerts': concerts})


def composers(request):
    compilations = Composer.objects.all()
    return render(request, 'list_composers.html', {'composers': compilations})


def compilations(request):
    compilations = Compilation.objects.all()
    if request.user.is_authenticated:
        compilations = sorted(
            compilations,
            key=lambda x: -math.fabs(request.user.profile.age - x.medium_age)
        )
    return render(request, 'list_compilations.html', {'compilations': compilations})


def compilation(request, compilation_id):
    try:
        comp = Compilation.objects.get(pk=compilation_id)
    except Composer.DoesNotExist:
        return HttpResponseNotFound()
    compositions = comp.compositions.all()
    return render(
        request, 'compilation.html', {
            'name': comp.name,
            'photo': comp.photo,
            'description': comp.description,
            'compositions': compositions
        })
