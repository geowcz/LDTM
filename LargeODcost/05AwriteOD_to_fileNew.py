import os, sys, arcpy, math

OD_id = arcpy.GetParameterAsText(0) #It's usually 'Name'

ODlv1 = arcpy.GetParameterAsText(1)
ODlv1_time_name = arcpy.GetParameterAsText(2)  # "Total_TravelTime"
ODlv1_mile_name = arcpy.GetParameterAsText(3)  #'Total_Miles'

ODlv2 = arcpy.GetParameterAsText(4)
ODlv2_time_name = arcpy.GetParameterAsText(5)  #"Total_Time"
ODlv2_mile_name = arcpy.GetParameterAsText(6)  #'Total_Miles'

zcta_file = arcpy.GetParameterAsText(7) 
zcta_field = arcpy.GetParameterAsText(8) 
x_field = arcpy.GetParameterAsText(9) 
y_field = arcpy.GetParameterAsText(10)
speed_Geodesic = arcpy.GetParameterAsText(11) 

isCalirbateLv3 = arcpy.GetParameterAsText(12)
lvl3_bt = arcpy.GetParameterAsText(13)
lvl3_at = arcpy.GetParameterAsText(14)
lvl3_bd = arcpy.GetParameterAsText(15)
lvl3_ad = arcpy.GetParameterAsText(16)

outputfolder = arcpy.GetParameterAsText(17)

'''
OD_id ="Name"
ODlv1 = r"D:\Code\HSABook\Chapter2\Large_OD_Data\Test40\OD_cost_out.gdb"
ODlv1_time_name = "Total_Time"
ODlv1_mile_name = "Total_Miles"

ODlv2 = r"D:\Code\HSABook\Chapter2\Large_OD_Data\Test41\OD_cost_out.gdb"
ODlv2_time_name = "Total_Time"
ODlv2_mile_name = "Total_Miles"

zcta_file = r"D:\Code\HSABook\Chapter2\Large_OD_Data\ZCTA_Test.gdb\ZIP_Code_Area_Florida_R30"
zcta_field = "ZCTA5CE10"
x_field = "POINT_X"
y_field = "POINT_Y"
speed_Geodesic = 50

outputfolder = r"D:\Code\HSABook\Chapter2\Large_OD_Data\Test72"
'''

# the default speed is 50 mph
if speed_Geodesic == '#' or speed_Geodesic == '':
    speed_Geodesic = 50
else:
    speed_Geodesic = int(speed_Geodesic) 


# Handles lv1 returns (within 3 hrs drive time)
arcpy.env.workspace = ODlv1
all_tbs = arcpy.ListTables()
for each_tb in all_tbs:
    #print (each_tb)
    O_id = ''
    zcta_dict = dict()
    expression1 = u'{} is not null and {} is not null'.format(ODlv1_time_name, ODlv1_mile_name) 
    with arcpy.da.SearchCursor(each_tb, [OD_id, ODlv1_time_name, ODlv1_mile_name], where_clause=expression1) as cursor:
        for row in cursor:
            od_id_val = row[0]
            cO_id = od_id_val.split(' - ')[0]
            D_id = od_id_val.split(' - ')[1]
            if cO_id != O_id:
                if len(zcta_dict) != 0:
                    #print(outputfolder+'\\'+O_id[0:3]+'\\'+O_id+'.txt')
                    f = open(outputfolder+'\\'+O_id[0:3]+'\\'+O_id+'.txt', 'w')
                    f.write(str(zcta_dict))
                    arcpy.AddMessage("1. {}".format(str(zcta_dict)))
                    print("1. {}".format(str(zcta_dict)))
                    f.close()
                    #break
                O_id = cO_id
                if not os.path.exists(outputfolder+'\\'+O_id[0:3]):
                    os.makedirs(outputfolder+'\\'+O_id[0:3])
                if os.path.exists(outputfolder+'\\'+O_id[0:3]+'\\'+O_id+'.txt'):
                    f = open(outputfolder+'\\'+O_id[0:3]+'\\'+O_id+'.txt', 'r')
                    zcta_dict = eval(f.read())
                    f.close()
                else:
                    zcta_dict = dict()
            else:
                if D_id != O_id and (D_id not in zcta_dict):
                    #zcta_dict[D_id] = [max(float('{0:.2f}'.format(row.getValue('Total_TravelTime'))),180), float('{0:.2f}'.format(row.getValue('Total_Miles'))), 2]  for formal ZCTAs
                    zcta_dict[D_id] = [float('{0:.2f}'.format(row[1])), float('{0:.2f}'.format(row[2])), 1]
                    arcpy.AddMessage("1 is running")
    

