class Test:
    def __init__(self) -> None:
        self.l = [i for i in range(10)]
    
    def add(self):
        self.l.extend([f"test_{i}" for i in range(10)])
    
    @property
    def func(self):
        while self.l:
            yield self.l.pop(0)

test = Test()
print(list(test.func))

for i in test.func:
    print(i)

test.add()
for i in test.func:
    print(i)