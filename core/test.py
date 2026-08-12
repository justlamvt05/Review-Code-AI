from core.security import PasswordService
from core.security import JwtService
hashed = PasswordService.hash("123456")

print(hashed)

# print(PasswordService.verify_password("123456", hashed))
#
# print(PasswordService.verify_password("abc", hashed))
#
#
#
# token = JwtService.create_access_token("123")
#
# print(token)
#
# print(JwtService.decode_token(token))