# Handles lv2 returns (3-6 hrs drive, snap to highway that within 5 miles) Part I
arcpy.env.workspace = ODlv2
all_tbs = arcpy.ListTables()
for each_tb in all_tbs:
    #print (each_tb)
    O_id = ''
    zcta_dict = dict()
    expression2 = u'{} is not null and {} is not null'.format(ODlv2_time_name, ODlv2_mile_name)    
    with arcpy.da.SearchCursor(each_tb, [OD_id, ODlv2_time_name, ODlv2_mile_name], where_clause = expression2) as cursor:
        for row in cursor:
            od_id_val = row[0]
            cO_id = od_id_val.split(' - ')[0]
            D_id = od_id_val.split(' - ')[1]
            if cO_id != O_id:
                if len(zcta_dict) != 0:
                    #print(outputfolder+'\\'+O_id[0:3]+'\\'+O_id+'.txt')
                    f = open(outputfolder+'\\'+ O_id[0:3]+'\\'+ O_id+'.txt', 'w')
                    f.write(str(zcta_dict))
                    f.close()
                    arcpy.AddMessage("2. {}".format(str(zcta_dict)))
                    print("2. {}".format(str(zcta_dict)))
                    #break
                O_id = cO_id
                if not os.path.exists(outputfolder+'\\'+O_id[0:3]):
                    os.makedirs(outputfolder+'\\'+O_id[0:3])
                if os.path.exists(outputfolder+'\\'+O_id[0:3]+'\\'+O_id+'.txt'):
                    f = open(outputfolder+'\\'+O_id[0:3]+'\\'+O_id+'.txt', 'r')
                    zcta_dict = eval(f.read())
                    f.close()
                else:
                    zcta_dict = dict()
            else:
                arcpy.AddMessage("2 is running but failed {} {} {}".format(D_id, O_id, zcta_dict))
                if D_id != O_id and (D_id not in zcta_dict):
                    #zcta_dict[D_id] = [max(float('{0:.2f}'.format(row.getValue('Total_TravelTime'))),180), float('{0:.2f}'.format(row.getValue('Total_Miles'))), 2]  for formal ZCTAs
                    zcta_dict[D_id] = [float('{0:.2f}'.format(row[1])), float('{0:.2f}'.format(row[2])), 2]
                    arcpy.AddMessage("2 is running")
          

# Handles lv3 returns (Geodesic distance and time based on 50mph) 
# return minutes and miles           
def cal_geodesic_dist_time (x1, y1, x2, y2, speed):
    r = 3959 #miles 
    #p1 = math.radians(y1)
    #p2 = math.radians(y2)
    #dp = math.radians(y1-y2)
    #dl = math.radians(x1-x2)
    #a = math.sin(dp/2) ** 2 + math.cos(p1)*math.cos(p2)*(math.sin(dl/2)**2)
    #c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    #d = r * c
    # prefer to use the formula in our book by CZWang
    a = math.radians(x1)
    b = math.radians(y1)
    c = math.radians(x2)
    d = math.radians(y2)
    d = r * math.acos(math.sin(b) * math.sin(d) + math.cos(b) * math.cos(d) * math.cos(c - a))
    t = d/speed * 60
    return t, d

