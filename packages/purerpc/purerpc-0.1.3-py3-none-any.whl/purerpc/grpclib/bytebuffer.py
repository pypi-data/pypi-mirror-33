import collections


class ByteBuffer:
    def __init__(self):
        self._deque = collections.deque()
        self._size = 0

    def append(self, data):
        if not isinstance(data, bytes):
            raise ValueError("Expected bytes")
        if data:
            self._deque.append(data)
            self._size += len(data)

    def popleft(self, amount):
        if amount > self._size:
            raise ValueError("Trying to extract {} bytes from ByteBuffer of length {}".format(
                amount, self._size))
        data = []
        while amount > 0:
            next_element = self._deque[0]
            if amount >= len(next_element):
                self._size -= len(next_element)
                amount -= len(next_element)
                data.append(self._deque.popleft())
            else:
                data.append(next_element[:amount])
                self._deque[0] = next_element[amount:]
                self._size -= amount
                amount = 0
        return b"".join(data)

    def __len__(self):
        return self._size