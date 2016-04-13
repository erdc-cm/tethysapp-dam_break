from tethys_sdk.base import TethysAppBase, url_map_maker
from tethys_sdk.stores import PersistentStore

class DamBreak(TethysAppBase):
    """
    Tethys app class for Dam Break.
    """

    name = 'Dam Break'
    index = 'dam_break:home'
    icon = 'dam_break/images/icon.gif'
    package = 'dam_break'
    root_url = 'dam-break'
    color = '#1abc9c'
    description = 'Place a brief description of your app here.'
    enable_feedback = False
    feedback_emails = []

        
    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (UrlMap(name='home',
                           url='dam-break',
                           controller='dam_break.controllers.home'),
                    UrlMap(name='hydrograph',
                           url='dam-break/hydrograph',
                           controller='dam_break.controllers.hydrograph'),
                    UrlMap(name='map',
                           url='dam-break/map',
                           controller='dam_break.controllers.map'),
                    UrlMap(name='hydrograph_ajax',
                           url='dam-break/map/hydrograph',
                           controller='dam_break.controllers.hydrograph_ajax'),
                    UrlMap(name='table',
                           url='dam-break/table',
                           controller='dam_break.controllers.table'),
        )

        return url_maps
        
    def persistent_stores(self):
        """
        Add one or more persistent stores
        """
        stores = (PersistentStore(name='dam_info_db',
                                  initializer='dam_break.init_stores.init_dam_info_db',
                                  spatial=True
                ),
        )

        return stores