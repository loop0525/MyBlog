# Generated by Django 4.2.1 on 2023-05-24 09:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0005_alter_articlepost_body'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articlepost',
            name='body',
            field=models.TextField(),
        ),
    ]