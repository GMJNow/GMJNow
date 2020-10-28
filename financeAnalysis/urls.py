"""financeAnalysis URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import re_path, path
from django.views.generic import DetailView
from . import views
from .models import StockTicker, StockTickerHistory

app_name = 'financeAnalysis'
urlpatterns = [
    path(r'all/', views.StockTickerListView.as_view(model=StockTicker, template_name="views/allTickers.html"),
         name='stockticker-view'),
    path(r'<str:symbol_id>/', DetailView.as_view(model=StockTickerHistory, template_name="views/finance.html"), name='symbol_id'),
    re_path(r'', views.financeAnalysisDetail.analysis_page, name='analysis_page'),
]
