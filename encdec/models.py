from django.db import models

# Create your models here.
class Product(models.Model):
    product_id = models.AutoField
    product_folder = models.TextField(default="", max_length=50)
    product_type = models.TextField(default="", max_length=50)
    product_name = models.FileField(default="" , upload_to='encdec/files')

    def __str__(self):
        return str(self.product_name)