import arcpy, math, os

zcta_area_file = arcpy.GetParameterAsText(0)  
zcta_field_name = arcpy.GetParameterAsText(1) 
b_peri_t = arcpy.GetParameterAsText(2)
b_area_t = arcpy.GetParameterAsText(3)
a_t = arcpy.GetParameterAsText(4)
b_peri_d = arcpy.GetParameterAsText(5)
b_area_d = arcpy.GetParameterAsText(6)
a_d = arcpy.GetParameterAsText(7)
output_csv= arcpy.GetParameterAsText(8)

'''
zcta_area_file = r"D:\Code\HSABook\Chapter2\FL_HSA.gdb\ZIP_Code_Area"
zcta_field_name = "OBJECTID"
output_csv = "D:\\Code\\HSABook\\Chapter2\\Large_ZIP-to-ZIP_OD\\intra_zcta_OD_cost.csv"
b_peri_t = "0.04"
b_area_t = "0.88"
a_t ="-0.02"
b_peri_d = "0.02"
b_area_d = "0.37"
a_d = "-0.01"
'''
# coefficent of perimeter for time estimate
if b_peri_t == "":
    b_peri_t = 0.04
else:
    b_peri_t = float(b_peri_t)

# coefficent of area for time estimate   
if b_area_t == "":
    b_area_t = 0.88
else:
    b_area_t = float(b_area_t)

# intercept for time estimate
if a_t == "":
    a_t = -0.02
else:
    a_t = float(a_t)

# coefficent of perimeter for distance estimate
if b_peri_d == "":
    b_peri_d = 0.02
else:
    b_peri_d = float(b_peri_d)  

# coefficent of area for distance estimate
if b_area_d == "":
    b_area_d = 0.37
else:
    b_area_d = float(b_area_d)

# intercept for distance estimate   
if a_d == "":
    a_d = -0.01
else:
    a_d = float(a_d)

# output table
outdata = open(output_csv, "w")
outdata.write("OZCTA, DZCTA, TimeEst_min, DistEst_mi, Level\n")

# delete fields of perimeter and area if exists
all_fields = arcpy.ListFields(zcta_area_file)
#bool_peri = False
#bool_area = False
for field in all_fields:
    print(field.name)
    if field.name == "PeriLenMI":
       arcpy.DeleteField_management(zcta_area_file, "PeriLenMI")
    if field.name == "AreaMI":
       arcpy.DeleteField_management(zcta_area_file, "AreaMI")
    #if bool_peri and bool_area:
        #break

# add two new fields and calculate the values
arcpy.AddField_management(zcta_area_file, "PeriLenMI", "float")
arcpy.AddField_management(zcta_area_file, "AreaMI", "float")
arcpy.CalculateGeometryAttributes_management(zcta_area_file, [["PeriLenMI", "PERIMETER_LENGTH"]], length_unit = "MILES_US")
arcpy.CalculateGeometryAttributes_management(zcta_area_file, [["AreaMI", "AREA"]], area_unit = "SQUARE_MILES_US")

# iterate input features and estimate the travel costs
sc = arcpy.SearchCursor(zcta_area_file)
row = sc.next()
while row:
    zcta = row.getValue(zcta_field_name)
    peri = row.getValue("PeriLenMI")
    area = row.getValue("AreaMI")
    time = a_t + b_peri_t * peri + b_area_t * math.sqrt(area)
    distance = a_d + b_peri_d * peri + b_area_d * math.sqrt(area)
    outdata.write("{0},{1},{2},{3},0\n".format(zcta, zcta, time, distance))
    row = sc.next()  
outdata.close()

arcpy.DeleteField_management(zcta_area_file, ["PeriLenMI"])
arcpy.DeleteField_management(zcta_area_file, ["AreaMI"])