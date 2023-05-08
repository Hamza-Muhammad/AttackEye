from django.urls import re_path
from django.urls import path
from apps.core import views
from apps.nmap.views import port_info, nmap_report, generate_nmap_xml_report, portscan, porttable, deleteport
from django.contrib import admin

urlpatterns = [
    path("", views.userlogin, name="login_user"),
    re_path(r'^api/view/subdomain$', views.subdomainpage),
    re_path(r'register',views.registeruser, name='register'),
    # re_path(r'^register$',views.registeruser, name='register_user'),
    re_path(r'^front$', views.front),
    re_path(r'^mainpage$', views.mainpage),
    re_path(r'login', views.login, name='login'),
    re_path(r'^api/graphtable$', views.graphtable),
    re_path(r'logout', views.userlogout, name='logoutbtn'),
    # re_path(r'^api/showgraph/(?P<description>[a-z].+)', views.showgraph,name='showgraph'),
    re_path(r'^api/showgraph', views.showgraph,name='showgraph'),
    # re_path(r'^api/deletedomain/(?P<description>[a-z].+)', views.deletedomain,name='deletedomain'),
    re_path(r'^api/deletedomain',views.deletedomain,name="deletedomain"),
    re_path(r'^surface/(?P<value>[a-z].+)', views.surface,name='surface'),
    re_path(r'^api/attackeye$', views.attackeye_list,name='attackeye_list'),
    re_path(r'^api/load/graph/(?P<graphdomain>[a-z].+)', views.graph_json),
    # re_path(r'^api/load/graph$', views.graph_json),
    # re_path(r'^api/load/graph_list$', views.graph_list,name="graphlist"),
    # re_path(r'^api/load/graph_list$', views.graph_list,name="graphlist"),
    # re_path(r'^api/download/csv$', views.download_csv),
    re_path(r'^api/download/csv/([a-z].+)$', views.download_csv),
    re_path(r'^api/attackeye/(?P<pk>[0-9]+)$', views.attackeye_detail),
    re_path(r'^api/attackeye/published$', views.attackeye_list_published),
    re_path(r'^api/view/table$', views.table_view),

    # re_path(r'^index/nmap$', views.nmap,name='nmap'),
    # re_path(r'^api/viewreport',views.deletedomain,name="deletedomain"),
    re_path(r'^api/nmapreport/(?P<value>[a-z].+)', nmap_report, name='nmapreport'),
    re_path(r'^api/portinfo/(?P<value1>[a-z].+)/(?P<value2>[A-Za-z0-9].+)', port_info, name='portinfo'),
    re_path(r'^api/generatenmapxmlreport', generate_nmap_xml_report, name='generatenmapxmlreport'),
    re_path(r'^portscan', portscan, name='portscan'),
    re_path(r'^api/porttable$', porttable, name='porttable'),
    re_path(r'^api/deleteport$', deleteport, name='deleteport'),
]


