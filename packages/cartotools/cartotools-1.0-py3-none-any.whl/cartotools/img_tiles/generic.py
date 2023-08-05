from . import GoogleTiles
from .cached import Cache

class AppleTiles(Cache, GoogleTiles):

    def _image_url(self, tile):
        x, y, z = tile
        return "http://gsp2.apple.com/tile?api=1&style=slideshow&layers=default&z=%s&x=%s&y=%s&v=10" % (z, x, y)

