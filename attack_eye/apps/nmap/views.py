from django.shortcuts import render
from django.conf import settings
from .nmap import parse_nmap_xml_report, generate_xml_report
from rest_framework.decorators import api_view
from rest_framework.response import Response
from nmap.models import port_scan
# from celery import Celery
import tldextract
import validators
import requests


@api_view(["GET"])
def nmap_report(request, value):
    if request.method == "GET":
        graph = open(f'{settings.SITE_ROOT}/attack_eye/apps/amass/generated_subdomains/'+value+'.txt', 'r')
        content = graph.read()
        enumerated_subdomains = content.splitlines()
        return render(request, 'nmap_report.html', {'filename': value, 'enumerated_subdomains': enumerated_subdomains})

@api_view(["GET", "POST"])
def portscan(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            user = request.session["_auth_user_id"]
            graph_list = []
            graph = port_scan.objects.filter(UserId=user)

            return render(
                request, "main_nmap.html", {"graph_list": graph, "userLoggedIn": True}
            )
        else:
            return render(
                request, "main_nmap.html", {"graph_list": [], "userLoggedIn": False}
            )
        
    elif request.method == "POST":
        domain = request.data["domain"]

        # extSubdomain = tldextract.extract(domain).subdomain
        # extDomain = (
        #     tldextract.extract(domain).domain + "." + tldextract.extract(domain).suffix
        # )

        isValidDomain = validators.domain(domain)

        try:
            domainStatusCode = requests.get(
                f"http://{domain}", headers={"User-Agent": "Mozilla/5.0"}
            ).status_code
        except requests.exceptions.ConnectionError as e:
            print(e)
            domainStatusCode = 0

        print(domainStatusCode)
        # if extSubdomain != "":
        #     return Response(
        #         {
        #             "message": "Subdomains are not allowed",
        #             "domain": domain,
        #             "messageDescription": f"A subdomain cannot be scanned. You can only proceed with scanning the organization domain ({domain})",
        #             "error": 405,
        #         }
        #     )
        if isValidDomain and (
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
            domainbyuser = port_scan.objects.filter(UserId=user, domain=domain)
            domainfromdb = port_scan.objects.filter(domain=domain)
            # if domain exists
            if domainbyuser:
                domainbyuser.delete()
            # if domain exists for the current user
            elif domainfromdb and len(domainbyuser) == 0:
                print('running 1')
                timeDateEnd = domainfromdb.values("timeDateEnd")[0]["timeDateEnd"]
                timeDateStart = domainfromdb.values("timeDateStart")[0]["timeDateStart"]
                port_scan.objects.create(UserId=user, domain=domain, pending=1)
                port_scan.objects.filter(UserId=user, domain=domain).update(
                    timeDateStart=timeDateStart, timeDateEnd=timeDateEnd
                )
                return Response({"requestData": request.data, "domain": domain})

            attackeye = port_scan.objects.create(UserId=user, domain=domain, pending=0)

            # amass.delay(str(extDomain), str(user))
            print('running 2')
            return Response({"response": request.data})
        else:
            print("empty")
            print(isValidDomain)
            return Response(
                {
                    "message": "Invalid Domain",
                    "domain": domain,
                    "messageDescription": "Your input cannot be scanned at this moment.",
                    "error": 500,
                }
            )
        
@api_view(["GET"])
def graph_table(request):
    print('i am running')
    if request.method == "GET":
        print('hello')
        if request.user.is_authenticated:
            user = request.session["_auth_user_id"]
            graph_list = []
            graph = port_scan.objects.filter(UserId=user).values()
            print(graph)
            return Response({"graph": graph})
    else:
        Response({"failed": "true"})


def port_info(request, value1, value2):
    report = parse_nmap_xml_report(value1, value2)
    context = {'report': report}
    return render(request, 'portsinfo.html', context)

@api_view(["POST"])
def generate_nmap_xml_report(request):
    if request.method == "POST":
        domain = request.data["domain"]
        generate_xml_report(domain)
        return Response()
