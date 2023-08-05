from . import GoogleTiles
from .cached import Cache


class IGN(Cache, GoogleTiles):

    def __init__(self, layer_name, key=None):
        super(IGN, self).__init__()
        self.layer_name = layer_name
        self.params['headers'] = {
            "Accept": "image/webp,image/*,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "en-US,en;q=0.8,fr;q=0.6",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            # 'Host': 'wxs.ign.fr',
            'Referer': 'www.xoolive.org'
        }

        if key is None:
            self.key = '8scw06w0m9j6p8cu54e3bexa'
        # self.key = 'an7nvfzojv5wa96dsga5nk8w'

    def _image_url(self, tile):
        x, y, z = tile
        url = 'https://wxs.ign.fr/%s/geoportail/wmts?layer=%s&style=normal&tilematrixset=PM&Service=WMTS&Request=GetTile&Version=1.0.0&Format=image%%2Fjpeg&TileMatrix=%s&TileCol=%s&TileRow=%s' % (self.key, self.layer_name, z, x, y)
        # print(url)
        return url


class IGN_Standard(IGN):
    def __init__(self):
        super(IGN_Standard, self).__init__(
            layer_name='GEOGRAPHICALGRIDSYSTEMS.MAPS.SCAN-EXPRESS.STANDARD')


class IGN_Classique(IGN):
    def __init__(self):
        super(IGN_Classique, self).__init__(
            layer_name="GEOGRAPHICALGRIDSYSTEMS.MAPS.SCAN-EXPRESS.CLASSIQUE")


class IGN_Topo(IGN):
    def __init__(self):
        super(IGN_Topo, self).__init__(
            layer_name='GEOGRAPHICALGRIDSYSTEMS.MAPS.SCAN25TOUR')


class IGN_OACI(IGN):
    def __init__(self):
        super(IGN_OACI, self).__init__(
            layer_name='GEOGRAPHICALGRIDSYSTEMS.MAPS.SCAN-OACI')


class IGN_Routier(IGN):
    def __init__(self):
        super(IGN_Routier, self).__init__(
            layer_name='GEOGRAPHICALGRIDSYSTEMS.MAPS.SCAN-EXPRESS.ROUTIER')
