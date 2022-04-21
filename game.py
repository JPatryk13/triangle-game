from player import HumanPlayer, RandomComputerPlayer, AIComputerPlayer
from typing import NoReturn
import time
import random


class Triangle:
    board: list[list[str]] = []
    allowed_fields: list[list[int]] = []
    crossed_fields: list[list[int]] = []
    width: int = 0
    height: int = 0
    field_spacing: str = ""
    axis_str: str = ""
    y_coord_axis: list[str] = []
    # points for each player
    p1: int = 0
    p2: int = 0

    def __init__(self, width: int) -> None:
        # some error handling just in case
        if type(width) is not int:
            raise TypeError("The width variable must be an integer number.")
        elif not width % 2:
            raise ValueError("The number (width) must be odd. Got even instead.")
        else:
            pass

        # set height based on the width of the triangle so that it always has odd number of fields in each row
        # smaller by 2 compared to the lower level
        self.width = width
        self.height = int((self.width + 1) / 2)
        self.board = [["O" for field in range(self.width)] for row in range(self.height)]

        # "filter" out some fields so that the board has a triangular shape. Not allowed fields in the board are
        # going to be replaced with " " while the allowed ones remain as "0"
        for row_ind in range(len(self.board)):
            no_of_allowed_fields = row_ind * 2 + 1
            # number of fields that need to be subtracted from each side of the current row
            not_allowed_fields_per_side = int((len(self.board[row_ind]) - no_of_allowed_fields) / 2)
            for col_ind in range(len(self.board[row_ind])):
                # I.e. if the column index falls outside the indices of allowed fields
                if col_ind < not_allowed_fields_per_side or \
                        col_ind >= (not_allowed_fields_per_side + no_of_allowed_fields):
                    self.board[row_ind][col_ind] = " "
                else:
                    self.allowed_fields.append([row_ind + 1, col_ind + 1])

        x_coord_axis = [str(i + 1) + "." for i in range(len(self.board[0]))]

        # adjusting the spacing between fields based on the largest number's number of digits. E.g. spacing = " " if
        # the highest number has one digit, spacing = "  " if the highest number has two digits (then the spacing
        # between single digit number is going  to be "  " but the spacing between two-digit numbers will be "  ", etc.
        self.field_spacing = "".join([str(" ") for i in range(len(x_coord_axis[-1]))])

        self.y_coord_axis = []
        for i in range(len(self.board)):
            self.y_coord_axis.append(str(i + 1) + "." + (len(self.field_spacing) - len(str(i + 1))) * " ")

        for coordinate in x_coord_axis:
            self.axis_str += coordinate + "".join([" " for i in range(len(self.field_spacing) + 1 - len(coordinate))])

    @staticmethod
    def __str_crossed_fields(fields_dict: dict) -> str:
        crossed_fields = ""
        # fields_dict will be empty right after initialization in the play function
        if fields_dict != {}:
            # create a long string containing all H/V/D directions of crossing with fields coordinates
            if fields_dict['horizontal']:
                crossed_fields += "Horizontal: " + str(fields_dict['horizontal']) + " "
            if fields_dict['vertical']:
                crossed_fields += "Vertical: " + str(fields_dict['vertical']) + " "
            if fields_dict['diagonal']:
                crossed_fields += "Diagonal: " + str(fields_dict['diagonal']) + " "

        return crossed_fields

    def print_board(self, p1: HumanPlayer, p2: HumanPlayer | RandomComputerPlayer | AIComputerPlayer, x_fields: dict, p: int) -> NoReturn:
        """
        Printing the board.
        :return: N/A
        """

        # compose a string displaying players' names, points and crossed fields next to the appropriate player
        str_x_fields = self.__str_crossed_fields(x_fields)
        if str_x_fields != "" and p == 1:
            point_board = p1.name + ": " + str(self.p1) + " " + "\n" \
                          + p2.name + ": " + str(self.p2) + " " + str(str_x_fields)
        elif str_x_fields != "" and p == 2:
            point_board = p1.name + ": " + str(self.p1) + " " + str(str_x_fields) + "\n" \
                          + p2.name + ": " + str(self.p2)
        else:
            point_board = p1.name + ": " + str(self.p1) + "\n" + p2.name + ": " + str(self.p2)

        # print points
        print(point_board)
        # print the board row by row
        for row in range(len(self.board)):
            print(self.y_coord_axis[row] + self.field_spacing.join(self.board[row]))
        # print the bottom axis
        print(" " + self.field_spacing + self.axis_str)

    def make_move(self, coordinates: list) -> bool:
        """
        Takes the coordinates from the player and fills up the field that was the targeted field - swaps "O" for "0".
        :return:
        """
        if coordinates in self.allowed_fields:
            row_ind = coordinates[0] - 1
            col_ind = coordinates[1] - 1
            # set the chosen field to "0" - filled up
            self.board[row_ind][col_ind] = "0"
            # remove the field from the allowed fields list
            self.allowed_fields.pop(self.allowed_fields.index(coordinates))
            return True
        else:
            print("The field coordinates do not match any allowed field.")
            return False

    @staticmethod
    def __index_in_list(li: list, i: int) -> bool:
        return True if i in range(0, len(li)) else False

    def __check_diagonal_combo(self, coordinate_matrix: list[list[int]]) -> [int, list[list[int]]]:
        # filter out sets of coordinates with out-of-range row indices or the ones that point at the field with " "
        # entry on the board
        coord_ind = 0
        diagonal_axis_points = 0
        crossed_fields_coordinates = []

        while True:
            # unpack each coordinate set
            var_row_ind, var_col_ind = coordinate_matrix[coord_ind]

            # pop set out if it's out of range or is " "-field
            if self.__index_in_list(self.board, var_row_ind):
                if self.board[var_row_ind][var_col_ind] == " ":
                    coordinate_matrix.pop(coord_ind)
                else:
                    coord_ind += 1
            else:
                coordinate_matrix.pop(coord_ind)

            # if there is no more coordinates sets to check...
            if coord_ind == len(coordinate_matrix):
                # if all fields are filled up then swap them for "X" and return number of points gained, in not return 0
                if "O" not in [self.board[row_ind][col_ind] for row_ind, col_ind in coordinate_matrix]:
                    for row_ind, col_ind in coordinate_matrix:
                        # cross field
                        self.board[row_ind][col_ind] = "X"

                        # add points
                        diagonal_axis_points += 1

                        # append the matrix
                        crossed_fields_coordinates.append([row_ind + 1, col_ind + 1])
                    break
                else:
                    break
        return [diagonal_axis_points, crossed_fields_coordinates]

    def check_if_combo(self, coordinates: list, player_number: int) -> [int, dict]:
        """
        Checks if the previous move made any set-ups in which a number of fields can be crossed - e.g. second row, all
        three fields filled up. If so, then change them from "0" to "X" and return number of points gained, return 0
        otherwise.
        :return: points, coordinate_matrix
        """
        row_ind = coordinates[0] - 1
        col_ind = coordinates[1] - 1
        points = 0
        coordinate_matrix = {
            'horizontal': [],
            'vertical': [],
            'diagonal': []
        }

        # check horizontally
        if "O" not in self.board[row_ind]:
            # add points
            points += self.board[row_ind].count("0") + self.board[row_ind].count("X")

            # cross fields
            self.board[row_ind] = ["X" if field == "0" else field for field in self.board[row_ind]]

            # append coordinates of crossed fields to the list
            for i in range(len(self.board[row_ind])):
                if self.board[row_ind][i] == "0" or self.board[row_ind][i] == "X":
                    coordinate_matrix['horizontal'].append([row_ind + 1, i + 1])
            # Alternative expression: [coordinate_matrix['horizontal'].append([row_ind + 1, i + 1]) for i in
            # range(len(self.board[row_ind])) if self.board[row_ind][i] == "0" or self.board[row_ind][i] == "X"]

        # check vertically
        column = [self.board[i][col_ind] for i in range(self.height)]
        if "O" not in column:
            # add points
            points += column.count("0") + column.count("X")

            # cross fields
            for row_ind in range(len(self.board)):
                if self.board[row_ind][col_ind] == "0":
                    self.board[row_ind][col_ind] = "X"

            # append coordinates of crossed fields to the list (column still contains 0's not X's so that we check if
            # each entry is equal to 0)
            [coordinate_matrix['vertical'].append([i + 1, col_ind + 1]) for i in range(len(column)) if column[i] == "0" or column[i] == "X"]

        # check diagonally from left to right
        # a matrix with coordinate sets pointing at potential fields placed diagonally from the user entry
        diagonal_coord_matrix = [[row_ind - col_ind + var_col_ind, var_col_ind] for var_col_ind in range(self.width)]

        points_temp, coordinate_matrix_temp = self.__check_diagonal_combo(diagonal_coord_matrix)
        points += points_temp
        coordinate_matrix['diagonal'] += coordinate_matrix_temp

        # check diagonally from right to left
        diagonal_coord_matrix = [[row_ind + col_ind - var_col_ind, var_col_ind] for var_col_ind in range(self.width)]

        points_temp, coordinate_matrix_temp = self.__check_diagonal_combo(diagonal_coord_matrix)
        points += points_temp
        coordinate_matrix['diagonal'] += coordinate_matrix_temp

        # I want it also to return a matrix with list of crossed fields as well as points + update the local variables
        if player_number == 1:
            self.p1 += points
            total_points = self.p1
        else:
            self.p2 += points
            total_points = self.p1
        return total_points, coordinate_matrix

    def is_end(self) -> bool:
        """
        If all fields are "X"s then return True.
        :return:
        """
        if not self.allowed_fields:
            return True
        else:
            return False


