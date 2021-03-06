# Generated by Django 2.1.8 on 2019-10-05 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Login_user',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('password', models.CharField(max_length=32)),
                ('username', models.CharField(blank=True, max_length=32, null=True)),
                ('phonenumber', models.CharField(blank=True, max_length=32, null=True)),
                ('adress', models.TextField(blank=True, max_length=254, null=True)),
                ('photo', models.ImageField(default='seller/images/default_photo.jpg', upload_to='images')),
                ('QQ', models.IntegerField(blank=True, null=True)),
                ('hoby', models.CharField(blank=True, max_length=254, null=True)),
                ('user_type', models.IntegerField(default=0)),
            ],
        ),
    ]
