from django.db import models

"""
    Author: Pranali Kambli
    Date: 10/10/2019
    Purpose: Model view of groups table.
             -- table_name : group_permissions
"""


class group_permissions(models.Model):
    class Meta:
        db_table = 'group_permissions'

    id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100)
    codename = models.CharField(max_length=100)


"""
    Author Name : Pranali Kambli
    Date : 10/10/2019
    Purpose : Model view of role group permissions table.
                -- table_name : 'role_group_permissions'
"""


class role_group_permissions(models.Model):
    """
        Role Group Permissions models
    """

    class Meta:
        db_table = 'role_group_permissions'

    id = models.AutoField(primary_key=True)
    role_id = models.PositiveIntegerField()
    group_permission = models.CharField(max_length=1000)
    last_modified_by = models.ImageField()
    modified_on = models.PositiveIntegerField()
