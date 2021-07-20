from typing import Any, Sequence

import pytmx
from raylibpy.colors import BLACK, RED, WHITE
from raylibpy.consts import PIXELFORMAT_UNCOMPRESSED_GRAYSCALE
from raylibpy.spartan import (gen_image_color, image_draw_pixel, image_format,
                              load_texture, load_texture_from_image,
                              unload_image)

from ucs.foundation import Position
from ucs.gfx import (DrawRectOutlineCommand, DrawTextureRectCommand,
                     RenderContext, gfx_set_map_params)


class TileMap:

    def __init__(self, filename) -> None:
        self.textures = {}
        self.map = pytmx.TiledMap(filename, self._image_loader)
        self.x = 0
        self.y = 0

        try:
            entry = self.map.objects_by_name['entry']
            entry_x = entry.x // self.map.tilewidth * self.map.tilewidth
            entry_y = entry.y // self.map.tileheight * self.map.tileheight
            self.entry = entry_x, entry_y

        except KeyError:
            raise ValueError(f'no entry point defined for map {filename}')

        non_walkable_tiles = {
            k for k, props in self.map.tile_properties.items()
            if props.get('type') == 'obstacle'
        }

        # walkability matrix
        self.walk_matrix = [True] * self.map.width * self.map.height

        # map of occupants for each tile
        self.occupants = [None] * self.map.width * self.map.height

        # image for foreground mask texture
        img = gen_image_color(self.map.width, self.map.height, WHITE)

        # iterate over the layers and initialize the walkability matrix and the
        # foreground mask
        for row in range(self.map.height):
            for col in range(self.map.width):
                for layer in self.map.layers:
                    if 'meta' in layer.name:
                        continue

                    tile_id = layer.data[row][col]
                    tile = self.map.images[tile_id]

                    # draw a black pixel on the mask if there's a tile on the
                    # foreground layer
                    if layer.properties.get('foreground', False) and tile is not None:
                        image_draw_pixel(img, col, row, BLACK)

                    # flag the current cell in the walk matrix as non-walkable
                    # if the tile id is in the set of non-walkable tiles
                    if tile_id in non_walkable_tiles:
                        self.walk_matrix[row * self.map.width + col] = False

        # convert the mask image to 1-byte grayscale format and create a texture
        # from it for the shader
        image_format(img, PIXELFORMAT_UNCOMPRESSED_GRAYSCALE)
        tex = load_texture_from_image(img)
        unload_image(img)
        self.foreground_mask_texture = tex

    def pixels_to_coords(self, pixels_pos: Position) -> Position:
        col = int((pixels_pos[0] - self.x) // self.map.tilewidth)
        row = int((pixels_pos[1] - self.y) // self.map.tileheight)
        return col, row

    def is_walkable_at(self, col, row) -> bool:
        if col >= 0 and col < self.map.width and row >= 0 and row < self.map.height:
            index = row * self.map.width + col
            return self.walk_matrix[index] and not self.occupants[index]
        return False

    def set_occupant_at(self, col: int, row: int, occupant: Any):
        if col >= 0 and col < self.map.width and row >= 0 and row < self.map.height:
            self.occupants[row * self.map.width + col] = occupant

    def get_occupant_at(self, col: int, row: int) -> Any:
        if col >= 0 and col < self.map.width and row >= 0 and row < self.map.height:
            return self.occupants[row * self.map.width + col]
        return None

    def get_nearest_occupants(self, col, row) -> Sequence[Any]:
        adjacent_coords = [(col - 1, row), (col + 1, row), (col, row - 1), (col, row + 1)]
        for coord in adjacent_coords:
            actor = self.get_occupant_at(*coord)
            if actor is not None:
                yield actor

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

        for i, occupant in enumerate(self.occupants):
            if occupant is None:
                continue
            w = self.map.tilewidth
            h = self.map.tileheight
            x = self.x + (i % self.map.width) * w
            y = self.y + (i // self.map.width) * h
            ctx.append(DrawRectOutlineCommand(1e6, (x, y, w, h), RED))

    def _image_loader(self, filename, flags, **kwargs):
        if filename not in self.textures:
            self.textures[filename] = load_texture(filename)

        def load(rect=None, flags=None):
            return filename, rect, flags

        return load


_active_tilemap: TileMap = None


def tilemap_set_active(tilemap: TileMap):
    global _active_tilemap
    _active_tilemap = tilemap

    gfx_set_map_params(
        tilemap.foreground_mask_texture,
        (tilemap.map.tilewidth, tilemap.map.tileheight),
        (tilemap.map.width, tilemap.map.height))


def tilemap_get_active() -> TileMap:
    return _active_tilemap
