import itertools
import random


class Minesweeper:
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence:
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return self.cells

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI:
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function:
            1) marks the cell as a move that has been made
            2) marks the cell as safe
            3) adds a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) marks any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) adds any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        # Marks move as made
        self.moves_made.add(cell)

        # Adding to safe cells
        self.safes.add(cell)

        # Updating any sentence with the new safe cell
        if len(self.knowledge) > 1:
            for sentence in self.knowledge:
                if cell in sentence.cells:
                    sentence.mark_safe(cell)
        elif len(self.knowledge) == 1:
            if cell in self.knowledge[0].cells:
                self.knowledge[0].mark_safe(cell)

        # Adding new knowledge
        x, y = cell
        cells_to_add_to_sentence = set()
        for i in range(-1, 2):
            for j in range(-1, 2):
                if x + i > 0 and y + j > 0 and x + i < 8 and y + i < 8:
                    if i != 0 or j != 0:
                        cells_to_add_to_sentence.add((x + i, y + j))
        self.knowledge.append(Sentence(cells_to_add_to_sentence, count))

        # Deducing any new mines or safes
        known_mines = None
        known_safes = None

        for sentence in self.knowledge:
            known_mines = sentence.known_mines()
            known_safes = sentence.known_safes()

        if known_mines != None:
            self.mines.update(known_mines)
        if known_safes != None:
            self.safes.update(known_safes)

        condensed_data = []
        data_to_be_removed = []

        # Updating/Condensing sets
        for i in range(len(self.knowledge)):
            changes = 0
            for sentence1 in self.knowledge:
                for sentence2 in self.knowledge:
                    if sentence1 != sentence2 and sentence1.cells.issubset(
                        sentence2.cells
                    ):
                        data_to_be_removed.append(sentence1)
                        data_to_be_removed.append(sentence2)
                        condensed_data.append(
                            Sentence(
                                sentence2.cells - sentence1.cells,
                                sentence2.count - sentence1.count,
                            )
                        )
                        changes += 1
            if changes == 0:
                break

        for item in data_to_be_removed:
            try:
                self.knowledge.remove(item)
            except:
                continue
        for item in condensed_data:
            try:
                self.knowledge.append(item)
            except:
                continue

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        """
        if len(self.safes) == 0:
            return None
        for move in self.safes:
            if not move in self.moves_made:
                return move

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        for x_count in range(8):
            for y_count in range(8):
                cell = (x_count, y_count)
                if not cell in self.moves_made and not cell in self.mines:
                    return cell
