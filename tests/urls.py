from django.http import HttpResponse
from django.urls import path


def hello(request):
    if request.method == "GET":
        arg = request.GET.get("name")
    elif request.method == "POST":
        arg = request.POST.get("name")
    name = arg or "World"
    return HttpResponse("Hello %s!" % name)


def hello_meta(request):
    return HttpResponse(
        "From %s" % request.META.get("HTTP_REFERER") or "",
        content_type=request.META.get("CONTENT_TYPE"),
    )


urlpatterns = [
    path("", hello),
    path("meta/", hello_meta),
]
