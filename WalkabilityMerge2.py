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
    workspace = arcpy.env.workspace
    for county in countyFolders:
        arcpy.env.workspace = homedir + "\\data\\" + county
        arcpy.AddField_management(feature, fieldname, fieldType)
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
        arcpy.env.workspace = homedir + "\\data\\" + county
        destination = "Parcels.shp"
        layername = "destLyr" + str(n)
        arcpy.MakeFeatureLayer_management(str(destination), layername)
        arcpy.SelectLayerByAttribute_management(layername, "NEW_SELECTION", expression1)
        arcpy.SelectLayerByAttribute_management(layername, "SUBSET_SELECTION", expression2)
        arcpy.SelectLayerByAttribute_management(layername, "ADD_TO_SELECTION", expression3)
        arcpy.CopyFeatures_management(layername, homedir + "\\data\\" + county + "\\" + str(outputName))
        n = n + 1

# OR

def selectDestinationsByDestinationAttribute(destinations,ouputName):
    Dir = arcpy.env.workspace
    arcpy.MakeFeatureLayer_management(destinations, "destLyr")
    expression = '"destination" > \'0\''
    arcpy.SelectLayerByAttribute_management("destLyr", "NEW_SELECTION", expression)
    arcpy.CopyFeatures_management("destLyr", Dir + "\\" + str(outputName))

def removeFields(countyFolders):
    for county in countyFolders:
        arcpy.env.workspace = homedir + "\\data\\" + county
        #arcpy.env.workspace = homedir + "\\data\\" + fip + "\\" + geoDataBaseName
        #fcList = arcpy.ListFeatureClasses() #get a list of feature classes
        #for fc in fcList:  #loop through feature classes
        #fieldList = [f.baseName for f in arcpy.ListFields("Parcels.shp",None,"String")]  #get a list of fields for each feature class
        #rmlist = list(set(fieldList) - set(["IMPR_VALUE","STD_LAND_U","DEST","OWNER","MINX","MAXX","MINY","MAXY"]))
        # Process: Delete Field
        arcpy.DeleteField_management("Parcels.shp", "APN2;STATE;COUNTY;FIPS;SIT_HSE_NU;SIT_DIR;SIT_STR_NA;SIT_STR_SF;SIT_FULL_S;SIT_CITY;SIT_STATE;SIT_ZIP;SIT_ZIP4;SIT_POST;LAND_VALUE;TOT_VALUE;ASSMT_YEAR;MKT_LAND_V;MKT_IMPR_V;TOT_MKT_VA;MKT_VAL_YR;REC_DATE;SALES_PRIC;SALES_CODE;YEAR_BUILT;CONST_TYPE;BEDROOMS;BATHROOMS;OWNADDRES2;OWNCTYSTZP")
        #arcpy.DeleteField_management("Parcels.shp", rmlist)

def trim2MinFields(fc,geoDataBaseName):
    #arcpy.env.workspace = homedir + "\\data\\" + fip + "\\" + geoDataBaseName
    fieldList = [f.baseName for f in arcpy.ListFields(fc,None,"String")]   #get a list of fields for each feature class
    rmlist = list(set(fieldList) - set(["DEST","MINX","MAXX","MINY","MAXY"]))
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
                if n > 0:
                    filename = fc.split('.')[0]
                    typ = fc.split('.')[1]
                    newfilelist.append(filename + "_" + str(n) + "." + typ)
                else:
                    newfilelist.append(fc)
        n = n + 1
    return newfilelist

