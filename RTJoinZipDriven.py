import zipfile
import arcpy
import os
import time
import dbf
import csv
import shapefile as shp
import time
from datetime import date
import shutil
import subprocess as sp
from pyth.plugins.rtf15.reader import Rtf15Reader
from pyth.plugins.rtf15.writer import Rtf15Writer
from pyth.plugins.plaintext.writer import PlaintextWriter
from pyth import document
import re
from Tkinter import Tk
from tkFileDialog import askdirectory

from arcpy import env
import xml.etree.ElementTree as ET
import subprocess


filenum = 0
fields = "APN APN2 STATE COUNTY FIPS SIT_HSE_NU    SIT_DIR    SIT_STR_NA SIT_STR_SF SIT_FULL_S SIT_CITY   SIT_STATE  SIT_ZIP    SIT_ZIP4   SIT_POST   LAND_VALUE IMPR_VALUE TOT_VALUE  ASSMT_YEAR MKT_LAND_V MKT_IMPR_V TOT_MKT_VA MKT_VAL_YR REC_DATE   SALES_PRIC SALES_CODE YEAR_BUILT CONST_TYPE STD_LAND_U BLDG_AREA  LOT_SIZE   NO_OF_STOR NO_OF_UNIT BEDROOMS   BATHROOMS  OWNER  OWNER2 OWNADDRESS OWNADDRES2 OWNCTYSTZP Xcoord Ycoord"
fields = fields.lower().split()

today = str(time.time()).split('.')[0]

filefilename= "failedinprocessing_" + today + ".txt"
performancefile = "performancefile_" + today + ".txt"
failout = open(filefilename,'w')
performanceout = open(performancefile,'w')
performanceout.write("time:" + str(time.time()) + '\n')

homedir = os.getcwd() #"C:\\rtjoin_project"  # Also set ws in joinGDB ( near line 150 )
homepath = homedir + "\\"

csvdir = 'csvfiles'
zipdir = 'zipfiles'
shpdir = 'shpfiles'
gdbdir = 'gdbdata'
#gdb2dir = 'gdb2data'
parcelsdir = 'parcels'
outputshapefilesdir = "output"

csvpath = csvdir + '\\'
zippath = zipdir + '\\'
shppath = shpdir + '\\'
gdbpath = gdbdir + '\\'
parcelspath = parcelsdir + '\\'
#gdb2path = gdb2dir + '\\'
outputshapefilespath = outputshapefilesdir + '\\'
rtGeoDataBaseName = 'RTGeoDataBase.gdb'

def unzipfile(fipsZip,fipsPath):
    print "called unzipfile"
    listinfo = None
    with zipfile.ZipFile(zippath + fipsZip,'r',zipfile.ZIP_DEFLATED) as zip:
        listinfo = zip.infolist()
        zip.extractall(fipsPath)
    os.remove(zippath + fipsZip)
    infoLargest = None
    largestSize = 0
    for info in listinfo:
        if info.file_size > largestSize:
            largestSize = info.file_size
            infoLargest = info
    print infoLargest.file_size, infoLargest.date_time
    return infoLargest.date_time

def zipfiles(fip):
    print "called zipfiles"
    os.chdir(homepath + outputshapefilesdir)
    files = os.listdir(fip)
    zf = zipfile.ZipFile(fip + '.zip', mode='w')
    for f in files:
        zf.write(fip + "\\" + f)
    zf.close()

def csv2shp(fip):
    print "called csv2shp"
    os.chdir(csvdir)

    os.mkdir("my_dir")
    vrtfiletemplate = "countyvrt.xml"
    tree = ET.parse(vrtfiletemplate)
    root = tree.getroot()

    layer = root.find('OGRVRTLayer')
    element = layer.find('SrcLayer')
    element.text = "county_" + fip
    #element.set('updated','yes')

    tree.write("county_"+fip+".vrt")
    #os.chdir("my_dir")

    path = homepath + csvpath + "my_dir"
    os.rename("county_"+fip+".txt","county_"+fip+".csv")
    args1 = ['ogr2ogr','-f',"ESRI Shapefile","my_dir","county_"+fip+".csv"]
    args2 = ['ogr2ogr','-f',"ESRI Shapefile",'-overwrite',"my_dir","county_"+fip+".vrt"]
    subprocess.check_call(args1)
    subprocess.check_call(args2)
    os.chdir("./my_dir")
    os.remove("county_"+fip+".dbf")
    fippath = fip + '\\'
    shutil.move("parcelsrt.shp", homepath + shppath + fippath + "county_"+ fip + ".shp")
    shutil.move("parcelsrt.dbf", homepath + shppath + fippath + "county_"+ fip + ".dbf")
    shutil.move("parcelsrt.shx", homepath + shppath + fippath + "county_"+ fip + ".shx")
    shutil.move("parcelsrt.prj", homepath + shppath + fippath + "county_"+ fip + ".prj")
    os.rename("county_"+fip+".csv","county_"+fip+".txt")
    os.chdir(homedir)


