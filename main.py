from __future__ import annotations

import sys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.colors import BoundaryNorm, ListedColormap


class Node:
    """
    Represents node in a search tree.

    Args:
        state (tuple[int, int]): Current position represented as (row, column).
        parent (Node | None): The preceding node in the search path. Set to None for the root node.
        action (str | None): The action taken from the parent to reach this node ("up", "down", "left", "right"). None for the root node.
        cost (int): The cost from initial state to node.
        man_dist (int): Manhattan distance from current position to end point.
    """

    def __init__(
        self,
        state: tuple[int, int],
        parent: Node | None,
        action: str | None,
        cost: int,
        man_dist: int,
    ):
        self.state = state
        self.parent = parent
        self.action = action
        self.cost = cost
        self.man_dist = man_dist


class StackFrontier:
    """
    Frontier implementing last in first out operations.
    """

    def __init__(self):
        self._frontier = []

    def __repr__(self):
        return f"Stack({self._frontier})"

    def add(self, node: Node):
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


class QueueFrontier(StackFrontier):
    """
    Frontier implementing first in first out opertations.
    """

    def remove(self):
        """
        Pop the first node added to the queue.

        Returns:
            Node: The first added node.
        """
        if self.is_empty():
            raise IndexError("Empty frontier")
        return self._frontier.pop(0)


class GreedyFrontier(QueueFrontier):
    """
    Frontier prioritising nodes with the lowest manhattan distance heuristic to the goal.
    """

    def remove(self):
        """
        Pop node with lowest manhattan distance heuristic to goal.

        Returns:
            Node: The node with the lowest manhattan distance to goal.
        """
        if self.is_empty():
            raise IndexError("Empty frontier")
        self._frontier.sort(key=lambda n: n.man_dist)
        return self._frontier.pop(0)


class AstarFrontier(QueueFrontier):
    """
    Frontier prioritising nodes with lowest sum of manhattan distance to goal and cost to reach node.
    """

    def remove(self):
        """
        Pop node with lowest sum of manhattan distance to goal and cost to reach node.

        Returns:
            Node: The node with lowest sum of manhattan distance to goal and cost to reach node.
        """
        if self.is_empty():
            raise IndexError("Empty frontier")
        self._frontier.sort(key=lambda n: n.man_dist + n.cost)
        return self._frontier.pop(0)