def bufferDestinations(destinations,bufferedName, geoDataBaseName):
    print "bufferDestinations"
    arcpy.Buffer_analysis( targetdir + "\\" + geoDataBaseName + "\\" + destinations, targetdir + "\\" + geoDataBaseName + "\\" + bufferedName, "2640 Feet")

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
    targetFeature = targetFeature # + "_shp"
    nearFeature = nearFeature
    print "scoreParcels"
    #;UNIT_CNT_1 \"UNIT_CNT_1\" true true false 4 Long 0 0 ,Sum,#,destinationsCommercialBufferedHalf,UNIT_CNT,-1,-1

    # Local variables:
    # Local variables:
    #Parcels = "C:\\Users\\rbjork\\PycharmProjects\\2Maps\\data\\06041\\walk2.gdb\\Parcels"
    #destinationsCommercialBufferedHalf = "C:\\Users\\rbjork\\PycharmProjects\\2Maps\\data\\06041\\walk2.gdb\\destinationsCommercialBufferedHalf"
    #Parcels_SpatialJoin1 = "C:\\Users\\rbjork\\PycharmProjects\\2Maps\\data\\06041\\walk2.gdb\\Parcels_SpatialJoin1"
    # Process: Spatial Join
    #parcel_layer = "parcels_lyr"
    #destinations_layer = "destinations_layer"
    #arcpy.MakeFeatureLayer_management(Parcels, parcel_layer)
    #arcpy.MakeFeatureLayer_management(destinationsCommercialBufferedHalf, destinations_layer)

    # Field Mappings
    arcpy.env.workspace = 'C:\\Users\\rbjork\\PycharmProjects\\2Maps\\data\\06041\\walk2.gdb'

    in_file1 = 'Parcels'
               #destinationsCommercialBufferedHalf
    in_file2 = 'destinationsCommercialBufferedHalf'
    output_file = 'Parcels_SpatialJoin1'

    fms = arcpy.FieldMappings()
    fm_parcels1 = arcpy.FieldMap()
    fm_parcels2 = arcpy.FieldMap()
    fm_destinations1 = arcpy.FieldMap()

    # Add fields to their corresponding FieldMap objects
    apn_field = "APN"
    fm_parcels1.addInputField(in_file1, apn_field)

    landuse_field = "STD_LAND_U"
    fm_parcels2.addInputField(in_file1, landuse_field)

    unit_cnt_field = "UNIT_CNT"
    fm_destinations1.addInputField(in_file2, unit_cnt_field)

    fm_destinations1.mergeRule = 'Sum'

    f_name = fm_destinations1.outputField
    f_name.name = 'UNIT_CNT_SUM'
    f_name.aliasName = 'UNIT_CNT_SUM'
    fm_destinations1.outputField = f_name

    fms.addFieldMap(fm_parcels1)
    fms.addFieldMap(fm_parcels2)
    fms.addFieldMap(fm_destinations1)
    #KEEP_COMMON
    arcpy.SpatialJoin_analysis(in_file1, in_file2, output_file, "JOIN_ONE_TO_ONE", "KEEP_COMMON",fms , "INTERSECT", "", "")
    #arcpy.SpatialJoin_analysis(parcel_layer, destinations_layer, Parcels_SpatialJoin1, "JOIN_ONE_TO_ONE", "KEEP_COMMON", "APN \"APN\" true true false 50 Text 0 0 ,First,#,C:\\Users\\rbjork\\PycharmProjects\\2Maps\\data\\06041\\walk2.gdb\\Parcels,APN,-1,-1;BLDG_AREA_1 \"BLDG_AREA_1\" true true false 15 Text 0 0 ,First,#,destinationsCommercialBufferedHalf,BLDG_AREA,-1,-1;UNIT_CNT \"UNIT_CNT\" true true false 4 Long 0 0 ,Sum,#,destinationsCommercialBufferedHalf,UNIT_CNT,-1,-1", "INTERSECT", "", "")
    #arcpy.SpatialJoin_analysis(Parcels, destinationsCommercialBufferedHalf, Parcels_SpatialJoin1, "JOIN_ONE_TO_ONE", "KEEP_COMMON", "APN \"APN\" true true false 50 Text 0 0 ,First,#,C:\\Users\\rbjork\\PycharmProjects\\2Maps\\data\\06041\\walk2.gdb\\Parcels,APN,-1,-1;BLDG_AREA_1 \"BLDG_AREA_1\" true true false 15 Text 0 0 ,First,#,destinationsCommercialBufferedHalf,BLDG_AREA,-1,-1;UNIT_CNT_1 \"UNIT_CNT_1\" true true false 4 Long 0 0 ,Sum,#,destinationsCommercialBufferedHalf,UNIT_CNT,-1,-1", "INTERSECT", "", "")
    arcpy.AddField_management(output_file, "walkable", "TEXT")
    # Process: Spatial Join
    #arcpy.SpatialJoin_analysis(targetdir + "\\" + geoDataBaseName + "\\" + targetFeature, targetdir + "\\" + geoDataBaseName + "\\" +nearFeature, "targetFeatureScored", "JOIN_ONE_TO_ONE", "KEEP_COMMON", "APN \"APN\" true true false 50 Text 0 0 ,First,#,Parcels,APN,-1,-1;APN2 \"APN2\" true true false 50 Text 0 0 ,First,#,Parcels,APN2,-1,-1;IMPR_VALUE \"IMPR_VALUE\" true true false 15 Text 0 0 ,First,#,Parcels,IMPR_VALUE,-1,-1;BLDG_AREA \"BLDG_AREA\" true true false 15 Text 0 0 ,First,#,Parcels,BLDG_AREA,-1,-1;UNIT_CNT \"UNIT_CNT\" true true false 4 Long 0 0 ,First,#,Parcels,UNIT_CNT,-1,-1;UNIT_CNT_1 \"UNIT_CNT_1\" true true false 4 Long 0 0 ,Sum,#,destinationsCommercialBufferedHalf,UNIT_CNT,-1,-1", "INTERSECT", "", "")
    #arcpy.FeatureClassToGeodatabase_conversion(targetdir + "\\" +"targetFeatureScored.shp", geoDataBaseName)
    #arcpy.AddField_management(targetdir + "\\" + geoDataBaseName + "\\targetFeatureScored", "walkable", "TEXT")
    expression = "getScore(!UNIT_CNT_SUM!)"  # this is sum of unit counts of destinatios in join intersection
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
    #arcpy.CalculateField_management(targetdir + "\\" + geoDataBaseName + "\\targetFeatureScored", "walkable", expression,"PYTHON_9.3",codeblock)


