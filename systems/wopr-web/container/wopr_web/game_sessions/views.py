from django.shortcuts import render


# Create your views here.
def game_sessions_index(request):
    context = {}
    return render(request, "game_sessions_index.html", context)