def about():
    print("The game is similar to tic-tac-toe. You choose a field\n"
          "from the board and you check if you hit a combo. In this\n"
          "specific case you are presented with triangular board.\n"
          "E.g. 11-fields-base triangle:\n"
          "1.                     O                    \n"
          "2.                 O   O   O                \n"
          "3.             O   O   O   O   O            \n"
          "4.         O   O   O   O   O   O   O        \n"
          "5.     O   O   O   O   O   O   O   O   O    \n"
          "6. O   O   O   O   O   O   O   O   O   O   O\n"
          "   1.  2.  3.  4.  5.  6.  7.  8.  9.  10. 11.\n"
          "Then you choose set of coordinates pointing at the field\n"
          "that hasn't been filled up yet, for example: '3 4'.\n"
          "Remember, you need to separate two integer numbers by\n"
          "a space and first coordinate is the number of the row\n"
          "(e.g. 1-6), the second one is number of the column\n"
          "(e.g. 1-11). After your choice the field is filled up\n"
          "and then turn for another player's move. After a successful\n"
          "set of actions you may fill up row, column or one of the\n"
          "diagonal axis which gives you points.\n"
          "Player 1: 3\n"
          "Player 2: 2\n"
          "1.                     O                    \n"
          "2.                 O   O   O                \n"
          "3.             O   O   O   O   O            \n"
          "4.         X   O   O   O   O   O   O        \n"
          "5.     O   X   O   O   O   O   O   O   X    \n"
          "6. O   O   X   O   O   O   O   O   X   O   O\n"
          "   1.  2.  3.  4.  5.  6.  7.  8.  9.  10. 11.\n"
          "In the above scenario player 1 crossed off column number 3\n"
          "and therefore gained 3 points, whereas player 2 crossed the\n"
          "diagonal axis on the right gaining 2 points.\n"
          "You can also interrupt someone's sequence and gain points:\n"
          "1.                     O                    \n"
          "2.                 O   O   O                \n"
          "3.             0   0   0   O   0            \n"
          "4.         X   O   O   O   O   O   O        \n"
          "5.     O   X   O   O   O   O   O   O   X    \n"
          "6. O   O   X   O   O   O   O   O   X   O   O\n"
          "   1.  2.  3.  4.  5.  6.  7.  8.  9.  10. 11.\n"
          "Here, let's presume that player 2 filled up almost the whole\n"
          "3rd row, the player 1 now can fill up the field '3 7' to\n"
          "cross of the row and gain 5 points.\n"
          "The game ends when all field all filled up; then the winner\n"
          "is the player with the highest score.\n"
          "Some combos can provide extra score. The one that you see\n"
          "below is a double combo. Vertically two fields been crossed\n"
          "and diagonally one: '6 2'. That gives the player three points.\n"
          "1.                     O                    \n"
          "2.                 O   O   O                \n"
          "3.             O   O   O   O   O            \n"
          "4.         O   O   O   O   O   O   O        \n"
          "5.     X   O   O   O   O   O   O   O   O    \n"
          "6. O   X   O   O   O   O   O   O   O   O   O\n"
          "   1.  2.  3.  4.  5.  6.  7.  8.  9.  10. 11.\n")


