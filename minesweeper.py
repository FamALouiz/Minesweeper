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
        else:
            return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        else:
            return set()

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
        if cell not in self.safes:
            self.mark_safe(cell)

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
                if x + i >= 0 and y + j >= 0 and x + i <= 7 and y + j <= 7:
                    if i != 0 or j != 0 and not ((x + i, y + j) in self.moves_made):
                        cells_to_add_to_sentence.add((x + i, y + j))

        new_sentence = Sentence(cells_to_add_to_sentence, count)
        self.knowledge.append(new_sentence)

        for sentence in self.knowledge:
            if len(sentence.cells) == 0:
                self.knowledge.remove(sentence)
            safe_cells = list(sentence.known_safes())
            mine_cells = list(sentence.known_mines())
            for safe in safe_cells:
                self.mark_safe(safe)
            for mine in mine_cells:
                self.mark_mine(mine)

        condensed_data = []
        data_to_be_removed = []

        # Updating/Condensing sets
        for sentence in self.knowledge:
            if len(sentence.cells) == 0:
                self.knowledge.remove(sentence)
            elif len(sentence.cells) == len(new_sentence.cells):
                continue
            elif new_sentence.cells.issubset(sentence.cells):
                data_to_be_removed.append(new_sentence)
                data_to_be_removed.append(sentence)
                condensed_data.append(
                    Sentence(
                        sentence.cells - new_sentence.cells,
                        sentence.count - new_sentence.count,
                    )
                )
            elif sentence.cells.issubset(new_sentence.cells):
                data_to_be_removed.append(new_sentence)
                data_to_be_removed.append(sentence)
                condensed_data.append(
                    Sentence(
                        new_sentence.cells - sentence.cells,
                        new_sentence.count - sentence.count,
                    )
                )
            else:
                to_be_removed = []
                for cell in sentence.cells:
                    if cell in self.moves_made:
                        to_be_removed.append(cell)
                for cell in to_be_removed:
                    sentence.cells.remove(cell)

        # Adding new conclusion to knowledge base
        if len(data_to_be_removed) > 1:
            for sentence in data_to_be_removed:
                if sentence in self.knowledge:
                    self.knowledge.remove(sentence)
        elif len(data_to_be_removed) == 1:
            if sentence in self.knowledge:
                self.knowledge.remove(data_to_be_removed[0])
        if len(condensed_data) > 1:
            for sentence in condensed_data:
                if not sentence in self.knowledge:
                    self.knowledge.append(sentence)
        elif len(condensed_data) == 1:
            if not sentence in self.knowledge:
                self.knowledge.append(condensed_data[0])

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
        board = set()

        for i in range(8):
            for j in range(8):
                board.add((i, j))

        for move in self.moves_made:
            board.remove(move)

        possible_moves = []

        for move in board:
            if not move in self.mines:
                possible_moves.append(move)

        for move in possible_moves:
            for sentence in self.knowledge:
                if not move in sentence.cells:
                    return move
        if len(possible_moves) != 1 and len(possible_moves) != 0:
            return possible_moves[random.randint(0, len(possible_moves) - 1)]
        elif len(possible_moves) == 0:
            return None
        else:
            possible_moves[0]
