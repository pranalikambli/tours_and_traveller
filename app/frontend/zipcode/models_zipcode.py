from django.db import models

class zipcode(models.Model):
    class Meta:
        abstract = True

class zipcode_us(zipcode):
    class Meta:
        db_table = 'zipcode_us'

    zip_id = models.AutoField(primary_key=True)
    state = models.CharField(max_length=45)
    state_code = models.CharField(max_length=5)
    county = models.CharField(max_length=45)
    city = models.CharField(max_length=45)
    zipcode = models.CharField(max_length=10)
    country = models.CharField(max_length=45)
    country_code = models.CharField(max_length=5)
    longitude = models.CharField(max_length=45)
    latitude = models.CharField(max_length=45)
    active = models.SmallIntegerField(default=1)