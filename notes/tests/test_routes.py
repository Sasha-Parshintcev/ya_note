from http.client import OK, NOT_FOUND

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note

User = get_user_model()

class TestNotes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.notes = Note.objects.create(title='Заголовок', text='Текст', author=cls.author)
    # def setUp(self):
    #     self.author = User.objects.create(username='Лев Толстой')
    #     self.reader = User.objects.create(username='Читатель простой')
    #     self.notes = Note.objects.create(title='Заголовок', text='Текст', author=self.author)


    def test_pages_availability(self):
        urls = (
            ('notes:home', None),
            ('users:signup', None),
            ('users:login', None),
            ('users:logout', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, OK)


    def test_notes_page_accessible(self):
        self.client.force_login(self.reader)
        for name in ('notes:list', 'notes:success', 'notes:add'):
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, OK)


    def test_detail_edit_delete(self):
        users_statuses = (
            (self.author, OK),
            (self.reader, NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:detail', 'notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.notes.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)


    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        for name in ('notes:list', 'notes:success', 'notes:add'):
            with self.subTest(name=name):
                url = reverse(name)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
        for name in ('notes:detail', 'notes:edit', 'notes:delete'):
            with self.subTest(name=name):
                url = reverse(name, args=(self.notes.slug,))
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)