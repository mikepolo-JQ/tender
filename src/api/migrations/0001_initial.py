# Generated by Django 3.2.5 on 2021-07-26 16:26

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lmd_id', models.CharField(default=None, max_length=25, unique=True)),
                ('store', models.CharField(max_length=50)),
                ('offer_text', models.TextField(blank=True, default='', null=True)),
                ('offer_value', models.CharField(max_length=1000)),
                ('description', models.TextField(blank=True, null=True)),
                ('code', models.CharField(blank=True, max_length=100, null=True)),
                ('title', models.TextField()),
                ('categories', models.CharField(max_length=1000)),
                ('featured', models.BooleanField()),
                ('url', models.URLField(max_length=1000)),
                ('smart_link', models.URLField(max_length=1000)),
                ('image_url', models.URLField(max_length=1000)),
                ('type', models.CharField(max_length=25)),
                ('offer', models.CharField(blank=True, default='', max_length=50, null=True)),
                ('status', models.CharField(max_length=25)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
            ],
        ),
    ]
