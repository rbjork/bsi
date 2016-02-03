__author__ = 'dev'
# This is the Best of version


# This version merges all the counties in the metro, filters out the destinations in the metro.
# Then it bufferes all the destinations
# Then takes then

import arcpy,os,sys

import time
from Tkinter import Tk
from tkFileDialog import askdirectory
import os

# Note that if the attribute 'destination' in parcels exist (from maybe RTJoinFor2Maps) that the lengthy
# queuies in 'selectDestination' can be replaced by simple check of destination attribute

def addFields(countyFolders,feature,fieldname,fieldType):
    print "addFields called"
    workspace = arcpy.env.workspace
    for county in countyFolders:
        try:
            arcpy.env.workspace = homedir + "\\data\\" + county
            arcpy.AddField_management(feature, fieldname, fieldType)
        except:
            print "addField likely done for county ",county
    arcpy.env.workspace = workspace


def selectDestinations(countyFolders,outputName):
    print "selectDestinations"
    #arcpy.env.workspace = arcpy.GetParameterAsText(0)
    Dir = arcpy.env.workspace
    expression1 = 'NOT "STD_LAND_U" = \'RAPT\' AND NOT "STD_LAND_U" = \'RSFR\' AND NOT "STD_LAND_U" = \'RCON\' AND NOT "STD_LAND_U" = \'RCOO\' AND NOT "STD_LAND_U" = \'RDUP\' AND NOT "STD_LAND_U" = \'RMOB\' AND NOT "STD_LAND_U" = \'RMSC\' AND NOT "STD_LAND_U" = \'RQUA\' AND NOT "STD_LAND_U" = \'RSFR\' AND NOT "STD_LAND_U" = \'RTIM\' AND NOT "STD_LAND_U" = \'RTRI\' AND NOT "STD_LAND_U" = \'RMFD\''
    expression2 = '"IMPR_VALUE" > \'0\''
    expression3 = '"OWNER" LIKE \'%PARK%\' OR "OWNER" LIKE \'%RECREATION%\'  OR "OWNER" LIKE \'%TOWN%\'  OR "OWNER" LIKE \'%COUNTY%\'  OR "OWNER" LIKE \'%STATE%\'  OR "OWNER" LIKE \'%DISTRICT%\' OR "OWNER" LIKE \'%SCHOOL%\'  OR "OWNER" LIKE \'%ELEMENTARY%\'  OR "OWNER" LIKE \'%MIDDLE%\'  OR "OWNER" LIKE \'%LIBRARY%\'  OR "OWNER" LIKE \'%K8 K12%\'  OR "OWNER" LIKE \'%HOSPITAL%\' OR "OWNER" LIKE \'%CIVIC%\'  OR "OWNER" LIKE \'%CLINIC%\'  OR "OWNER" LIKE \'%FACILITY%\' OR "OWNER" LIKE \'%COMMUNITY%\'  OR "OWNER" LIKE \'%PLAYGROUND%\' OR "OWNER" LIKE \'%CHURCH%\'  OR "OWNER" LIKE \'%TEMPLE%\'  OR "OWNER" LIKE \'%MOSQUE%\' OR "OWNER" LIKE \'%FOREST%\'  OR "OWNER" LIKE \'%MUNICIPAL%\' OR "OWNER" LIKE \'%UNIVERSITY%\'  OR "OWNER" LIKE \'%DAYCARE%\''
    # Within selected features, further select based on a SQL query within the script tool
    n = 1
    for county in countyFolders:
        print "for ",county
        try:
            arcpy.env.workspace = homedir + "\\data\\" + county
            destination = "Parcels.shp"
            layername = "destLyr" + str(n)
            arcpy.MakeFeatureLayer_management(str(destination), layername)
            arcpy.SelectLayerByAttribute_management(layername, "NEW_SELECTION", expression1)
            arcpy.SelectLayerByAttribute_management(layername, "SUBSET_SELECTION", expression2)
            arcpy.SelectLayerByAttribute_management(layername, "ADD_TO_SELECTION", expression3)
            arcpy.CopyFeatures_management(layername, homedir + "\\data\\" + county + "\\" + str(outputName))
        except:
            print "failed selectDestinations for ",county
        n = n + 1

# OR

