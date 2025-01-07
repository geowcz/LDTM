import os, arcpy
import timer_class as tc

#input = r"D:\Code\HSABook\Chapter2\FL_HSA.gdb\ZIP_Points"
#outputgdb = r"D:\Code\HSABook\Chapter2\Large_ZIP-to-ZIP_OD\zcta_test.gdb"
#ID = 'OBJECTID'
#step = 200


input = arcpy.GetParameterAsText(0)
outputgdb = arcpy.GetParameterAsText(1)
ID = arcpy.GetParameterAsText(2)
step = arcpy.GetParameterAsText(3)

totaln = int(arcpy.GetCount_management(input).getOutput(0))

if step == '#' or step == '':
	if totaln > 200:
		step = 200
	else:
		step = totaln
else:
	step = int(step)

sys.path.append(os.path.split(os.path.realpath(__file__))[0])

'''
outputfolder = os.path.split(outputgdb)[0]
for k in range(0,6):
	gdbfile = outputfolder + "\\"+ os.path.splitext(os.path.split(outputgdb)[1])[0]+str(k)+'.gdb'
	if os.path.exists(gdbfile):
		arcpy.Delete_management(gdbfile)
	arcpy.CreateFileGDB_management(outputfolder, os.path.splitext(os.path.split(outputgdb)[1])[0]+str(k)+'.gdb')
'''

arcpy.SetProgressor("step", "Reading files...")


newfieldname = str(ID) + "COPY"
fieldList = arcpy.ListFields(input)
for field in fieldList:
	if field.name == newfieldname:
		arcpy.DeleteField_management(input, [newfieldname])

arcpy.AddField_management(input, newfieldname, "TEXT")
arcpy.CalculateField_management(input, newfieldname, "!" + ID + "!", "PYTHON3")

i = 1
sc = arcpy.SearchCursor(input)
select_list = []
row = sc.next()
while row:
	#select_list.append(str(row.getValue(ID)))
	select_list.append(str(row.getValue(newfieldname)))
	if i % 10000 == 0:
		arcpy.SetProgressorPosition(int(i/totaln*100))
	i += 1
	row = sc.next()

select_list.sort()
arcpy.ResetProgressor()
	
i = 0
#nfile = 0
watch = tc.timer()	
arcpy.SetProgressor("step", "Splitting files in to smaller trunks...")	
while i < totaln:
	criteria = str(select_list[i:i+step])
	outfeatname = os.path.splitext(os.path.split(input)[1])[0]+"_"+str(i)
	arcpy.FeatureClassToFeatureClass_conversion(input, outputgdb, outfeatname, "{0} IN ({1})".format(newfieldname, str(criteria[1:len(criteria)-1])))
	arcpy.DeleteField_management(outputgdb +"\\" + outfeatname, [newfieldname])
	progress = int(i/totaln*100)
	watch.lap()
	arcpy.SetProgressorPosition (progress)
	
	if i % (step*5) == 0 and i > 0:
		togo = watch.format_time(watch.avg_sec*(int((totaln-i)/step)+1))
		arcpy.AddMessage('Each batch takes about {0}secs. {1} hours  {2} mins {3} secs to go...'.format(str(watch.avg_sec)[0:5], togo[0], togo[1], togo[2]))
	
	i += step
	#nfile += 1

arcpy.DeleteField_management(input, [newfieldname])