from datetime import datetime
from dateutil import tz





def convert_time(current_date):
		here = tz.tzlocal()
		utc = tz.gettz('UTC')
		print utc,type(current_date)
		gmt = current_date.replace(tzinfo=utc)
		return gmt.astimezone(here)
		
	
