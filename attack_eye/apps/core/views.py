# from django.template import loader
# from django.template.loader import get_template
from django.template import Template, Context
from ..Celery.tasks import amass
from ..nmap.nmap import parse_nmap_xml_report
from django.shortcuts import render, redirect
import json
from rest_framework.decorators import parser_classes
import validators
import requests
import tldextract
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from rest_framework.response import Response
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
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
from core.models import scan

# from attackeye.models import Domain
from core.serializers import scanSerializer
from rest_framework.decorators import api_view
# from celery import Celery
import subprocess
# from .tasks import amass
from django.http import FileResponse
from django.contrib import messages
import logging
from django.contrib.auth.decorators import login_required


@login_required
def surface(request, value):
    return render(request, 'surface.html', {'nmap_report_file_name': value})


# logging.basicConfig(filename='/tmp/example.log', encoding='utf-8', level=logging.DEBUG)


# @login_required
def front(request):
    if request.user.is_authenticated:
        return render(request, "front.html")
    else:
        return render(request, "login.html")


# @login_required
def login(request):
    return render(request, "login.html")


@api_view(["GET"])
def subdomainpage(request):
    return render(request, "nmap.html")


@login_required
def mainpage(request):
    graph_list = []
    graph = scan.objects.filter(UserId=user.id)
    print(graph)
    print("*****************************")
    for i in range(len(graph)):
        graph_list.append(graph[i])
    print(graph_list)

    return render(request, "mainpage.html", {"graph_list": graph_list})


# logging.basicConfig(filename='/tmp/example.log', encoding='utf-8', level=logging.DEBUG)


@api_view(["POST", "GET"])
def userlogin(request):
    if request.method == "POST":
        username = request.POST.get("name")
        password = request.POST.get("password")
        user = authenticate(username=username, password=password)
        print(username, password)

        if user is not None:
            auth_login(request, user)
            # return render(request,'front.html',{"graph_list":graph_list})
            return redirect("/")
        else:
            return render(request, "login.html")

    elif request.method == "GET":
        if request.user.is_authenticated:
            user = request.session["_auth_user_id"]
            graph_list = []
            graph = scan.objects.filter(UserId=user)

            return render(
                request, "mainpage.html", {"graph_list": graph, "userLoggedIn": True}
            )
        else:
            return render(
                request, "mainpage.html", {"graph_list": [], "userLoggedIn": False}
            )


@api_view(["GET"])
def graph_json(request, graphdomain):
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
    graph = open(
        f"{settings.SITE_ROOT}/attack_eye/apps/amass/generated_subdomains/"
        + graphdomain,
        "rb",
    )
    # graph = open('/home/hamza/django-rest-api/django-rest-api-master/DjangoRestApi/attackeye/templates/data.json','rb')
    print(graph)
    response = FileResponse(graph)
    print(response)
    # return render(request,'index.html',response)
    return response


@api_view(["GET"])
def table_view(request):
    return render(request, "webdatarocks.html")


# "http://localhost:8080/api/download/csv
@api_view(["GET"])
def download_csv(request, graphname):
    # attackeye = scan.objects.last()
    # logging.info(attackeye.description)
    # domain = attackeye.description
    # logging.info(str(domain))
    # print("hamza", graphname)
    subprocess.call(
        [
            "bash",
            f"{settings.SITE_ROOT}/attack_eye/apps/amass/scripts/SubDomainDownload.sh",
            graphname,
        ]
    )
    print(
        f"{settings.SITE_ROOT}/attack_eye/apps/amass/scripts/SubDomainDownload.sh",
        " ++ ",
        graphname,
    )
    # img = open(f'{settings.SITE_ROOT}/go/pkg/mod/pkg/mod/github.com/OWASP/Amass/v3/cmd/amass/amass_maltego.csv', 'rb')
    img = open(f"{settings.SITE_ROOT}/amass_output/amass_maltego.csv", "rb")

    response = FileResponse(img)
    return response


