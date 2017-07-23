from typing import Union

from aiohttp.web import Request

from . import auth

async def get_session_from_request(request: Request) -> Union[
  auth.UserSession,
  None
]:
  authorization_header = request.headers.get('Authorization')
  if authorization_header is None:
    return None

  string_user_session = authorization_header.replace('Bearer ', '')
  if string_user_session is None:
    return None

  return auth.decode(string_user_session)
