

class UndoRedoStack:

    def __init__(self, undo_limit=10, redo_limit=5):
        self.undo_limit = undo_limit
        self.redo_limit = redo_limit

        self.undo_stack = list()
        self.redo_stack = list()

    def __str__(self):
        return f"undo stack: {self.undo_stack}\n redo stack: {self.redo_stack}"

    def add(self, item):

        if len(self.undo_stack) == self.undo_limit:
            self.undo_stack.pop()

        self.undo_stack.append(item)

    def _update_redo(self, item):

        if len(self.redo_stack) == self.redo_limit:
            self.redo_stack.pop()

        self.redo_stack.append(item)

    def undo_move(self):

        if len(self.undo_stack) != 0:
            undo = self.undo_stack.pop()
            self._update_redo(undo)

        else:
            undo = None

        return undo

    def redo_move(self):

        if len(self.redo_stack) != 0:
            redo = self.redo_stack.pop()

        else:
            redo = None

        return redo

    def pop_undo(self):
        self.undo_stack.pop()