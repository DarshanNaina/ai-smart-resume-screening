# Generated migration for adding location field to Job model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_application_custom_offer_letter'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='location',
            field=models.CharField(blank=True, default='Remote', max_length=200),
        ),
    ]