def csv2Shape(csvfileinput,shpfile,dbfoutfile,shxfile,dirpath):
    print "called csv2Shape"
    #dataFields = []
    #pointgeoms = []
    neworder= list(range(0,19)) + list(range(27,41)) + list(range(19,27)) + list(range(41,43))
    try:
        path = shppath + dirpath
        with open(csvfileinput, 'rb') as csvfile:
            latindex = len(fields)- 2
            longindex = len(fields) - 1
            tabledbf = dbf.Table(path + dbfoutfile,'apn C(50);apn2 C(50);state C(2);county C(25);fips C(5);sit_hse_nu C(30);sit_dir C(4);sit_str_na C(50);sit_str_sf C(4);sit_full_s C(80);sit_city C(50);sit_state C(4);sit_zip C(5);sit_zip4 C(4);sit_post C(4);land_value C(15);impr_value C(15);tot_value C(15);assmt_year C(4);mkt_land_v C(15);mkt_impr_v C(15);tot_mkt_va C(15);mkt_val_yr C(4);rec_date C(10);sales_pric C(15);sales_code C(12);year_built C(4);const_type C(8);std_land_u C(10);lot_size C(15);bldg_area C(15);no_of_stor C(10);no_of_unit C(10);bedrooms C(32);bathrooms C(32);owner C(50);owner2 C(50);ownaddress C(50);ownaddres2 C(50);  ownctystzp C(70);  xcoord N(14,8);  ycoord N(14,8)')
            tabledbf.open()
            r = csv.reader(csvfile, delimiter=',')
            w = shp.Writer(shp.POINT)
            cnt = 1
            for i,row in enumerate(r):
               # print len(row)
                if cnt < 2:
                    cnt = cnt + 1
                    continue
                if i > 0: #skip header
                    if len(row) > 41:
                       # mylist=['a','b','c','d','e']
                        row[41] = float(row[41])
                        row[40] = float(row[40])
                        #rowordered = [row[i] for i in neworder]
                        #tabledbf.append(tuple(rowordered))
                        tabledbf.append(tuple(row))
                        lat = float(row[latindex])
                        long = float(row[longindex])
                        w.point(lat,long)
                        w.field("xcoord","C","15")
                        w.field("ycoord","C","15")
            #w.save(path+shpfile)
            w.saveShp(path+shpfile)
        #   w.saveDbf(path+dbfoutfile)
            w.saveShx(path+shxfile)
            maxStringLength = 50
            w.field('name','C',maxStringLength)
        #   for point ,otherdata in zip(pointgeoms, dataFields):
        #      w.poly(parts=point)

    except IOError as e:
        print e.message + " IOError for " + csvfileinput
        failout.write(e.message + " IOError for " + csvfileinput + '\n')
    except TypeError as e:
        print e.message + " TypeError for " + csvfileinput
        failout.write(e.message + " TypeError for " + csvfileinput + '\n')
    except AttributeError as e:
        print e.message + " AttributeError for " + csvfileinput
        failout.write(e.message + " AttributeError for " + csvfileinput + '\n')
    except IndexError as e:
        print e.message + " IndexError for " + csvfileinput
        failout.write(e.message + " IndexError for " + csvfileinput + '\n')

# FASTER than csv2shp + shp2gdb

