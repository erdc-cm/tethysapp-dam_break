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
    var getModalHTML;


    /************************************************************************
     *                    PRIVATE FUNCTION IMPLEMENTATIONS
     *************************************************************************/
    getModalHTML = function() {
        $.ajax({
            url: 'hydrograph',
            method: 'GET',
            data: {
                'peak_flow': m_selected_feature.get('peak_flow'),
                'time_to_peak': m_selected_feature.get('time_peak'),
                'peak_duration': m_selected_feature.get('peak_duration'),
                'falling_limb_duration': m_selected_feature.get('falling_limb_duration'),
            },
            success: function(data) {
                // add plot data to modal
                $("#hydrograph_modal").find('.modal-body').html(data);
                // display modal
                $('#hydrograph_modal').modal('show');    
                //Initialize Plot
                TETHYS_PLOT_VIEW.initHighChartsPlot($('.highcharts-plot'));
            }
        });
    };

    /************************************************************************
    *                  INITIALIZATION / CONSTRUCTOR
    *************************************************************************/
    
    $(function() {

        //var overview_map = new ol.control.OverviewMap(),
        //overview_map.setMap(m_map);
        m_select_interaction = TETHYS_MAP_VIEW.getSelectInteraction();
        //to make sure that you always get something on click
        var map = TETHYS_MAP_VIEW.getMap();
        map.on("click", function(evt) {
            var feature_collection = m_select_interaction.getFeatures();
            if(feature_collection.getArray().length <=0) {
                this.getLayers().forEach(function(layer, i) {
                    var source = layer.getSource()
                    if (source instanceof ol.source.Vector) {
                        var closest_feature = source.getClosestFeatureToCoordinate(evt.coordinate);
                        feature_collection.push(closest_feature);
                    }
                });
            }

        });

        //when selected, call function to make hydrograph
        m_select_interaction.getFeatures().on('change:length', function(e) {
            if (e.target.getArray().length > 0) {
                // this means there is at least 1 feature selected
                m_selected_feature = e.target.item(0); // 1st feature in Collection
                getModalHTML();
            }
        });
        $('#hydrograph_modal').on('hidden.bs.modal', function () {
            m_select_interaction.getFeatures().clear(); //clear selection on close
        });
    }); //document ready
}()); // End of package wrapper 