from django.shortcuts import render

def home(request):
    return render(request,'home.html',{})

def login_general(request):
    return render(request,'login_general.html',{})

def not_found_view(request,exception):
    return render(request,'404.html')