import zipfile, os, json, arcpy
import timer_class as tc

try:
	import urllib2  # Python 2
except ImportError:
	import urllib.request as urllib2  # Python 3

apikey = arcpy.GetParameterAsText(0) 
inputfile = arcpy.GetParameterAsText(1)
org_id = arcpy.GetParameterAsText(2)
org_name = arcpy.GetParameterAsText(3)
dest_id = arcpy.GetParameterAsText(4)
dest_name = arcpy.GetParameterAsText(5)
outputfile = arcpy.GetParameterAsText(6)

'''
apikey = ''
inputfile = r"D:\Code\HSABook\Chapter2\Large_ZIP-to-ZIP_OD\Test\ZIP_Points.gdb\OD_Google_Test"
org_id = 'Patient_ZipCode'
org_name = 'oaddr1'
dest_id = 'Hosp_ZipCode'
dest_name ='daddr1' 
outputfile = 'D:\Code\HSABook\Chapter2\Large_ZIP-to-ZIP_OD\Test\OD_Google_Test3.csv'
'''

def fetch_google_OD (download_link):
	nt_time=''
	nt_dist=''
	try:
		download_link = basestring.format(org_add, dest_add, apikey)
		req = urllib2.urlopen(download_link)
		jsonout = json.loads(req.read())
		#nt_time = jsonout['rows'][0]['elements'][0]['duration']['text']
		#nt_dist = jsonout['rows'][0]['elements'][0]['distance']['text']
		nt_time = jsonout['rows'][0]['elements'][0]['duration']['value'] #meters
		nt_dist = jsonout['rows'][0]['elements'][0]['distance']['value'] #seconds

		# transform seconds to minutes and meters to miles
		nt_time = round(nt_time / 60, 2)
		nt_dist = round(nt_dist * 0.000621371 , 2)
	except Exception:
		arcpy.AddMessage("The request link is invalid!")  
	return [nt_time, nt_dist]
	
	
basestring = 'https://maps.googleapis.com/maps/api/distancematrix/json?language=en&units=imperial&origins={0}&destinations={1}&key={2}'


sc = arcpy.SearchCursor(inputfile)	
f = open(outputfile, 'w')
f.write('{0}, {1}, Time_min, Dist_mi\n'.format(org_id, dest_id))

totaln = int(str(arcpy.GetCount_management(inputfile)))
i = 0
watch = tc.timer()
row = sc.next()
while row:
	org_add = row.getValue(org_name)
	dest_add = row.getValue(dest_name)
	if type(org_add) == type('a'):
		org_add = org_add.replace(' ', '%20')
	if type(dest_add) == type('a'):
		dest_add = dest_add.replace(' ', '%20')
	orgid_text = row.getValue(org_id)
	destid_text = row.getValue(dest_id)
	
	arcpy.AddMessage('Fetching travel time and distance from origin address = {0} to destination address = {1}...'.format(org_add.replace('%20', ' '), dest_add.replace('%20', ' ')))
	download_link = basestring.format(org_add, dest_add, apikey)
	ggl_cost = fetch_google_OD(download_link)
	f.write('{0}, {1}, {2}, {3}\n'.format(orgid_text, destid_text, ggl_cost[0], ggl_cost[1]))
	
	i += 1
	if i % 100 == 0:
		watch.lap()
		togo = watch.format_time(watch.avg_sec*(totaln-i)/100)
		arcpy.AddMessage('Each batch takes about {0} secs. {1} hours {2} mins {3} secs to go...'.format(str(watch.avg_sec)[0:5], togo[0], togo[1], togo[2]))
	
	row = sc.next()
	

f.close()