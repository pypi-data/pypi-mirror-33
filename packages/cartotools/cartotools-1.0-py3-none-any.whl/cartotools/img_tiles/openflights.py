from . import GoogleTiles
from .cached import Cache


class OpenFlight1806(Cache, GoogleTiles):

    extension = ".png"

    def _image_url(self, tile):
        x, y, z = tile
        url = (
            "https://snapshots.openflightmaps.org/live/1806/tiles/world/noninteractive/epsg3857/merged/512/latest/%s/%s/%s.png"
            % (z, x, y)
        )
        return url
