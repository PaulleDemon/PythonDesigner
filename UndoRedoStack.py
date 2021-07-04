from copy import deepcopy


class UndoRedoStack:  # stores undo redo moves in a list

    def __init__(self, undo_limit=10, redo_limit=5):
        self.undo_limit = undo_limit
        self.redo_limit = redo_limit

        self.undo_stack = list()
        self.redo_stack = list()

    def __str__(self):
        return f"undo stack: {self.undo_stack}\n redo stack: {self.redo_stack}"

    def __len__(self):
        return len(self.undo_stack)

    def add(self, item):

        if len(self.undo_stack) == self.undo_limit:
            self.undo_stack.pop()

        if item not in self.undo_stack:
            self.undo_stack.append(item)

    def add_redo(self, item):
        if len(self.redo_stack) == self.undo_limit:
            self.undo_stack.pop()

        if item not in self.redo_stack:
            self.redo_stack.append(item)

    def _update_redo(self, item):

        if len(self.redo_stack) == self.redo_limit:
            self.redo_stack.pop(0)
        # deepcopy is necessary else both deserialize and redo stack will point to same address hence deleting
        # from viewport deserialize will delete here in redo stack too
        self.redo_stack.append(deepcopy(item))

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
