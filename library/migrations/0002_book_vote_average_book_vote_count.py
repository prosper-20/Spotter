# Generated by Django 4.2.16 on 2024-09-16 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='vote_average',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='book',
            name='vote_count',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
