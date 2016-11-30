from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from json import dumps as jdumps
import numpy as np
from tethys_sdk.gizmos import *

from .model import SessionMaker, Dam
from .utilities import generate_flood_hydrograph, write_hydrograph_input_file

@login_required()
def home(request):
    """
    Controller for the app home page.
    """
    peak_flow_slider = RangeSlider(
                display_text='Peak Flow (cms)',
                name='peak_flow',
                min=500,
                max=2400,
                initial=800,
                step=50
    )

    time_peak_slider = RangeSlider(
                display_text='Time to Peak (hrs.)',
                name='time_to_peak',
                min=1,
                max=12,
                initial=6,
                step=1
    )

    peak_duration_slider = RangeSlider(
                display_text='Peak Duration (hrs.)',
                name='peak_duration',
                min=1,
                max=12,
                initial=6,
                step=1
    )

    falling_limb_duration = RangeSlider(
                display_text='Falling Limb Duration (hrs.)',
                name='falling_limb_duration',
                min=48,
                max=96,
                initial=72,
                step=1
    )

    submit_button = Button(
                display_text='Generate Hydrograph',
                name='submit',
                attributes='form=hydrograph-form',
                submit=True
    )

    context = {'peak_flow_slider': peak_flow_slider,
               'time_peak_slider': time_peak_slider,
               'peak_duration_slider': peak_duration_slider,
               'falling_limb_duration': falling_limb_duration,
               'submit_button': submit_button
    }

    return render(request, 'dam_break/home.html', context)

@login_required()
def hydrograph(request):
    """
    Controller for the hydrograph page.
    """
    # Default Values
    peak_flow = 800.0
    time_to_peak = 6
    peak_duration = 6
    falling_limb_duration = 24

    if request.POST  and 'submit' in request.POST:
        peak_flow = float(request.POST['peak_flow'])
        time_to_peak = int(request.POST['time_to_peak'])
        peak_duration = int(request.POST['peak_duration'])
        falling_limb_duration = int(request.POST['falling_limb_duration'])

    # Generate hydrograph
    hydrograph = generate_flood_hydrograph(
        peak_flow=peak_flow, 
        time_to_peak=time_to_peak, 
        peak_duration=peak_duration, 
        falling_limb_duration=falling_limb_duration
    )

    # Write GSSHA file
    write_hydrograph_input_file(
        username=request.user.username, 
        hydrograph=hydrograph                  
    )

    # Configure the Hydrograph Plot View
    flood_plot = TimeSeries(
        title='Flood Hydrograph',
        y_axis_title='Flow',
        y_axis_units='cms',
        series=[
           {
               'name': 'Flood Hydrograph',
               'color': '#0066ff',
               'data': hydrograph,
           },
        ],
        width='100%',
        height='500px'
    )

    context = {'flood_plot': flood_plot}

    return render(request, 'dam_break/hydrograph.html', context)

@login_required()
def map(request):
    """
    Controller to handle map page.
    """
    # Create a session
    session = SessionMaker()

    # Query DB for dam objects
    dams = session.query(Dam).all()

    # Transform into GeoJSON format
    features = []
    lat_list = []
    lon_list = []
    for dam in dams:
        lon_list.append(dam.longitude)
        lat_list.append(dam.latitude)
        dam_feature = {
          'type': 'Feature',
          'geometry': {
            'type': 'Point',
            'coordinates': [dam.longitude, dam.latitude]
          },
          'properties': {
              'peak_flow' : dam.peak_flow,
              'time_peak' : dam.time_peak,
              'peak_duration' : dam.peak_duration,
              'falling_limb_duration' : dam.falling_limb_duration,
          }
        }

        features.append(dam_feature)

    #make sure you close the session
    session.close()
    
    geojson_gages = {
      'type': 'FeatureCollection',
      'crs': {
        'type': 'name',
        'properties': {
          'name': 'EPSG:4326'
        }
      },
      'features': features
    }

    # Define layer for Map View
    delta = 0.01
    geojson_layer = MVLayer(source='GeoJSON',
                            options=geojson_gages,
                            legend_title='Dam Locations',
                            legend_extent=[min(lon_list)-delta, min(lat_list)-delta, max(lon_list)+delta, max(lat_list)+delta],
                            feature_selection=True)

    # Define initial view for Map View
    view_options = MVView(
        projection='EPSG:4326',
        center=[sum(lon_list)/float(len(lon_list)), sum(lat_list)/float(len(lat_list))],
        zoom=10,
        maxZoom=18,
        minZoom=2,
    )

    # Configure the map
    map_options = MapView(height='500px',
                          width='100%',
                          layers=[geojson_layer],
                          view=view_options,
                          basemap='OpenStreetMap',
                          legend=True,
                          )

    hydrograph_box = MessageBox(name='hydrograph_modal',
                                title='Flood Hydrograph',
                                message='Loading ...')
                            
    # Pass variables to the template via the context dictionary
    context = {'map_options': map_options,
               'hydrograph_box': hydrograph_box}

    return render(request, 'dam_break/map.html', context)

