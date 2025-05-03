import pygame


class Selection:

    def __init__(self, x, y, length, tile_size, tile_data=None):
        self.x, self.y = x, y
        self.buffer_index = (20, 0)
        self.width = length
        self.height = length
        self.line_length = 1 / 5 * length
        self.line_width = int(self.line_length / 4)
        self.h_width = self.width / 2
        self.h_height = self.height / 2
        self.hitbox = pygame.Rect((x, y, self.width, self.height))
        self.surface = pygame.Surface((self.width, self.height))

        self.tile_size = tile_size

        self.colors = [(33, 44, 82), (200, 49, 49), (100, 0, 0)]
        self.board_length = 5 * tile_size + 5
        self.board_pos = 0
        self.hovered_over = False
        self.clicked_on = False

        if tile_data is None:
            self.tile_data = [[0 for i in range(5)] for j in range(5)]
            self.blank = True
        else:
            self.tile_data = tile_data
            self.blank = False
            self.restore_data()
            self.create_tile_surface()

    def __repr__(self):
        return_str = ""
        for i in self.tile_data:
            for n in i:
                if n == 1:
                    return_str += "1"
                else:
                    return_str += " "
            return_str += '\n'
        return return_str

    def draw_selection(self):
        if self.blank:
            self.surface.fill((66, 93, 159))
            if not self.hovered_over:
                pygame.draw.rect(self.surface, (24, 36, 74), (0, 0, self.width, self.height), self.line_width)
                pygame.draw.line(self.surface, (24, 36, 74), (self.h_width, self.line_length),
                                 (self.h_width, self.height - self.line_length), self.line_width)
                pygame.draw.line(self.surface, (24, 36, 74), (self.line_length, self.h_height),
                                 (self.width - self.line_length, self.h_height), self.line_width)
            else:
                pygame.draw.rect(self.surface, (24, 36, 74), (0, 0, self.width, self.height))
        return self.surface

    def draw_selection_screen(self, screen):
        self.create_selection()

        screen.fill((66, 93, 159))

        board_surf = pygame.Surface((self.board_length, self.board_length))
        board_surf.fill((66, 93, 159))
        pygame.draw.rect(board_surf, (24, 36, 74), (0, 0, self.board_length, self.board_length))

        side_length = self.tile_size - (self.tile_size / 12)

        for i, row in enumerate(self.tile_data):
            for j, col in enumerate(row):
                pygame.draw.rect(board_surf, (self.colors[col]),
                                 (i * self.tile_size + 5, j * self.tile_size + 5, side_length, side_length),
                                 border_radius=4)

        screen.blit(board_surf, (self.board_pos, self.board_pos))

    def create_selection(self):
        if self.buffer_index[0] != 20:
            self.tile_data[self.buffer_index[0]][self.buffer_index[1]] = 0

        mouse_x, mouse_y = pygame.mouse.get_pos()
        if 0 < mouse_x < self.board_length - 5 and 0 < mouse_y < self.board_length - 5:
            row = int(mouse_x // self.tile_size)
            col = int(mouse_y // self.tile_size)

            click = pygame.mouse.get_pressed()

            if self.tile_data[row][col] != 1:
                self.tile_data[row][col] = 2

                if click[0]:
                    self.tile_data[row][col] = 1
                    self.buffer_index = (20, col)
                    self.blank = False
                else:
                    self.buffer_index = (row, col)

            if click[2]:
                self.tile_data[row][col] = 0
                self.blank = sum(sum(row) for row in self.tile_data) == 0

        keys = pygame.key.get_pressed()
        if keys[pygame.K_e]:
            self.create_tile_surface()
            self.clicked_on = False

    def trim_data(self):
        self.restore_data()
        if self.buffer_index[0] != 20:
            self.tile_data[self.buffer_index[0]][self.buffer_index[1]] = 0

        trimmed_x = []
        min_x = 6
        max_x = -1
        for n, i in enumerate(self.tile_data):
            if sum(i) != 0:
                min_x = min(min_x, n)
                max_x = max(max_x, n)

        for i in range(min_x, max_x+1):
            trimmed_x.append(self.tile_data[i])

        min_y = 6
        max_y = -1
        for i in range(5):
            if sum([j[i] for j in self.tile_data]) != 0:
                min_y = min(min_y, i)
                max_y = max(max_y, i)

        trimmed = []
        for row in trimmed_x:
            trimmed.append(row[min_y:max_y+1])

        self.tile_data = trimmed

    def restore_data(self):
        dim_x = len(self.tile_data)
        dim_y = len(self.tile_data[0])

        for i in self.tile_data:
            i.extend([0] * (5-dim_y))

        for i in range(5-dim_x):
            self.tile_data.append([0] * 5)

    def hover_surface(self, tile_size, color):
        self.trim_data()
        length = max(len(self.tile_data), len(self.tile_data[0]))
        length *= tile_size
        surf = pygame.Surface((length, length), pygame.SRCALPHA, 32)
        surf = surf.convert_alpha()
        surf.fill((0, 0, 0, 0))

        for i, row in enumerate(self.tile_data):
            for j, col in enumerate(row):
                if col == 1:
                    pygame.draw.rect(surf,
                                     color,
                                     (i * tile_size, j * tile_size, tile_size,
                                      self.tile_size),
                                     border_radius=4)

        return surf

    def create_tile_surface(self):
        self.trim_data()

        try:
            self.surface.fill((66, 93, 159))
            surface_tile_size = self.width/max(len(self.tile_data), len(self.tile_data[0]))

            for i, row in enumerate(self.tile_data):
                for j, col in enumerate(row):
                    if col == 1:
                        pygame.draw.rect(self.surface,
                                         (self.colors[col]),
                                         (i * surface_tile_size, j * surface_tile_size, surface_tile_size, surface_tile_size),
                                         border_radius=4)

        except IndexError:
            self.blank = True
            self.tile_data = [[0 for i in range(5)] for j in range(5)]
