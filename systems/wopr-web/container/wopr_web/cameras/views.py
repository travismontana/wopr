from django.shortcuts import render

# Create your views here.
def cameras_index(request):
    context = {}
    return render(request, "cameras_still_stream.html", context)
   