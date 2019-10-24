from django.views import View
from django.views.generic import ListView
from django.http import JsonResponse
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .services import get_city_details_by_search, remove_non_ascii
from frontend.user.models_user import guide_profile, city, guide_city

"""
    Author Name : Pranali Kambli
    Date : 27/08/2019
    Purpose : Auto search functionality.
"""


class SearchAutocomplete(View):

    def post(self, request, *args, **kwargs):
        search_filter = self.request.POST.get('search', '')
        search_filter_text = search_filter.strip()
        data = {}

        result = get_city_details_by_search(search_filter_text)
        for each in result:
            data[each[0]] = {'city': remove_non_ascii(each[1]), 'state': remove_non_ascii(each[2]),
                             'country': remove_non_ascii(each[3])}
        return JsonResponse(data)


"""
    Author Name : Pranali Kambli
    Date : 30/08/2019
    Purpose : Search Functionality to get the all guide details by city name.
"""


class SearchList(ListView):
    template_name = 'search/listing.html'

    def get(self, request, *args, **kwargs):
        search_filter = self.request.GET.get('search', '')
        search_filter_text = search_filter.strip()

        if not search_filter:
            queryset = guide_profile.objects.filter(is_verified=True).all()
        else:
            city_obj = city.objects.get(city=search_filter_text)
            guide_list = guide_city.objects.filter(city_id=city_obj.city_id).values_list('guide_id', flat=True)
            queryset = guide_profile.objects.filter(is_verified=True, user_id__in=set(guide_list)).all()

        paginator = Paginator(queryset, 6)
        try:
            page = int(request.GET.get('page', '1'))
        except:
            page = 1

        try:
            user_list = paginator.page(page)
        except PageNotAnInteger:
            user_list = paginator.page(1)
        except EmptyPage:
            user_list = paginator.page(paginator.num_pages)

        # Get the index of the current page
        index = user_list.number - 1

        # This value is maximum index of pages, so the last page - 1
        max_index = len(paginator.page_range)

        # range of 7, calculate where to slice the list
        start_index = index - 3 if index >= 3 else 0
        end_index = index + 4 if index <= max_index - 4 else max_index

        # new page range
        page_range = paginator.page_range[start_index:end_index]

        # showing first and last links in pagination
        if index >= 4:
            start_index = 1
        if end_index - index >= 4 and end_index != max_index:
            end_index = max_index
        else:
            end_index = None

        return render(request, self.template_name,
                      {'record_list': user_list, 'search_filter': search_filter, 'page_range': page_range,
                       'start_index': start_index,
                       'end_index': end_index, 'max_index': max_index})
