import jwt
import simplecrypt

import binascii
from typing import Union
import os
import json


class UserSession:
  username: str
  password: str


def encode(session: UserSession) -> str:
  """
  Encode a payload into a JWT Web Token to symbolize a session
  :param payload:
  :return:
  """
  session_as_string = json.dumps(session.__dict__)
  encrypted_payload = binascii.hexlify(simplecrypt.encrypt(
    os.getenv('TOKEN_SECRET'),
    session_as_string
  )).decode('utf-8')

  return jwt.encode(
    {'payload': encrypted_payload},
    os.getenv('TOKEN_SECRET'),
    algorithm='HS256'
  ).decode('utf-8')


def decode(token: str) -> Union[UserSession, None]:
  """
  Decode a JWT Web Token that symbolizes a session to a payload
  :param token: String
  :return:
  """
  encrypted_payload = jwt.decode(
    token,
    os.getenv('TOKEN_SECRET'),
    algorithms=['HS256']
  ).get('payload')
  if encrypted_payload is None:
    return None

  try:
    decrypted_payload_str = simplecrypt.decrypt(
      os.getenv('TOKEN_SECRET'),
      binascii.unhexlify(encrypted_payload)
    ).decode('utf-8')
    decrypted_payload_dict = json.loads(
      decrypted_payload_str
    )
  except:
    return None

  user_credentials = UserSession()
  user_credentials.username = str(decrypted_payload_dict.get('username'))
  user_credentials.password = str(decrypted_payload_dict.get('password'))

  return user_credentials

