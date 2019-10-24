from django import template
from frontend.user.models_user import user, guide_rating, guide_profile, user_roles_master
from frontend.message_board.models_message import message_board

register = template.Library()

"""
    Author Name : Pranali Kambli
    Date : 30/08/2019
    Purpose : This function will return the user details by user_id.
"""


@register.filter(name='user_name')
def user_name(user_id):
    user_obj = user.objects.filter(user_id=user_id).first()
    if user_obj:
        first_name = user_obj.first_name
        last_name = user_obj.last_name
        result = first_name + " " + last_name
    else:
        result = ''
    return result


"""
    Author Name : Pranali Kambli
    Date : 05/09/2019
    Purpose : This function will return the guide ratings by guide id and user id.
"""


@register.filter(name='get_guide_ratings')
def get_guide_ratings(guide_id, user_id):
    guide_rating_obj = guide_rating.objects.filter(guide_id=guide_id, user_id=user_id).first()
    if guide_rating_obj:
        result = guide_rating_obj.rating
        return result


"""
    Author Name : Pranali Kambli
    Date : 06/09/2019
    Purpose : This function will return the average rating by guide id.
"""


@register.filter(name='get_avg_rating')
def get_avg_rating(guide_id):
    guide_profile_obj = guide_profile.objects.filter(user_id=guide_id).first()
    if guide_profile_obj:
        try:
            result = round(guide_profile_obj.ratings/guide_profile_obj.total_ratings)
        except Exception as e:
            result = 0
        return result


"""
    Author Name : Pranali Kambli
    Date : 21/10/2019
    Purpose : This function will return True if login user id guide else Falsr\e.
"""


@register.filter(name='is_guide')
def is_guide(user_id):
    is_guide_chk = guide_profile.objects.filter(user_id=user_id).first()
    if is_guide_chk:
        return True
    return False


"""
    Author Name : Pranali Kambli
    Date : 22/10/2019
    Purpose : This function will return the role name by role_id.
"""


@register.filter(name='get_role_name')
def get_role_name(role_id):
    role_obj = user_roles_master.objects.filter(role_id=role_id).first()
    if role_obj:
        role_name = role_obj.role
        result = role_name
    else:
        result = ''
    return result


"""
    Author Name : Pranali Kambli
    Date : 23/10/2019
    Purpose : This function will return the latest message by sender_id.
"""


@register.filter(name='get_msg')
def get_msg(sender_id):
    msg_obj = message_board.objects.filter(sender_id=sender_id).last()
    if msg_obj:
        txt_msg = msg_obj.text_msg
        result = txt_msg
    else:
        result = ''
    return result