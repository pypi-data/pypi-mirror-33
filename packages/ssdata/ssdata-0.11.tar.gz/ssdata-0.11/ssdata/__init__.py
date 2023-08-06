import pandas as pd
import requests
def get_data(**kw):
	secid=kw['secid']
	end_date=kw['end_date']
	start_date=kw['start_date']
	field=kw['field']
	payload={'secid':secid,'start_date':start_date,'end_date':end_date,'field':field}
	r = requests.post('http://118.24.142.78:5678/polls/get_data',data = payload)
	return pd.read_json(r.text,orient='index')


# ~ print(get_data(secid='000001.XSHE',start_date='2017-01-01',end_date='2017-02-01',field='pb'))
