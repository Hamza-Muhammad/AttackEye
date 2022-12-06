# from django.template import loader
# from django.template.loader import get_template
from django.template import Template,Context
from .nmap import parse_nmap_xml_report
from django.shortcuts import render, redirect
import json
from rest_framework.decorators import parser_classes
import validators
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from rest_framework.response import Response
from django.contrib.auth import authenticate ,logout
from django.contrib.auth import login as authlogin
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser 
from rest_framework import status
from django.contrib import auth
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.urls import reverse
from django.conf import settings
import datetime
from .forms import UserRegistrationForm
# from django.contrib.auth.forms import UserRegistrationForm
from attackeye.models import scan
# from attackeye.models import Domain
from attackeye.serializers import scanSerializer
from rest_framework.decorators import api_view
from celery import Celery
import subprocess
from .tasks import amass
from django.http import FileResponse
from django.contrib import messages
import logging
from django.contrib.auth.decorators import login_required


# @login_required
def index(request):
    if request.user.is_authenticated:
       return render(request, 'index.html')
    else:
        return render(request, 'login.html')

# logging.basicConfig(filename='/tmp/example.log', encoding='utf-8', level=logging.DEBUG)

# @login_required
def front(request):
  if request.user.is_authenticated:
    return render(request, 'front.html')
  else:
    return render(request, 'login.html')

# @login_required
def login(request):
    return render(request, "login.html")

def mainpage(request):
    return render(request, "mainpage.html")

api_view(['GET'])
def subdomainpage(request):
    return render(request, 'nmap.html')

# logging.basicConfig(filename='/tmp/example.log', encoding='utf-8', level=logging.DEBUG)


@api_view(['GET'])
def graph_json(request,graphdomain):
    print("*******************************************************************")
    print(graphdomain)
    # graph = open('/home/hamza/django-rest-api/django-rest-api-master/DjangoRestApi/attackeye/templates/data.json', 'rb')
    # graph_data = JSONParser().parse(request)
    # x = graph_data["title"]
    # y = graph_data["description"]
        # global check
        # check=y
    # print(request)
    # print(request.data["title"])
    graph = open(f'{settings.SITE_ROOT}/DjangoRestApi/generated_subdomains/'+graphdomain,'rb')
    # graph = open('/home/hamza/django-rest-api/django-rest-api-master/DjangoRestApi/attackeye/templates/data.json','rb')
    print(graph)
    response = FileResponse(graph)
    print(response)  
    # return render(request,'index.html',response)
    return response

@api_view(['GET'])
def table_view(request):
    return render(request, 'webdatarocks.html')

# "http://localhost:8080/api/download/csv
@api_view(['GET'])
def download_csv(request,graphname):
    # attackeye = scan.objects.last()
    # logging.info(attackeye.description)
    # domain = attackeye.description
    # logging.info(str(domain))
    print("hamza",graphname)
    subprocess.call(['bash',f'{settings.SITE_ROOT}/SubDomainDownload.sh',graphname])
    img = open(f'{settings.SITE_ROOT}/go/pkg/mod/pkg/mod/github.com/OWASP/Amass/v3/cmd/amass/amass_maltego.csv', 'rb') 
    response = FileResponse(img)
    return response

@parser_classes([JSONParser])
@api_view(['GET', 'POST', 'DELETE'])
def attackeye_list(request):
    if request.method == 'GET':
        attackeye = scan.objects.all()
        
        title = request.query_params.get('title', None)
        if title is not None:
            attackeye = attackeye.filter(title__icontains=title)
        
        attackeye_serializer = scanSerializer(attackeye, many=True)
        return JsonResponse(attackeye_serializer.data, safe=False)
        # 'safe=False' for objects serialization
 
    elif request.method == 'POST':
        # y=request.data["description"]
        
         y=request.data["description"]
         x=validators.domain(y)
         
         if x == True:
            print(x,'done')
            user= request.session["_auth_user_id"]
            graphold=scan.objects.filter(UserId=user,description=y)
            graph=scan.objects.filter(description=y)
            if graphold:
                graphold.delete()
            elif graph:
                tutorial=scan.objects.create(UserId=user,description=y,pending=1)
                return Response({'recieved data': request.data})
            
            
                # tutorial=scan.objects.create(UserId=user,description=y)
            #  print("llllllllllllllllllllllllllllllllllllllllllll")
            tutorial=scan.objects.create(UserId=user,description=y,pending=0)
            amass.delay(str(y),str(user)) 
            return Response({'received data': request.data})
        #  response = redirect('/home')
        #  return response 
         else:
             print("empty")
             print(x)
             return Response({'received data': 'enter valid input'})
              
    
    elif request.method == 'DELETE':
        count = scan.objects.all().delete()
        return JsonResponse({'message': '{} Tutorials were deleted successfully!'.format(count[0])}, status=status.HTTP_204_NO_CONTENT)
