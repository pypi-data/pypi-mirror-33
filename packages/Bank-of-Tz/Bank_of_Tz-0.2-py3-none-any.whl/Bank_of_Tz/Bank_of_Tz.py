'''
This program was made so as to simplify getting data from the
website's page and Intergrate it to your project

By  : Mbonea Godwin Mjema
Year: 2017
'''

from requests import Session as Browser
from bs4 import BeautifulSoup as Parser
import re
import datetime
import pprint
pp = pprint.PrettyPrinter(indent=4)

browser=Browser()
browser.headers=eaders = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

TB={}

class Bank_of_Tz():
    def __init__(self):
    
        '''
    When called the fuction creates a beautifulsoup(parsed html) object of
    the website's main page 
        '''
        raw_html=browser.get('http://www.bot.go.tz/')
        main_page=Parser(raw_html.text,'html.parser')

        self.main_page=main_page

        
    def get_rates(self):
        '''
    Gets exchange rates in the page 
        '''
        rates={}
        table=self.main_page.findAll('table',{ 'width':"214", 'align':"right", 'id':"table47"})[0]('tr')
        for i in range(4,13,2):
                rates[table[i]('td')[1].text.replace(':','')]=[table[i]('td')[2].text.replace('\xa0',''),table[i]('td')[3].text.replace('\xa0','')]
        return rates

    def jsonfy(self,Attribute,Durations):
        
        data={}
        try:
            for T in Durations:
                t={}
                for index in range(len(Attribute)):
                    t[Attribute[index]]=T[index+1]
                if T !=[]:
                    data[T[0].replace("Days","").strip()]=t
        except:
            pass
        return data


    def get_Treasury_bill(self,Auc_number):
        '''
        Returns the Auction Results of a particular Tressury 
        '''
        global browser
        # they changed are now using https not http!!
        url='https://www.bot.go.tz/FinancialMarkets/TBills/TBillsAuctionSummary.asp'
        
        data={
            'TreasuryBillAuctionResults':Auc_number,
            'TBills_Calls_for_Tender_btn':'Go'}
        

        raw_html=browser.post(url,data=data)
        print(raw_html.status_code)
        if str(raw_html.status_code)!='200':
            print('check the Auction number')
            return None        
        
        TBills=Parser(raw_html.text,'html.parser')

        widths=['121','89','68','70']
        #Recorded the widths of the cells but the cell with widths of 70 there is a weird pattern
        Columns=[]
        for width in widths:
            Columns.append(TBills.findAll('td',{'width':width}))

        #Some cleaning was done to the data and we get a list of strings     
        Attributes=[row.text.replace('\n','').replace('\r','').replace('\xa0','').replace('      ','') for row in Columns[0]]
        Days_35 =[row.text.replace('\n','').replace('\r','').replace('\xa0','').replace('      ','') for row in Columns[1]]
        Days_182=[row.text.replace('\n','').replace('\r','').replace('\xa0','').replace('      ','') for row in Columns[2]]

        #this is for that 70
        Days=[row.text.replace('\n','').replace('\r','').replace('\xa0','').replace('      ','') for row in Columns[3]]
        Days364=[]
        Days91=[]
        if '-' in Days:
            Days.remove('-')
        for d in range(0,len(Days),2):
            Days91.append(Days[d])
            Days364.append(Days[d+1])
        
        return self.jsonfy(Attributes,[Days_35,Days_182,Days91,Days364])
        #return(Attributes,Days_35,Days_182,Days91,Days364)
       # return(Days_35[0],Days_35[7],Days_35[8]),(Days91[0],Days91[7],Days91[8]),(Days_182[0],Days_182[7],Days_182[8]),(Days364[0],Days364[7],Days364[8])

    def get_All_bond_prices(self,year):
        url_transaction='https://www.bot.go.tz/FinancialMarkets/FinancialMarkets.asp'
        raw_html=browser.get(url_transaction)
        data_raw=Parser(raw_html.text,'html.parser').findAll('select',
                                                             {'name':"TreasuryBondAuctionResults"})[0]('option')

        two_years,five_years,seven_years,ten_years,fifteen_years=[
						   [info.attrs['value'] for info in data_raw if '2 years' in info.text],
                                                   [info.attrs['value'] for info in data_raw if '5 years' in info.text],
                                                   [info.attrs['value'] for info in data_raw if '7 years' in info.text],
                                                   [info.attrs['value'] for info in data_raw if '10 years' in info.text],
                                                   [info.attrs['value'] for info in data_raw if '15 years' in info.text]]
        if year == '2':
           Year=two_years
        elif year == '5':
            Year=five_years
        elif year == '7':
            Year=seven_years
        elif year == '10':
            Year=ten_years
        elif year == '15':
            Year=fifteen_years
        
        Result=[]
        for auction in Year:
            

            data={'TreasuryBondAuctionResults':auction,
            'TBonds_2_Year_btn':'Go'}
            
            url='https://www.bot.go.tz/FinancialMarkets/TBonds/TBondsAuctionSummary.asp'
            res=browser.post(url,data=data)
            soup=Parser(res.text,'html.parser')
            print(res.status_code)
            try:
                date=re.search(r'(\d+/\w+/\d\d\d\d+)',soup.find('font', {'face':"Verdana,arial"}).text).group()
                date=datetime.datetime.strptime(date, '%d/%b/%Y').date().strftime('%d-%b-%Y')
                lowest_bid=soup.findAll('td',{'width':'89'})[5].text.strip()
            except:
                print('missed: '+auction)
                continue
            lowest_bid = float(lowest_bid)
            if lowest_bid == 0.00:
                continue
            print('Processed: '+auction)
            Result.append((lowest_bid,date))
        print('the result',Result)

        Result.reverse()
        return Result

    
    
        

    def get_Tbils(self,number_of_results):
        global browser
   
       ## browser.headers['origin']=" https://www.bot.go.tz"
       ## browser.headers['Cookie']=" ASPSESSIONIDCUBSCTSB=CGIFEPJBOJIOFIPBMIHFGDEP"
        url_transaction='http://www.bot.go.tz/FinancialMarkets/FinancialMarkets.asp'
        raw_html=browser.get(url_transaction)
        data_raw=Parser(raw_html.text,'html.parser').findAll('select',
                                                             {'name':"TreasuryBillAuctionResults"})[0]('option')
        if number_of_results is 0 :
            auctions=[auc.attrs['value'] for auc in data_raw]
        else :
            auctions=list(self.stop() if data_raw.index(auc) == number_of_results else auc.attrs['value'] for auc in data_raw)
            print(auctions)
        
        result={auc:self.get_Treasury_bill(auc) for auc in auctions}
        
        return result

    def stop(self):
        raise StopIteration
        

    
