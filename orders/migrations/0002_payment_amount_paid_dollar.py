# Generated by Django 4.0.5 on 2022-08-02 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='amount_paid_dollar',
            field=models.CharField(blank=True, default=None, max_length=100),
        ),
    ]