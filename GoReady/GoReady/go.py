import copy
import math
import random

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class Stone(object):
    def __init__(self, board, point, color):
        self.board = board
        self.point = point
        self.color = color
        self.group = self.find_group()

    def remove(self):

        self.group.stones.remove(self)
        del self

    @property
    def neighbors(self):
        neighboring = [(self.point[0] - 1, self.point[1]),
                       (self.point[0] + 1, self.point[1]),
                       (self.point[0], self.point[1] - 1),
                       (self.point[0], self.point[1] + 1)]
        for point in neighboring:
            if not 0 < point[0] < 20 or not 0 < point[1] < 20:
                neighboring.remove(point)
        return neighboring




    @property
    def liberties(self):
        liberties = self.neighbors
        stones = self.board.search(points=self.neighbors)
        for stone in stones:
            liberties.remove(stone.point)
        return liberties

    def find_group(self):
        groups = []
        stones = self.board.search(points=self.neighbors)
        for stone in stones:
            if stone.color == self.color and stone.group not in groups:
                groups.append(stone.group)
        if not groups:
            group = Group(self.board, self)
            return group
        else:
            if len(groups) > 1:
                for group in groups[1:]:
                    groups[0].merge(group)
            groups[0].stones.append(self)
            return groups[0]

    def __str__(self):
        """Return the location of the stone, e.g. 'D17'."""
        return 'ABCDEFGHJKLMNOPQRST'[self.point[0]-1] + str(20-(self.point[1]))


class Group(object):
    def __init__(self, board, stone):
        """Create and initialize a new group.

        Arguments:
        board -- the board which this group resides in
        stone -- the initial stone in the group

        """
        self.board = board
        self.board.groups.append(self)
        self.stones = [stone]
        self.liberties = None


    def merge(self, group):
        """Merge two groups.

        This method merges the argument group with this one by adding
        all its stones into this one. After that it removes the group
        from the board.

        Arguments:
        group -- the group to be merged with this one

        """
        for stone in group.stones:
            stone.group = self
            self.stones.append(stone)
        self.board.groups.remove(group)
        del group

    def remove(self):
        """Remove the entire group."""
        while self.stones:
            self.stones[0].remove()
        self.board.groups.remove(self)
        del self

    def update_liberties(self):
        """Update the group's liberties.

        As this method will remove the entire group if no liberties can
        be found, it should only be called once per turn.

        """
        liberties = []
        for stone in self.stones:
            for liberty in stone.liberties:
                liberties.append(liberty)
        self.liberties = set(liberties)
        if len(self.liberties) == 0:
            self.remove()
    def __str__(self):
        """Return a list of the group's stones as a string."""
        return str([str(stone) for stone in self.stones])


