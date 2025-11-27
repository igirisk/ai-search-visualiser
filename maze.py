import matplotlib.pyplot as plt
import numpy as np


class Node:
    """
    Represents node in a search tree.

    Args:
        state (tuple[int, int]): Current position represented as (row, column).
        parent (Node | None): The preceding node in the search path. Set to None for the root node.
        action (str | None): The action taken from the parent to reach this node ("up", "down", "left", "right"). None for the root node.
    """

    def __init__(self, state: tuple[int, int], parent: tuple[int, int], action: str):
        self.state = state
        self.parent = parent
        self.action = action


class StackFrontier:
    """
    Stack implementation using a Python list.
    Supports last in first out operations.
    """

    def __init__(self):
        self._frontier = []

    def __repr__(self):
        return f"Stack({self._frontier})"

    def add(self, node):
        """
        Push a node onto the stack.

        Args:
            node (Node): The node to be added.
        """
        self._frontier.append(node)

    def is_empty(self):
        """
        Check whether the stack is empty.

        Returns:
            bool: True if the stack is empty, False otherwise.
        """
        return not self._frontier

    def remove(self):
        """
        Pop the last node added to the stack.

        Returns:
            Node: The most recently added node.
        """
        if self.is_empty():
            raise IndexError("Empty frontier")
        return self._frontier.pop()

    def contains_state(self, state):
        """
        Check if frontier contains node with desired state.

        Args:
            state (tuple[int, int]): Current position represented as (row, column).

        Returns:
            bool: True is node with desired state is in frontier, false otherwise.
        """

        for node in self._frontier:
            if node.state == state:
                return True

        return False


class Maze:
    def __init__(self, file_path: str):
        self.name = file_path.split("/")[-1]

        with open(file_path, "r", encoding="utf-8") as file:
            contents = file.read()

        # Check valid maze
        if contents.count("S") != 1:
            raise Exception("Maze should have exactly one starting point.")
        if contents.count("E") != 1:
            raise Exception("Maze should have exactly one ending point.")

        # Get height and width of maze
        contents = contents.splitlines()
        self.height = len(contents)
        self.width = max(len(line) for line in contents)

        # Create nested list represetation of walls in maze
        self.walls = []
        for i, row in enumerate(contents):
            walls = []
            for j, cell in enumerate(row):
                if cell == "S":
                    self.start = (i, j)
                    walls.append(False)
                elif cell == "E":
                    self.end = (i, j)
                    walls.append(False)
                elif cell == " ":
                    walls.append(False)
                else:
                    walls.append(True)
            self.walls.append(walls)

        # Track visited node
        self.explored_set = set()

        # Action and node of path
        self.solution = None

    def neighbours(self, state):
        """
        Provides all valid moves from the given position in the maze.

        Args:
            state (tuple[int, int]): Current position represented as (row, column).

        Return:
            list[tuple[str, tuple[int, int]]]: A list of pairs where each element contains an action label (e.g. "up") and the resulting position after applying that action.
        """
        row, col = state
        candidates = [
            ("up", (row - 1, col)),
            ("down", (row + 1, col)),
            ("left", (row, col - 1)),
            ("right", (row, col + 1)),
        ]
        result = []
        for action, (r, c) in candidates:
            if 0 <= r < self.height and 0 <= c < self.width and not self.walls[r][c]:
                result.append((action, (r, c)))
        return result

    def solve(self):
        """
        Finds solution to the maze.
        """

        # Initialize frontier to starting position
        start = Node(self.start, None, None)
        frontier = StackFrontier()
        frontier.add(start)

        while True:
            # Check if there is no solution
            if frontier.is_empty():
                self.solution = None
                return

            current_node = frontier.remove()

            # Check current node is goal
            if current_node.state == self.end:
                actions = []
                cells = []
                # Creates actions and cells list from root to child
                while current_node.parent is not None:
                    actions.append(current_node.action)
                    cells.append(current_node.parent)
                    current_node = current_node.parent
                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)
                return

            # Add node to explored
            self.explored_set.add(current_node.state)

            # Expand node, add resulting node to frontier
            for action, state in self.neighbours(current_node.state):
                # Exclude nodes explored and already in frontier
                if state not in self.explored_set and not frontier.contains_state(
                    state
                ):
                    frontier.add(Node(state, current_node, action))

    def print_maze(self):
        """
        Visualize maze using matplotlib.

        Legend:
        white (path)
        black (wall)
        S (start point)
        E (end point)
        """

        # Visualize the maze using matplot
        plt.figure()
        plt.imshow(
            self.walls, cmap="binary", interpolation="nearest", origin="upper"
        )  # 'binary' colormap for black/white

        # Hide x-axis anc y-axis ticks
        plt.xticks([])
        plt.yticks([])

        # Set maze title
        plt.title(self.name)

        # Mark out start and end
        textstyle = {"fontsize": 16, "ha": "center", "va": "center", "color": "red"}
        plt.text(self.start[1], self.start[0], "S", **textstyle)
        plt.text(self.end[1], self.end[0], "E", **textstyle)

        plt.show()


print("======= Maze 1 solution =======")
maze1 = Maze("mazes/maze1.txt")
maze1.print_maze()
