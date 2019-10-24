from django.db import models

"""
    Author: Pranali Kambli
    Date: 16/10/2019
    Purpose: message_board model
             -- table_name : message_board
"""


class message_board(models.Model):
    class Meta:
        db_table = 'message_board'

    msg_id = models.AutoField(primary_key=True)
    sender_id = models.IntegerField()
    receiver_id = models.IntegerField()
    text_msg = models.TextField()
    created_at = models.DateTimeField(auto_now=True)


"""
    Author: Pranali Kambli
    Date: 22/10/2019
    Purpose: predefine_messages model
             -- table_name : predefine_messages
"""


class predefine_messages(models.Model):
    class Meta:
        db_table = 'predefine_messages'

    msg_id = models.AutoField(primary_key=True)
    message = models.CharField(max_length=250)