# Generated by Django 4.2.4 on 2023-08-16 09:11

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("posts", "0005_alter_post_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4),
        ),
    ]
