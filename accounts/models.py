from django.db import models

# Create your models here.
class Accounts_info(models.Model):
    email=models.EmailField(max_length=254,null=False)
    password = models.CharField(max_length=16,null=False)
    