# # "http://localhost:8080/api/attackeye
# @api_view(['GET', 'POST', 'DELETE'])
# def attackeye_list(request):
#     if request.method == 'GET':
#         attackeye = scan.objects.all()
        
#         title = request.query_params.get('title', None)
#         if title is not None:
#             attackeye = attackeye.filter(title__icontains=title)
        
#         tutorials_serializer = scanSerializer(attackeye, many=True)
#         return JsonResponse(tutorials_serializer.data, safe=False)
#         # 'safe=False' for objects serialization
 
#     elif request.method == 'POST':
#         attackeye_data = JSONParser().parse(request)
#         x = attackeye_data["title"]
#         y = attackeye_data["description"]
#         attackeye_serializer = scanSerializer(data=attackeye_data)
#         if attackeye_serializer.is_valid():
#             attackeye_serializer.save()
#             amass.delay(str(y))
#             # subprocess.call(['bash','/home/hamza/abc.sh',str(y)])
#             return JsonResponse(attackeye_serializer.data, status=status.HTTP_201_CREATED) 
#         return JsonResponse(attackeye_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         #  attackeye_data = JSONParser().parse(request)
#         #  x = attackeye_data["title"]
#         #  y = attackeye_data["description"]
#         # attackeye_serializer = scanSerializer(data=attackeye_data)
#         #  print("ssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss")
#         #  user= request.session["_auth_user_id"]
#         #  y=request.POST.get("domain")
#         #  print("rerereeeeeeeeeeeeeeeeeeeeeeeeeeee",y)
#         #  graphold=scan.objects.filter(UserId=user,description=y)
#         #  graph=scan.objects.filter(description=y)
#         #  print("graph",graph[0].published)
#         #  now=datetime.datetime.now()
#         #  print(now)
#         #  print("Date: "+ now.strftime("%Y-%m-%d")) 
#         #  a=graph[0].published
#         #  b=now.strftime(("%Y-%m-%d"))
#         #  print(a>b)
#         #  if graphold:
#         #     # print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAa")
#         #     graphold.delete()
#         #  elif graph:
#         #     tutorial=scan.objects.create(UserId=user,description=y)
#         #     response = redirect('/home')
#         #     return response 
#             # return render(request,"dummy.html")
#             # print("KKKKKKKKKKKKKKKKKKKKKKKKK")
#             # return render(request,'front.html') 
           
#             # tutorial=scan.objects.create(UserId=user,description=y)
#         #  print("llllllllllllllllllllllllllllllllllllllllllll")
#         #  amass.delay(str(y),str(user)) 
#         #  response = redirect('/home')
#         #  return response 
#         #  return render(request,"dummy.html")
#         #  return render(request,'front.html')   
            
          
             
         
         
#         #  print(description)
         
        
#         #  messages.success(request,'Data has been submitted')
         
#         #  return JsonResponse({"msg":"done"}, status=status.HTTP_201_CREATED) 
#         # username = request.POST.get('name')
#         # password= request.POST.get("password")
#         # attackeye_data = JSONParser().parse(request)
#         # x = attackeye_data["title"]

#         # print("*************************************************************")
#         # print(username,password)
#         # z=attackeye_data["published"]
#         # attackeye_serializer = scanSerializer(data=attackeye_data)
#         # if attackeye_serializer.is_valid():
#         #     attackeye_serializer.save()
          
