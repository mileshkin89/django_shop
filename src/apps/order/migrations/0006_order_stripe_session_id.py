from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0005_alter_inventory_options_alter_order_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='stripe_session_id',
            field=models.CharField(
                blank=True, db_index=True, max_length=255,
                null=True, unique=True,
            ),
        ),
    ]
