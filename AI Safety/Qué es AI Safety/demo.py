class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if not self.is_empty():
            return self.items.pop()

    def peek(self):
        return self.items[-1]
        pass

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)


stack = Stack()
stack.push(10)
stack.push(25)
stack.push(7)

print("Top:", stack.peek())
print("Size:", stack.size())
stack.pop()
print("After pop, top:", stack.peek())
