from concurrent import futures
import numpy as np
from cartopy.io.img_tiles import _merge_tiles


class Parallel(object):

    def one_image(self, tile):
        img, extent, origin = self.get_image(tile)
        img = np.array(img)
        x = np.linspace(extent[0], extent[1], img.shape[1])
        y = np.linspace(extent[2], extent[3], img.shape[0])
        return [img, x, y, origin]

    def image_for_domain(self, target_domain, target_z):
        tiles = []
        with futures.ThreadPoolExecutor(max_workers=20) as executor:
            todo = {}
            for tile in self.find_images(target_domain, target_z):
                future = executor.submit(self.one_image, tile)
                todo[future] = tile

            done_iter = futures.as_completed(todo)
            for future in done_iter:
                try:
                    res = future.result()
                except IOError:
                    continue
                tiles.append(res)
        img, extent, origin = _merge_tiles(tiles)
        return img, extent, origin