def selectDestinationsByDestinationAttribute(destinations,ouputName):
    Dir = arcpy.env.workspace
    arcpy.MakeFeatureLayer_management(destinations, "destLyr")
    expression = '"destination" > \'0\''
    arcpy.SelectLayerByAttribute_management("destLyr", "NEW_SELECTION", expression)
    arcpy.CopyFeatures_management("destLyr", Dir + "\\" + str(outputName))

def removeFields(countyFolders):
    print "removeFields called"
    for county in countyFolders:
        print "for ",county
        try:
            arcpy.env.workspace = homedir + "\\data\\" + county
            arcpy.DeleteField_management("Parcels.shp", "APN2;STATE;COUNTY;FIPS;SIT_HSE_NU;SIT_DIR;SIT_STR_NA;SIT_STR_SF;SIT_FULL_S;SIT_CITY;SIT_STATE;SIT_ZIP;SIT_ZIP4;SIT_POST;LAND_VALUE;TOT_VALUE;ASSMT_YEAR;MKT_LAND_V;MKT_IMPR_V;TOT_MKT_VA;MKT_VAL_YR;REC_DATE;SALES_PRIC;SALES_CODE;YEAR_BUILT;CONST_TYPE;BEDROOMS;BATHROOMS;OWNADDRES2;OWNCTYSTZP")
        except:
            print "Remove done already for county ",county

def removeFields2(county,parcelsFC):
    print "removeFields2 called"
    arcpy.env.workspace = homedir + "\\destinations\\walk2.gdb"
    try:
        fc = parcelsFC
        arcpy.DeleteField_management(fc, "IMPR_VALUE;STD_LAND_U;BLDG_AREA;OWNER;OWNER2;OWNADDRESS;")
    except:
        print "Remove done already for county ",county

def removeFields3(county,parcelsFC):
    print "removeFields2 called"
    arcpy.env.workspace = homedir + "\\destinations\\walk2.gdb"
    try:
        fc = parcelsFC
        arcpy.DeleteField_management(fc, "Join_Count;MINX;MINY;MAXX;MAXY;Shape_Area;Shape_Length;LOT_SIZE;NO_OF_STOR;UNIT_CNT_1;XCOORD;YCOORD")
    except:
        print "Remove done already for county ",county

def trim2MinFields(fc,geoDataBaseName):
    #arcpy.env.workspace = homedir + "\\data\\" + fip + "\\" + geoDataBaseName
    fieldList = [f.baseName for f in arcpy.ListFields(fc,None,"String")]   #get a list of fields for each feature class
    rmlist = list(set(fieldList) - set(["DEST","MINX","MAXX","MINY","MAXY","NO_OF_UNIT","STD_LAND_U","BLDG_AREA"]))
    arcpy.DeleteField_management(fc, rmlist)

#arcpy.Buffer_analysis("C:/Users/dev/Documents/boundarysolutions/marin/commercial.shp", "C:/Users/dev/Documents/boundarysolutions/marin/commercialBufferedHalf.shp","2640 Feet")

def createWalkabilityLayer(featureScored,walklayer):
    logout.write('calling createWalkabilityLayer'+ '\n')
    print "createWalkabilityLayer"
    expression = '"walkable" = \'' + walklayer + '\''
    Dir = arcpy.env.workspace
    arcpy.MakeFeatureLayer_management(featureScored, "walkLyr")
    arcpy.SelectLayerByAttribute_management("walkLyr", "NEW_SELECTION", expression)
    arcpy.CopyFeatures_management("walkLyr", Dir + "\\" + str(walklayer))

def shapeFileRename(srcfile,dstfile):
    src = srcfile.split('.')[0]
    dst = dstfile.split('.')[0]
    for typ in ['.shp','.dbf','.shx','.sbn','.sbx','.prj']:
        srcfile = src + typ
        dstfile = dst + typ
        os.rename(srcfile,dstfile)

def features2gdb(countyfoldersList,outdir,geodbname):
    print "features2gdb"
    outWorkspace = outdir + "\\" + geodbname
    newfilelist = []

    n = 0
    for countyfolder in countyfoldersList:
        arcpy.env.workspace = homedir + "\\data\\" + str(countyfolder)
        for fc in arcpy.ListFeatureClasses():
            if fc.find("distinationParcels") != -1:
                arcpy.FeatureClassToGeodatabase_conversion(fc, outWorkspace)
                trim2MinFields(fc,outWorkspace)
                #typ = fc.split('.')[1]
                if n > 0:
                    filename = fc.split('.')[0]
                    newfilelist.append(filename + "_" + str(n)) # + "." + typ)
                else:
                    newfilelist.append(fc)
        n = n + 1
    return newfilelist

