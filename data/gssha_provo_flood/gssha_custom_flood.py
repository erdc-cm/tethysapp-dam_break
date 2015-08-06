#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      mscott90
#
# Created:     21/02/2014
# Copyright:   (c) mscott90 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import shutil, sys, re, subprocess, time, os
from tethys_dataset_services.engines import GeoServerSpatialDatasetEngine
from zipfile import ZipFile

geoserver_engine = GeoServerSpatialDatasetEngine(endpoint='http://ciwmap.chpc.utah.edu:8080/geoserver/rest', username='admin', password='geoserver')

GSSHA_EXE = 'gssha.exe'

def main(prj, job_id):
    os.chdir('gssha_provo_flood')
    runGSSHA(prj)
    reformat(prj, job_id)
    zip_floodmap(job_id)
    upload_to_geoserver(job_id)
    os.chdir('..')

def runGSSHA(prjFile):
    #outFile = "run.out"
    #out = open(outFile, 'w')
    process = subprocess.Popen([GSSHA_EXE, prjFile])
    process.wait()
    #out.close()

def reformat(prj, job_id):
    projectName = re.sub('.prj','',prj)
    gfl = projectName + '_StochOutput/' + projectName + '.gfl'
    reformatGFL(gfl, job_id)


def reformatGFL(gfl, job_id, threshold=0.03):
    HEADER = """ncols 	122
nrows 	96
xllcenter 437269.78
yllcenter 4450221.00
cellsize     90.00
NODATA_value 0
    """

    NCOLS = 122
    START_VALUES = 11720

    output = open(gfl, 'r')
    lines = output.readlines()
    if len(lines) > 7:
        with open('max_flood_%s.txt' % (job_id,), 'w') as f:
            f.write(HEADER)
            values = lines[START_VALUES:-1]
            col = 0
            for value in values:
                col += 1
                value = float(value)
                value = '1' if value > threshold else '0'
                if(col % NCOLS == 0):
                    value += '\n'
                else:
                    value += '\t'
                f.write(value)

def zip_floodmap(job_id):
    src = '../max_flood_1.prj'
    dst = 'max_flood_%s.prj' % (job_id,)
    shutil.copyfile(src, dst)

    with ZipFile('Max Flood.zip', 'w') as zip_file:
        zip_file.write(dst)
        zip_file.write('max_flood_%s.txt' % (job_id,))



def upload_to_geoserver(job_id):
    ## Paths
    raster_archive = 'Max Flood.zip'
    max_flood_sld = '../provo_max_flood.sld'

    ## Upload raster as coverage
    geoserver_engine.create_coverage_resource(
        store_id='dambreak:max_flood_%s' % (job_id,),
        coverage_file=raster_archive,
        coverage_type='arcgrid',
        debug=False,
        overwrite=True
    )

    ## Upload SLD style (if it doesn't exist)
    response = geoserver_engine.list_styles()

    if response['success']:
        styles = response['result']
        print(styles)
        if 'provo_max_flood' not in styles:
            with open(max_flood_sld, 'r') as sld:
                geoserver_engine.create_style(
                    style_id='provo_max_flood',
                    sld=sld.read()
                )

    ## Apply style to raster layer
    geoserver_engine.update_layer(
        layer_id='dambreak:max_flood_%s' % (job_id,),
        default_style='provo_max_flood'
    )

if __name__ == '__main__':
    prj = 'ProvoStochastic.prj'
    if len(sys.argv) == 2:
        job_id = sys.argv[1]
    else:
        job_id = 1
    main(prj, job_id)
