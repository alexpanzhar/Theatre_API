# Generated by Django 5.1.3 on 2024-12-02 13:33

import theatre.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("theatre", "0003_play_actors"),
    ]

    operations = [
        migrations.AddField(
            model_name="play",
            name="image",
            field=models.ImageField(
                null=True, upload_to=theatre.models.play_image_file_path
            ),
        ),
        migrations.AlterField(
            model_name="theatrehall",
            name="name",
            field=models.CharField(max_length=64, unique=True),
        ),
    ]