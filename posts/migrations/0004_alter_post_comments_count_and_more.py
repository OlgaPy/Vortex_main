# Generated by Django 4.2.4 on 2023-08-10 18:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("posts", "0003_alter_postvote_unique_together_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="post",
            name="comments_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="post",
            name="votes_down_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="post",
            name="votes_up_count",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
