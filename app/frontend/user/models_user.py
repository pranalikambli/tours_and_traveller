from django.db import models

#Extended in frontend/models.py

#--
# `salt` varchar(45) NOT NULL,
# `token` varchar(45) NOT NULL,
#--
class user(models.Model):
    class Meta:
        db_table = 'user'

    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    email = models.EmailField(max_length=75)
    password = models.CharField(max_length=75)
    salt = models.CharField(max_length=20)
    role_id =  models.SmallIntegerField(default = 0)
    sex = models.SmallIntegerField(null=True)
    profile_picture = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    active = models.SmallIntegerField(default=0)

class user_profile(models.Model):
    class Meta:
        db_table = 'user_profile'

    user_id = models.IntegerField(primary_key=True)
    phone = models.CharField(max_length=15,null=True)
    dob = models.DateField(null=True)

class user_address(models.Model):
    class Meta:
        db_table = 'user_address'

    address_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()

class user_login(models.Model):
    class Meta:
        db_table = 'user_login'

    record_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    login_ip = models.CharField(max_length=50)
    login_time = models.BigIntegerField()

class user_password_tokens(models.Model):
    class Meta:
        db_table = 'user_password_tokens'

    token_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    token=models.CharField(max_length=25)
    used=models.SmallIntegerField(default=0)
    expired=models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

#roles

class user_roles_master(models.Model):
    class Meta:
        db_table = 'user_roles_master'

    role_id = models.AutoField(primary_key=True)
    role = models.CharField(max_length=50) #Admin, customer or guide


#guide
class guide_profile(models.Model):
    class Meta:
        db_table = 'guide_profile'

    user_id = models.IntegerField()
    ratings = models.IntegerField(default = 0)
    total_ratings = models.IntegerField(default = 0) #count of ratings given by users
    total_reviews = models.IntegerField(default = 0) #count of review given by users
    is_verified = models.SmallIntegerField(default = 0)

class guide_rating(models.Model):
    class Meta:
        db_table = 'guide_ratings'

    rating_id = models.IntegerField()
    #combination of guide id and user id (eg.unq_id: 101-2005, 101:guide id where as 2005:user id)
    # this helps to keep single field check instead creating multiple comlumn with join index
    unq_id = models.CharField(max_length=25)
    user_id = models.IntegerField()
    guide_id = models.IntegerField()
    rating = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

class guide_reviews(models.Model):
    class Meta:
        db_table = 'guide_reviews'

    review_id = models.IntegerField()
    #combination of guide id and user id (eg.unq_id: 101-2005, 101:guide id where as 2005:user id)
    # this helps to keep single field check instead creating multiple comlumn with join index
    unq_id = models.CharField(max_length=25)
    user_id = models.IntegerField()
    guide_id = models.IntegerField()
    review = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)


"""
    Author: Pranali Kambli
    Date: 26/08/2019
    Purpose: City model
             -- table_name : city
"""


class city(models.Model):
    class Meta:
        db_table = 'city'

    city_id = models.AutoField(primary_key=True)
    city = models.CharField(max_length=50)
    state_id = models.IntegerField()
    country_id = models.IntegerField()


"""
    Author: Pranali Kambli
    Date: 26/08/2019
    Purpose: State model
             -- table_name : state
"""


class state(models.Model):
    class Meta:
        db_table = 'state'

    state_id = models.AutoField(primary_key=True)
    state = models.CharField(max_length=50)
    country_id = models.IntegerField()


"""
    Author: Pranali Kambli
    Date: 26/08/2019
    Purpose: Country model
             -- table_name : country
"""


class country(models.Model):
    class Meta:
        db_table = 'country'

    country_id = models.AutoField(primary_key=True)
    country = models.CharField(max_length=50)


"""
    Author: Pranali Kambli
    Date: 19/09/2019
    Purpose: This model will store city id against guide id.
             -- table_name : country
"""


class guide_city(models.Model):
    class Meta:
        db_table = 'guide_city'

    guide_id = models.IntegerField()
    city_id = models.IntegerField()