def csv2gdb(csvfileinput,fip,outdir):
    inTable = csvfileinput
    outLocation = outdir + "\\" + rtGeoDataBaseName
    outTable = "county_" + fip
    arcpy.TableToTable_conversion(inTable, outLocation, outTable)
    #sp.call(["ogr2ogr","-f","SHP",inTable,outTable,"X_POSSIBLE_NAMES=XCOORD","Y_POSSIBLE_NAMES=YCOORD","GEOMETRY=AS_XY"])

def shp2gdb(workspace, outdir, creategdb, outCS):
    print "called shp2gdb"
    print "workspace",workspace
    if creategdb:
        arcpy.CreateFileGDB_management(outdir, rtGeoDataBaseName)
    arcpy.env.workspace = workspace
    outWorkspace = outdir + '/' + rtGeoDataBaseName
    try:
        # project data
        for fc in arcpy.ListFeatureClasses():
            print "fc", fc
            arcpy.FeatureClassToGeodatabase_conversion(fc, outWorkspace)
            print os.path.join(workspace, fc, "TO GDB")
        for ws in arcpy.ListWorkspaces():
            shp2gdb(os.path.join(workspace, ws),outWorkspace)
    except TypeError as e:
        print e.message + " TypeError for " + workspace
        failout.write(e.message + " AttributeError for " + workspace + '\n')
    #lyrfile = "Parcels"
    #row_count = int(arcpy.GetCount_management(lyrfile).getOutput(0))
    #return row_count

def trimParcelsFAST(shpfile,fip,trimmedshp):
    print "called trimParcelsFAST"
    #set GDAL_DATA= homepath + gdbpath + fip + "\\" + rtGeoDataBaseName
    os.chdir(homepath + fip)
    os.environ["GDAL_DATA"] = homepath + gdbpath + fip + "\\" + rtGeoDataBaseName
    args = ['ogr2ogr','-f',"ESRI Shapefile",'-dialect','SQLite','-sql',"SELECT apn,apn2,minX,minY,maxX,maxY FROM Parcels",trimmedshp,shpfile]
    subprocess.call(args)
    os.remove(shpfile)
    os.rename(trimmedshp,shpfile)

def trimParcels(dbffile,trimmeddbf):
    print "called trimParcels"
    tabledbf = dbf.Table(dbffile) #,'apn C(50);apn2 C(50);state C(2);county C(25);fips C(5);sit_hse_nu C(15);sit_dir C(4);sit_str_na C(50);sit_str_sf C(4);sit_full_s C(80);sit_city C(50);sit_state C(4);sit_zip C(5);sit_zip4 C(4);sit_post C(4);land_value C(15);impr_value C(15);tot_value C(15);assmt_year C(4);mkt_land_v C(15);mkt_impr_v C(15);tot_mkt_va C(15);mkt_val_yr C(4);rec_date C(10);sales_pric C(15);sales_code C(12);year_built C(4);const_type C(8);std_land_u C(10);lot_size C(15);bldg_area C(15);no_of_stor C(10);no_of_unit C(10);bedrooms C(32);bathrooms C(32);owner C(50);owner2 C(50);ownaddress C(50);ownaddres2 C(50);  ownctystzp C(70);  xcoord N(14,8);  ycoord N(14,8)')
    tabledbf.open()
    tabledbfTrimmed = dbf.Table(trimmeddbf,'apn C(50);apn2 C(50); minX N(14,8);  minY N(14,8); maxX N(14,8); maxY N(14,8)')
    tabledbfTrimmed.open()
    needFailRecord = True
    totalRecordCnt = 0
    rowcnt = -1
    for row in tabledbf:
        rowcnt = rowcnt + 1
        totalRecordCnt = totalRecordCnt + 1
        if len(row) > 45:
            try:
                tabledbfTrimmed.append((row[0],row[1],row[42],row[43],row[44],row[45]))
            except IndexError as e:
                print e.message + " IndexError at",str(rowcnt)
                failout.write(e.message + " IndexError \n")
        else:
            tabledbfTrimmed.append((row[0],row[1],0,0,0,0))
            if needFailRecord:
                failout.write("short record for " + dbffile + '\n')
                needFailRecord = False
    tabledbfTrimmed.close()
    tabledbf.close()
    os.remove(dbffile)
    os.rename(trimmeddbf,dbffile)
    print "trimParcels done"
    return totalRecordCnt