#             # amass.delay(str(y))
#             # subprocess.call(['bash','/home/hamza/abc.sh',str(y)])
#         #     return JsonResponse(attackeye_serializer.data, status=status.HTTP_201_CREATED) 
#         # return JsonResponse(attackeye_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#     elif request.method == 'DELETE':
#         count = scan.objects.all().delete()
#         return JsonResponse({'message': '{} Tutorials were deleted successfully!'.format(count[0])}, status=status.HTTP_204_NO_CONTENT)
 
 
@api_view(['GET', 'PUT', 'DELETE'])
def attackeye_detail(request, pk):
    try: 
        tutorial = scan.objects.get(pk=pk) 
    except scan.DoesNotExist: 
        return JsonResponse({'message': 'The tutorial does not exist'}, status=status.HTTP_404_NOT_FOUND) 
 
    if request.method == 'GET': 
        attackeye_serializer = scanSerializer(tutorial) 
        return JsonResponse(attackeye_serializer.data) 
 
    elif request.method == 'PUT': 
        attackeye_data = JSONParser().parse(request) 
        attackeye_serializer = scanSerializer(tutorial, data=attackeye_data) 
        if attackeye_serializer.is_valid(): 
            attackeye_serializer.save() 
            return JsonResponse(attackeye_serializer.data) 
        return JsonResponse(attackeye_serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
 
    elif request.method == 'DELETE': 
        tutorial.delete() 
        return JsonResponse({'message': 'scan was deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)
    
        
@api_view(['GET'])
def attackeye_list_published(request):
    attackeye = scan.objects.filter(published=True)
        
    if request.method == 'GET': 
        tutorials_serializer = scanSerializer(attackeye, many=True)
        return JsonResponse(tutorials_serializer.data, safe=False)
    
# @api_view(['GET'])
# def graph_get(request):
#     # hamza=Domain.objects.all().delete()
#     graph=Domain.objects.get(id="9")
#     return JsonResponse(graph.data) 
#     # print(graph.data)
#     # response=graph.data
#     # return response
#     # response=FileResponse(graph)
#     # return graph
#     # print(graph)
#     # graph = open('/home/hamza/django-rest-api/django-rest-api-master/DjangoRestApi/attackeye/templates/data.json', 'rb')
#     # response = FileResponse(graph)
#     # return response
    
# @api_view(['GET'])
# def graph_list(request):
#     if request.method=="GET":
#         user= request.session["userId"]
#         print(user)
#         graph_list=[]
#         graph=scan.objects.filter(UserId=user)
#         print(graph)
#         print("*****************************")
#         for i in range(len(graph)):
#             graph_list.append(graph[i])
#         print(graph_list)
#         # return HttpResponseRedirect(reverse({"graph_list":graph_list}))
#         # return redirect(request.META['HTTP_REFERER']) 
#         # return JsonResponse({"graph_list":graph_list})
#         return render(request,"front.html",{"graph_list":graph_list})
    # user= request.session["userId"]
    # graph_list=[]
    # graph=scan.objects.all()
    # for i in range(len(graph)):
    #     graph_list.append(graph[i].description)
        
    # print(graph_list)
    
    # print((user))
    # for key, value in request.session.items():
    #     print('{} => {}'.format(key, value))
    # print(fav_color)
     

# @api_view(['POST'])
# def graph_display(request):
#    print(request)
#    attackeye_data = JSONParser().parse(request) 
#    attackeye_serializer = scanSerializer(tutorial, data=attackeye_data) 
#    return JsonResponse(attackeye_serializer.data) 
   
# @api_view(['GET', 'POST', 'DELETE'])
# def graph_display(request):
#         # graph_data = JSONParser().parse(request)
#         # x = graph_data["title"]
#         # y = graph_data["description"]
#         # try: 
#         #     tutorial = scan.objects.get(description=y) 
#         # except scan.DoesNotExist: 
#         #     return JsonResponse({'message': 'The tutorial does not exist'}, status=status.HTTP_404_NOT_FOUND) 
#         # # if request.method == 'GET': 
#         #     attackeye_serializer = scanSerializer(tutorial) 
#         #     return JsonResponse(attackeye_serializer.data) 
 
#         # if request.method == 'GET':
#         # attackeye = scan.objects.all()
#         # graph_data = JSONParser().parse(request)
#         # x = graph_data["title"]
#         # y = graph_data["description"]
#         # print(x,y)
#         # title = request.query_params.get('title', None)
#         # print(title)
#         # if title is not None:
#         #     attackeye = attackeye.filter(title__icontains=title)
#         #     print("tutorial",attackeye)
        
#         # tutorials_serializer = scanSerializer(attackeye, many=True)
#         # return JsonResponse(tutorials_serializer.data, safe=False)
#         # 'safe=False' for objects serialization
 
#     if request.method == 'POST':
#         graph_data = JSONParser().parse(request)
#         x = graph_data["title"]
#         y = graph_data["description"]
#         global check
#         check=y
#         # tutorial = scan.objects.get(description=y) #not necessary bcoz button will only be pressed if data present
#         # print("yes",tutorial)
        
#         # subprocess.call(['bash','/home/hamza/hamza.sh',str(y)])
#         return JsonResponse({'message': 'Done successfully!'}, status=status.HTTP_201_CREATED) 
#         # z=attackeye_data["published"]
#         # graph_serializer = scanSerializer(data=graph_data)
#         # if graph_serializer.is_valid():
#         #     graph_serializer.save()
#         #     # print(y)
#         #     # amass.delay(str(y))
#         #     subprocess.call(['bash','/home/hamza/hamza.sh',str(y)])
#         #     return JsonResponse(graph_serializer.data, status=status.HTTP_201_CREATED) 
#         # return JsonResponse(graph_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#     # elif request.method == 'DELETE':
#     #     count = scan.objects.all().delete()
#     #     return JsonResponse({'message': '{} Tutorials were deleted successfully!'.format(count[0])}, status=status.HTTP_204_NO_CONTENT)
# @login_required()
# @csrf_exempt

@api_view(["POST","GET"])
def userlogin(request):
    if request.method == 'POST':
        username = request.POST.get('name')
        password= request.POST.get("password")
        user = authenticate(username=username,password=password)
        print(username,password)
        if user is not None :
            authlogin(request, user)
            # user= request.session["_auth_user_id"]
            # request.session['userId'] = user.id
            graph_list=[]
            graph=scan.objects.filter(UserId=user.id)
            print(graph)
            print("*****************************")
            for i in range(len(graph)):
                graph_list.append(graph[i])
            print(graph_list)
            # return render(request,'front.html',{"graph_list":graph_list})
            return render(request,'mainpage.html',{"graph_list":graph_list})
        else:
            return render(request,'login.html')
    elif  request.method == "GET":
        if request.user.is_authenticated:
            print("fffffffffffffffffffffffiiiiiiiiiiiiiiiiiiiiffffffffffffffffffffff")
            user= request.session["_auth_user_id"]
            print("userhamza",user)
            graph_list=[]
            graph=scan.objects.filter(UserId=user)
            print(graph)
            print("*****************************")
            for i in range(len(graph)):
                graph_list.append(graph[i])
            print(graph_list)
            return render(request,'mainpage.html',{"graph_list":graph_list})
        else:
            return render(request,'login.html')

    # graph_data = JSONParser().parse(request)
    # x=graph_data["userName"]
    # y=graph_data["userPassword"]
    # print(x,y)
    # user = authenticate(username='humza', password='hamzahamza')
    # 
    # print(user)
        
@api_view(["GET"])
def graphtable(request):
    if request.method == 'GET':     
        if request.user.is_authenticated:
            user= request.session["_auth_user_id"]
            print("userhamza",user)
            graph_list=[]
            graph=scan.objects.filter(UserId=user).values()
            print(graph)
            return Response({'graph':graph})
         
            for i in range(len(graph)):
                graph_list.append(graph[i])
            print("list",graph_list)
            # return Response(graph)
            # return Response({'received data': request.data})
        # Response({"graph_list":graph_list})    
    else:
        Response({"failed":"true"})   
    #    print("loggedout")


@api_view(["GET"])
def userlogout(request):
    if request.method == 'GET':        
    #    print("loggedout")
       request.session.flush()
       return render(request,'login.html')


@api_view(["POST","GET"])   
def showgraph(request):
    # return render(request,"front.html")
    if request.method=='POST':
        graph= request.GET.get('graph')
        description=request.data["description"]
        print(description)
        print("QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ")
        # global graph
        graph=description
        # return render(request,'login.html')
        # return render (request,"index.html")
        return render(request,'index.html',{"description":graph})
        # print("ddommffffffffffff")
        # return HttpResponse(request,'index.html',{"description":graph})
    # elif method=="GET":
    #     return render(request,"index.html")    

@api_view(["POST","DELETE"])   
def deletedomain(request): 
    if request.method == "POST":
        # description=request.POST.get('mybtn2')
        # print("aaaaaaaaaallllllllllllllllllllllllllllllllllllllllllllaaaaaaaaaaaaaaaaaa")
        # print(request.data)
        description=request.data["description"]
        print("deleting",description)
        user= request.session["_auth_user_id"]
        print(user)
        graphold=scan.objects.filter(id=description)
        print(graphold)
        graphold.delete()
        return Response({'received data': request.data})
        # response = redirect('/home')
        # return response 
        
 
@api_view(["POST"])
def registeruser(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Your account has been created. You can log in now!')    
            return render(request,'login.html')
    else:
        form = UserRegistrationForm()
    context = {'form': form}
    return render(request, 'register.html', context)

@api_view(["POST"])
def nmap(request):
    if request.method=="POST":
        description=request.data["description"]
        graph = open(f'{settings.SITE_ROOT}/DjangoRestApi/attackeye/templates/'+description+'.txt','r')
        content=graph.read()
        lines=content.splitlines()
        print(lines)
        return Response({'received data': lines})
        # for i in content:
        #     subdomains.append(i)
        # print(subdomains)    
        # return render(request, 'nmap.html',{'subdomain':lines})
        

def portinfo(request):
    #   template=Template('My name is {{name}}')
    report = parse_nmap_xml_report('testscan', 'example.com')
    context = {'report': report}
    #   context = Context({'name': 'hamza'})
    #   return render(template.render(context))
    #   return Response({'received data':'ok'})
      
    print(context)
    # hamza(request,context)
    # template = loader.get_template('portsinfo.html')
    # return HttpResponse(template.render(context, request))
    return render(request, 'portsinfo.html', context)

# def hamza(request,context):
#     print("inside")
#     return render(request, 'portsinfo.html', context)