class BBox:
    def __init__(self, r1=None, c1=None, r2=None, c2=None, label=None):
        self.r1 = r1
        self.c1 = c1
        self.r2 = r2
        self.c2 = c2
        self.label = label

    def __repr__(self):
        return '{} object at ({}, {}) : ({}, {})'.\
            format(self.label, self.c1, self.r1, self.c2, self.r2)