# read the ZCTA feature class and calculate geodesic distance based on coorindates of O and D
zcta_coord_dict = dict()
with arcpy.da.SearchCursor(zcta_file, [zcta_field, x_field, y_field]) as cursor:
    for row3 in cursor:
        zcta_coord_dict[row3[0]] = [row3[1], row3[2]]

for each_org_key in zcta_coord_dict:
    #print(outputfolder+'\\'+each_org_key[0:3]+'\\'+each_org_key+'.txt')
    #arcpy.AddMessage(outputfolder+'\\'+each_org_key[0:3]+'\\'+each_org_key+'.txt')
    if not os.path.exists(outputfolder+'\\'+ each_org_key[0:3]):
        os.makedirs(outputfolder+'\\'+each_org_key[0:3])
    if os.path.exists(outputfolder+'\\'+each_org_key[0:3]+'\\'+each_org_key+'.txt'):
        f = open(outputfolder+'\\'+each_org_key[0:3]+'\\'+each_org_key+'.txt', 'r')
        zcta_dict = eval(f.read())
        arcpy.AddMessage("3. {}".format(str(zcta_dict)))
        print("3. {}".format(str(zcta_dict)))
        f.close()
    else:
        zcta_dict = dict()
    for each_dest_key in zcta_coord_dict:
        if each_dest_key not in zcta_dict and each_dest_key != each_org_key:
            time, dist = cal_geodesic_dist_time(zcta_coord_dict[each_org_key][0], zcta_coord_dict[each_org_key][1], zcta_coord_dict[each_dest_key][0], zcta_coord_dict[each_dest_key][1], speed_Geodesic)
            if isCalirbateLv3 == "Yes":
                time = float(lvl3_bt) * time + float(lvl3_at)
                dist = float(lvl3_bd) * dist + float(lvl3_ad)            
            zcta_dict[each_dest_key] = [float('{0:.2f}'.format(time)), float('{0:.2f}'.format(dist)), 3]
    f = open(outputfolder+'\\'+ each_org_key[0:3]+'\\'+ each_org_key+'.txt', 'w')
    f.write(str(zcta_dict))
    f.close()


# Check if file created correctly
def FileSearcher(folder, suffix): #suffix should not include '.'
    allfile = os.listdir(folder)
    return_value = []
    if(len(allfile) > 0):
        i = 0
        while(i < len(allfile)):
            temp = allfile[i].split('.')
            if (len(temp) > 1):
                act_suffix = temp[len(temp)-1]
            else:
                act_suffix = ''
            if(act_suffix == suffix):
                wholepath = folder + "\\" + allfile[i]
                return_value.append(wholepath)
            i += 1
    return return_value

all_out_folders = FileSearcher(outputfolder, '')    
for each_out_folder in all_out_folders:
    all_text = FileSearcher(each_out_folder, 'txt')
    for each_text in all_text:
        f = open(each_text, 'r')
        test_dict = eval(f.read())
        f.close()
        print ('{0}:{1}'.format(os.path.split(each_text)[1], len(test_dict)))
    
arcpy.AddMessage("OD_id = {}".format(OD_id))
arcpy.AddMessage("ODlv1 = {}".format(ODlv1))
arcpy.AddMessage("ODlv1_time_name = {}".format(ODlv1_time_name))
arcpy.AddMessage("ODlv1_mile_name = {}".format(ODlv1_mile_name))
arcpy.AddMessage("ODlv2 = {}".format(ODlv2))
arcpy.AddMessage("ODlv2_time_name = {}".format(ODlv2_time_name))
arcpy.AddMessage("ODlv2_mile_name = {}".format(ODlv2_mile_name))
arcpy.AddMessage("zcta_file = {}".format(zcta_file))
arcpy.AddMessage("zcta_field = {}".format(zcta_field))
arcpy.AddMessage("x_field = {}".format(x_field))
arcpy.AddMessage("y_field = {}".format(y_field))
arcpy.AddMessage("speed_Geodesic = {}".format(speed_Geodesic))
arcpy.AddMessage("outputfolder = {}".format(outputfolder))




    
        
        
