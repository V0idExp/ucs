from raylibpy.colors import BLACK, WHITE
from raylibpy.spartan import (draw_rectangle, draw_text_ex, get_font_default,
                              get_key_pressed, get_time, measure_text_ex)

from ucs.gfx import DrawCommand, StageID, RenderContext


MESSAGE_TIMEOUT = 3.0


class MessageDrawCommand(DrawCommand):

    def __init__(self, anchor_x: int, anchor_y: int, message: str) -> None:
        self.stage = StageID.UI
        self.order = 0
        self.message = message
        self.anchor_x = anchor_x
        self.anchor_y = anchor_y

    def draw(self):
        font = get_font_default()
        tw, th = measure_text_ex(font, self.message, 14.0, 1.0)
        tx = self.anchor_x - tw / 2
        ty = self.anchor_y - th / 2
        rx = tx - 10
        ry = ty - 10
        rw = tw + 20
        rh = th + 10
        draw_rectangle(rx, ry, rw, rh, WHITE)
        draw_text_ex(font, self.message, (tx, ty), 14.0, 1.0, BLACK)


class UI:

    prompt: bool = False  # is the UI currently waiting for prompt

    def __init__(self, width, height) -> None:
        self.message = None
        self.message_show_time = 0
        self.prompt = False
        self.width = width
        self.height = height

    def update(self) -> bool:
        has_message = self.message is not None
        timeout_elapsed = (get_time() - self.message_show_time) > MESSAGE_TIMEOUT
        any_key_pressed = get_key_pressed() != 0
        if has_message and (timeout_elapsed or any_key_pressed):
            self.message = None

        self.prompt = bool(self.message)
        return self.prompt

    def show_message(self, message: str) -> None:
        self.message = message
        self.message_show_time = get_time()

    def draw(self, ctx: RenderContext):
        if self.message is not None:
            anchor_x = self.width / 2
            anchor_y = self.height - 150
            ctx.append(MessageDrawCommand(anchor_x, anchor_y, self.message))


_instance: UI = None


def ui_init(width, height):
    global _instance
    _instance = UI(width, height)


def ui_get_instance() -> UI:
    return _instance
