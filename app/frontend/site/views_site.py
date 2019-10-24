from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from frontend.site.services import add_contact_us


# Create your views here.
def index(request):
    return render(request, 'site/index.html')


def contactus(request):
    if request.method == 'POST' and request.is_ajax():

        name = request.POST.get('name', '')
        result = add_contact_us(
            name,
            request.POST.get('email', ''),
            request.POST.get('phone', ''),
            request.POST.get('message', ''))
        if result == True:
            http_response = "<fieldset>";
            http_response += "<div id='success_page'>";
            http_response += "<h3>Email Sent Successfully.</h3>";
            http_response += "<p>Thank you <strong>" + name + "</strong>, your message has been submitted to us.</p>";
            http_response += "</div>";
            http_response += "</fieldset>";
        else:
            http_response = '<div class="error_message">Error occurred, please try after sometime.</div>';

        return HttpResponse(http_response)
    else:
        return render(request, 'site/contactus.html')
