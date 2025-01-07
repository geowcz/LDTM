import os, arcpy
import timer_class as tc

zcta_file = arcpy.GetParameterAsText(0)
zcta_field = arcpy.GetParameterAsText(1)
x_field = arcpy.GetParameterAsText(2)
y_field = arcpy.GetParameterAsText(3)
input_zips = arcpy.GetParameterAsText(4)
zip_field = arcpy.GetParameterAsText(5)
output_file = arcpy.GetParameterAsText(6)

t1 = tc.timer()
arcpy.AddMessage("Reading zip codes from the input table...")
selected_zctas = {}

with arcpy.da.SearchCursor(input_zips, [zip_field]) as cursor:
    for row in cursor:
        zip = row[0]
        if zip not in selected_zctas:
            selected_zctas[zip] = False
        else:
            arcpy.AddWarning("Zip code {0} in the list found one duplicate.".format(zip))


arcpy.AddMessage("Gathering info from the input ZCTA feature layer...")
zctas = {}

with arcpy.da.SearchCursor(zcta_file, [zcta_field, x_field, y_field]) as cursor:
    for row in cursor:
        zcta = row[0]
        if zcta in selected_zctas:
            if zcta not in zctas:
                zctas[zcta] = [row[1], row[2]]
            else:
                arcpy.AddWarning("{0} zcta duplicated!!!".format(zcta))

arcpy.AddMessage("there are {0} zctas found in the zcta feature layer...".format(len(zctas)))

notfound = 0
for each_zcta in selected_zctas:
    if each_zcta not in zctas:
        arcpy.AddWarning("{0} is not found in ZCTA file".format(each_zcta))
        arcpy.AddWarning("Please ensure the input ZCTA list have correct ZIP codes (usually in 5 digits), that correspond to the ZCTA values in the input ZCTA feature layer. Otherwise, contact rli24@nd.edu to update the tool!!!!!!")
        notfound += 1
if notfound == 0:
    arcpy.AddMessage("All zcta(s) have been found!!")

arcpy.AddMessage("Generating tables to save OD pairs...")
arcpy.AddWarning("Note that the same O and D are not included in the table!! If you want to compute it, use the tool of Calibrate Intra-zonal OD Matrix")
f = open(output_file, "w")
f.write("OZCTA,DZCTA,olat,olong,dlat,dlong\n")
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


