from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('characters', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='character',
            name='alignment',
            field=models.CharField(
                blank=True,
                default='',
                help_text='阵营 slug，如 lawful-good',
                max_length=30,
            ),
            preserve_default=False,
        ),
    ]
