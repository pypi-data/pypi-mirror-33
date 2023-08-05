import pandas as pd
import matplotlib.pyplot as plt
import requests
import json
import urllib

def call_api(ticker, from_date, to_date):
    url_call = 'http://michelaa.pythonanywhere.com/stockdatareaderapi/'+ticker.upper()+'/'+from_date+'/'+to_date+'/'
    r = requests.get(url_call)
    rr = json.loads(r.content)
    return rr

def  datareader_doc():
    """ function to return the string 'my first package' """
    return("IE GMBD 2017 Group A first package that anyone can install it! The purpose of the package is to read the technology stock prices between 2 dates")
