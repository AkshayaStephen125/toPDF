from user_app import modules
from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.
def index(request):
    return render(request, 'index.html')

def upload(request, type):
    return render(request, 'upload.html',{'type': type})

def upload_and_generate_pdf(request):
    if request.method == "POST":
        file_type = request.POST.get("type")
        if file_type == "text":
            file_content = request.POST.get("text")
        else:
            file_content =request.FILES.get("file")
        result, message, download_url = modules.convert_to_pdf(file_type, file_content)
        return JsonResponse({
            "result": result,
            "message": message,
            "download_url" : download_url
        })
    return JsonResponse({
            "result": False,
            "message": '',
            "download_url" : ''
        })