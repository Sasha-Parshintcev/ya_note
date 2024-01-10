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
        cls.note = Note.objects.create(title='Заголовок', text='Текст заметки',
                                       slug='note-slug', author=cls.author)

    def test_user_can_create_note(self):
        """Залогиненный пользователь может создать заметку."""
        notes_count = Note.objects.count()
        response = self.user_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, '/done/')
        self.assertEqual(notes_count + 1, Note.objects.count())
        note = Note.objects.order_by('pk').last()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.user)

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        notes_count = Note.objects.count()
        response = self.client.post(self.url, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={self.url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(notes_count, Note.objects.count())

    def test_not_unique_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        notes_count = Note.objects.count()
        self.form_data['slug'] = self.note.slug
        response = self.user_client.post(self.url, data=self.form_data)
        self.assertFormError(
            response, 'form', 'slug', errors=(self.note.slug + WARNING)
        )
        self.assertEqual(notes_count, Note.objects.count())

    def test_empty_slug(self):
        """Автоматическое формирование slug."""
        notes_count = Note.objects.count()
        self.form_data.pop('slug')
        response = self.user_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(notes_count + 1, Note.objects.count())
        new_note = Note.objects.order_by('pk').last()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        """Пользователь может редактировать свои заметки."""
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.auth_client.post(url, self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])
        self.assertEqual(self.note.author, self.author)

    def test_other_user_cant_edit_note(self):
        """Пользователь не может редактировать чужие заметки."""
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.user_client.post(url, self.form_data)
        self.assertEqual(response.status_code, NOT_FOUND)
        note_from_db = Note.objects.get(slug=self.note.slug)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        """Пользователь может удалить свои заметки."""
        notes_count = Note.objects.count()
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.auth_client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(notes_count - 1, Note.objects.count())

    def test_other_user_cant_delete_note(self):
        """Пользователь не может удалить чужие заметки."""
        notes_count = Note.objects.count()
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.user_client.post(url)
        self.assertEqual(response.status_code, NOT_FOUND)
        self.assertEqual(notes_count, Note.objects.count())
