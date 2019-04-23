from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
import time, os

from .forms import LoginForm
from .models import User, Document
from django.conf import settings
from .image_process import processPdf

def login(request):
    userid = request.session.get('userid', -1)
    if userid >= 0:
        return HttpResponseRedirect('index')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            usr = User.objects.filter(email = email, password = password).first()
            if usr is None:
                # login failed
                return render(request, 'robocop/login_fail.html', {'form': form})
            else:
                # login success
                # Set session variable
                request.session['userid'] = usr.id
                return HttpResponseRedirect('index')
    else:
        form = LoginForm()

    return render(request, 'robocop/login.html', {'form': form})

def index(request):
    userid = request.session.get('userid', -1)
    match_url = settings.BASE_URL + 'findmatch'
    if userid >= 0:
        return render(request, 'robocop/main.html', {'match_url': match_url})
    else:
        return HttpResponseRedirect('login')

def upload_file(request):
    userid = request.session.get('userid', -1)
    if request.method == 'POST':
        file = request.FILES['file']
        if not file is None and userid >= 0:
            userid = request.session['userid']
            filepath = handle_uploaded_file(request.FILES['file'], userid)
            print(filepath)
            print(filepath['name'])
            ret = {}
            ret['status'] = True
            ret['id'] = filepath['id']
            ret['fileUrl'] = settings.UPLOAD_URL + filepath['name']
            ret['errMsg'] = ''

        else:
            ret = {}
            ret['status'] = False
            ret['id'] = -1
            ret['fileUrl'] = ''
            ret['errMsg'] = 'Invalid file or user.'
    else:
        ret = {}
        ret['status'] = False
        ret['id'] = -1
        ret['fileUrl'] = ''
        ret['errMsg'] = 'Invalid file or user.'
    
    return JsonResponse(ret)

def find_match(request, file_id):
    doc = Document.objects.get(pk = file_id)
    ret = {}
    if doc is None:
        ret['status'] = False
        ret['errMsg'] = 'Cannot find the file.'
        return JsonResponse(ret)
    
    res = processPdf(doc.path)
    if res == {}:
        ret['status'] = False
        ret['errMsg'] = 'Failed to process.'
        return JsonResponse(ret)

    ret['status'] = True
    ret['errMsg'] = ''
    ret['accuracy'] = res['accuracy']
    ret['imageUrl'] = settings.PROCESS_URL + res['image']
    ret['masterPdfUrl'] = settings.PROCESS_URL + 'master.pdf'
    ret['masterJpgUrl'] = settings.PROCESS_URL + 'master.jpg'
    ret['match'] = res['match']
    ret['ismatch'] = res['ismatch']
    ret['score'] = res['score']

    return JsonResponse(ret)

def handle_uploaded_file(f, userid):
    timestr = time.strftime("%Y%m%d-%H%M%S")
    filename, file_extension = os.path.splitext(f.name)
    filename = timestr + file_extension
    filepath = settings.UPLOAD_DIR + '/' + filename
    with open(filepath, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    
    usr = User.objects.get(pk = userid)
    doc = Document(name = f.name, path = filename, user = usr)
    doc.save()

    ret = {}
    ret['id'] = doc.id
    ret['name'] = filename
    
    return ret