# Loads county.shp into geo database and renames them so they are unique
def countyBorder2gdb(countyfoldersList,outdir,geodbname):
    print "countyBorder2gdb called"
    outWorkspace = destinationsDir + "\\" + geodbname
    data_type = "FeatureClass"
    countyFeatures = {}
    n = 0
    for countyfolder in countyfoldersList:
        print "for ",countyfolder
        try:
            arcpy.env.workspace = homedir + "\\data\\" + str(countyfolder)
            for fc in arcpy.ListFeatureClasses():
                if fc.lower().startswith("county"):
                    arcpy.FeatureClassToGeodatabase_conversion(fc, outWorkspace)
                    if n > 0:
                        countyFCName = fc.split('.')[0] + "_" + str(n)
                    else:
                        countyFCName = fc.split('.')[0]
                    countyFeatures[countyfolder] = countyFCName
            n = n + 1
        except:
            print "failed ",countyfolder
    return countyFeatures

def bufferDestinations(destinations,bufferedName, geoDataBaseName):
    print "bufferDestinations"
    arcpy.Buffer_analysis( destinations, destinationsDir + "\\" + geoDataBaseName + "\\" + bufferedName, "2640 Feet")

def scoreParcelsShape(targetFeature,nearFeature, outputName, geoDataBaseName):
    fcnear = nearFeature + "_shp" #'c:/data/base.gdb/well'
    fctarget = targetFeature + "_shp"
    arcpy.env.workspace = homedir + "\\" + geoDataBaseName
    arcpy.MakeFeatureLayer_management(targetFeature, 'parcels_lyr')
    fields = ['owner_1', 'std_landuse', 'SHAPE@XY']
    with arcpy.da.SearchCursor(fcnear, fields) as cursor1:
        for row1 in cursor1:
            # Make a layer and select cities which overlap the chihuahua polygon
            arcpy.SelectLayerByLocation_management('parcels_lyr', 'intersect', fctarget)
            # Within the previous selection sub-select cities which have population > 10,000
            arcpy.SelectLayerByAttribute_management('parcels_lyr','SUBSET_SELECTION', '"intersect_count" > 1')

#If features matched criteria write them to a new feature class
#matchcount = int(arcpy.GetCount_management('cities_lyr').getOutput(0))
'''
def scoreParcelsFAST(targetFeature,nearFeature, outputName, geoDataBaseName):
    arcpy.SpatialJoin_analysis(targetdir + "\\" + geoDataBaseName + "\\" + targetFeature,
        targetdir + "\\" + geoDataBaseName + "\\" +nearFeature,"targetFeatureScored","#","#",field_mapping = None, match_option = "WITHIN_A_DISTANCE",2313, distance_field_name = "Dist")
    arcpy.FeatureClassToGeodatabase_conversion(targetdir + "\\" +"targetFeatureScored.shp", geoDataBaseName)
    arcpy.AddField_management(targetdir + "\\" + geoDataBaseName + "\\targetFeatureScored", "walkable", "TEXT")
    expression = "getScore(!Join_Count!)"
    codeblock = """def getScore(cnt):
    cnt = int(cnt)
    if cnt <= 31:
        return 'walk1'
    if cnt > 31 and cnt <= 60:
        return 'walk2'
    if cnt > 60 and cnt <= 90:
        return 'walk3'
    if cnt > 90 and cnt <= 121:
        return 'walk4'
    if cnt > 121:
        return 'walk5'
    else:
        return 'walk0'"""
    arcpy.CalculateField_management(targetdir + "\\" + geoDataBaseName + "\\targetFeatureScored", "walkable", expression,"PYTHON_9.3",codeblock)
'''

