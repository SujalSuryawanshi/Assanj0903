# Generated by Django 5.0.3 on 2024-08-05 14:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menuitems',
            name='menu_photo',
            field=models.ImageField(upload_to='static/images/menu_pics/'),
        ),
        migrations.CreateModel(
            name='New_offer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('offer_photo', models.ImageField(upload_to='static/images/offer_pics/')),
                ('message', models.CharField(max_length=10000)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='offers', to='core.staller')),
            ],
        ),
    ]
