"""ptt_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from home.views import home
from id_query.views import query
from id_query.views import show
from id_query.views import node_info
from id_query.views import link_info
from id_query.views import common_token
from keywords.views import keywords
from keywords.views import setDateInterval
from keywords.views import setDateInterval_CNT
from keywords.views import setDateInterval_CPT
from keywords.views import setDateInterval_NLT


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'home', home, name = 'home'),
    url(r'query', query, name = 'query'),
    url(r'show', show, name = 'show'),
    url(r'node_info', node_info, name = 'node_info'),
    url(r'link_info', link_info, name = 'link_info'),
    url(r'common_token', common_token, name = 'common_token'),
    url(r'keywords', keywords, name = 'keywords'),
    url(r'setDateInterval_CNT', setDateInterval_CNT, name = 'setDateInterval_CNT'),
    url(r'setDateInterval_CPT', setDateInterval_CPT, name = 'setDateInterval_CPT'),
    url(r'setDateInterval_NLT', setDateInterval_NLT, name = 'setDateInterval_NLT'),
    url(r'setDateInterval', setDateInterval, name = 'setDateInterval'),
]
