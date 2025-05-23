# Generated by Django 4.2.20 on 2025-04-20 19:55

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_relacionpaciente_alter_usuario_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='antecedentespersonales',
            name='activo',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='antecedentespersonales',
            name='actualizado_en',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='antecedentespersonales',
            name='creado_en',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='condicion',
            name='activo',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='condicion',
            name='actualizado_en',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='condicion',
            name='creado_en',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
