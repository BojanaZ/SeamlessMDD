class EmptyHeapError(Exception):
    pass


class Heap(object):

    def __init__(self, data=None):
        """
        Max heap.
        """

        if not data:
            self._data = []
            self._size = 0
            return

        self._data = data
        self._size = len(self._data)
        self._build_max_heap()

    def _left(self, i):
        """
        Left child index.

        - `i`: parent node index
        """
        return 2 * i + 1

    def _right(self, i):
        """
        Right child index.

        Argument:
        - `i`: parent node index
        """
        return 2 * i + 2

    def _parent(self, index):
        """
        Parent node index.

        Argument:
        - `i`: child node index
        """
        return (index-1)//2

    def _swap(self, a, b):
        """
        Swaps two nodes by index.

        Argument:
        - `a`: first node index.
        - `b`: second node index.
        """
        self._data[a], self._data[b] = self._data[b], self._data[a]

    def _downheap(self, i):
        """
        Builds max-heap from tree with root node on index i.

        Argument:
        - `i`: root node index
        """

        left = self._left(i)
        right = self._right(i)

        if left < self._size and self._data[left] > self._data[i]:
            largest = left
        else:
            largest = i

        if right < self._size and self._data[right] > self._data[largest]:
            largest = right

        if largest != i:
            self._swap(i, largest)
            self._downheap(largest)

    def _build_max_heap(self):
        """
        Builds max heap from all nodes.
        """
        self._size = len(self._data)

        start = (self._size - 1) // 2
        for i in range(start, -1, -1):
            self._downheap(i)

    def add(self, new_item):
        """
        Inserts single element to heap
        :param new_item:
        :return:
        """
        self._data.append(new_item)
        self._size += 1
        self._upheap(len(self._data)-1)

    def extend(self, items):
        for item in items:
            self.add(item)

    def _upheap(self, index):
        parent_index = self._parent(index)
        if parent_index < 0 or self._data[index] < self._data[parent_index]:
            return
        self._swap(index, parent_index)
        self._upheap(parent_index)

    def sort(self):
        """
        Heap sort algorithm.
        """
        for i in range(self._size - 1, 0, -1):
            self._swap(0, i)

            self._size -= 1

            self._downheap(0)

    def __len__(self):
        return self._size

    def is_empty(self):
        return len(self) == 0

    def remove_max(self):
        """
        Finds and removes element with maximum priority
        """
        if self.is_empty():
            raise EmptyHeapError("Empty task heap")

        self._swap(0, self._size - 1)
        ret_node = self._data.pop(self._size - 1)
        self._size -= 1

        self._downheap(0)
        return ret_node

    def max(self):
        if self.is_empty():
            raise EmptyHeapError("Empty task heap")
        return self._data[0]

    def get_items(self):
        return self._data