def scoreParcels(targetFeature, nearFeature, outputName, geoDataBaseName):
    print "scoreParcels with targetFeature ",targetFeature

    arcpy.env.workspace = homedir + '\\destinations\\walk2.gdb'

    in_file1 = targetFeature
    in_file2 = nearFeature
    output_file = targetFeature + '_SpatialJoin1'

    fms = arcpy.FieldMappings()
    fm_destinations1 = arcpy.FieldMap()

    unit_cnt_field = "UNIT_CNT"
    fm_destinations1.addInputField(in_file2, unit_cnt_field)

    fm_destinations1.mergeRule = 'Sum'

    '''
    f_name = fm_destinations1.outputField
    f_name.name = 'UNIT_CNT'
    f_name.aliasName = 'UNIT_CNT'
    fm_destinations1.outputField = f_name
    '''

    #fms.addTable(in_file2)
    fms.addTable(in_file1)
    fms.addFieldMap(fm_destinations1)

    arcpy.SpatialJoin_analysis(in_file1, in_file2, output_file, "JOIN_ONE_TO_ONE", "KEEP_COMMON",fms, "INTERSECT", "", "")
    arcpy.AddField_management(output_file, "walkable", "TEXT")

    expression = "getScore(!UNIT_CNT!)"  # this is sum of unit counts of destinatios in join intersection

    codeblock = """def getScore(cnt):
    if cnt <= 60:
        return 'walk1'
    if cnt > 60 and cnt <= 180:
        return 'walk2'
    if cnt > 180 and cnt <= 270:
        return 'walk3'
    if cnt > 270 and cnt <= 360:
        return 'walk4'
    if cnt > 360:
        return 'walk5'
    else:
        return 'walk0'"""
    arcpy.CalculateField_management(output_file, "walkable", expression,"PYTHON_9.3",codeblock)
    return output_file


# NEW and needs integration
def loadAndMergeCountiesInMetro(targetdir,metroCountyParcels):  # These are from county shape files - not parcel shapefiles
    print "loadAndMergeCountiesInMetro"
    fieldMappings = None
    metroOut = targetdir + "\\walk2.gdb\\metroOut"
    print "merging:",metroOut
    mcparcelsnames = [targetdir + "\\walk2.gdb\\"+ mc.split('.')[0] for mc in metroCountyParcels]
    arcpy.Merge_management(mcparcelsnames, metroOut, fieldMappings)
    for dp in mcparcelsnames:
        arcpy.Delete_management(outdir + "\\walk2.gdb\\" + dp)
    return metroOut

# NEW and needs integration
def promptForFoldersForMetro():
    print("Please select the directory containing the metro .ZIP files to be processed:")
    Tk().withdraw() #prevents Tk window from showing up unnecessarily
    file_directory = askdirectory() #opens directory selection dialog
    os.chdir(homedir)
    arcpy.env.workspace = homedir
    metro_counties = os.listdir(file_directory)
    return metro_counties

def promptWhetherMulticounty():
    multicounty = False
    while True:
       ans = raw_input('"Are you using multiple county? Enter Y for yes, or N for no: ')
       yes = 'y'
       no = 'n'
       if ans.lower() == yes :
            multicounty = True
            break
       elif ans.lower() == no:
            multicounty = False
            break
    return multicounty

def cleanCounties(outdir,counties):
    for county in  counties:
        if os.path.isfile(homedir + "\\data\\" + str(county) + "\\distinationParcels.prj"):
            os.remove(homedir + "\\data\\" + str(county) + "\\distinationParcels.prj")
        if os.path.isfile(homedir + "\\data\\" + str(county) + "\\distinationParcels.dbf"):
            os.remove(homedir + "\\data\\" + str(county) + "\\distinationParcels.dbf")
        if os.path.isfile(homedir + "\\data\\" + str(county) + "\\distinationParcels.sbn"):
            os.remove(homedir + "\\data\\" + str(county) + "\\distinationParcels.sbn")
        if os.path.isfile(homedir + "\\data\\" + str(county) + "\\distinationParcels.shp"):
            os.remove(homedir + "\\data\\" + str(county) + "\\distinationParcels.shp")
        if os.path.isfile(homedir + "\\data\\" + str(county) + "\\distinationParcels.shx"):
            os.remove(homedir + "\\data\\" + str(county) + "\\distinationParcels.shx")
        path = outdir + "\\walk2.gdb\\"
        arcpy.env.workspace = outdir + "\\walk2.gdb"
        for fc in arcpy.ListFeatureClasses():
            if int(arcpy.GetCount_management(fc).getOutput(0)) == 0:
                arcpy.Delete_management(path + fc)
                arcpy.AddMessage('Deleted "{}" because it contains no features!'.format(fc))
    os.remove(outdir + "\\walk2.gdb")