class Maze:
    def __init__(self, file_path: str, search_type: str):
        self.name = file_path.split("/")[-1]
        self.search_type = search_type

        with open(file_path, "r", encoding="utf-8") as file:
            contents = file.read()

        lines = contents.splitlines()

        # Check valid maze
        if contents.count("S") != 1:
            raise Exception("Maze should have exactly one starting point.")
        if contents.count("E") != 1:
            raise Exception("Maze should have exactly one ending point.")

        # Check all rows same length
        if len(set(len(line) for line in lines)) != 1:
            raise Exception("Maze rows are not all the same length.")

        # Get height and width of maze
        self.height = len(lines)
        self.width = max(len(line) for line in lines)

        # Create nested list represetation of walls in maze
        self.walls = []
        for i, row in enumerate(lines):
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
        self.explored_list = []

        # Action and node of path
        self.solution = None

        # Tracks cost to reach cell from start point
        self.cost = {}

        # Save matplotlib .Text instance
        self.text_dict = {}

    def get_manhattan_distance(self, current: tuple[int, int], target: tuple[int, int]):
        """
        Calculates the manhattan distance from current state to target state.

        Args:
            current (tuple[int, int]): Current position represented as (row, column).
            target (tuple[int, int]): target position represented as (row, column).
        """
        return abs(current[0] - target[0]) + abs(current[1] - target[1])

    def neighbours(self, state: tuple[int, int]):
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

        # Initialize frontier to start position
        start = Node(
            self.start, None, None, 0, self.get_manhattan_distance(self.start, self.end)
        )

        search_type = self.search_type

        # Set frontier based on search type
        if search_type == "dfs":
            frontier = StackFrontier()
        elif search_type == "bfs":
            frontier = QueueFrontier()
        elif search_type == "gfs":
            frontier = GreedyFrontier()
        else:
            frontier = AstarFrontier()

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
            self.explored_list.append(current_node.state)

            # Expand node, add resulting node to frontier
            for action, state in self.neighbours(current_node.state):
                # Exclude nodes explored and already in frontier
                if state not in self.explored_list and not frontier.contains_state(
                    state
                ):
                    child_cost = current_node.cost + 1
                    frontier.add(
                        Node(
                            state,
                            current_node,
                            action,
                            child_cost,
                            self.get_manhattan_distance(state, self.end),
                        )
                    )
                    self.cost[state] = child_cost

    def draw(self, maze: list[list[int]]):
        """
        Draw maze using matplotlib.

        Legend:
        white (path)
        black (wall)
        yellow (visitied)
        green (solution)
        S (start point)
        E (end point)

        Args:
            maze (list[list[int]]): Nested list representation of the maze

        Return:
            fig : .Figure from matplotlib.
            ax : ~matplotlib.axes.Axes from matplotlib.
            im : ~matplotlib.image.AxesImage from matplotlib.
            start_text: .Text instance from matplotlib marking start point.
            end_text: .Text instance from matplotlib marking end point.
        """

        cmap = ListedColormap(
            ["white", "black", "yellow", "lightgreen"]
        )  # 0=path, 1=wall, 2=visited, 3=solution
        bounds = [0, 1, 2, 3, 4]  # integer bins
        norm = BoundaryNorm(bounds, cmap.N)

        fig, ax = plt.subplots()

        # Now use the colormap
        im = ax.imshow(
            maze, cmap=cmap, norm=norm, interpolation="nearest", origin="upper"
        )

        # Hide x-axis anc y-axis ticks
        ax.set_xticks([])
        ax.set_yticks([])

        # Set maze title
        ax.set_title(self.name)

        # Mark out start and end
        textstyle = {"fontsize": 16, "ha": "center", "va": "center", "color": "blue"}
        start_text = ax.text(self.start[1], self.start[0], "S", **textstyle)
        end_text = ax.text(self.end[1], self.end[0], "E", **textstyle)

        #  Mark cells greedy first and a star search
        if self.search_type in ("gfs", "astar"):
            for r, row in enumerate(self.walls):
                for c, cell_value in enumerate(row):
                    cell = (r, c)

                    # Mark path cells based on manhattan distance to endpoint
                    if cell_value is False and cell not in (self.start, self.end):
                        cell_text = ax.text(
                            c,
                            r,
                            str(self.get_manhattan_distance(cell, self.end)),
                            **textstyle,
                        )
                        self.text_dict[cell] = cell_text
        return (fig, ax, im, start_text, end_text)

    def animate(self):
        # Convert boolean to int
        maze_int = np.array(self.walls, dtype=int)

        fig, ax, im, start_text, end_text = self.draw(maze_int)

        visited_cells = self.explored_list
        if self.solution:
            solution_cells = [node.state for node in self.solution[1]]
            solution_cells.append(self.end)
        else:
            solution_cells = None

        def finding_solution(frame_index):
            if frame_index < len(visited_cells):
                # Mark cells as visited in yellow
                cell = visited_cells[frame_index]
                maze_int[cell] = 2  # 2 = visited

                # astar search type mark visited cells with manhattan + cost
                if self.search_type == "astar" and cell not in (self.start, self.end):
                    t_obj = self.text_dict[cell]

                    # Set smaller font
                    t_obj.set_fontsize(10)

                    current_text = t_obj.get_text()
                    t_obj.set_text(f"{current_text}+{self.cost[cell]}")

            elif solution_cells is not None:
                for x, y in solution_cells:
                    maze_int[x, y] = 3  # 3 = solution
            else:
                ax.text(
                    1,
                    self.height,
                    "No solution",
                    fontsize=20,
                    ha="center",
                    va="center",
                    color="red",
                )
            im.set_data(maze_int)  # Update the image
            return [im, start_text, end_text]

        total_frames = len(visited_cells) + 1

        ani = FuncAnimation(
            fig, finding_solution, frames=total_frames, interval=400, repeat=False
        )

        # Save animation as gif. Before use comment out 'plt.show' below
        # ani.save(filename="animation/pillow_example.gif", writer="pillow")

        plt.show()


# Check valid script useage
if len(sys.argv) != 3:
    print("Usage: maze.py <path_to_maze> <search_type>")
    sys.exit(1)

_, maze_path, search = sys.argv

valid_search_type = {"bfs", "dfs", "gfs", "astar"}

# Check valid search type provided
if search not in valid_search_type:
    print(f"Invalid search type: {search}")
    print(f"Please provide valid search type: {valid_search_type}")
    sys.exit(1)

maze = Maze(maze_path, search)
maze.solve()
maze.animate()
