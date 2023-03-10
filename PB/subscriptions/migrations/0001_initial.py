# Generated by Django 4.1.3 on 2022-12-09 01:21

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_on_card', models.CharField(default='', max_length=50)),
                ('card_number', models.IntegerField(default=None, null=True)),
                ('expiry_month', models.IntegerField(default=None, null=True)),
                ('expiry_year', models.IntegerField(default=None, null=True)),
                ('cvc', models.IntegerField(default=None, null=True)),
                ('subscribed', models.BooleanField(default=False)),
                ('price', models.IntegerField(blank=None, null=True)),
                ('length', models.CharField(max_length=10)),
                ('current_charge', models.DateTimeField(null=True)),
                ('next_charge', models.DateTimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=200)),
                ('price', models.IntegerField()),
                ('length', models.CharField(max_length=200)),
            ],
        ),
    ]