def joinGDB(gdb, shp):
    print "called joinGDB"
    #ws = r"C:\Users\rbjork\PycharmProjects\RTJoin" + "\\gdbdata\\" + gdb + '\\' + rtGeoDataBaseName
    ws = homepath + "gdbdata\\" + gdb + '\\' + rtGeoDataBaseName
    joinFeatures = os.path.join(ws, shp.lower().split('.')[0])
    targetFeatures = os.path.join(ws, "Parcels")
    print "targetFeatures",targetFeatures
    print "joinFeatures",joinFeatures
    outfc = "ParcelsRT"

    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable(joinFeatures)
    fieldmappings.addTable(targetFeatures)
   # fieldmappings.mergeRule = "mean"
    arcpy.SpatialJoin_analysis(targetFeatures, joinFeatures, outfc, "#", "#", fieldmappings, match_option = "INTERSECT")

## NEW
def queryForCounts(gdb,fip,totalCnt):
    print "queryForCounts"
    gdpFullPath =  gdbpath + gdb + '\\' + rtGeoDataBaseName
    #gdpFullPath =  homepath + gdbpath  + rtGeoDataBaseName
    arcpy.env.workspace = gdpFullPath
    fc = homepath + gdbpath + gdb + '\\' + rtGeoDataBaseName + '\\ParcelsRT'
    #fc = homepath + gdbpath  + gdb + '\\' + rtGeoDataBaseName + '\\Parcels'
    readableFieldNames = ('APN','SITUS','OWNER','USE CODE')
    fields = ('APN','SIT_FULL_S', 'OWNER','STD_LAND_U')
    fieldThatsLargest = ('LAND_VALUE','IMPR_VALUE','TOT_VALUE')
    largestValue = 0
    counts = []
    fcnt = 0
    margin = "                                    " # 35 chars
    #c = arcpy.da.SearchCursor(fc,"*")
    #totalCnt = 0
    #for row in c:
    #    totalCnt = totalCnt + 1
    for field in fields:
        c = arcpy.da.SearchCursor(fc, field, "(" + field + " IS NOT NULL) AND (" + field + " > '0' )")
        i = 0
        for row in c:
            i = i + 1
        readableFieldName = readableFieldNames[fcnt] + " COUNT"
        rfmlen = len(readableFieldName)
        if rfmlen < 30:
            readableFieldName = margin[rfmlen:] + readableFieldName
        if i < totalCnt:
            if i > 0:
                counts.append(prependspace + readableFieldName+ "\t"  + "{:,}".format(i) + "\t" + "{0:.2%}".format(i*1.0/totalCnt))
            else:
                counts.append(prependspace +readableFieldName+ "\t"  + "{:,}".format(i) + "\t\t" + "{0:.2%}".format(i*1.0/totalCnt))
        else:
            counts.append(prependspace +readableFieldName+ "\t"  + str(i) + "\t100%")
        fcnt = fcnt + 1

    for field in fieldThatsLargest:
        c = arcpy.da.SearchCursor(fc, field, "(" + field + " IS NOT NULL) AND (" + field + " > '0' )")
        i = 0
        for row in c:
            i = i + 1
        if i > largestValue:
            largestValue = i
    characteristicCountLabel = "VALUATION COUNT" #"CHARACTERISTIC ATTRIBUTE COUNT"
    rfmlen = len(characteristicCountLabel)
    if rfmlen < 30:
        characteristicCountLabel = margin[rfmlen:] + characteristicCountLabel
    #counts.append(characteristicCountLabel + "\t" + str(largestValue))
    if largestValue > 0:
        counts.append(prependspace +characteristicCountLabel + "\t"   + "{:,}".format(largestValue) + "\t" + "{0:.2%}".format(largestValue*1.0/totalCnt))
    else:
        counts.append(prependspace +characteristicCountLabel + "\t"   + "{:,}".format(largestValue) + "\t\t" + "{0:.2%}".format(largestValue*1.0/totalCnt))
    return counts