class Board(object):
    def __init__(self):

        self.groups = []
        self.next = BLACK
        self.passed = []
        self.territories = []
        self.played_moves = []

    def printPass(self):
        return self.passed

    def checkPass(self):
        if len(self.passed) > 2:
            if self.passed[-1] == self.passed[-2] == 1:
                return  True
        return False

    def appendPass(self, x):
        self.passed.append(x)

        return True

    def search(self, point=None, points=[]):
        """Search the board for a stone.

        The board is searched in a linear fashion, looking for either a
        stone in a single point (which the method will immediately
        return if found) or all stones within a group of points.

        Arguments:
        point -- a single point (tuple) to look for
        points -- a list of points to be searched

        """
        stones = []
        for group in self.groups:
            for stone in group.stones:
                if stone.point == point and not points:
                    return stone
                if stone.point in points:
                    stones.append(stone)
        return stones

    def turn(self):
        """Keep track of the turn by flipping between BLACK and WHITE."""
        if self.next == BLACK:
            self.next = WHITE
            return BLACK
        else:
            self.next = BLACK
            return WHITE

    def empty_intersections(self):
        points = [(i, j) for i in range(1, 20) for j in range(1, 20)]
        for group in self.groups:
            for stone in group.stones:
                if stone.point in points:
                    points.remove(stone.point)
        return points

    def calculate_territory(self, empty):
        b_score = 0
        w_score = 0
        for point in empty:
            w_count = 0
            b_count = 0
            neighbours = [[point[0] - 1, point[1]],
                          [point[0] + 1, point[1]],
                          [point[0], point[1] - 1],
                          [point[0], point[1] + 1]]
            for i in range(4):
                while tuple(neighbours[i]) in empty:
                    if i == 0:
                        neighbours[i][0] -= 1
                    if i == 1:
                        neighbours[i][0] += 1
                    if i == 2:
                        neighbours[i][1] -= 1
                    if i == 3:
                        neighbours[i][1] += 1

            for neighbour in neighbours:
                if not 0 < neighbour[0] < 20 or not 0 < neighbour[1] < 20:
                    neighbours.remove(neighbour)
            neighbours = [tuple(neighbour) for neighbour in neighbours]

            for group in self.groups:
                for stone in group.stones:
                    if stone.point in neighbours:
                        if stone.color == WHITE:
                            w_count += 1
                        if stone.color == BLACK:
                            b_count += 1
            if b_count == 4:
                b_score += 1
            if w_count == 4:
                w_score += 1

            if len(neighbours) == 3:
                if point[0] in [1, 19] or point[1] in [1, 19]:
                    if w_count == 3:
                        w_score += 1
                    if b_count == 3:
                        b_score += 1

            if len(neighbours) == 2:
                if point in [(1, 1), (19, 19), (1, 19), (19, 1)]:
                    if w_count == 2:
                        w_score += 1
                    if b_count == 2:
                        b_score += 1
        return b_score, w_score

    def calculate_liberties(self):
        w_libs = []
        b_libs = []
        for group in self.groups:
            if group.stones[0].color == WHITE:
                w_libs.append(group.liberties)
            else:
                b_libs.append(group.liberties)
        return b_libs, w_libs

    def calculate_point_liberty(self, point, empty):
        neighbours = [[point[0] - 1, point[1]],
                      [point[0] + 1, point[1]],
                      [point[0], point[1] - 1],
                      [point[0], point[1] + 1]]
        for i in range(4):
            while tuple(neighbours[i]) in empty:
                if i == 0:
                    neighbours[i][0] -= 1
                if i == 1:
                    neighbours[i][0] += 1
                if i == 2:
                    neighbours[i][1] -= 1
                if i == 3:
                    neighbours[i][1] += 1

        for neighbour in neighbours:
            if not 0 < neighbour[0] < 20 or not 0 < neighbour[1] < 20:
                neighbours.remove(neighbour)
        neighbours = [tuple(neighbour) for neighbour in neighbours]
        b_count = 0
        w_count = 0
        for group in self.groups:
            for stone in group.stones:
                for neighbour in neighbours:
                    if stone.point == neighbour and stone.color == BLACK:
                        b_count += 1
                    else:
                        w_count += 1
        if self.next == BLACK:
            liberty = 4 - len(neighbours) - b_count
        if self.next == WHITE:
            liberty = 4 - len(neighbours) - b_count
        return liberty

    def calc_stones(self):
        w_pieces = []
        b_pieces = []
        for group in self.groups:
            for stone in group.stones:
                if stone.color == WHITE:
                    w_pieces.append(stone.point)
                else:
                    b_pieces.append(stone.point)
        return b_pieces, w_pieces

    def game_finished(self, stones, terras, empty):
        b_score = len(stones[0]) + terras[0]
        w_score = len(stones[1]) + terras[1]
        if b_score > 60 or w_score > 60 or len(empty) == 0 or self.checkPass():
            return 1, b_score, w_score
        else:
            return 0, b_score, w_score

    def calculate_point_liberty(self, point, empty, color):
        neighbours = [[point[0] - 1, point[1]],
                      [point[0] + 1, point[1]],
                      [point[0], point[1] - 1],
                      [point[0], point[1] + 1]]
        for i in range(4):
            while tuple(neighbours[i]) in empty:
                if i == 0:
                    neighbours[i][0] -= 1
                if i == 1:
                    neighbours[i][0] += 1
                if i == 2:
                    neighbours[i][1] -= 1
                if i == 3:
                    neighbours[i][1] += 1

        for neighbour in neighbours:
            if not 0 < neighbour[0] < 20 or not 0 < neighbour[1] < 20:
                neighbours.remove(neighbour)
        neighbours = [tuple(neighbour) for neighbour in neighbours]
        b_count = 0
        w_count = 0
        for group in self.groups:
            for stone in group.stones:
                for neighbour in neighbours:
                    if stone.point == neighbour and stone.color == BLACK:
                        b_count += 1
                    else:
                        w_count += 1
        if color == BLACK:
            liberty = 4 - len(neighbours) - w_count
        if color == WHITE:
            liberty = 4 - len(neighbours) - b_count
        return liberty

    def calc_point_score(self, point, libs, color, empty):
        score = 0.0
        if color == WHITE:
            my_libs = libs[1]
            opp_libs = libs[0]
        else:
            my_libs = libs[0]
            opp_libs = libs[1]

        for group in opp_libs:
            if point in group:
                score += 1 / len(group)
        for group in my_libs:
            if group:
                if point in group:
                    score -= 1 / len(group)
        this_point_libs = self.calculate_point_liberty(point, empty, color)
        if this_point_libs == 0:
            score -= 50
        else:
            score += this_point_libs / 6
        return score

    def update_liberties(self, added_stone=None):

        for group in self.groups:
            if added_stone:
                if group == added_stone.group:
                    continue
            group.update_liberties()
        if added_stone:
            added_stone.group.update_liberties()

    def pieces_range(self, stones):
        b_stones = stones[0]
        w_stones = stones[1]
        b_range = []
        w_range = []
        for stone in b_stones:
            b_range.extend(neighbour_block(stone))
        for stone in w_stones:
            w_range.extend(neighbour_block(stone))
        b_range = list(set(b_range))
        w_range = list(set(w_range))
        return b_range, w_range

    def miniMax_agent(self):
        stones = self.calc_stones()
        empty = self.empty_intersections()
        ranges = self.pieces_range(stones)
        libs = self.calculate_liberties()
        best_point = (random.randint(1, 19), random.randint(1, 19))
        score = -math.inf
        locations = valid_locations(self, ranges[0])
        for loc in locations:
            temp_score = self.calc_point_score(loc, libs, self.next, empty)
            if temp_score > score:
                score = temp_score
                best_point = loc
        best_point, score = minimax(self, 2, True, best_point,-1000000000000000,100000000000000000)
        return best_point, score


