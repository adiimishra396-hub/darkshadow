from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_razorpaysettings'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpinMachineSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('spin_pack_spins', models.PositiveIntegerField(default=3, help_text='Number of spins per purchase pack')),
                ('spin_pack_amount', models.DecimalField(decimal_places=2, default='10.00', help_text='Price per spin pack (INR)', max_digits=8)),
                ('prize_diamonds', models.DecimalField(decimal_places=2, default='500.00', help_text='Prize for 3x Diamonds (wallet credit)', max_digits=10)),
                ('prize_sevens', models.DecimalField(decimal_places=2, default='300.00', help_text='Prize for 3x Lucky Sevens (wallet credit)', max_digits=10)),
                ('prize_cherries', models.DecimalField(decimal_places=2, default='100.00', help_text='Prize for 3x Cherries (wallet credit)', max_digits=10)),
                ('prize_two_of_kind', models.DecimalField(decimal_places=2, default='20.00', help_text='Prize for any two-of-a-kind match (wallet credit)', max_digits=10)),
                ('is_active', models.BooleanField(default=True, help_text='Show/hide the spin machine on the homepage')),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Spin Machine Settings',
            },
        ),
    ]