def writeMetaFile(fip,totalCnt, fieldcounts, headtxt,createDate):
    print "writeMetaFile"
    createYear = createDate[0]
    createMonth = createDate[1]
    createDay = createDate[2]
    #headtxtList = headtxt.split("\n")
    fieldcountsfile = open("output\\" + fip + "\\" + fip + ".rtf",'w')
    fieldcountsfile.write(headtxt + "\n")
    fieldcountsfile.write(prependspace +"                        VERSION DATE\t" + str(createYear) + "/" +  str(createMonth) + "/" +  str(createDay) + "\n")
    fieldcountsfile.write(prependspace +"                        PARCEL COUNT\t" + str(totalCnt) +  "\n")
    fieldcountsfile.write('\n'.join(fieldcounts))
    fieldcountsfile.close()

'''
def getRTFHead(fip):
    filepointer = open(fip + "\\" + fip + '.rtf')
    #try:
    #    doc = Rtf15Reader.read(filepointer)
    #    txt = PlaintextWriter.write(doc).getvalue()
    #except:
    txt = filepointer.read()
    filepointer.close()

    ctxt = re.sub("\\n\\n","\\n",txt)
    result = re.finditer("NATIVE MAP PROJECTION[^\\n]*",ctxt)

    span = None
    for i in result:
        span =  i.span()
        break
    margin = "                              " # 30 chars
    txt = ctxt[0:span[1]]
    txtlist = txt.splitlines()
    newtxtlist = []
    for t in txtlist:
        label = t.split("\t")
        if re.match("MAJOR METRO",t):
            continue
        tlen = len(label[0]) - 1
        if tlen < 30:
            t2 = margin[tlen:] + t
        else:
            t2 = "\t"+ t
        newtxtlist.append(t2)
    txt = "\n".join(newtxtlist)
    return txt
##
'''

# import pythonDoc
#
# def createRTF():
#     doc = pythonDoc.buildDoc()
#     print Rtf15Writer.write(doc).getvalue()

def getRTFHead(fip):
    print "getRTFHead"
    try:
        doc = Rtf15Reader.read(open(homepath + fip + "\\" + fip + '.rtf'))
        txt = PlaintextWriter.write(doc).getvalue()
    except:
        print "Not RTF"
        fp = open(homepath + fip + "\\" + fip + '.rtf')
        txtarray = fp.readlines()
        txt = '\n'.join(txtarray)
    ctxt = re.sub("\\n\\n","\\n",txt)
    result = re.finditer("NATIVE MAP PROJECTION[^\\n]*",ctxt)
    span = None
    for i in result:
        span =  i.span()
        break
    margin = "                                    " # 35 chars
    txt = ctxt[0:span[1]]
    txtlist = txt.splitlines()
    newtxtlist = []

    for t in txtlist:
        label = t.split("\t")
        if re.search("MAJOR METRO",t):
            continue
        if re.search("VERSION DATE",t):
            continue
        if re.search("METADATA PROFILE RECORD",t):
            newtxtlist.append(t)
            continue
        tlen = len(label[0]) - 1
        if tlen < 40:
            t2 = margin[tlen:] + t
        else:
            t2 = "\t"+ t
        newtxtlist.append(t2)
    txt = "\n".join(newtxtlist)
    return txt

'''
def queryForCounts(gdb,fip,totalCnt):
    gdpFullPath =  gdbpath + gdb + '/' + rtGeoDataBaseName
    arcpy.env.workspace = gdpFullPath
    fc = homepath + gdbpath + gdb + '/' + rtGeoDataBaseName + '/ParcelsRT'
    readableFieldNames = ('APN','SITUS','OWNER','BEDROOMS', 'BATHROOMS', 'NO. OF STORIES', 'LOT SIZE', 'BLDG AREA', 'YEAR BUILT')
    #       ('APN','SIT_FULL_S', 'OWNER','STD_LAND_U')
    fields = ('APN','SIT_FULL_S', 'OWNER', 'BEDROOMS', 'BATHROOMS', 'NO_OF_STOR', 'LOT_SIZE', 'BLDG_AREA', 'YEAR_BUILT')
    counts = []
    fcnt = 0
    for field in fields:
        c = arcpy.da.SearchCursor(fc, field, field + " IS NOT NULL")
        i = 0
        for row in c:
            i = i + 1
        counts.append(readableFieldNames[fcnt] + " COUNT: " + str(i) + " PERCENT: " + str(i*100.0/totalCnt))
        fcnt = fcnt + 1
    return counts
'''

