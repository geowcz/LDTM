import arcpy, os, sys
import timer_class as tc

# the geodatabase that stores the raw OD cost tables
# all OD cost tables have identical fields
inputgdb = arcpy.GetParameterAsText(0)

# the travel time field in the OD cost table
ttime_field = arcpy.GetParameterAsText(1)

# coefficent and intercept for travel time
coef_ttime = arcpy.GetParameterAsText(2)
itpt_ttime = arcpy.GetParameterAsText(3)

# the travel distance field in the OD cost table
dist_field = arcpy.GetParameterAsText(4)

# coefficient and intercept for travel distance
coef_dist = arcpy.GetParameterAsText(5)
itpt_dist = arcpy.GetParameterAsText(6)

if ttime_field == "" or ttime_field =="#":
	arcpy.AddError("please input the name of travel time field")

# set workspace to the input Geodatabase
arcpy.env.workspace = inputgdb
tbs = arcpy.ListTables()


i = 0
watch = tc.timer()
for each_tb in tbs:
	# for each table, add two fields to represent the estimated travel time and distance
	arcpy.AddField_management(each_tb, "TimeEst_min", "Float")

	expression1 = coef_ttime + " * !" + ttime_field + "! + " + itpt_ttime
	arcpy.CalculateField_management(each_tb, "TimeEst_min", expression1, "PYTHON3")

	if dist_field != "":
		arcpy.AddField_management(each_tb, "DistEst_mi", "Float")
		expression2 = coef_dist + " * !" + dist_field + "! + " + itpt_dist
		arcpy.CalculateField_management(each_tb, "DistEst_mi", expression2, "PYTHON3")

	i += 1
	watch.lap()
	togo = watch.format_time(watch.avg_sec*(len(tbs)-i))
	arcpy.AddMessage('Each batch take about {0} secs. {1} hours  {2} mins {3} secs to go...'.format(str(watch.avg_sec)[0:5], togo[0], togo[1], togo[2]))
