import buffer

buf = buffer.Buffer()

buf.set_length(10)
buf.put(b"aaaaa")
print(buf.get(), buf.is_full())
print(buf.put(b'bbbbbb'))
print(buf.is_full())
print(buf.get())