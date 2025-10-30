import jwt
print("jwt包的所有方法:")
print([x for x in dir(jwt) if not x.startswith('_')])