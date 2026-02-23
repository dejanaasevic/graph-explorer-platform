from django.http import HttpResponse

def index(request):
    return HttpResponse("Graph Explorer is working!")