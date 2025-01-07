import os, arcpy
import timer_class as tc

zcta_file = arcpy.GetParameterAsText(0)
zcta_field = arcpy.GetParameterAsText(1)
state_field = arcpy.GetParameterAsText(2)
x_field = arcpy.GetParameterAsText(3)
y_field = arcpy.GetParameterAsText(4)
selected_states = arcpy.GetParameterAsText(5)
output_file = arcpy.GetParameterAsText(6)


selected_states = selected_states.replace("\'", "").split(";")    
arcpy.AddMessage(output_file)

t1 = tc.timer()
arcpy.AddMessage("Gathering all zctas from the selected state...")
zctas = {}
states = {}

with arcpy.da.SearchCursor(zcta_file, [zcta_field, state_field, x_field, y_field]) as cursor:
    for row in cursor:
        state = row[1]
        if state in selected_states:
            zctas[row[0]] = [row[2], row[3]]
        if state not in states:
            states[state] = 1        

notfound = 0
for each_state in selected_states:
    if each_state not in states:
        arcpy.AddWarning("{0} state is not found in ZCTA file... ".format(each_state))
        arcpy.AddWarning("Please ensure the input ZCTA point layer have an explicit state value corresponding to the interested state list. Otherwise, contact rli24@nd.edu to update the tool!!!!!!")
        notfound += 1
if notfound == 0:
    arcpy.AddMessage("All state(s) have been found!!")
    
arcpy.AddMessage("Generating tables to save OD pairs...")
arcpy.AddWarning("Note that the same O and D are not included in the table!! If you want to compute it, use the tool of Calibrate Intra-zonal OD Matrix")
f = open(output_file, "w")
f.write("OZCTA,DZCTA,olat,olong,dlat,dlong\n") # the extraction of latitude and longtitude of OD is for the computation of geodesic distance, CZWang
i = 0
for each_ozcta in zctas:
    for each_dzcta in zctas:        
        if each_ozcta != each_dzcta:
            if i%10000 == 0:
                arcpy.AddMessage("Processing {0} records...".format(i))
            f.write( "{0},{1},{2},{3},{4},{5}\n".format(each_ozcta, each_dzcta, zctas[each_ozcta][1], zctas[each_ozcta][0], zctas[each_dzcta][1], zctas[each_dzcta][0]))
            i += 1
f.close()
t1.lap()
time_used = t1.format_time(t1.total_sec)
arcpy.AddMessage("Process finished in {0} hours {1} minutes {2} seconds.".format(time_used[0], time_used[1], time_used[2]))