# NEW and needs integration
def loadAndMergeCountiesInMetro(targetdir,targetParcels,metroCountyParcels):  # These are from county shape files - not parcel shapefiles
    print "loadAndMergeCountiesInMetro"
    fieldMappings = None
    metro = targetParcels
    metroOut = targetdir + "\\walk2.gdb\\metroOut"
    print "merging:",metroOut
    mcparcelsnames = [targetdir + "\\walk2.gdb\\"+ mc.split('.')[0] for mc in metroCountyParcels]
    arcpy.Merge_management(mcparcelsnames, metroOut, fieldMappings)
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
        if os.path.isfile(homedir + "\\data\\" + str(county) + "\\destination.prj"):
            os.remove(homedir + "\\data\\" + str(county) + "\\destination.prj")
        if os.path.isfile(homedir + "\\data\\" + str(county) + "\\destination.dbf"):
            os.remove(homedir + "\\data\\" + str(county) + "\\destination.dbf")
        if os.path.isfile(homedir + "\\data\\" + str(county) + "\\destination.sbn"):
            os.remove(homedir + "\\data\\" + str(county) + "\\destination.sbn")
        if os.path.isfile(homedir + "\\data\\" + str(county) + "\\destination.shp"):
            os.remove(homedir + "\\data\\" + str(county) + "\\destination.shp")
        if os.path.isfile(homedir + "\\data\\" + str(county) + "\\destination.shx"):
            os.remove(homedir + "\\data\\" + str(county) + "\\destination.shx")
        gdbfiles = os.listdir(outdir + "\\walk2.gdb")
        for gf in gdbfiles:
                os.remove(outdir + "\\walk2.gdb\\" + gf)
        os.remove(outdir + "\\walk2.gdb")
        #os.remove(outdir + "\\walkability.gdb")

#if use_code.find('c') == 1:


def computeDestinationWeight(counties,featureName):
    print "computeDestinationWeight"
    # Process: Calculate Field
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
    except:
        units = 1
    return units"""
    for countyfolder in counties:
        arcpy.env.workspace = homedir + "\\data\\" + str(countyfolder)
        #arcpy.CalculateField_management("Parcels.shp", "UNIT_CNT", "computeUnitCount(!BLDG_AREA!, !NO_OF_UNIT! , !STD_LAND_U! )", "PYTHON", "def computeUnitCount(bldg_area, no_units, use_code):\\n    units = 1\\n    if use_code.find(\'c\') == 1:\\n        units = math.ceil( bldg_area /10000)\\n        if  no_units > units:\\n            units = no_units\\n    return units\\n")
        arcpy.CalculateField_management(featureName, "UNIT_CNT", expression, "PYTHON_9.3", codeblock)


multicounty2maps = False
logout = None
geoDataBaseName = "2mapsgdb"

if __name__ == '__main__':
    today = str(time.time()).split('.')[0]
    filefilename= "logfile_" + today + ".txt"
    logout = open(filefilename,'w')
    logout.write('main'+ '\n')
    homedir = os.getcwd() #"C:\\Users\\rbjork\\PycharmProjects\\2Maps"
    ouputdir = homedir + "\\output"
    arcpy.env.workspace = ouputdir + "\\" + geoDataBaseName

    nearParcelsList = None
    if len(sys.argv) > 1:   # Command line invocation
        nearParcelsList = [] #[sys.argv[1]]
        localParcels = sys.argv[1]
        targetdir = sys.argv[2]
    else:
        nearParcelsList = [arcpy.GetParameterAsText(0)]  # destinations
        localParcels = arcpy.GetParameterAsText(1) # parcels
        targetdir = arcpy.GetParameterAsText(2)

    targetCounty_shp = targetdir + "\\county.shp"
    targetFeatureClass = localParcels.split('.')[0]

    targetParcels = targetdir + "\\parcels.shp"

    outdir = targetdir
    geoDataBaseName = "walk2.gdb"
    #geoDataBaseOutput = "walkability.gdb"
    creategdb = True

    outputName = "walkability"

    # SETUP
    if creategdb:
        if os.path.isdir(outdir + "\\walk2.gdb"):
            gdbfiles = os.listdir(outdir + "\\walk2.gdb")
            for gf in gdbfiles:
                os.remove(outdir + "\\walk2.gdb\\" + gf)
            #gdbfiles2 = os.listdir(outdir + "\\walkability2.gdb")
            #for gf in gdbfiles:
                #os.remove(outdir + "\\walkability2.gdb\\" + gf)
            os.remove(outdir + "\\walk2.gdb")
            #os.remove(outdir + "\\walkability.gdb")
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
        arcpy.CreateFileGDB_management(outdir, geoDataBaseName)
        #arcpy.CreateFileGDB_management(outdir, geoDataBaseOutput)


    workspace = targetdir #+ "/" + geoDataBaseName #"C:/Users/dev/Documents/boundarysolutions/marin/Marin.gdb"
    geoDataBasePath = targetdir + "/" + geoDataBaseName
    #geoDataBaseOutputPath = targetdir + "\\" + geoDataBaseOutput
    arcpy.env.workspace = workspace
    logout.write('calling selectDestinations'+ '\n')
    multicounty2maps = promptWhetherMulticounty()

    outCS = arcpy.SpatialReference()
    outCS.factoryCode = 26911
    outCS.create()

    fastJoin = False

    if multicounty2maps:
        countyFolderList = promptForFoldersForMetro()
        for countyfolder in countyFolderList:
            #if targetdir.find(countyfolder) == -1:
            countyparcels = homedir + "\\data\\" + countyfolder + "\\parcels.shp"
            nearParcelsList.append(countyparcels) # might want to rename to parcels_[fip].shp

        #addFields(countyFolderList,"Parcels.shp","DEST","TEXT")   # DONE

        #removeFields(countyFolderList)
        selectDestinations(countyFolderList,"distinationParcels") # may not be needed

        addFields(countyFolderList,"distinationParcels.shp","UNIT_CNT","LONG") #DONE

        computeDestinationWeight(countyFolderList,"distinationParcels.shp")

        newgdbfiles = features2gdb(countyFolderList,outdir,geoDataBaseName)

        merged = loadAndMergeCountiesInMetro(targetdir,targetParcels,newgdbfiles)
        arcpy.env.workspace = targetdir
        outWorkspace = outdir + "\\" + geoDataBaseName
        arcpy.FeatureClassToGeodatabase_conversion("Parcels.shp", outWorkspace)
        #features2gdb(countyFolderList,geoDataBaseName) # may not be needd
        if fastJoin:
            pass #scoreParcelsFAST(targetFeatureClass,"metroOut", outputName, geoDataBaseName)
        else:
            bufferDestinations("metroOut","destinationsCommercialBufferedHalf",geoDataBaseName)
            scoreParcels(targetFeatureClass,"destinationsCommercialBufferedHalf", outputName, geoDataBaseName)
        #cleanCounties(outdir,countyFolderList)
    else:
        selectDestinations(nearParcelsList,"distinationParcels")
        logout.write('calling features2gdb'+ '\n')
        features2gdb(geoDataBaseName)
        logout.write('calling bufferDestinations'+ '\n')
        bufferDestinations("distinationParcels","destinationsCommercialBufferedHalf",geoDataBaseName)
        logout.write('calling scoreParcels'+ '\n')
        scoreParcels(targetFeatureClass,"destinationsCommercialBufferedHalf", outputName, geoDataBaseName)


    #logout.write('calling generateLayers'+ '\n')
    #scoreParcelsShape(targetFeatures,nearFeatures, outputName, geoDataBaseName)
    #generateLayers(targetFeatureClass,targetFeatures)