def copyzip(outdir,fip):
    os.chdir(homepath)
    files = os.listdir(fip)
    for f in files:
        suffix = f.split(".")[0]
        ext = f.split(".")[1]
        if ext.lower() == "zip":
            print "found",f
            shutil.copy2(fip + "\\" + f, outdir + "\\" + suffix + ".ZIP")
            try:
                os.rename(outdir + "\\" + suffix + ".zip",outdir + "\\" + suffix + ".ZIP")
            except:
                pass

def exportShapeFiles(gdb,outdir,fip):
    print "called exportShapeFiles"
    gdpFullPath =  gdbpath + gdb + '/' + rtGeoDataBaseName
    arcpy.env.workspace = gdpFullPath
    parcelsRT_shp = "ParcelsRT"
    inFeatures = ["ParcelsRT","roads","county"]
    # Execute FeatureClassToGeodatabase

    arcpy.DeleteField_management(parcelsRT_shp,"Join_Count")
    arcpy.DeleteField_management(parcelsRT_shp,"TARGET_FID")
    arcpy.FeatureClassToShapefile_conversion(inFeatures, outdir)

    try:
        os.rename(outdir + '\\' + 'ParcelsRT.shp', outdir + '\\' + 'Parcels.shp')
        os.rename(outdir + '\\' + 'ParcelsRT.prj', outdir + '\\' + 'Parcels.prj')
        os.rename(outdir + '\\' + 'ParcelsRT.shx', outdir + '\\' + 'Parcels.shx')
        os.rename(outdir + '\\' + 'ParcelsRT.dbf', outdir + '\\' + 'Parcels.dbf')
        os.rename(outdir + '\\' + 'ParcelsRT.sbx', outdir + '\\' + 'Parcels.sbx')
        os.rename(outdir + '\\' + 'ParcelsRT.sbn', outdir + '\\' + 'Parcels.sbn')
        os.rename(outdir + '\\' + 'ParcelsRT.shp.xml', outdir + '\\' + 'Parcels.shp.xml')
        shutil.copy2(outdir + '\\' + 'Parcels.dbf', outdir + '\\' + fip + '.dbf')
        shutil.copy2(fip + '\\' + fip + '.mxd', outdir + '\\' + fip + '.mxd')
        copyzip(outdir,fip)
    except IOError as e:
        print e.message + " IOError doing name change of ParcelsRT"
        failout.write(e.message + " AttributeError for " + gdpFullPath + '\n')

def cleanAddressField(directory,shapefile):
    print "cleanAddressField"
    arcpy.env.workspace = directory
    # expression1 = '"OwnCityZip" == \'0 0\' OR "OwnCityZip" == \'0 0 0\''
    # layername = 'owncityzip'
    # arcpy.MakeFeatureLayer_management(str(shapefile), layername)
    # arcpy.SelectLayerByAttribute_management(layername, "NEW_SELECTION", expression1)
    expression = "cleanOwnCityZip(!OWNCTYSTZP!)"  # this is sum of unit counts of destinatios in join intersection
    codeblock = """def cleanOwnCityZip(OwnCityZip):
    if OwnCityZip == '0 0' or OwnCityZip == '0 0 0':
        return ''
    else:
        return OwnCityZip"""
    arcpy.CalculateField_management(shapefile, "OWNCTYSTZP", expression,"PYTHON_9.3",codeblock)


