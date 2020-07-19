# Generated by Django 3.0.3 on 2020-05-19 09:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='WeatherBase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('iata_code', models.CharField(max_length=3)),
                ('temperature', models.FloatField()),
                ('precipitation', models.FloatField()),
                ('visibility', models.FloatField()),
                ('wind_speed', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='WeatherForecast',
            fields=[
                ('weatherbase_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='flight_delay_prediction.WeatherBase')),
                ('dt', models.DateTimeField()),
            ],
            bases=('flight_delay_prediction.weatherbase',),
        ),
        migrations.CreateModel(
            name='WeatherSummary',
            fields=[
                ('weatherbase_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='flight_delay_prediction.WeatherBase')),
                ('month', models.IntegerField()),
            ],
            bases=('flight_delay_prediction.weatherbase',),
        ),
    ]
