from django.views import View
from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import ListView
import time
import json
import operator

from frontend.user.models_user import user_roles_master
from .models_user_permissions import role_group_permissions, group_permissions

from frontend.constant import url_list


def get_form_value(form):
    """
    :return: Return the form value.
    """
    roles = {k: v for (k, v) in form.items() if k in url_list}
    return {'roles': roles}


"""
    Author Name : Pranali Kambli
    Date : 10/10/2019
    Purpose : List view for Role access rights.
"""


class RoleAccessRightsList(ListView):
    template_name = 'role_management/role_access_rights_list_view.html'

    def get(self, request, *args, **kwargs):
        """
        Return the list of all the active roles data.
        """

        record_list = user_roles_master.objects.all()
        return render(request, self.template_name, {'record_list': record_list})


"""
    Author Name : Pranali Kambli
    Date : 10/10/2019
    Purpose : Update Role Data.

"""


class RoleAccessRightsUpdate(View):
    template_name = 'role_management/role_access_rights.html'

    def get(self, request, role_id, *args, **kwargs):

        role_group_obj = role_group_permissions.objects.filter(role_id=role_id).first()
        role_id = role_group_obj.role_id
        get_role_name = user_roles_master.objects.filter(role_id=role_id).first()
        if get_role_name.role.lower() == 'admin':
            is_admin = True
            admin_id = get_role_name.role_id
        else:
            is_admin = False
            admin_id = 0

        role_permission = group_permissions.objects.all()
        role_list = [x for x in role_permission]

        return render(request, self.template_name, {'role_list': role_list,
                                                    'role_id': role_id,
                                                    'is_admin': is_admin,
                                                    'admin_id': admin_id})

    def post(self, request, role_id, *args, **kwargs):

        form = request.POST
        get_form_val = get_form_value(form)

        try:
            user_id = request.session.get('user')['user_id']
        except Exception as e:
            user_id = 0

        rights_val = 0
        url_permission_dict = {}
        group_permission_dict = {'roles': {}}
        for key, val in get_form_val.get('roles').items():
            if operator.contains(val, "can_edit"):
                rights_val = 1
            elif operator.contains(val, "view_only"):
                rights_val = 2
            elif operator.contains(val, "no_access"):
                rights_val = 3
            url_permission_dict[key] = rights_val
        group_permission_dict['roles'] = url_permission_dict

        modified_on = int(time.time())
        role_group_permissions.objects.filter(role_id=role_id).update(
            group_permission=json.dumps(group_permission_dict), last_modified_by=user_id,
            modified_on=modified_on)
        request.session.get('user')['role_group_permissions']['roles'] = url_permission_dict
        record_list = user_roles_master.objects.all()
        return render(request, 'role_management/role_access_rights_list_view.html',
                      {'msg': 'Access Role Rights Updated Successfully', 'record_list': record_list})


"""
    Author Name : Pranali Kambli
    Date : 10/10/2019
    Purpose : Get Role Data.

"""


class GetRoleValue(View):
    def get(self, request, *args, **kwargs):

        try:
            if self.request.GET.get('user') == '':
                role_id = 0
            if not isinstance(self.request.GET.get('user'), int):
                role_id = int(self.request.GET.get('user'))
            else:
                role_id = self.request.GET.get('user')

            get_grp_prmson = role_group_permissions.objects.filter(role_id=role_id).first()
            if get_grp_prmson:
                data = json.loads(get_grp_prmson.group_permission)
                return JsonResponse(data)
        except Exception as e:
            print(e)