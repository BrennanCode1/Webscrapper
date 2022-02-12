from importlib.machinery import WindowsRegistryFinder
from operator import truediv
from django.shortcuts import render
from django.http import HttpResponse
import requests


from requests_html import HTMLSession
from .models import Bookinfo
   
from django.shortcuts import render, redirect, get_object_or_404
from GG.forms import BookForm
from django_tables2 import SingleTableView, RequestConfig
from GG.tables import BookinfoTable

from types import SimpleNamespace   

# Create your views here.
def index(request):
    return render(request, "GG/index.html")


def webscrapper(link):

    #create dict and call for website
    book=dict()
    session = HTMLSession()
    r = session.get(link)
    iSBN=0
    Publisher=0
    PublicationDate=0
    Series=0
    EditionDescription=0
    Pages=0
    SalesRank=0
    
    
    isbn =r.html.find('#ProductDetailsTab', first=True )
    #key
    
    prevKey='0'
    skip=False
    for line in isbn.text.split('\n'):
        skip=False
        if line == 'Product Details':
            book[line] = [line]
            skip=True
            #skip to not name everything product details since we dont need this field if were already grabbing the css tab
        if skip ==False:
            if prevKey in book:
                #append value to the key created
                book[prevKey].append(line)
            else:
                #create key
                book[line] = [line]
            #assign the key
            prevKey=line
    #### seperate width length depth
    x=book['Product dimensions:'][1]
    for item in x.split(' '):
        if 'w' in item:
            width=item 
        if 'h' in item:
            length=item
        if 'd' in item:
            depth=item
    #Assigning to db using django
    productinfolist=('ISBN-13:','Publisher:','Publication date:','Series:','Edition description:','Pages:','Sales rank:')
    for item in productinfolist:
        if item in book:
            if 'ISBN-13:' == item:
                iSBN=book[item][1]
            if 'Publisher:' == item:
                Publisher=book[item][1]
            if 'Publication date:' == item:
                PublicationDate=book[item][1]
            if 'Series:' == item:
                Series=book[item][1]
            if 'Edition description:' == item:
                EditionDescription=book[item][1]
            if 'Pages:' == item:
                Pages=book[item][1]
            if 'Sales rank:' == item:
                SalesRank=book[item][1]
           

            
 
    Price=r.html.search('salePrice\" value=\"{}\"')[0]
    
    Bookinfo.objects.create(ISBN13=iSBN,
        Publisher=Publisher,
        PublicationDate=PublicationDate,
        Series=Series,
        EditionDescription=EditionDescription,
        Pages=Pages,
        SalesRank=SalesRank,
        ProductWidth=width,
        ProductHeight=length,
        ProductDepth=depth,
        Price=Price,
        LinkCalled=link
        )
    print(book)





def WebscrapperLinks(request):
    form = BookForm()
    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            LinkCalled = form.cleaned_data["LinkCalled"]
            webscrapper(LinkCalled)
            queryset = Bookinfo.objects.all()
            table = BookinfoTable(queryset)
            payload = {"table": table}

            return render(request, "GG/BookinfoTable.html", payload)
            

               
        else:
            print("Error Form invalid")
    return render(request, "GG/forms_page10.html", {"form": form})

