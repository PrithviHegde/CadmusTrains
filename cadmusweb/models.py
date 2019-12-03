from django.db import models

# Create your models here.
class querydata(models.Model):
    Sno = models.IntegerField(primary_key=True)
    Email = models.CharField(max_length = 50)
    Phone = models.IntegerField()
    Message = models.CharField(max_length = 100)
 