def play():
    """
    1. Show menu for the player: Start Game, About, Exit
    2a. New Game - choose opponent (if random computer player or real person then choose the size of the board,
    otherwise choose the 'skillfulness' of AI
    2b. Display some background and rules of the game
    2c. Quit the game
    3. Display the empty board and randomize who's going to start the game
    4. Take the move from the user and direct it to the make_move method
    5. Check for move vs field availability, field crossing and potential winner
    6. Display updated board or appropriate message
    """
    # game loop
    while True:
        # choose the type of the game
        print("1. Human Player vs Human Player\n"
              "2. Human Player vs Random Computer Player (easy)\n"
              "3. Human Player vs AI\n\n"
              "4. Go back to menu")
        game_type = input("Choose type of the game: ")

        player1 = HumanPlayer()
        if game_type == '1':
            player2 = HumanPlayer(player_no=2)
        elif game_type == '2':
            player2 = RandomComputerPlayer()
        elif game_type == '3':
            player2 = AIComputerPlayer()
        elif game_type == '4':
            break
        else:
            print("Wrong input.")
            continue

        # get the width of the board and validate the input
        while True:
            board_width = input("Choose width of the board (must be an odd number): ")

            # error handling similar to the one in the __init__ function
            try:
                board_width = int(board_width)
            except TypeError:
                print("Wrong input.")
                continue

            if not board_width % 2:
                print("Wrong input.")
                continue
            else:
                break

        t = Triangle(board_width)
        player_turn = 1
        crossed_fields = {}

        while True:
            # print the board
            t.print_board(player1, player2, crossed_fields, player_turn)

            coordinates = False
            is_move_possible = False

            while not (coordinates and is_move_possible):
                # get player's move
                if player_turn == 1:
                    coordinates = player1.get_move()
                elif player_turn == 2 and game_type == '3':
                    coordinates = player2.get_move(game=t)
                else:
                    time.sleep(2)
                    coordinates = player2.get_move(t.allowed_fields)

                # if field is available then proceed
                is_move_possible = t.make_move(coordinates)

            if player_turn == 1:
                player1.points, crossed_fields = t.check_if_combo(coordinates, player_turn)
            else:
                player2.points, crossed_fields = t.check_if_combo(coordinates, player_turn)

            if t.is_end():
                if player1.points > player2.points:
                    print("Player " + player1.name + " won the game!")
                elif player1.points < player2.points:
                    print("Player " + player2.name + " won the game!")
                else:
                    print("Both player have the same score. It's a draw!")
                return 0

            # alternate player numbers
            player_turn = 1 if player_turn == 2 else 2


# if the game.py is executed directly then the built-in variable __name__ is set to "__main__", if on the other hand
# it is imported/executed by the other script then the variable has different name - in such case running the game is
# prevented by the if statement
if __name__ == "__main__":
    # main menu loop
    while True:
        print("1. New Game\n"
              "2. About\n"
              "3. Exit")
        choice = input("Choose menu entry (1-3): ")

        if choice == '1':  # new game
            play()
            continue
        elif choice == '2':  # about
            about()
            continue
        elif choice == '3':  # exit
            break
        else:
            print("Wrong input.")
            continue
