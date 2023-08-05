import heapq

class HeapItem:
    def __init__(self, data, compFunc):
        self.data = data
        self.compFunc = compFunc

    def __lt__(self, other):
        return self.compFunc(self.data, other.data)

class Heap:
    def __init__(self, compFunc):
        self.heap = []
        self.compFunc = compFunc

    def __len__(self):
        return len(self.heap)

    def pop(self):
        return heapq.heappop(self.heap).data

    def push(self, data):
        heapq.heappush(self.heap, HeapItem(data, self.compFunc))
