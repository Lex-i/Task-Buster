# -*- coding: utf-8 -*-
# + This is unittest´s file
# + Unittests are meant to test small pieces of code, from the point of view of the developer
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import activate


class TestHomePage(TestCase):
    # +The idea is that index.html inherits from base.html (it uses all its contents)
    # + except for the blocks marked with these special template tags.
    def test_uses_index_template(self):
        activate('en')
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'taskbuster/index.html')

    def test_uses_base_template(self):
        activate('en')
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'base.html')
