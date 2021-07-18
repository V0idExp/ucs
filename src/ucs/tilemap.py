import pytmx
from raylibpy.colors import BLACK, WHITE
from raylibpy.consts import PIXELFORMAT_UNCOMPRESSED_GRAYSCALE
from raylibpy.spartan import (gen_image_color, image_draw_pixel, image_format,
                              load_texture, load_texture_from_image,
                              unload_image)

from ucs.gfx import DrawTextureRectCommand, RenderContext, gfx_set_map_params


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

    def is_walkable_at(self, col, row) -> bool:
        return self.walk_matrix[row * self.map.width + col]

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
