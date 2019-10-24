# from frontend.user.models_user import *
from Crypto.Cipher import AES
import base64
from django.conf import settings
from django.db import connection
from django.core.mail import send_mail
import random
import hashlib, uuid
import datetime
from frontend.user.models_user import guide_city, city, user_roles_master


def encrypt_val(clear_text):
    PADDING = '\0'
    pad_it = lambda s: bytes(s + (16 - len(s) % 16) * PADDING, encoding='utf8')
    generator = AES.new(settings.ENCRYPT_KEY[:32].encode('utf-8'), AES.MODE_CBC, settings.IV.encode('utf-8'))
    crypt = generator.encrypt(pad_it(clear_text))
    cryptedStr = base64.urlsafe_b64encode(crypt)
    return cryptedStr


def decrypt_val(cipher_text):
    key = settings.ENCRYPT_KEY[:32].encode('utf-8')
    iv = settings.IV.encode('utf-8')
    generator = AES.new(key, AES.MODE_CBC, iv)
    raw_decrypted = generator.decrypt(base64.urlsafe_b64decode(cipher_text))
    clear_val = raw_decrypted.decode().rstrip("\0")
    return clear_val


def get_user_by_token(user_id, token):
    query = "SELECT " \
            "	u.user_id, " \
            "	u.email, " \
            "	t.token_id " \
            "FROM user AS u " \
            "	JOIN user_password_tokens AS t ON u.user_id = t.user_id " \
            "WHERE " \
            "	u.user_id = %s " \
            "	AND u.active = 1 " \
            "	AND t.used =0 " \
            "	AND t.expired =0 " \
            "	AND t.created_at <= now() " \
            "	AND t.created_at >= now() - INTERVAL '1 HOUR'" \
            "	AND t.token = %s" \
            "LIMIT 1"

    cursor = connection.cursor()
    cursor.execute(query, [user_id, token])
    result = dictfetchall(cursor, True)
    return result


def expire_user_password_tokens(user_id, token_id):
    query = "UPDATE user_password_tokens SET expired=1 WHERE user_id=%s AND token_id!=%s"
    cursor = connection.cursor()
    cursor.execute(query, [user_id, token_id])
    return


def send_user_mail(subject, message, from_email, recipient_list,
                   fail_silently=False, auth_user=None, auth_password=None,
                   connection=None, html_message=None):
    send_mail(subject, message, from_email, recipient_list,
              fail_silently, auth_user, auth_password,
              connection, html_message)


def dictfetchall(cursor, fetchOne=False):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    data = []
    for row in cursor.fetchall():
        data.append(dict(zip([col[0] for col in desc], row)))
        if (fetchOne):
            break

    return data if not fetchOne else (data[0] if len(data) != 0 else [])


def get_salt():
    len = random.randint(10, 15)
    salt_str = uuid.uuid4().hex
    return str(salt_str)[:len]


def hashed_password(password, salt):
    return hashlib.sha256(password.encode('utf-8') + salt.encode('utf-8')).hexdigest()


def hashed_token(string, salt):
    return


"""
    Author Name : Pranali Kambli
    Date : 28/08/2019
    Purpose : This function will return city detail on the basis of search key in tuple format.
"""


def get_city_list(serach_text):
    serach_text = serach_text.replace("'", "")
    query = "select city.city_id, city.city from city where city.city ilike %(city)s limit 5"
    cursor = connection.cursor()
    cursor.execute(query, {"city": "%" + serach_text + "%"})
    result = cursor.fetchall()
    return result


"""
    Author Name : Pranali Kambli
    Date : 27/09/2019
    Purpose : This function will add the city id guide wise
"""


def add_city_guide_wiese(city_list, guide_id):
    for city_name in city_list:
        city_obj = city.objects.filter(city=city_name).first()
        if city_obj:
            check_city_exist = guide_city.objects.filter(city_id=city_obj.city_id, guide_id=guide_id)
            if not check_city_exist:
                guide_city.objects.create(guide_id=guide_id, city_id=city_obj.city_id)


"""
    Author Name : Pranali Kambli
    Date : 27/09/2019
    Purpose : This function will return unique value from 2 list.
"""


def list_comapre(li1, li2):
    return (list(set(li1) - set(li2)))


"""
    Author Name : Pranali Kambli
    Date : 27/09/2019
    Purpose : This function will return list of city id.

"""


def get_city_id_list(cites):
    city_list = []
    cities_list = cites.split(",")
    cities_list = [i for i in cities_list if i]  # remove blank string from list
    for city_name in cities_list:
        city_obj = city.objects.filter(city=city_name).first()
        city_list.append(city_obj.city_id)
    return city_list


"""
    Author Name : Pranali Kambli
    Date : 03/10/2019
    Purpose : This function will return datetime in integer format.
"""


def convert_datetime_to_int(date_time):
    result = int(date_time.strftime('%Y%m%d%H%M%S'))
    return result


"""
    Author Name : Pranali Kambli
    Date : 03/10/2019
    Purpose : This function will return integer in datetime format.
"""


def convert_int_to_datetime(int_date):
    result = datetime.datetime.strptime(str(int_date), '%Y%m%d%H%M%S')
    return result


"""
    Author Name : Pranali Kambli
    Date : 05/10/2019
    Purpose : This function will return client ip address.
"""


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


"""
    Author Name : Pranali Kambli
    Date : 08/10/2019
    Purpose : This function will return role_id by rolename.
"""


def get_roleid(role_name):
    role_master_obj = user_roles_master.objects.get(role=role_name)
    return role_master_obj.role_id