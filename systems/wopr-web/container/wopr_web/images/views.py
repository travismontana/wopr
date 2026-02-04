from django.shortcuts import render


# Create your views here.
def images_index(request):
    return render(request, "image_index.html")


def images_ondisk(request):

    return render(request, "images_ondisk.html", context)


def images_indb(request):
    return render(request, "images_indb.html")