@login_required()
def table(request):
    """
    Controller to handle table page.
    """
    # Create a session
    session = SessionMaker()

    # Query DB for dam objects
    dams = session.query(Dam).all()

    # Pass variables to the template via the context dictionary
    context = {'dams': dams}
    
    rendered_page = render(request, 'dam_break/table.html', context)
    
    #make sure you close the session before exiting
    session.close()
    
    return rendered_page

@login_required()
def hydrograph_ajax(request):
    """
    Controller for the hydrograph ajax request.
    """
    # Default Values
    peak_flow = 800.0
    time_to_peak = 6
    peak_duration = 6
    falling_limb_duration = 24

    if request.GET:
        peak_flow = float(request.GET['peak_flow'])
        time_to_peak = int(request.GET['time_to_peak'])
        peak_duration = int(request.GET['peak_duration'])
        falling_limb_duration = int(request.GET['falling_limb_duration'])

    # Generate hydrograph
    hydrograph = generate_flood_hydrograph(
        peak_flow=peak_flow, 
        time_to_peak=time_to_peak, 
        peak_duration=peak_duration, 
        falling_limb_duration=falling_limb_duration
    )

    # Configure the Hydrograph Plot View
    flood_plot = TimeSeries(
        engine='highcharts',
        title='Flood Hydrograph',
        y_axis_title='Flow',
        y_axis_units='cms',
        series=[
           {
               'name': 'Flood Hydrograph',
               'color': '#0066ff',
               'data': hydrograph,
           },
        ],
        width='500px',
        height='500px'
    )

    context = {'flood_plot': flood_plot}

    return render(request, 'dam_break/hydrograph_ajax.html', context)

@login_required()
def raster_map(request):
    """
    Controller for the raster_map request.
    """
    
    lat_list = np.arange(30, 31, 0.1)   
    lon_list = np.arange(-92, -90, 0.2)

    features = []
    for lat_idx in xrange(len(lat_list)-1):
        for lon_idx in xrange(len(lon_list)-1):
            features.append({
              'type': 'Feature',
              'geometry': {
                'type': 'Polygon',
                'coordinates': [
                                 [[lon_list[lon_idx], lat_list[lat_idx]], 
                                  [lon_list[lon_idx+1], lat_list[lat_idx]], 
                                  [lon_list[lon_idx+1], lat_list[lat_idx+1]], 
                                  [lon_list[lon_idx], lat_list[lat_idx+1]], 
                                  [lon_list[lon_idx], lat_list[lat_idx]]]
                               ]
              },
              'properties': {
                  'elevation' : np.random.rand()*100,
              }
            })

    raster_json = {
      'type': 'FeatureCollection',
      'crs': {
        'type': 'name',
        'properties': {
          'name': 'EPSG:4326'
        }
      },
      'features': features
    }
    
    
    context = {'raster_json': jdumps(raster_json)}

    return render(request, 'dam_break/raster_map.html', context)