def neighbour_block(point):
    neighbs = [(i, j) for i in range(point[0] - 1, point[0] + 2) for j in range(point[1] - 1, point[1] + 2)]
    for neighbour in neighbs:
        if not 0 < neighbour[0] < 20 or not 0 < neighbour[1] < 20:
            neighbs.remove(neighbour)
    return neighbs


def valid_locations(board, locations):
    valid = []
    empty = board.empty_intersections()
    for loc in locations:
        if loc in empty:
            valid.append(loc)
    return valid


def minimax(board, depth, maximizing, starting_point,alpha, beta):
    stones = board.calc_stones()
    empty = board.empty_intersections()
    terras = board.calculate_territory(empty)
    finish = board.game_finished(stones, terras, empty)
    if depth == 0 or finish[0] == 1:
        if finish[0] == 1:
            if finish[2] > finish[1]:
                return None, math.inf
            elif finish[1] > finish[2]:
                return None, -math.inf
            else:
                return None, 0
        else:
            return None, finish[2] - finish[1]
    if maximizing:
        value = -math.inf
        point = (random.randint(1, 19), random.randint(1, 19))
        neighbs = neighbour_block(starting_point)
        locations = valid_locations(board, neighbs)
        for loc in locations:
            b_copy = copy.deepcopy(board)
            added_stone = Stone(b_copy, loc, b_copy.turn())
            b_copy.update_liberties(added_stone)
            new_score = minimax(b_copy, depth - 1, False, loc,alpha,beta)
            print(new_score[1])
            if new_score[1] > value:
                value = new_score[1]
                point = loc

            if (value > alpha):
                alpha = value

            if alpha >= beta:
                break

            return point, value
    else:
        value = math.inf
        point = (random.randint(1, 19), random.randint(1, 19))
        neighbs = neighbour_block(starting_point)
        locations = valid_locations(board, neighbs)
        for loc in locations:
            b_copy = copy.deepcopy(board)
            added_stone = Stone(b_copy, loc, b_copy.turn())
            b_copy.update_liberties(added_stone)
            new_score = minimax(b_copy, depth - 1, True, loc,alpha,beta)
            if new_score[1] < value:
                value = new_score[1]
                point = loc

            if(value < beta):
             beta = value

             if alpha >= beta:
                break

            return point, value


