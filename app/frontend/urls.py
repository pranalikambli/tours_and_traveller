from django.urls import path

from . import views
from .site import views_site
from .user import views_user
from .search import views_search
from .role_management import views_roles
from .message_board import views_message

urlpatterns = [
    # site
    path('', views_site.index, name='index'),
    path('contactus', views_site.contactus, name='contactus'),

    # user
    path('sign-up', views_user.sign_up, name='sign-up'),
    path('forgot-password', views_user.forgot_password, name='forgot-password'),
    path('reset-password', views_user.reset_password, name='reset-password'),
    path('sign-in', views_user.user_sign_in, name='user-sign-in'),
    path('sign-out', views_user.user_sign_out, name='user-sign-out'),
    path('send_sms', views_user.send_sms, name='send-sms'),
    path('activate/<str:uidb64>/<str:token>', views_user.activate, name='activate-user-account'),
    path('city-autocomplete', views_user.city_autocomplete, name='city-autocomplete'),
    path('update-user/<int:pk>', views_user.UpdateUser.as_view(), name='update-user'),
    path('change-password/<int:pk>', views_user.ChangePassword.as_view(), name='change-password'),

    # search
    path('search', views_search.SearchList.as_view(), name='search'),
    path('search-autocomplete', views_search.SearchAutocomplete.as_view(), name='search-autocomplete'),
    path('guide-profile/<guide_id>', views_user.GuideProfile.as_view(), name='guide-profile'),
    path('guide-rating', views_user.GuideRating.as_view(), name='guide-rating'),

    # role_management
    path('roles-access-rights-list', views_roles.RoleAccessRightsList.as_view(), name='roles-access-rights-list'),
    path('role-access-rights-update/<role_id>', views_roles.RoleAccessRightsUpdate.as_view(),
         name='role-access-rights-update'),
    path('get-role-json', views_roles.GetRoleValue.as_view(), name='get-role-json'),

    # message board
    path('make-message', views_message.MakeMessage.as_view(), name='make-message'),
    path('get-messages/<sender_id>', views_message.GetMessage.as_view(), name='get-messages'),
    path('message-board', views_message.MessageBoard.as_view(), name='message-board'),
]