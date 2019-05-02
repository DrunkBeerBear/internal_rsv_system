# Generated by Django 2.1.7 on 2019-05-01 23:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inventory_name', models.TextField(max_length=255)),
                ('description', models.TextField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Inventory_list',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inventory_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.Inventory')),
            ],
        ),
        migrations.CreateModel(
            name='Lottery_pool',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('check_in_date', models.DateField()),
                ('stay_term', models.IntegerField()),
                ('number_of_guests', models.SmallIntegerField(max_length=100)),
                ('purpose', models.SmallIntegerField(max_length=3)),
            ],
        ),
        migrations.CreateModel(
            name='Request_pool',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('check_in_date', models.DateField()),
                ('stay_term', models.IntegerField()),
                ('number_of_guests', models.SmallIntegerField(max_length=100)),
                ('purpose', models.SmallIntegerField(max_length=3)),
                ('request_status', models.SmallIntegerField(max_length=3)),
                ('expire_date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Reservations',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('check_in_date', models.DateField()),
                ('stay_term', models.IntegerField()),
                ('number_of_guests', models.SmallIntegerField(max_length=100)),
                ('purpose', models.SmallIntegerField(max_length=3)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=40)),
                ('mail_address', models.CharField(max_length=255, unique=True)),
                ('password', models.CharField(max_length=10)),
            ],
        ),
        migrations.AddField(
            model_name='reservations',
            name='mail_address',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.User'),
        ),
        migrations.AddField(
            model_name='request_pool',
            name='mail_address',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.User'),
        ),
        migrations.AddField(
            model_name='lottery_pool',
            name='mail_address',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.User'),
        ),
    ]