@parser_classes([JSONParser])
@api_view(["GET", "POST", "DELETE"])
def attackeye_list(request):
    if request.method == "GET":
        attackeye = scan.objects.all()

        title = request.query_params.get("title", None)
        if title is not None:
            attackeye = attackeye.filter(title__icontains=title)

        attackeye_serializer = scanSerializer(attackeye, many=True)
        return JsonResponse(attackeye_serializer.data, safe=False)
        # 'safe=False' for objects serialization

    elif request.method == "POST":
        domain = request.data["domain"]
       
        

        extSubdomain = tldextract.extract(domain).subdomain
        extDomain = (
            tldextract.extract(domain).domain + "." + tldextract.extract(domain).suffix
        )

        isValidDomain = validators.domain(extDomain)
        
        
        try:
            domainStatusCode = requests.get(
                f"http://{extDomain}", headers={"User-Agent": "Mozilla/5.0"}
            ).status_code
        except requests.exceptions.ConnectionError as e:
            print(e)
            domainStatusCode = 0

        print(domainStatusCode)
        if extSubdomain != "":
            return Response(
                {
                    "message": "Subdomains are not allowed",
                    "domain": extDomain,
                    "messageDescription": f"A subdomain cannot be scanned. You can only proceed with scanning the organization domain ({extDomain})",
                    "error": 405,
                }
            )
        elif isValidDomain and (
            (
                domainStatusCode == 200
                or domainStatusCode == 201
                or domainStatusCode == 202  # Created
                or domainStatusCode == 401  # Accepted
                or domainStatusCode == 404  # Unauthorized
                or domainStatusCode == 406  # Not Found
                or domainStatusCode == 302  # Not Acceptable
                or domainStatusCode == 300  # Redirect
                or domainStatusCode == 301  # Multiple Choice
                or domainStatusCode == 303  # Moved Permanently
                or domainStatusCode == 304  # See Other
                or domainStatusCode == 305  # Not Modified
                or domainStatusCode == 306  # Use Proxy
                or domainStatusCode == 307  # unused
                or domainStatusCode == 308  # Temporary Redirect
                or domainStatusCode == 403  # Permanent Redirect
            )
            and (  # Forbidden
                domainStatusCode != 500
                or domainStatusCode != 501  # Internal Server Error
                or domainStatusCode != 502  # Not Implemented
                or domainStatusCode != 503  # Bad Gateway
                or domainStatusCode != 504  # Service Unavailable
                or domainStatusCode != 505  # Gateway Timeout
                or domainStatusCode != 506  # HTTP Version Not Supported
                or domainStatusCode != 507  # Variant Also Negotiates
                or domainStatusCode != 508  # Insufficient Storage (WebDAV)
                or domainStatusCode != 510  # Loop Detected (WebDAV)
                or domainStatusCode != 511  # Not Extended
            )
        ):  # Network Authentication Required
            print(isValidDomain, domain, "done")
            user = request.session["_auth_user_id"]
            domainbyuser = scan.objects.filter(UserId=user, domain=extDomain)
            domainfromdb = scan.objects.filter(domain=extDomain)
            # if domain exists
            if domainbyuser:
                domainbyuser.delete()
            # if domain exists for the current user
            elif domainfromdb and len(domainbyuser) == 0:
                timeDateEnd = domainfromdb.values("timeDateEnd")[0]["timeDateEnd"]
                timeDateStart = domainfromdb.values("timeDateStart")[0]["timeDateStart"]
                scan.objects.create(UserId=user, domain=extDomain, pending=1)
                scan.objects.filter(UserId=user, domain=extDomain).update(
                    timeDateStart=timeDateStart, timeDateEnd=timeDateEnd
                )
                return Response({"requestData": request.data, "domain": extDomain})

            attackeye = scan.objects.create(UserId=user, domain=extDomain, pending=0)
<<<<<<< HEAD
            
            amass.delay(str(extDomain), str(user))
=======

            # amass.delay(str(extDomain), str(user))
>>>>>>> fe96b6f0bef9428c6e2583b96172d8160b1bb5cf

            return Response({"response": request.data})
        else:
            print("empty")
            print(isValidDomain)
            return Response(
                {
                    "message": "Invalid Domain",
                    "domain": extDomain,
                    "messageDescription": "Your input cannot be scanned at this moment.",
                    "error": 500,
                }
            )

    elif request.method == "DELETE":
        count = scan.objects.all().delete()
        return JsonResponse(
            {"message": "{} Scans were deleted successfully!".format(count[0])},
            status=status.HTTP_204_NO_CONTENT,
        )


