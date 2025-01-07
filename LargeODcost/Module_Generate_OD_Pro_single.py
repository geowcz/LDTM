import os
import arcpy
import datetime

def add_zero (num, digit):
	string = str(num)
	while len(string) < digit:
		string = '0' + string
	return string
	
def file_search (folder, ext):
	result = []
	all_file = os.listdir(folder)
	for file in all_file:
		if(file.split(".")[-1].upper() == ext.upper()):
			result.append(folder + '\\' + file)
	return result

def set_up_OD_matrix(provider_file, u_shp, na_layer, smp, tempfolder, desID, cost, accost, restrict, hier, max_time_limit):
	temp_layer = arcpy.MakeFeatureLayer_management(provider_file, "Temp_Provider")
	selected_layer = arcpy.SelectLayerByLocation_management("Temp_Provider", "WITHIN_A_DISTANCE", u_shp, str(max_time_limit) + " Miles", "NEW_SELECTION")
	print(len(selected_layer))
	temp_output = arcpy.FeatureClassToFeatureClass_conversion(selected_layer, tempfolder, "temp.shp")
	exe_layer = arcpy.na.MakeODCostMatrixLayer(smp, na_layer, cost, max_time_limit/50*60, "", accost, "ALLOW_UTURNS", restrict, hier,"","NO_LINES")
	arcpy.na.AddLocations(exe_layer, "Destinations", temp_output, "Name "+desID+" #", "5000 meter")			
	return exe_layer
	
def str0(input, length):
	temp = str(input)
	while len(temp) < length:
		temp = '0' + temp
	return temp
	
def get_formatted_time():
	time_now = datetime.datetime.now()
	result = str(time_now.year) + "." + str0(time_now.month,2) + "." + str0(time_now.day,2) + " " + str0(time_now.hour,2) + ":" + str0(time_now.minute,2) + "." + str0(time_now.second,2)
	return result
	
	
def get_ODCost(provider_file, u_shp, n, na_layer, ODfolder, smp, tempfolder, log_file, orgID, desID, cost, accost, restrict, hier, max_time_limit):	
	try:
		# Check out Network Analyst license if available. Fail if the Network Analyst license is not available.
		if arcpy.CheckExtension("network") == "Available":
			arcpy.CheckOutExtension("Network")
		else:
			raise arcpy.ExecuteError("Network Analyst Extension license is not available.")

		f=open(log_file, 'a')
		ODcostout = ODfolder + '\\OD_cost_out.gdb'
		if not os.path.exists(ODcostout):
			arcpy.CreateFileGDB_management(ODfolder, 'OD_cost_out.gdb')
		f.write(get_formatted_time() + " Start working on " + os.path.split(u_shp)[1] + "...\n")
		f.write(get_formatted_time() + " Setting up OD cost matrix...\n")
		exe_layer = set_up_OD_matrix(provider_file, u_shp, na_layer, smp, tempfolder, desID, cost, accost, restrict, hier, max_time_limit)
		f.write(get_formatted_time() + " Adding Locations...\n")
		arcpy.na.AddLocations(exe_layer, "Origins", u_shp, "Name " + orgID + " #", "5000 Meters")
		f.write(get_formatted_time() + " Solving...\n")
		arcpy.na.Solve(exe_layer)
		f.write(get_formatted_time() + " Exporting...\n")
		N = int(str(arcpy.GetCount_management(r"OD Cost Matrix\Lines")))
		if N:
			arcpy.TableToTable_conversion(r"OD Cost Matrix\Lines", ODcostout , "OD_cost_out" + str(n))
		f.write("Successful with no Error!!!\n")
		f.close()
	except Exception as e:		
		f.write(get_formatted_time() + " ")
		f.write(e.message)
		f.write("\n")
		f.close()
		
		ef = open(ODfolder + '\\error.txt', 'a')
		ef.write("Error when working on file: " + u_shp + '\n')
		ef.write(get_formatted_time() + " ")
		ef.write(e.message)
		ef.write("\n\n")
		ef.close()
		
		if not os.path.exists(ODfolder + '\\error_shp.gdb'):
			arcpy.CreateFileGDB_management(ODfolder, 'error_shp.gdb')
		arcpy.FeatureClassToFeatureClass_conversion(u_shp, ODfolder + '\\error_shp.gdb' , os.path.split(u_shp)[1])
		
def remove_leading_space(string):
	while string[0] == ' ' and string != '':
		string  = string[1:]
	return string