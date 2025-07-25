# Generated by Django 4.2.23 on 2025-07-25 11:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employeecalendar',
            name='employee',
        ),
        migrations.RemoveField(
            model_name='timeoffrequest',
            name='employee',
        ),
        migrations.AddField(
            model_name='employeecalendar',
            name='user_profile',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.userprofile'),
        ),
        migrations.AddField(
            model_name='timeoffrequest',
            name='user_profile',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.userprofile'),
        ),
        migrations.DeleteModel(
            name='Employee',
        ),
    ]
