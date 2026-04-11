import apps.products.models
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProductImage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("image", models.ImageField(upload_to=apps.products.models._product_image_path, verbose_name="圖片")),
                ("alt_text", models.CharField(blank=True, max_length=255, verbose_name="替代文字")),
                ("order", models.PositiveSmallIntegerField(default=0, verbose_name="排序")),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="product_images",
                        to="products.product",
                        verbose_name="商品",
                    ),
                ),
            ],
            options={
                "verbose_name": "商品圖片",
                "verbose_name_plural": "商品圖片",
                "db_table": "product_images",
                "ordering": ["order"],
            },
        ),
    ]
