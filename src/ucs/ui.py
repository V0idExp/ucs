from raylibpy.colors import BLACK, WHITE
from raylibpy.spartan import (draw_rectangle, draw_text_ex, get_font_default,
                              get_key_pressed, get_time, measure_text_ex)


class UI:

    prompt: bool = False  # is the UI currently waiting for prompt

    def __init__(self, width, height) -> None:
        self.message = None
        self.message_show_time = None
        self.prompt = False
        self.width = width
        self.height = height

    def update(self):
        if self.message is not None \
           and (get_time() - self.message_show_time) > 1.0 \
           and get_key_pressed() != 0:
            self.message = None
            self.message_show_time = None

        if self.message is not None:
            anchor_x = self.width / 2
            anchor_y = self.height - 150
            font = get_font_default()
            tw, th = measure_text_ex(font, self.message, 14.0, 1.0)
            tx = anchor_x - tw / 2
            ty = anchor_y - th / 2
            rx = tx - 10
            ry = ty - 10
            rw = tw + 20
            rh = th + 10
            draw_rectangle(rx, ry, rw, rh, WHITE)
            draw_text_ex(font, self.message, (tx, ty), 14.0, 1.0, BLACK)
            self.prompt = True
        else:
            self.prompt = False

    def show_message(self, message: str) -> None:
        self.message = message
        self.message_show_time = get_time()
