"""Doubly linked list (next and prev pointers) used to model a bus route."""


class Node:
    def __init__(self, name, zone=""):
        self.name = name
        self.zone = zone
        self.next = None   # pointer to the next node
        self.prev = None   # pointer to the previous node


class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.current = None   # station where the bus is right now
        self.length = 0

    # ---------- insertion ----------
    def append(self, name, zone=""):
        """Add a node at the end."""
        new_node = Node(name, zone)
        if self.head is None:
            self.head = self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
        self._after_insert(new_node)

    def prepend(self, name, zone=""):
        """Add a node at the start."""
        new_node = Node(name, zone)
        if self.head is None:
            self.head = self.tail = new_node
        else:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node
        self._after_insert(new_node)

    def insert(self, index, name, zone=""):
        """Insert a node at any position (0..length)."""
        if index < 0 or index > self.length:
            raise IndexError(f"Index {index} out of range (0 to {self.length})")
        if index == 0:
            return self.prepend(name, zone)
        if index == self.length:
            return self.append(name, zone)
        new_node = Node(name, zone)
        follower = self.node_at(index)
        leader = follower.prev
        leader.next = new_node
        new_node.prev = leader
        new_node.next = follower
        follower.prev = new_node
        self._after_insert(new_node)

    def _after_insert(self, new_node):
        self.length += 1
        if self.current is None:
            self.current = new_node

    # ---------- deletion ----------
    def remove(self, index):
        """Remove the node at 'index' and return it."""
        if index < 0 or index >= self.length:
            raise IndexError(f"Index {index} out of range (0 to {self.length - 1})")
        node = self.node_at(index)
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next
        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev
        if self.current is node:
            self.current = node.next or node.prev
        node.next = node.prev = None
        self.length -= 1
        return node

    # ---------- queries ----------
    def node_at(self, index):
        """Walk from the head or from the tail, whichever is closer."""
        if index < self.length / 2:
            node = self.head
            for _ in range(index):
                node = node.next
        else:
            node = self.tail
            for _ in range(self.length - 1 - index):
                node = node.prev
        return node

    def path_to(self, index):
        """Indexes visited to reach 'index' (used for the animation)."""
        if index < self.length / 2:
            return list(range(0, index + 1))
        return list(range(self.length - 1, index - 1, -1))

    def search(self, text):
        """Index of the first station whose name contains 'text' (-1 if none)."""
        node, i = self.head, 0
        while node:
            if text.lower() in node.name.lower():
                return i
            node, i = node.next, i + 1
        return -1

    def to_list(self):
        result, node = [], self.head
        while node:
            result.append(node)
            node = node.next
        return result

    # ---------- bus ----------
    def next_stop(self):
        if self.current and self.current.next:
            self.current = self.current.next
            return True
        return False

    def prev_stop(self):
        if self.current and self.current.prev:
            self.current = self.current.prev
            return True
        return False

    def empty(self):
        self.head = self.tail = self.current = None
        self.length = 0
