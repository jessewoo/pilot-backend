# Reverses the 0004 migration - removes FlexiblePage and AdvancedFlexiblePage from home app

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_advancedflexiblepage_flexiblepage'),
    ]

    operations = [
        migrations.DeleteModel(
            name='AdvancedFlexiblePage',
        ),
        migrations.DeleteModel(
            name='FlexiblePage',
        ),
    ]
