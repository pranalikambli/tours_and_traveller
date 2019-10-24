from django.views import View
from django.shortcuts import render
from django.http import HttpResponseNotFound, JsonResponse
from django.template.loader import render_to_string
from django.db.models import Q

from .models_message import message_board
from frontend.user.models_user import user

"""
    Author: Pranali Kambli
    Date: 16/10/2019
    Purpose: To make text message.
"""


class MakeMessage(View):

    def post(self, request):
        if request.is_ajax() is False:
            return HttpResponseNotFound('Invalid Request')

        text_msg = request.POST.get('text_msg')
        error = 0
        msg = ''

        if text_msg == '':
            msg = "This is required field"
            error = 1

        context = {
            'msg': msg,
            'error': error
        }

        if request.is_ajax():
            json_data = {'html': render_to_string('message_board/make_message.html', context, request), 'error': error}
            if error == 0:
                message_board.objects.create(text_msg=text_msg, sender_id=request.POST.get('user_id'), receiver_id=request.POST.get('guide_id'))
            return JsonResponse(json_data)

        return render(request, 'message_board/make_message.html', context)


"""
    Author: Pranali Kambli
    Date: 17/10/2019
    Purpose: Get message list by user_id.
"""


class GetMessage(View):

    def get(self, request, sender_id):
        message_list = message_board.objects.filter(receiver_id=request.session.get('user')['user_id']).all(). \
            distinct('sender_id')
        chat_list = message_board.objects.filter(Q(sender_id=sender_id, receiver_id=request.session.get('user')['user_id']) |
                                                 Q(receiver_id=sender_id, sender_id=
                                                 request.session.get('user')['user_id'])).all().order_by('created_at')
        context = {'message_list': message_list, 'chat_list': chat_list, 'guide_id': request.session.get('user')['user_id']}
        return render(request, 'message_board/message_history.html', context)


"""
    Author: Pranali Kambli
    Date: 17/10/2019
    Purpose: Return list of users who messages to guide.
"""


class MessageBoard(View):
    def get(self, request):
        message_list = message_board.objects.filter(receiver_id=request.session.get('user')['user_id']).all(). \
            distinct('sender_id')

        return render(request, 'message_board/chat_user_list.html', {'message_list': message_list})