if __name__ == '__main__':
    prependspace = None
    while True:
       ans = raw_input('"Has your metafile been previously generated? Enter Y for yes, or N for no: ')
       #print "hi"
       yes = 'y'
       no = 'n'
       if ans == yes :
            prependspace = "\t"
            break
       elif ans == no:
            prependspace = ""
            break
    print "starting"

    print("Please select the directory containing the county .ZIP files to be processed:")
    Tk().withdraw() #prevents Tk window from showing up unnecessarily
    file_directory = askdirectory() #opens directory selection dialog
    zippath = file_directory + "\\"
    os.chdir(homedir)
    arcpy.env.workspace = homedir
    onlyfiles = os.listdir(file_directory)
    print onlyfiles

    if os.path.isdir(shppath) == False:
        os.mkdir(shppath)
    if os.path.isdir(gdbpath) == False:
        os.mkdir(gdbpath)
    if os.path.isdir(outputshapefilesdir) == False:
        os.mkdir(outputshapefilesdir)

    for file in onlyfiles:
        os.chdir(homedir)
        arcpy.env.workspace = homedir
        #print file
        if file.lower().endswith('.zip'):
            # Setting up paths
            try:
                fip = file.lower().split('.')[0] #[7:]
                performanceout.write("fip start:"+ fip + "  time:" + str(time.time()) + '\n')
                dir = fip
                dirpath = dir + '\\'
                exportdir = outputshapefilesdir + '\\' + dir

                filecsv = 'county_' + fip + '.txt'
                filedbf = 'county_' + fip + '.dbf'
                fileshp = 'county_' + fip + '.shp'
                fileshx = 'county_' + fip + '.shx'
                fileprj = 'county_' + fip + '.prj'
                fileprj = 'county_' + fip + '.prj'
                filezip = fip + '.zip'

                gdb = file.lower().split('.')[0]
                gdpFullPath =  gdbpath + gdb + '/' + rtGeoDataBaseName

                # Removing output folder from prior runs with same data
                if os.path.isdir(exportdir) == True:
                    files = os.listdir(exportdir)
                    for file in files:
                        os.remove(exportdir + "\\" + file)
                    os.chdir(homepath)
                    os.rmdir(homepath + exportdir)

                # Unzip new data

                if os.path.isdir(exportdir) == False:
                    os.mkdir(exportdir)

                creationDate = unzipfile(filezip,dir)
                #print creationDate

                # Create directory for generated shape files from csv
                if os.path.isdir(shppath + dir) == False:
                    os.mkdir(shppath + dir)
                if os.path.isdir(gdbpath+gdb) == False:
                    os.mkdir(gdbpath+gdb)

                outCS = arcpy.SpatialReference()
                outCS.factoryCode = 26911
                outCS.create()

                # Remove fields that'll be replaced by RT data in Join operation
                #trimParcelsFAST('Parcels.shp',fip,'Parcelstrim.shp')
                totalCnt = trimParcels(dirpath + 'Parcels.dbf',dirpath + 'Parcelstrim.dbf')
                shp2gdb(dir, gdbdir + '/' + gdb, True,  outCS)

                # OPTION 1
                print "Before",time.time()
                csv2Shape(csvpath + filecsv, fileshp, filedbf, fileshx, dirpath)
                #csv2shp(fip)
                print "After",time.time()

                shp2gdb(shppath + dir, gdbpath + gdb, False, outCS) # shppath + dir = workspace = shpfiles\\01001  # gdbpath+gdb =  gdbdata\\01001                                                 #  outWorkspace = gdbdata\\01001\\RTGeoDataBase.gdb
                # OR OPTION 2
                #csv2gdb(csvpath + filecsv, fip, gdbdir + '/' + gdb)

                shutil.copy2(dirpath + 'Parcels.prj', gdpFullPath + "/" + fileprj)

                arcpy.env.workspace = gdpFullPath
                joinGDB(gdb, fileshp)

                fieldcounts = queryForCounts(gdb,fip,totalCnt)
                fieldcountsfile = open("output\\" + fip + "\\" +fip+".txt",'w')
                headtxt = getRTFHead(fip)
                writeMetaFile(fip,totalCnt, fieldcounts, headtxt, creationDate)
                exportShapeFiles(gdb,exportdir,fip)

                cleanAddressField(exportdir, "Parcels.shp")
               # RTJoin_metagenerator.start(creationDate,fip)

                # Remove gdb database
                os.chdir(homepath + gdpFullPath)
                files = os.listdir('.')
                for file in files:
                    os.remove(file)
                os.chdir(homepath + gdbpath + gdb)
                os.rmdir(homepath + gdpFullPath)
                os.chdir(homepath + gdbpath)
                os.rmdir(homepath + gdbpath + gdb)

                zipfiles(fip) # zip files in output folder

                # remove input data with polygons
                print "removing unzipped folder",dir
                os.chdir(homepath + dir)
                files = os.listdir('.')
                for file in files:
                    os.remove(file)
                os.chdir(homedir)
                os.rmdir(homepath + dir)
                performanceout.write("fip done:"+ fip + "  time:" + str(time.time()) + '\n')

            except Exception as e:
                failout.write(e.message + " Exception for " + file + '\n')