from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    """Класс тест."""

    @classmethod
    def setUpTestData(cls):
        """Фикстуры для тестирования."""
        cls.url = reverse('notes:list')
        cls.author = User.objects.create(username='Лев Толстой')
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.note = Note.objects.create(title='Заголовок', text='Текст заметки',
                                       slug='slug', author=cls.author)

    def test_note_in_list_for_author(self):
        """
        Отдельная заметка передаётся на страницу со списком заметок
        в списке object_list в словаре context.
        """
        response = self.auth_client.get(self.url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_note_not_in_list_for_another_user(self):
        """
        В список заметок одного пользователя не попадают
        заметки другого пользователя.
        """
        response = self.user_client.get(self.url)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)

    def test_create_note_page_contains_form(self):
        """На страницы создания заметки передаются формы."""
        url = reverse('notes:add')
        response = self.auth_client.get(url)
        self.assertIn('form', response.context)

    def test_edit_note_page_contains_form(self):
        """На страницы редактирования заметки передаются формы."""
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.auth_client.get(url)
        self.assertIn('form', response.context)
