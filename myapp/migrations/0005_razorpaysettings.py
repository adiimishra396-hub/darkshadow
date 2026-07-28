from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_merge_0002_spinwallet_spinpurchase_0003_wallet'),
    ]

    operations = [
        migrations.CreateModel(
            name='RazorpaySettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key_id', models.CharField(blank=True, default='', max_length=200, verbose_name='Razorpay Key ID')),
                ('key_secret', models.CharField(blank=True, default='', max_length=200, verbose_name='Razorpay Key Secret')),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Razorpay Settings',
            },
        ),
    ]
