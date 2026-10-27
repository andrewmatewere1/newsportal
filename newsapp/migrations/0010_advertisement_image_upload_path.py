from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("newsapp", "0009_advertisement")]

    operations = [
        migrations.AlterField(
            model_name="advertisement",
            name="image",
            field=models.ImageField(upload_to="media/adverts/%Y/%m/"),
        ),
    ]
