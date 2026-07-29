from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0006_spinmachinesettings'),
    ]

    operations = [
        migrations.AddField(
            model_name='spinmachinesettings',
            name='jackpot_display_amount',
            field=models.CharField(default='84,52,910', help_text='Display amount shown on homepage jackpot card (e.g. 84,52,910)', max_length=30),
        ),
        migrations.AddField(
            model_name='spinmachinesettings',
            name='winning_reel_1',
            field=models.CharField(default='7', help_text='First reel symbol for winning code', max_length=10),
        ),
        migrations.AddField(
            model_name='spinmachinesettings',
            name='winning_reel_2',
            field=models.CharField(default='X', help_text='Second reel symbol for winning code', max_length=10),
        ),
        migrations.AddField(
            model_name='spinmachinesettings',
            name='winning_reel_3',
            field=models.CharField(default='7', help_text='Third reel symbol for winning code', max_length=10),
        ),
    ]
