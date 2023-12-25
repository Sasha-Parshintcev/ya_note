# Generated by Django 4.2.8 on 2023-12-25 08:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('notes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='note',
            name='title',
            field=models.CharField(default='Название заметки', help_text='Дайте короткое название заметке', max_length=100, verbose_name='Заголовок'),
        ),
    ]
