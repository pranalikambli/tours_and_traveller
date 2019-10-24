from django.db import connection

from unidecode import unidecode

"""
    Author Name : Pranali Kambli
    Date : 28/08/2019
    Purpose : This function will return city detail on the basis of search key in tuple format.
"""


def get_city_details_by_search(serach_text):
    serach_text = serach_text.replace("'", "")
    query = "select city.city_id, city.city, state.state, country.country from city " \
            "inner join state on city.state_id = state.state_id " \
            "inner join country on state.country_id = country.country_id " \
            "where city.city ilike %(city)s limit 5"
    cursor = connection.cursor()
    cursor.execute(query, {"city": "%"+serach_text+"%"})
    result = cursor.fetchall()
    return result


"""
    Author Name : Pranali Kambli
    Date : 28/08/2019
    Purpose : This function will return guide detail on the basis of city name in tuple format.
"""


def get_guide_details_by_city_name(city_name):
    city_name = city_name.replace("'", "")
    query = "select * from user where city = %s"
    cursor = connection.cursor()
    cursor.execute(query, [city_name])
    result = cursor.fetchall()
    return result


"""
    Author Name : Pranali Kambli
    Date : 28/08/2019
    Purpose : This function will remove the non ascii code.
"""


def remove_non_ascii(text):
    return unidecode(text)
