import urllib2
from bs4 import BeautifulSoup
import re
import sys
import pandas
from datetime import datetime
import time
from bokeh.plotting import figure, show, output_file, vplot, hplot

#Just want to take a look at the whole list first
ticket_list=pandas.read_csv\
            ("https://s3.amazonaws.com/quandl-static-content/Ticker+CSV%27s/WIKI_tickers.csv",\
            sep=",")
for i in xrange(ticket_list.shape[0]):
    temp=re.search(r'WIKI/',ticket_list.ix[i,0])
    if temp:
        ticket_list.ix[i,0]=ticket_list.ix[i,0][temp.end():]
ticket_name=ticket_list.set_index(list(ticket_list.columns.values)[0])[list(ticket_list.columns.values)[1]].to_dict()

##########
            
            
req = urllib2.Request("https://www.quandl.com/api/v3/datasets/WIKI/GOOG.xml")
response = urllib2.urlopen(req)
the_page = response.read()
stocks=BeautifulSoup(the_page,"html.parser")
colname=stocks.find_all('column-name')

colname_clean=[]
for i in xrange(len(colname)):
    colname_clean.append(repr(colname[i].contents))
    if repr(colname[i].contents)=="[u'Date']": date_ix=i
    elif repr(colname[i].contents)=="[u'Close']": close_ix=i
    elif repr(colname[i].contents)=="[u'Adj. Close']": adjclose_ix=i
    elif repr(colname[i].contents)=="[u'Volume']": vol_ix=i
#print "Date", date_ix, "Close", close_ix, "Adjusted Closing", adjclose_ix, "Volume", vol_ix
group=stocks.find_all('datum')
datelist=[]
closelist=[]
adjcloselist=[]
vollist=[]
for i in xrange(len(group)):
    if i%14==0: j=0
    else: j+=1
    if j==date_ix+1: datelist.append(datetime.strptime(repr(group[i].contents)[3:-2],'%Y-%m-%d'))    
    elif j==close_ix+1: closelist.append(float(repr(group[i].contents)[3:-2]))
    elif j==adjclose_ix+1:adjcloselist.append(float(repr(group[i].contents)[3:-2]))
    elif j==vol_ix+1:vollist.append(float(repr(group[i].contents)[3:-2]))

df=pandas.DataFrame({'Date':datelist, 'Closing':closelist, 'Adj Closing':adjcloselist\
                   , 'Volume':vollist})

#print df


#Now is the graph
now = time.time()

TOOLS = "pan,wheel_zoom,box_zoom,reset,save"

output_file("./templates/stock.html", title=ticket_name['GOOG'])

a = figure(x_axis_type = "datetime", tools=TOOLS)
a.line(df['Date'], df['Closing'], color='#1F78B4', legend='Closing Prices')
a.line(df['Date'], df['Adj Closing'], color='#FF0000', legend='Adjusted Closing Prices')
a.title = "%s Prices" %(ticket_name['GOOG'])
a.grid.grid_line_alpha=0.3


b = figure(x_axis_type = "datetime", tools=TOOLS)
b.line(df['Date'], df['Volume'], color='#228B22', legend='Volumes')
b.title = "%s Volumes" %(ticket_name['GOOG'])
b.grid.grid_line_alpha=0.3

show(hplot(a,b))  # open a browser
