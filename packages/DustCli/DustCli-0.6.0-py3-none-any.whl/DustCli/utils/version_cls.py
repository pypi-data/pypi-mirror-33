
class Version:
    def __init__(self, version):
        self.main = int(version.split('.')[0])
        self.mid = int(version.split('.')[1])
        self.last = int(version.split('.')[2])

    def higher_than(self, other):
        return self.main > other.main or (self.main == other.main and self.mid > other.mid) or (self.main == other.main and self.mid == other.mid and self.last > other.last)

    def equal_or_higher_than(self, other):
        equal = self.main == other.main and self.mid == other.mid and self.last == other.last
        return equal or self.higher_than(other)

    def __lt__(self, other):
        if self.main == other.main and self.mid == other.mid and self.last == other.last:
            return 0
        elif self.main > other.main or (self.main == other.main and self.mid > other.mid) or (self.main == other.main and self.mid == other.mid and self.last > other.last):
            return -1
        else:
            return 1

    def __str__(self):
        return '%d.%d.%d' % (self.main, self.mid, self.last)
