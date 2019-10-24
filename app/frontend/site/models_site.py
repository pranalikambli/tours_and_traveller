from django.db import models

#Extended in frontend/models.py

class contact_us(models.Model):
    class Meta:
        db_table = 'contact_us'

    record_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)
    email = models.EmailField(max_length=75)
    phone = models.CharField(max_length=15,null=True)
    message = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