@api_view(["GET", "PUT", "DELETE"])
def attackeye_detail(request, pk):
    try:
        tutorial = scan.objects.get(pk=pk)
    except scan.DoesNotExist:
        return JsonResponse(
            {"message": "The tutorial does not exist"}, status=status.HTTP_404_NOT_FOUND
        )

    if request.method == "GET":
        attackeye_serializer = scanSerializer(tutorial)
        return JsonResponse(attackeye_serializer.data)

    elif request.method == "PUT":
        attackeye_data = JSONParser().parse(request)
        attackeye_serializer = scanSerializer(tutorial, data=attackeye_data)
        if attackeye_serializer.is_valid():
            attackeye_serializer.save()
            return JsonResponse(attackeye_serializer.data)
        return JsonResponse(
            attackeye_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )

    elif request.method == "DELETE":
        tutorial.delete()
        return JsonResponse(
            {"message": "scan was deleted successfully!"},
            status=status.HTTP_204_NO_CONTENT,
        )


@api_view(["GET"])
def attackeye_list_published(request):
    attackeye = scan.objects.filter(published=True)

    if request.method == "GET":
        tutorials_serializer = scanSerializer(attackeye, many=True)
        return JsonResponse(tutorials_serializer.data, safe=False)


@api_view(["GET"])
def graphtable(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            user = request.session["_auth_user_id"]
            # print("userhamza",user)
            graph_list = []
            graph = scan.objects.filter(UserId=user).values()
            # print(graph)
            return Response({"graph": graph})

            # for i in range(len(graph)):
            #     graph_list.append(graph[i])
            # print("list",graph_list)
            # return Response(graph)
            # return Response({'received data': request.data})
        # Response({"graph_list":graph_list})
    else:
        Response({"failed": "true"})
    # print("loggedout")


@api_view(["GET"])
def userlogout(request):
    if request.method == "GET":
        request.session.flush()
        return render(request, "mainpage.html")


@api_view(["POST", "GET"])
def showgraph(request):
    # return render(request,"front.html")
    if request.method == "POST":
        graph = request.GET.get("graph")
        domain = request.data["domain"]
        print(domain)
        print("QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ")
        # global graph
        graph = domain
        # return render(request,'login.html')
        # return render (request,"index.html")
        return render(request, "index.html", {"domain": graph})
        # print("ddommffffffffffff")
        # return HttpResponse(request,'index.html',{"description":graph})
    # elif method=="GET":
    #     return render(request,"index.html")


@api_view(["POST", "DELETE"])
def deletedomain(request):
    if request.method == "POST":
        # description=request.POST.get('mybtn2')
        # print("aaaaaaaaaallllllllllllllllllllllllllllllllllllllllllllaaaaaaaaaaaaaaaaaa")
        # print(request.data)
        domain = request.data["domain"]
        print("deleting", domain)
        user = request.session["_auth_user_id"]
        print(user)
        graphold = scan.objects.filter(id=domain)
        print(graphold)
        graphold.delete()
        return Response({"received data": request.data})
        # response = redirect('/home')
        # return response


@api_view(["POST", "GET"])
def registeruser(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"Your account has been created. You can log in now!"
            )
            return render(request, "login.html")
    else:
        form = UserRegistrationForm()
    context = {"form": form}
    return render(request, "register.html", context)


# @api_view(["POST"])
# def nmap(request):
#     if request.method == "POST":
#         domain = request.data["domain"]
#         graph = open(
#             f"{settings.SITE_ROOT}/attack_eye/apps/core/templates/" + domain + ".txt",
#             "r",
#         )
#         content = graph.read()
#         lines = content.splitlines()
#         print(lines)
#         return Response({"received data": lines})
#         # for i in content:
#         #     subdomains.append(i)
#         # print(subdomains)
#         # return render(request, 'nmap.html',{'subdomain':lines})


# def portinfo(request):
#     #   template=Template('My name is {{name}}')
#     report = parse_nmap_xml_report("testscan", "example.com")
#     context = {"report": report}
#     #   context = Context({'name': 'hamza'})
#     #   return render(template.render(context))
#     #   return Response({'received data':'ok'})

#     print(context)
#     # hamza(request,context)
#     # template = loader.get_template('portsinfo.html')
#     # return HttpResponse(template.render(context, request))
#     return render(request, "portsinfo.html", context)


# # def hamza(request,context):
# #     print("inside")
# #     return render(request, 'portsinfo.html', context)
