from http.client import NOT_FOUND
from pytils.translit import slugify

from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


class TestNoteCreation(TestCase):
    """Класс тест."""

    @classmethod
    def setUpTestData(cls):
        """Фикстуры для тестирования."""
        cls.url = reverse('notes:add')
        cls.form_data = {'title': 'Новый заголовок',
                         'text': 'Новый текст',
                         'slug': 'new-slug'}
        cls.author = User.objects.create(username='Лев Толстой')
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)

    def test_user_can_create_note(self):
        """Залогиненный пользователь может создать заметку."""
        response = self.user_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, '/done/')
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.user)

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        response = self.client.post(self.url, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={self.url}'
        self.assertRedirects(response, expected_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_not_unique_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        note = Note.objects.create(title='Заголовок', text='Текст заметки',
                                   slug='note-slug', author=self.author)
        self.form_data['slug'] = note.slug
        response = self.user_client.post(self.url, data=self.form_data)
        self.assertFormError(
            response, 'form', 'slug', errors=(note.slug + WARNING)
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_empty_slug(self):
        """Автоматическое формирование slug."""
        self.form_data.pop('slug')
        response = self.user_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        """Пользователь может редактировать свои заметки."""
        note = Note.objects.create(title='Заголовок', text='Текст',
                                   slug='slug', author=self.author)
        url = reverse('notes:edit', args=(note.slug,))
        response = self.auth_client.post(url, self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        note.refresh_from_db()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.author)

    def test_other_user_cant_edit_note(self):
        """Пользователь не может редактировать чужие заметки."""
        note = Note.objects.create(title='Заголовок', text='Текст',
                                   slug='slug', author=self.author)
        url = reverse('notes:edit', args=(note.slug,))
        response = self.user_client.post(url, self.form_data)
        self.assertEqual(response.status_code, NOT_FOUND)
        note_from_db = Note.objects.get(slug=note.slug)
        self.assertEqual(note.title, note_from_db.title)
        self.assertEqual(note.text, note_from_db.text)
        self.assertEqual(note.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        """Пользователь может удалить свои заметки."""
        note = Note.objects.create(title='Заголовок', text='Текст',
                                   slug='slug', author=self.author)
        url = reverse('notes:delete', args=(note.slug,))
        response = self.auth_client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        """Пользователь не может удалить чужие заметки."""
        note = Note.objects.create(title='Заголовок', text='Текст',
                                   slug='slug', author=self.author)
        url = reverse('notes:delete', args=(note.slug,))
        response = self.user_client.post(url)
        self.assertEqual(response.status_code, NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
