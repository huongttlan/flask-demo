
from flask import Flask, render_template, request, redirect
from flask_bootstrap import Bootstrap
import urllib2
from bs4 import BeautifulSoup
import re
import sys
import pandas

from datetime import datetime
import time
from bokeh.plotting import figure, show, output_file, vplot, hplot

#Function to Just want to take a look at the whole list first
def ticket_dbs():
    ticket_list=pandas.read_csv\
            ("https://s3.amazonaws.com/quandl-static-content/Ticker+CSV%27s/WIKI_tickers.csv",\
            sep=",")
    for i in xrange(ticket_list.shape[0]):
        temp=re.search(r'WIKI/',ticket_list.ix[i,0])
        if temp:
            ticket_list.ix[i,0]=ticket_list.ix[i,0][temp.end():]
    ticket_name=ticket_list.set_index(list(ticket_list.columns.values)[0])\
                [list(ticket_list.columns.values)[1]].to_dict()
    return ticket_name #A dictionary that u have all of the name of the stocks

#Function to read in the web and create data frame
def extract_data(link):
    #Open the data to get the values
        req = urllib2.Request(link)
        response = urllib2.urlopen(req)
        the_page = response.read()
        stocks=BeautifulSoup(the_page,"html.parser")
        colname=stocks.find_all('column-name') 
        #Get the column names to know which one to extract
        
        colname_clean=[]
        for i in xrange(len(colname)):
            colname_clean.append(repr(colname[i].contents))
            if repr(colname[i].contents)=="[u'Date']": date_ix=i
            elif repr(colname[i].contents)=="[u'Close']": close_ix=i
            elif repr(colname[i].contents)=="[u'Adj. Close']": adjclose_ix=i
            elif repr(colname[i].contents)=="[u'Volume']": vol_ix=i

        group=stocks.find_all('datum')
        datelist=[] #list for date
        closelist=[] #list for closing prices
        adjcloselist=[] #list for adjcloselist
        vollist=[] #list for volist
        for i in xrange(len(group)):
            if i%14==0: j=0
            else: j+=1
            if j==date_ix+1: 
                datelist.append(datetime.strptime(repr(group[i].contents)[3:-2],'%Y-%m-%d'))    
            elif j==close_ix+1: 
                closelist.append(float(repr(group[i].contents)[3:-2]))
            elif j==adjclose_ix+1:
                adjcloselist.append(float(repr(group[i].contents)[3:-2]))
            elif j==vol_ix+1:vollist.append(float(repr(group[i].contents)[3:-2]))
    
        df=pandas.DataFrame({'Date':datelist, 'Closing':closelist, 'Adj Closing':adjcloselist\
                   , 'Volume':vollist})

        return df
        