def removeCountyDestinations(outdir):
    print "removeCountyDestinations called"
    arcpy.env.workspace = outdir + "\\walk2.gdb"
    for fc in arcpy.ListFeatureClasses():
        if fc.lower().startswith("distinationParcels"):
            arcpy.Delete_management(outdir + "\\walk2.gdb\\" + fc)

def createBufferedCountyDestinations(outdir,countyFC,metroFC,county):
    print "createBufferedCountyDestinations called for " + county
    arcpy.env.workspace = outdir + "\\walk2.gdb"
    metroLayer = metroFC + '_lyr'
    countyBuffered = countyFC + "_buf"
    arcpy.Buffer_analysis( countyFC, countyBuffered, "2640 Feet")
    arcpy.MakeFeatureLayer_management(metroFC, metroLayer)
    arcpy.SelectLayerByLocation_management(metroLayer, 'intersect', countyBuffered)
    destinationsOut = "destination_" + county
    arcpy.CopyFeatures_management(metroLayer, destinationsOut)
    bufferedDestinationOut = "destinationBuffered_" + county
    bufferDestinations(destinationsOut,bufferedDestinationOut,"walk2.gdb")
    arcpy.Delete_management(outdir + "\\walk2.gdb\\" + destinationsOut)
    return bufferedDestinationOut

#if use_code.find('c') == 1:

def computeDestinationWeight(destinations,geoDataBaseName):
    print "computeDestinationWeight"
    arcpy.env.workspace = homedir + "\\destinations\\" + geoDataBaseName
    expression = "computeUnitCount(!BLDG_AREA!, !NO_OF_UNIT! , !STD_LAND_U! )"  # this is sum of unit counts of destinatios in join intersection
    codeblock = """def computeUnitCount(bldg_area, no_units, use_code):
    units = 1
    try:
        if str(use_code).find('C') == 0:
            no_of_units = int(no_units)
            if no_of_units > units:
                units = no_of_units
            unitsbyarea = int(math.ceil(float(bldg_area)/10000))
            if unitsbyarea > units:
                units = unitsbyarea
            if units > 10:
                units = 10
    except:
        units = 1
    return units"""

    for featureName in destinations:
        try:
            print "for ",featureName
            arcpy.CalculateField_management(featureName, "UNIT_CNT", expression, "PYTHON_9.3", codeblock)
        except:
            print "failed ",countyfolder

def renameFeature(featureClass,county,workspace):
    print "renameFeature called"
    shpfiles = os.listdir(workspace)
    newShapeFile = ""
    try:
        for shpfile in shpfiles:
            shpfilestr =  str(shpfile)
            if shpfilestr.lower().startswith(featureClass.lower()):
                shpfileparts = shpfile.split('.')
                newShapeFile = shpfileparts[0] + county + ".shp"
                if len(shpfileparts) == 3:
                    parcelsNewName = workspace + "\\" + shpfileparts[0] + county + "." + shpfileparts[1] + "."  + shpfileparts[-1]
                elif len(shpfileparts) == 2:
                    parcelsNewName = workspace + "\\" + shpfileparts[0] + county + "."  + shpfileparts[-1]
                else:
                    continue
                os.rename(workspace + "\\" + shpfile, parcelsNewName)
    except:
        print "Rename done already for ",parcelsFC
    return newShapeFile

multicounty2maps = False
logout = None

