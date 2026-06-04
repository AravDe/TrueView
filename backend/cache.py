import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

r.set('foo', 'bar')
# True
output1 = r.get('bar')
print(output1)
# bar

r.hset('user-session:123', mapping={
    'name': 'John',
    "surname": 'Smith',
    "company": 'Redis',
    "age": 29
})
# True

output = r.hgetall('user-session:123')
print(output)
# {'surname': 'Smith', 'name': 'John', 'company': 'Redis', 'age': '29'}

r.close()