#Function to create graph
def create_grph(lst,df,stock,dbs):
    TOOLS = "pan,wheel_zoom,box_zoom,reset,save"
    
    #Just figure out how to divide the graph to make it nicer
    
    if u'Closing' in lst and u'Adjusted' in lst and u'Volume' in lst:
        output_file("./templates/stock.html", title=dbs[stock])
        a = figure(x_axis_type = "datetime", tools=TOOLS)
        a.line(df['Date'], df['Closing'], color='#1F78B4', legend='Closing Prices')
        a.title = "%s Closing Prices" %(dbs[stock])
        a.grid.grid_line_alpha=0.3
        
        b = figure(x_axis_type = "datetime", tools=TOOLS)
        b.line(df['Date'], df['Adj Closing'], color='#FF0000', legend='Adjusted Closing Prices')
        b.title = "%s Adjusted Closing Prices" %(dbs[stock])
        b.grid.grid_line_alpha=0.3

        c = figure(x_axis_type = "datetime", tools=TOOLS)
        c.line(df['Date'], df['Volume'], color='#228B22', legend='Volumes')
        c.title = "%s Volumes" %(dbs[stock])
        c.grid.grid_line_alpha=0.3 
        p=vplot(hplot(a,b),c)
        show(p)
        return None
        
    elif u'Closing' in lst and u'Adjusted' in lst:
        output_file("./templates/stock.html", title=dbs[stock])
        a = figure(x_axis_type = "datetime", tools=TOOLS)
        a.line(df['Date'], df['Closing'], color='#1F78B4', legend='Closing Prices')
        a.title = "%s Closing Prices" %(dbs[stock])
        a.grid.grid_line_alpha=0.3

        b = figure(x_axis_type = "datetime", tools=TOOLS)
        b.line(df['Date'], df['Adj Closing'], color='#FF0000', legend='Adjusted Closing Prices')
        b.title = "%s Adjusted Closing Prices" %(dbs[stock])
        b.grid.grid_line_alpha=0.3 
        p=hplot(a,b)
        show(p)
        return None
        
    elif u'Closing' in lst and u'Volume' in lst:
        output_file("./templates/stock.html", title=dbs[stock])
        a = figure(x_axis_type = "datetime", tools=TOOLS)
        a.line(df['Date'], df['Closing'], color='#1F78B4', legend='Closing Prices')
        a.title = "%s Closing Prices" %(dbs[stock])
        a.grid.grid_line_alpha=0.3

        c = figure(x_axis_type = "datetime", tools=TOOLS)
        c.line(df['Date'], df['Volume'], color='#228B22', legend='Volumes')
        c.title = "%s Volumes" %(dbs[stock])
        c.grid.grid_line_alpha=0.3 
        p=hplot(a,c)
        show(p)
        return None
        
    elif u'Adjusted' in lst and u'Volume' in lst:
        output_file("./templates/stock.html", title=dbs[stock])
        b = figure(x_axis_type = "datetime", tools=TOOLS)
        b.line(df['Date'], df['Adj Closing'], color='#FF0000', legend='Adjusted Closing Prices')
        b.title = "%s Adjusted Closing Prices" %(dbs[stock])
        b.grid.grid_line_alpha=0.3 

        c = figure(x_axis_type = "datetime", tools=TOOLS)
        c.line(df['Date'], df['Volume'], color='#228B22', legend='Volumes')
        c.title = "%s Volumes" %(dbs[stock])
        c.grid.grid_line_alpha=0.3 
        p=hplot(b,c)
        show(p)
        return None
    
    elif u'Closing' in lst:
        output_file("./templates/stock.html", title=dbs[stock])
        a = figure(x_axis_type = "datetime", tools=TOOLS)
        a.line(df['Date'], df['Closing'], color='#1F78B4', legend='Closing Prices')
        a.title = "%s Closing Prices" %(dbs[stock])
        a.grid.grid_line_alpha=0.3
        show(a)
        return None
        
    elif u'Adjusted' in lst:
        output_file("./templates/stock.html", title=dbs[stock])
        b = figure(x_axis_type = "datetime", tools=TOOLS)
        b.line(df['Date'], df['Adj Closing'], color='#FF0000', legend='Adjusted Closing Prices')
        b.title = "%s Adjusted Closing Prices" %(dbs[stock])
        b.grid.grid_line_alpha=0.3 
        show(b)
        return None
    
    elif u'Volume' in lst:
        output_file("./templates/stock.html", title=dbs[stock])
        c = figure(x_axis_type = "datetime", tools=TOOLS)
        c.line(df['Date'], df['Volume'], color='#228B22', legend='Volumes')
        c.title = "%s Volumes" %(dbs[stock])
        c.grid.grid_line_alpha=0.3 
        show(c)
        return None

app = Flask(__name__)
Bootstrap(app)

#@app.route('/')
#def main():
  #return redirect('/index')

#@app.route('/index',methods=['GET','POST'])
#def index():
  #return render_template('index.html')

#Multiple choice questions
app.questions={}
app.questions['Stock']=('Closing price','Adjusted closing price','Volume')
app.nquestions=len(app.questions)

#Just a dictionary for the name of the stock
ticket_database=ticket_dbs()

@app.route('/index',methods=['GET','POST'])
def index():
    nquestions=app.nquestions
    a1=app.questions['Stock'][0]
    a2=app.questions['Stock'][1]
    a3=app.questions['Stock'][2]
    if request.method == 'GET':
        return render_template('index.html',num=nquestions, ans1=a1,ans2=a2,ans3=a3)
    else:
        #request was a POST
        #Get stock name
        stock_name=request.form['symbol'].upper()
        lst=request.form.getlist('Type')
        
        #Now deal with when no choice is chosen
        
        if stock_name not in ticket_database.keys(): 
            return redirect('/errormsg')
        elif u'Closing' not in lst and u'Adjusted' not in lst and u'Volume' not in lst:
            return redirect('/nochoice')
        else:
            link="https://www.quandl.com/api/v3/datasets/WIKI/" + \
                 stock_name +".xml"
            #Data frame for stock value
            df=extract_data(link)
            #Now create graph
            create_grph(lst,df,stock_name,ticket_database)
            return redirect('/answer')

@app.route('/errormsg') 
def errormsg():
    return render_template('errormsg.html')

@app.route('/nochoice',methods=['GET','POST']) 
def nochoice():
    if request.method == 'GET':
        return render_template('nochoice.html')
    else:
        return redirect('/index')

@app.route('/answer') 
def answer():
    return render_template("stock.html")
    
if __name__ == '__main__':
  #app.run(port=33507)
    app.run(debug=True)

