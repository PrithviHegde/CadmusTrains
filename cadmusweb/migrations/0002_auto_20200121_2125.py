# Generated by Django 3.0 on 2020-01-21 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cadmusweb', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='querydata',
            name='Sno',
        ),
        migrations.AddField(
            model_name='querydata',
            name='id',
            field=models.AutoField(auto_created=True, default=1, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
    ]
