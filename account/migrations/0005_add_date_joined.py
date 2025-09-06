# Generated manually to add date_joined field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_classlevel_subject_studentclassenrollment_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='date_joined',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
