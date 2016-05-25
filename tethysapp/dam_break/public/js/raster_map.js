/*****************************************************************************
 *                      LIBRARY WRAPPER
 *****************************************************************************/

var MAP_DAM_BREAK = (function() {
    // Wrap the library in a package function
    "use strict"; // And enable strict mode for this library
    
    /************************************************************************
    *                      MODULE LEVEL / GLOBAL VARIABLES
    *************************************************************************/
    var m_select_interaction, m_selected_feature;

    /************************************************************************
     *                    PRIVATE FUNCTION DECLARATIONS
     *************************************************************************/
    var getStyleColor;


    /************************************************************************
     *                    PRIVATE FUNCTION IMPLEMENTATIONS
     *************************************************************************/
    getStyleColor = function(value) {
        if (value > 75)
            return [64,196,64,1];
        else if (value > 50)
            return [108,152,64,1];
        else if (value > 25)
            return [152,108,64,1];
        else
            return [196,32,32,1];
    };

    /************************************************************************
    *                  INITIALIZATION / CONSTRUCTOR
    *************************************************************************/
    
    $(function() {

        var raster = new ol.layer.Tile({
          source: new ol.source.MapQuest({layer: 'sat'})
        });
        

        // a default style is good practice!
        var defaultStyle = new ol.style.Style({
          fill: new ol.style.Fill({
            color: [250,250,250,1]
          }),
          stroke: new ol.style.Stroke({
            color: [220,220,220,1],
            width: 1
          })
        });

        // a javascript object literal can be used to cache
        // previously created styles. Its very important for
        // performance to cache styles.
        var styleCache = {};
        // the style function returns an array of styles
        // for the given feature and resolution.
        // Return null to hide the feature.
        function styleFunction(feature, resolution) {
          // get the incomeLevel from the feature properties
          var elevation = feature.get('elevation');
          // if there is no level or its one we don't recognize,
          // return the default style (in an array!)
          if (!elevation) {
            return [defaultStyle];
          }
          // check the cache and create a new style for the income
          // level if its not been created before.
          if (!styleCache[elevation]) {
 
            var style_color = getStyleColor(elevation);
            styleCache[elevation] = new ol.style.Style({
              fill: new ol.style.Fill({
                color: style_color
              }),
              stroke: defaultStyle.stroke
            });
          }
          // at this point, the style for the current level is in the cache
          // so return it (as an array!)
          return [styleCache[elevation]];
        }

        //load data passed from controller to vector
        var collection = $('#raster_map').data('raster_json');
        var format = new ol.format.GeoJSON();

        var vectorSource = new ol.source.Vector({
            features: format.readFeatures(collection,
            {featureProjection:"EPSG:3857"})
        });
        
        var vector = new ol.layer.Image({
                    source: new ol.source.ImageVector({
                        source: vectorSource,
                        style: styleFunction
                    })
        });
        
        // select interaction working on "mousemove"
        var selectMouseMove = new ol.interaction.Select({
          condition: ol.events.condition.mouseMove,
            style: new ol.style.Style({
                            fill: new ol.style.Stroke({
                                color: 'blue',
                                width: 1
                            }),
                            stroke: new ol.style.Stroke({
                                color: '#fff',
                                width: 1
                            })
                        })
        });
        

        var map = new ol.Map({
          layers: [raster, vector],
          interactions: ol.interaction.defaults().extend([
              selectMouseMove,
          ]),
          target: 'raster_map',
          view: new ol.View({
            center: ol.proj.transform([-91, 30.5], 'EPSG:4326', 'EPSG:3857'),
            zoom: 8
          })
        });

    }); //document ready
}()); // End of package wrapper 