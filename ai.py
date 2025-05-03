import copy
 
def check_clear(board):
    cleared_count = 0

    # Make a fresh copy of the board's rows.
    board_copy = [row[:] for row in board]

    # Check and clear full rows.
    for n, row in enumerate(board_copy):
        if len(set(row)) == 1 and row[0] == 1:  # If all elements in the row are 1 (blocks)
            board[n] = [0 for _ in range(8)]
            cleared_count += 1

    # Transpose board to check columns as if they were rows idk I didn't write this line
    board_copy = list(zip(*board_copy[::-1]))

    # Check and clear full columns.
    for n, i in enumerate(board_copy):
        if len(set(i)) == 1 and i[0] == 1:  # If all elements in the column are 1
            for m in range(8):
                board[m][n] = 0  # Clear the column
                cleared_count += 1

    return board, cleared_count


def add_tile(board, block, row, col, visual_overlay=None, current_block=-1, is_human=False):
    if visual_overlay is None:  # idk pycharm wanted me to do it
        visual_overlay = [[[0, 0, 0] for i in range(8)] for j in range(8)]

    # Check if the tile can be placed without going out of bounds or overlapping another tile
    for n1, i in enumerate(block):
        for n2, j in enumerate(i):
            if (row + n1 - 1) < 0 or (row + n1 - 1) > 7 or (col + n2 - 1) < 0 or (col + n2 - 1) > 7:
                return False, board  # Out of bounds
            if board[row + n1 - 1][col + n2 - 1] == 1 and j == 1:
                return False, board  # Overlapping another tile

    # Place the tile on the board
    for n1, i in enumerate(block):
        for n2, j in enumerate(i):
            if j == 1:
                place_row, place_col = row + n1 - 1, col + n2 - 1
                board[place_row][place_col] = 1
                if is_human:
                    visual_overlay[place_row][place_col] = [0, 0, 0]
                if current_block != -1:
                    visual_overlay[place_row][place_col][current_block] = 255

    return True, board


def print_board(board):
    for i in board:
        print(i)
    print("-" * 24)


def make_moves(board, tiles, required_clear_count=1):
    def backtrack(b, current_block, clear_count, visual_overlay, correct_tile, must_clear):
        # Termination: if all three blocks have been placed
        if current_block == 3:
            # If a clear is required, check that we achieved enough clears
            if must_clear:
                if clear_count >= required_clear_count:
                    return b, visual_overlay
                else:
                    return None
            else:
                return b, visual_overlay

        # Try every board position for the current block
        for row in range(9):
            for col in range(9):
                board_copy = copy.deepcopy(b)
                overlay_copy = copy.deepcopy(visual_overlay)

                # Try placing the current block
                can_place, new_board = add_tile(board_copy, correct_tile[current_block].tile_data, row, col,
                                                overlay_copy,
                                                current_block)
                if not can_place:
                    continue  # Skip invalid placements

                # Clear rows/columns and get the number of clears from this placement
                new_board, new_clears = check_clear(new_board)
                total_clear_count = clear_count + new_clears

                # Recurse to place the next block.
                result = backtrack(new_board, current_block + 1, total_clear_count, overlay_copy, correct_tile,
                                   must_clear)

                if result is not None:
                    return result

                    # No valid placement found for this branch.
        return None

    initial_board = copy.deepcopy(board)
    initial_overlay = [[[0, 0, 0] for _ in range(8)] for _ in range(8)]

    for i in range(6):  # goes through 6 times for sequencing
        new_tiles = tiles[:]
        correct_tiles = [new_tiles.pop(i % 3)]
        extra_tiles = new_tiles[:2]
        if i > 2:
            extra_tiles.reverse()
        correct_tiles.extend(extra_tiles)

        result = backtrack(initial_board, 0, 0, initial_overlay, correct_tiles, must_clear=True)
        if result is not None:
            print("Solved with a clear")
            return result

    # Fallback: if no solution with the required clears is found, relax the requirement.
    print("No solution with required clears found. Falling back to non-clearing solution")
    result = backtrack(initial_board, 0, 0, initial_overlay, tiles, must_clear=False)
    if result is not None:
        print("Solved without a clear")
        return result
    else:
        print("No solution")
        return None, None
