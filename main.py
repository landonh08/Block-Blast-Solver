import pygame
from tile import Selection
from ai import *


class Game:
    def __init__(self):
        pygame.init()

        self.board = [[0 for j in range(8)] for i in range(8)]
        # blue-blank, red-block color, green-where to place tile
        self.colors = {
            0: (33, 44, 82),
            1: (200, 49, 49),
        }

        self.screen_width, self.screen_height = pygame.display.Info().current_w / 2, pygame.display.Info().current_h / 2

        self.min_len = min(self.screen_width, self.screen_height)

        self.board_length = (4 / 5) * self.min_len + 5
        self.board_pos = (self.min_len - self.board_length) / 2

        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.tile_size = self.min_len / 10

        self.selection_length = self.min_len / 4
        self.selection_x = (self.board_pos + self.board_length +
                            ((self.screen_width - (
                                    self.board_pos + self.board_length)) / 2 - self.selection_length / 2))

        self.selections = [Selection(self.selection_x,
                                     self.board_pos + i * ((self.board_length - self.selection_length * 3) / 2 +
                                                           self.selection_length), self.selection_length,
                                     self.tile_size)
                           for i in range(3)]
        self.blanks = [True, True, True]

        self.creating_tile = False
        self.clicked_tile = 0

        self.selected_tile = None
        self.selected_tile_row = None
        self.selected_tile_col = None
        self.selected_tile_index = None

        self.mouse_hitbox = pygame.Rect(0, 0, 1, 1)

        self.clicked = False  # left mouse button
        self.clicked_2 = False  # right mouse button
        self.try_to_solve = True  # used to make sure the algorithm doesn't run over and over again

        self.place_timer = 0  # prevents the user from placing a block right after a tile was placed

        self.solved_board = None

        self.visual_overlay = []

        self.font = pygame.font.SysFont('arial', 30)

    def main(self):
        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        self.save_edge_case()

            keys = pygame.key.get_pressed()
            for i in range(10):
                if keys[pygame.K_0 + i]:
                    self.load_edge_case(i)

            mouse = pygame.mouse.get_pos()
            self.mouse_hitbox.x, self.mouse_hitbox.y = mouse[0], mouse[1]

            clicks = pygame.mouse.get_pressed()

            self.clicked, self.clicked_2 = clicks[0], clicks[2]

            if self.visual_overlay and all(self.blanks):
                self.visual_overlay.clear()

            if not any(self.blanks) and self.try_to_solve:  # when three tiles have been created
                print("Trying to solve")
                solution = make_moves(self.board, self.selections)
                if solution[0] is not None:
                    self.solved_board, self.visual_overlay = solution
                self.try_to_solve = False

            self.draw_screen()

            if self.clicked and self.selected_tile_row is not None and not self.creating_tile:
                replace = add_tile(self.board, self.selected_tile.tile_data, self.selected_tile_row,
                                   self.selected_tile_col, is_human=True)
                if replace[0]:
                    self.place_timer = 100  # starts the place timer
                    self.reset_hand()
                    # refreshes the selection
                    self.selections[self.selected_tile_index] = Selection(self.selection_x,
                                                                          self.board_pos + self.selected_tile_index * ((
                                                                                                                               self.board_length - self.selection_length * 3) / 2 +
                                                                                                                       self.selection_length),
                                                                          self.selection_length, self.tile_size)
                    self.selected_tile_index = None

            if self.place_timer != 0:
                self.place_timer -= 1
            self.board = check_clear(self.board)[0]

    def draw_screen(self):
        if not self.creating_tile:
            self.draw_board()
            self.update_tiles()
            if self.selected_tile is not None:
                self.screen.blit(
                    self.selected_tile.hover_surface(self.tile_size - (self.tile_size / 12) + 5, (200, 49, 49)),
                    (self.mouse_hitbox[0], self.mouse_hitbox[1]))
        else:
            self.clicked_tile.draw_selection_screen(self.screen)
            self.creating_tile = self.clicked_tile.clicked_on
        pygame.display.update()

    def save_edge_case(self):
        with open("cases.txt", "a+") as c:
            board_string = ""
            for row in self.board:
                row_string = "".join(map(str, row))
                board_string += row_string

            board_string += "|"

            for s in self.selections:
                data = s.tile_data
                for row in data:
                    row_string = "".join(map(str, row))
                    board_string += row_string + ","

                board_string = board_string[:-1]
                board_string += "|"

            board_string = board_string[:-1]
            c.write(board_string + "\n")

            c.seek(0)
            print(f"Saved to line: {len(c.readlines())}")

    def load_edge_case(self, line):
        try:
            with open("cases.txt", "r") as c:
                cases = c.readlines()
                data_str = cases[line - 1].strip().split("|")
                board_str = data_str[0]
                selection_list = data_str[1:]
                self.board.clear()
                for n in range(8):
                    self.board.append(list(map(int, list(board_str[n * 8:(n + 1) * 8]))))
                self.selections.clear()
                for n, i in enumerate(selection_list):
                    new_selection = Selection(self.selection_x,
                                              self.board_pos + n * (
                                                      (self.board_length - self.selection_length * 3) / 2 +
                                                      self.selection_length), self.selection_length,
                                              self.tile_size, tile_data=[list(map(int, list(j))) for j in i.split(",")])
                    self.selections.append(new_selection)

                if not any(self.blanks):
                    self.try_to_solve = True

                self.visual_overlay.clear()

        except IndexError:
            print("No case saved to that slot")

    def draw_board(self):

        self.screen.fill((66, 93, 159))

        board_surf = pygame.Surface((self.board_length, self.board_length))
        board_surf.fill((66, 93, 159))
        pygame.draw.rect(board_surf, (24, 36, 74), (0, 0, self.board_length, self.board_length))

        side_length = self.tile_size - (self.tile_size / 12)

        for i, row in enumerate(self.board):
            for j, col in enumerate(row):
                pygame.draw.rect(board_surf, (self.colors[col]),
                                 (i * self.tile_size + 5, j * self.tile_size + 5, side_length, side_length),
                                 border_radius=4)
                if self.visual_overlay and sum(self.visual_overlay[i][j]) != 0 and col != 1:
                    pygame.draw.rect(board_surf, (self.visual_overlay[i][j]),
                                     (i * self.tile_size + 5, j * self.tile_size + 5, side_length, side_length),
                                     border_radius=4)

        self.screen.blit(board_surf, (self.board_pos, self.board_pos))

        if self.board_pos < self.mouse_hitbox[0] < self.board_pos + self.board_length - 5 and self.board_pos < \
                self.mouse_hitbox[0] < self.board_pos + self.board_length - 5:
            row = int(self.mouse_hitbox[0] // self.tile_size)
            col = int(self.mouse_hitbox[1] // self.tile_size)
            if self.selected_tile is not None:
                if 0 < row < 10 - len(self.selected_tile.tile_data) and 0 < col < 10 - len(
                        self.selected_tile.tile_data[0]):
                    self.selected_tile_row = row
                    self.selected_tile_col = col
                    pos_x = row * self.tile_size
                    pos_y = col * self.tile_size

                    self.screen.blit(
                        self.selected_tile.hover_surface(self.tile_size - (self.tile_size / 12) + 5, (100, 0, 0)),
                        (pos_x, pos_y))
            elif 0 < row < 9 and 0 < col < 9:
                # manually draw on board
                if self.clicked and self.selected_tile is None and self.place_timer == 0:
                    self.board[row - 1][col - 1] = 1
                elif self.clicked_2:
                    self.board[row - 1][col - 1] = 0

    def update_tiles(self):
        # 'i' is the three plus signs on the side of the screen
        for n, i in enumerate(self.selections):
            self.blanks[n] = i.blank

            if i.hitbox.colliderect(self.mouse_hitbox):
                i.hovered_over = True
                if self.clicked and i.blank:
                    self.reset_hand()
                    self.creating_tile = True  # changes the screen
                    self.clicked_tile = i
                    self.clicked_tile.clicked_on = True
                    self.try_to_solve = True  # tells the program a block has been changed, so it can try solving again
                elif self.clicked:
                    self.selected_tile = i
                    self.selected_tile_index = n
            elif self.mouse_hitbox[0] > self.board_pos + self.board_length and self.clicked:
                # self.selected_tile = None
                pass
            else:
                i.hovered_over = False

        for n, tile in enumerate(self.selections):
            t_surf = tile.draw_selection()
            self.screen.blit(t_surf, (tile.x, tile.y))

    def reset_hand(self):
        self.selected_tile = None
        self.selected_tile_row = None
        self.selected_tile_col = None


def remove_blank_lines():
    with open("cases.txt", 'r') as file:
        lines = file.readlines()

    with open("cases.txt", 'w') as file:
        for line in lines:
            if line.strip():
                file.write(line)


if __name__ == "__main__":
    remove_blank_lines()
    game = Game()
    game.main()
