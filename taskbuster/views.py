# -*- coding: utf-8 -*-
from django.shortcuts import render
import datetime
from django.utils.timezone import now


def home(request):
    today = datetime.date.today()  # pass the today variable in the home view
    return render(request, "taskbuster/index.html", {'today': today, 'now': now()})
    # + RENDER lets you load a template, create a context
    # + adding a bunch of variables by default,
    # + such as information about the current logged-in user,
    # + or the current language, render it and return an HttpResponse, all in one function.
    # + Note: the information added by default depends on the template context processors
    # + that you have included in your settings file.


def home_files(request, filename):
    return render(request, filename, {}, content_type="text/plain")