if __name__ == '__main__':

    geoDataBaseName = "walk2.gdb"
    today = str(time.time()).split('.')[0]
    filefilename= "logfile_" + today + ".txt"
    logout = open(filefilename,'w')
    logout.write('main'+ '\n')
    homedir = os.getcwd() #"C:\\Users\\rbjork\\PycharmProjects\\2Maps"
    ouputdir = homedir + "\\output"
    arcpy.env.workspace = ouputdir + "\\" + geoDataBaseName

    nearParcelsList = None

    destinationsDir = homedir + "\\destinations"
    destinationsPath = destinationsDir + "\\"

    targetFeatureClass = "Parcels" #localParcels.split('.')[0]
    dataDir = homedir + "\\data"
    dataPath = dataDir + "\\"

    outdir = destinationsDir

    creategdb = True

    outputName = "walkability"

    # SETUP

    if creategdb:
        '''
        if os.path.isfile(outdir + "\\destination.prj"):
            os.remove(outdir + "\\destination.prj")
        if os.path.isfile(outdir + "\\destination.dbf"):
            os.remove(outdir + "\\destination.dbf")
        if os.path.isfile(outdir + "\\destination.sbn"):
            os.remove(outdir + "\\destination.sbn")
        if os.path.isfile(outdir + "\\destination.shp"):
            os.remove(outdir + "\\destination.shp")
        if os.path.isfile(outdir + "\\destination.shx"):
            os.remove(outdir + "\\destination.shx")
        if os.path.isdir(outdir + "\\walk2.gdb"):
            gdbfiles = os.listdir(outdir + "\\walk2.gdb")
            for gf in gdbfiles:
                os.remove(outdir + "\\walk2.gdb\\" + gf)
            os.remove(outdir + "\\walk2.gdb")
        '''
        if os.path.isdir(outdir + "\\walk2.gdb") == False:
            arcpy.CreateFileGDB_management(outdir, geoDataBaseName)


    workspace = destinationsDir
    geoDataBasePath = destinationsDir + "/" + geoDataBaseName

    arcpy.env.workspace = workspace
    logout.write('calling selectDestinations'+ '\n')
    #multicounty2maps = promptWhetherMulticounty()

    outCS = arcpy.SpatialReference()
    outCS.factoryCode = 26911
    outCS.create()

    countyFolderList = promptForFoldersForMetro()

    addFields(countyFolderList,"Parcels.shp","DEST","TEXT")   # DONE
    removeFields(countyFolderList)

    selectDestinations(countyFolderList,"distinationParcels") # may not be needed
    addFields(countyFolderList,"distinationParcels.shp","UNIT_CNT","LONG") #DONE
    addFields(countyFolderList,"Parcels.shp","UNIT_CNT","LONG")

    newgdbfiles = features2gdb(countyFolderList,destinationsDir,geoDataBaseName)
    computeDestinationWeight(newgdbfiles,geoDataBaseName)
    mergedMetroDestinations = loadAndMergeCountiesInMetro(destinationsDir,newgdbfiles)


    removeCountyDestinations(outdir)  # removes destinations features - they aren't needed since metro has the aggregate
    countyBorderFeatures = countyBorder2gdb(countyFolderList,outdir,geoDataBaseName)
    countyBufferedDestination = {}

    for countyfolder in countyFolderList:
        countyFC = countyBorderFeatures[countyfolder]
        countyBufferedDestination[countyfolder] = createBufferedCountyDestinations(outdir, countyFC, mergedMetroDestinations, countyfolder)

    arcpy.Delete_management(mergedMetroDestinations)


    outWorkspace = destinationsDir + "\\" + geoDataBaseName

    for countyfolder in countyFolderList:
        workspace = dataPath + countyfolder
        arcpy.env.workspace = workspace
        fc = "Parcels.shp"
        featureClass = fc.split('.')[0]
        parcelsFC = destinationsPath + geoDataBaseName + "\\" + featureClass +  countyfolder
        parcelsSHP = renameFeature(featureClass, countyfolder, workspace)
        print "now will execute FeatureClassToGeodatabase_conversion"
        arcpy.FeatureClassToGeodatabase_conversion(parcelsSHP, outWorkspace)
        removeFields2(countyfolder,parcelsFC)

    for countyfolder in countyFolderList:
        workspace = dataPath + countyfolder
        arcpy.env.workspace = workspace
        fc = "Parcels.shp"
        featureClass = fc.split('.')[0]
        parcelsFC = destinationsPath + geoDataBaseName + "\\" + featureClass +  countyfolder
        bufferedCountyDestinations = countyBufferedDestination[countyfolder]
        scoredParcels = scoreParcels(parcelsFC,bufferedCountyDestinations, outputName, geoDataBaseName)
        removeFields3(countyfolder,scoredParcels)
        arcpy.Delete_management(parcelsFC)
        arcpy.Delete_management(destinationsPath + geoDataBaseName + "\\" + bufferedCountyDestinations)
    #cleanCounties(outdir,countyFolderList)

