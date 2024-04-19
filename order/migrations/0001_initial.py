# Generated by Django 5.0.4 on 2024-04-18 16:57

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('coupon', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total', models.FloatField()),
                ('qtd_total', models.PositiveIntegerField()),
                ('status', models.CharField(choices=[('A', 'Approved'), ('C', 'Created'), ('D', 'Disapproved'), ('P', 'Pending'), ('S', 'Sended'), ('F', 'Finished')], default='C', max_length=1)),
                ('applied_coupon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='coupon.coupon')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product', models.CharField(max_length=255)),
                ('product_id', models.PositiveIntegerField()),
                ('variation', models.CharField(max_length=255)),
                ('variation_id', models.CharField(max_length=50)),
                ('price', models.FloatField()),
                ('promotional_price', models.FloatField(default=0)),
                ('quantity', models.PositiveIntegerField()),
                ('image', models.CharField(max_length=2000)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order.order')),
            ],
            options={
                'verbose_name': 'Order item',
                'verbose_name_plural': 'Order items',
            },
        ),
    ]