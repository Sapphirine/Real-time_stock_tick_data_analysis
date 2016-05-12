from kafka import KafkaProducer
from time import sleep
from bs4 import BeautifulSoup
import urllib, time, os, re, csv,json,time,thread,datetime
import mysql.connector as mariadb

#stocks = ['BAC', 'C', 'IBM', 'AAPL', 'GE', 'T', 'MCD', 'NKE', 'TWTR', 'TSLA','FTAG', 'DAIO', 'CNSL', 'MENT', 'FV', 'SGYP', 'TTEK', 'PANL', 'KMDA', 'PME', 'IIVI', 'FRME', 'ISNS', 'DTEA', 'DISCB', 'LMFA', 'IXYS', 'SMMF', 'TUBE', 'NVET', 'VOXX', 'BVSN', 'SCYX', 'NFEC', 'EXPO', 'BKEP', 'KRNY', 'HLG', 'SSYS', 'BIOC', 'LITE', 'SLMBP', 'NMRX', 'AAXJ', 'STKS', 'UTHR', 'PACW', 'ICFI', 'LOB', 'SKUL', 'DXCM', 'CZNC', 'TWMC', 'RKDA', 'MCEP', 'PSMT', 'ACTX', 'ULTR', 'ARWA', 'SIGI', 'SALM', 'HALL', 'NRCIA', 'MYOS', 'SNFCA', 'SBRA', 'SGEN', 'PLAY', 'FORR', 'GRMN', 'WFD', 'RBCAA', 'PTI', 'IBTX', 'GIGA', 'CYNO', 'CIFC', 'EFII', 'SINA', 'AEGR', 'DTUL', 'RRM', 'MDXG', 'ESSA', 'BNCL', 'CTBI', 'FUEL', 'BYLK', 'GPAC', 'CCRC', 'IDXX', 'BLRX', 'MEOH', 'JKHY', 'MYRG', 'GGACU', 'AMAG', 'ECPG', 'EXXI', 'AZPN', 'LJPC', 'SPIL', 'CNLMU', 'IMGN', 'ZIV', 'BLDP', 'UPLD', 'CNFR', 'LBRDK', 'PXS', 'SNCR', 'JOUT', 'GENE', 'RDWR', 'BIOL', 'PLXS', 'SAUC', 'AMAT', 'UVSP', 'ROVI', 'RLYP', 'LOXO', 'ERII', 'EPRS', 'HAIN', 'ACOR', 'RESN', 'SCZ', 'SHPG', 'DORM', 'LDRH', 'PSCF', 'SNPS', 'KZ', 'MYOK', 'AMSC', 'NEWP', 'LOGM', 'GPRO', 'GPOR', 'FEIM', 'PRSS', 'LWAY', 'UCTT', 'USAP', 'IFGL', 'HART', 'TROV', 'IDXG', 'UPIP', 'FONE', 'TRST', 'DHRM', 'STLD', 'BRID', 'CFGE', 'SOFO', 'IESC', 'TFSL', 'TNGO', 'CARZ', 'QLC', 'LGCYO', 'ESPR', 'BWEN', 'THRM', 'WEYS', 'SCSS', 'LCUT', 'UBOH', 'TRMB', 'MLVF', 'IEP', 'VBLT', 'CTXS', 'WATT', 'IRDM', 'NTCT', 'KITE', 'ENT', 'RGNX', 'USEG', 'SMMT', 'DDAY', 'TINY', 'NAKD', 'SAGE', 'FULL', 'CRNT', 'FEMB', 'ASML', 'BOBE', 'LAND', 'PLPM', 'SSNC', 'VASC', 'EXFO', 'KERX', 'IPCI', 'GLRI']
stocks = ['BAC', 'C', 'IBM', 'AAPL', 'GE', 'T', 'MCD', 'NKE', 'TWTR', 'TSLA']
#stocks = ['AAPL','TSLA']

def create_tables():
	mariadb_connection = mariadb.connect(host='52.34.22.14',port=3306,user='root', password='final_project',database='historical_stock')
	cursor = mariadb_connection.cursor()
	for ind in range(0,len(stocks)):
		cmd_str = "CREATE TABLE IF NOT EXISTS %s (UNICODE varchar(10),PRICE float,PRIMARY KEY (UNICODE))" % (stocks[ind])
		cursor.execute(cmd_str)
	mariadb_connection.commit()
	mariadb_connection.close()
#cmd_str = "CREATE TABLE IF NOT EXISTS STOCKS (TICKER varchar(5),PRIMARY KEY (TICKER))"
def stock_quote(stock):
	url = 'http://www.nasdaq.com/symbol/'+stock+'/real-time'
	html = urllib.urlopen(url)
	soup = BeautifulSoup(html,"html.parser")
	divs = soup.findAll('div',class_="qwidget-dollar",id = "qwidget_lastsale")
	time = soup.findAll('span',id = "qwidget_markettime")
	try:
		price = divs[0].get_text().replace('$','')
		time = time[0].get_text().encode('utf-8')
		#return time+':'+price+'\n'
		return (time,price)
	except:
		return "Error time\n"

def str2unixtime(tmstr):
	d = datetime.datetime.strptime(tmstr, "%m/%d/%Y %I:%M:%S %p")
	unixtime = time.mktime(d.timetuple())
	return str(int(unixtime))

def thread_starter(ind):
	mariadb_connection = mariadb.connect(host='52.34.22.14',port=3306,user='root', password='final_project',database='historical_stock')
	time_ = 0
	producer = KafkaProducer(bootstrap_servers='172.31.10.74:9092')
	sleep(2) 
	#to wait for kafka connection established
	#f = open('data/'+stocks[ind],'w+')
	cursor = mariadb_connection.cursor()
	prev_price = ''
	dif_cnt = 0
	while time_<5000:
		time_ = time_ + 1
		res = stock_quote(stocks[ind])
		if prev_price!=res[1]:
			try:
				uni_str = str2unixtime(res[0])
				producer.send('test', str(stocks[ind]+":"+uni_str+":"+res[1]))
				cmd_str = "INSERT INTO %s (UNICODE,PRICE) VALUES (%s,%s)" % (stocks[ind],uni_str,res[1])
				cursor.execute(cmd_str)
				prev_price = res[1]
				dif_cnt = dif_cnt + 1
				if dif_cnt==10:
					mariadb_connection.commit()
					dif_cnt = 0
			except:
				pass
			#f.write(res_str)
		time.sleep(2)
	mariadb_connection.close()
	#f.close()

# for i in range(0,len(stocks)):
# 	thread.start_new_thread(thread_starter,(i,))

# # for i in range(0,len(stocks)):
# # 	stock_quote(stocks[i])

# while 1:
# 	pass
thread_starter(9)


