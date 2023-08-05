from typing import Tuple, List

import termcolor


class Boundary:
    def __init__(self, x: int, y: int, w: int, h: int):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return '%d,%d %dx%d' % (self.x, self.y, self.w, self.h)


class RasterCell:
    def __init__(self, character: str = ' ', origin: object = None, color: str = None, attrs: List[str] = None):
        self.character = character
        self.origin = origin
        self.color = color
        self.attrs = attrs

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class Raster:
    def __init__(self):
        self._cells = []
        self._default = RasterCell()

    def write(self, x: int, y: int, text, origin: object = None, color: str = None, attrs: List[str] = None):
        if type(text) is Raster:
            rastersize_x, rastersize_y = text.size()

            for ry in range(rastersize_y):
                for rx in range(rastersize_x):
                    cell = text.get(rx, ry)
                    self.write(x + rx, y + ry, origin=cell.origin, color=cell.color, attrs=cell.attrs,
                               text=cell.character)
        else:
            self._expand(x + len(text), y + 1)

            for i in range(len(text)):
                self._cells[y][x + i] = RasterCell(character=text[i], origin=origin, color=color, attrs=attrs)

    def draw_line(self, src_x, src_y, dst_x, dst_y, color: str = None, attrs: List[str] = None):
        med_x = int((src_x + dst_x) / 2)

        for x in range(src_x, dst_x):
            y = src_y if x < med_x else dst_y
            if self.get(x, y).character in ['|', '+']:
                self.write(x, y, '+', color=color, attrs=attrs)
            else:
                self.write(x, y, '-', color=color, attrs=attrs)

        for y in range(min(src_y, dst_y), max(src_y, dst_y)):
            if self.get(med_x, y).character != '+':
                self.write(med_x, y, '|', color=color, attrs=attrs)

        if src_y != dst_y:
            self.write(med_x, src_y, '+', color=color, attrs=attrs)
            self.write(med_x, dst_y, '+', color=color, attrs=attrs)

    def _expand(self, x, y):
        while len(self._cells) < y:
            self._cells.append([])

        while len(self._cells[y - 1]) < x:
            self._cells[y - 1].append(self._default)

    def get(self, x: int, y: int) -> RasterCell:
        if y >= 0 and y < len(self._cells) and x >= 0 and x < len(self._cells[y]):
            return self._cells[y][x]
        else:
            return self._default

    def size(self) -> Tuple[int]:
        if len(self._cells) == 0:
            return 0, 0
        else:
            return max([len(l) for l in self._cells]), len(self._cells)

    def origin_bounds(self, origin: object) -> Boundary:
        raster_w, raster_h = self.size()

        b_x, b_y, b_w, b_h = 0, 0, 0, 0

        for y in range(raster_h):
            for x in range(raster_w):
                cell = self.get(x, y)
                if origin == cell.origin:
                    if b_w == 0:
                        b_x, b_y, b_w, b_h = x, y, 1, 1
                    else:
                        if x >= b_x + b_w:
                            b_w = x - b_x + 1

                        if y >= b_y + b_h:
                            b_h = y - b_y + 1

        return Boundary(b_x, b_y, b_w, b_h) if b_w > 0 else None

    def text(self, color: bool = False):
        text = ''

        for line in self._cells:
            for c in line:
                if color and c.color:
                    text += termcolor.colored(c.character, c.color, attrs=c.attrs)
                else:
                    text += c.character

            text += '\n'

        return text

    def __str__(self):
        return self.text()
