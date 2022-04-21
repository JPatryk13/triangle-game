import random
import math
from typing import Dict, Type, List


class Player:
    name: str = ""
    points: int = 0

    def __init__(self):
        pass


class HumanPlayer(Player):
    name: str = ""
    points: int = 0

    def __init__(self, player_no: int = 1):
        self.name = input("Set name for the player number " + str(player_no) + ": ")
        super().__init__()

    def get_move(self) -> list[int] | bool:
        # take input from the player
        user_input = input(self.name + "'s turn. Choose available field from the board: ")

        # clean user input
        coordinates_cleaned_str = ""
        allowed_chars = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ' ']
        for char in user_input:
            if char in allowed_chars:
                coordinates_cleaned_str += char

        # split input string into list elements
        coordinates_list = coordinates_cleaned_str.split(" ")

        # remove empty chars from the list
        while '' in coordinates_list:
            coordinates_list.pop(coordinates_list.index(''))

        # check if there is only 2 numbers left in the list
        if len(coordinates_list) != 2:
            print("Wrong input.")
            return False
        else:
            # convert the list to integers
            coordinates = [int(coordinates_list[0]), int(coordinates_list[1])]

            return coordinates


class RandomComputerPlayer(Player):
    name: str = ""
    points: int = 0

    def __init__(self, player_no: int = 1):
        # two lists of names so that it doesn't happen that two random players have the same names
        names = [
            ["Mark", "Tobias", "Otto", "Jason", "Rachel", "Lisa", "Rebecca", "Sammy"],
            ["Dominic", "Andy", "John", "Mike", "Alexa", "Tina", "Debby", "Claudia"]
        ]
        self.name = random.choice(names[player_no - 1])
        super().__init__()

    def get_move(self, allowed_fields: list[list[int]]) -> list[int]:
        move = random.choice(allowed_fields)
        print(self.name + "'s move: " + str(move))
        return move


class AIComputerPlayer(Player):
    name: str = ""
    points: int = 0

    def __init__(self, player_no: int = 1):
        self.name = "OliverAI"
        super().__init__()

    def get_move(self, game, player_no: int = 2) -> list[int]:
        # no type hinting @ game to avoid importing the Triangle class and therefore loop import error
        corner_field = {
            'left': [game.height, 1],
            'right': [game.height, game.width]
        }
        # if both fields in the bottom left and right corners of the triangle are available then randomly choose one,
        # else choose whichever is available - those fields are a good starting tactic as they give instantly 2
        # points without increasing opponents chances of getting a combo
        if corner_field['left'] and corner_field['right'] in game.allowed_fields:
            move = random.choice([corner_field['left'], corner_field['right']])
        elif corner_field['left'] in game.allowed_fields:
            move = corner_field['left']
        elif corner_field['right'] in game.allowed_fields:
            move = corner_field['right']
        else:
            # use minimax algorithm to find the best possible move or set of moves
            move = self.__minimax(state=game, depth=5)['position']

        print(self.name + "'s move: " + str(move))
        return move

    def __minimax(self, state, depth: int, current_player: int = 2, current_child_pos: list = None) \
            -> dict[str, Type[int | list[int]]]:
        """
        Algorithm deducing the most optimal move. Considers evaluation of each field on the board and maximises the
        value for AI while minimising the value for the other player. When it's AI's turn to make a move we evaluate if
        it will bring any points and save the max number of points to evaluation variable, then, going back up to the
        top of the tree, we consider all moves that the other player can make and write the min to the evaluation
        variable, etc...
        Unfortunately, the minimax aims only at the highest combos that it can get which makes it easy to defeat.
        I spent a good deal amount of time trying to fix it, although, it doesn't seem to work. I'm going to leave the
        code as it is now. Good enough for first AI.

        :param state: Triangle class obj
        :param depth: How far down the tree the algorithm should go (depth > 0)
        :param current_player: number (ID) of the current player - 2 for the AI, 1 for the other player
        :param current_child_pos: coordinates of the child node to be considered when returning static evaluation of the
        current position
        :return: dictionary with evaluation value and list containing two integer numbers - coordinates
        """
        minimax_dict = {
            'evaluation': float,
            'points': int,
            'position': list[int]
        }

        # at the bottom of the tree evaluate child node at specified position and return the dictionary to the parent
        # node
        if depth == 1 and current_child_pos is not None:
            minimax_dict['points'] = state.check_if_combo(current_child_pos, current_player)[0]
            minimax_dict['position'] = current_child_pos
            return minimax_dict

        if depth > 2 and current_child_pos:
            parent_points = state.check_if_combo(current_child_pos, current_player)[0]
        else:
            parent_points = 0

        if current_player == 2:
            # if the current player is AI then set max_evaluation to -inf - i.e. worse than the worst possible
            # evaluation
            max_evaluation = -math.inf
            for child_position in state.allowed_fields:
                # go down the tree node for each possible position on the board then from the depth == 1 go back up
                child_minimax_dict = self.__minimax(state, depth - 1, current_player=1,
                                                    current_child_pos=child_position)

                # evaluate for the child node
                child_eval = int(child_minimax_dict['points'])*(depth - 1) + parent_points*depth

                # save the best evaluation present
                minimax_dict['evaluation'] = max(max_evaluation, child_eval)
                minimax_dict['points'] = child_minimax_dict['points'] if depth == 2 else parent_points

                # save the coordinate that has the max evaluation. Note that child_minimax_dict['position'] ==
                # child_position. We are saving the new position if it has higher evaluation than the previous, else we
                # leave it as it was
                if child_eval > max_evaluation:
                    minimax_dict['position'] = child_position

            return minimax_dict
        else:
            # if the current player is the other player then max_evaluation is set to the worse than the worst (from the
            # AI perspective)
            min_evaluation = math.inf
            for child_position in state.allowed_fields:
                # go down the tree and back up recursively for the other player
                child_minimax_dict = self.__minimax(state, depth - 1, current_player=1,
                                                    current_child_pos=child_position)

                child_eval = int(child_minimax_dict['points'])*(depth - 1) + parent_points*depth

                # minimise the evaluation for the other player
                minimax_dict['evaluation'] = min(min_evaluation, child_eval)
                minimax_dict['points'] = child_minimax_dict['points'] if depth == 2 else parent_points

                # save the coordinate that has the min evaluation
                if child_eval < min_evaluation:
                    minimax_dict['position'] = child_position

            return minimax_dict


