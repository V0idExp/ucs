from typing import NamedTuple, Sequence

import pytmx
from raylibpy.colors import BLACK, WHITE
from raylibpy.consts import PIXELFORMAT_UNCOMPRESSED_GRAYSCALE
from raylibpy.spartan import (gen_image_color, image_draw_pixel, image_format,
                              load_texture, load_texture_from_image,
                              unload_image)

from ucs.foundation import Pos, Rect
from ucs.gfx import DrawTextureRectCommand, RenderContext


class Tile(NamedTuple):

    tile_id: int
    rect: Rect


class TileMap:

    def __init__(self, filename) -> None:
        self.textures = {}
        self.map = pytmx.TiledMap(filename, self._image_loader)
        self.x = 0
        self.y = 0

        try:
            self.entry = self.map.objects_by_name['entry']
        except KeyError:
            raise ValueError(f'no entry point defined for map {filename}')

        self.non_walkable_tiles = {
            k for k, props in self.map.tile_properties.items()
            if props.get('type') == 'obstacle'
        }

        # create the mask of foreground tiles on the GPU, for applying silouette
        # effects on sprites rendered "behind" foreground (walls, etc.)
        img = gen_image_color(self.map.width, self.map.height, WHITE)
        for row in range(self.map.height):
            for col in range(self.map.width):
                for layer in self.map.layers:
                    if not layer.properties.get('foreground', False):
                        continue
                    tile_id = layer.data[row][col]
                    tile = self.map.images[tile_id]
                    if tile is not None:
                        image_draw_pixel(img, col, row, BLACK)

        image_format(img, PIXELFORMAT_UNCOMPRESSED_GRAYSCALE)
        tex = load_texture_from_image(img)
        unload_image(img)
        self.foreground_mask_texture = tex

    def is_walkable_at(self, point) -> bool:
        for tile in self.tiles_at(point):
            if tile.tile_id in self.non_walkable_tiles:
                return False
        return True

    def tiles_at(self, point: Pos) -> Sequence[Tile]:
        x, y = point
        x -= self.x
        y -= self.y
        row = int(y // self.map.tilewidth)
        col = int(x // self.map.tileheight)
        visited = set()
        for layer in self.map.layers:
            if 'meta' in layer.name.lower():
                continue
            tile_id = layer.data[row][col]
            tile = self.map.images[tile_id]
            if tile is not None and tile_id not in visited:
                visited.add(tile_id)
                w, h = tile[1][2:]
                x0 = self.x + col * self.map.tilewidth
                y0 = self.y + row * self.map.tileheight
                yield Tile(tile_id, (x0, y0, w, h))

    def draw(self, ctx: RenderContext):
        tile_width = self.map.tilewidth
        tile_height = self.map.tileheight

        for layer in self.map.layers:
            name = layer.name.lower()
            if any(skip in name for skip in ('meta', 'obstacles')):
                continue

            for r, row in enumerate(layer.data):
                y_offset = self.y + r * tile_width
                for c, col in enumerate(row):
                    x_offset = self.x + c * tile_height
                    if self.map.images[col] is not None:
                        filename, rect, _ = self.map.images[col]
                        tex = self.textures[filename]
                        ctx.append(DrawTextureRectCommand(
                            r * self.map.width + c, tex, rect, (x_offset, y_offset)))

    def _image_loader(self, filename, flags, **kwargs):
        if filename not in self.textures:
            self.textures[filename] = load_texture(filename)

        def load(rect=None, flags=None):
            return filename, rect, flags

        return load
