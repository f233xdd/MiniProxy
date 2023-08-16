import queue_ex

q = queue_ex.DoubleQueue()
q.add_flag(1)
q.add_flag(2)

q.put(123, 1, exchange=True)
q.put(123, 1)
q.put(123, 1, exchange=True)

for i in q.get_all(1, exchange=False):
    print(i)

for i in q.get_all(2, exchange=True):
    print(i)