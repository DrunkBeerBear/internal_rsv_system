# Generated by Django 2.1.7 on 2019-05-02 01:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20190502_0929'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lottery_pool',
            name='mail_address',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.User', verbose_name='mail_address'),
        ),
        migrations.AlterField(
            model_name='request_pool',
            name='mail_address',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.User', verbose_name='mail_address'),
        ),
        migrations.AlterField(
            model_name='reservations',
            name='mail_address',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.User', verbose_name='mail_address'),
        ),
    ]
