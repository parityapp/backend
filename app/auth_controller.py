from aiohttp.web import Request, Response, json_response
from cerberus import Validator

from .utils import auth
from .utils.mattermost import client
from .utils.messages import pulse

async def auth_route(request: Request) -> Response:
  validator = Validator({
    'username': {'required': True, 'type': 'string'},
    'password': {'required': True, 'type': 'string'}
  })

  try:
    request_body = await request.json()
  except:
    return json_response({
      'status': 400,
      'data': {},
      'message': 'No payload provided',
      'errors': []
    })

  if not validator.validate(request_body):
    return json_response({
      'status': 400,
      'data': {},
      'message': 'Payload must have username and password props',
      'errors': validator.errors
    })

  user_session = client.UserSession()
  user_session.username = request_body.get('username')
  user_session.password = request_body.get('password')

  try:
    client.construct_driver(user_session)
  except:
    return json_response({
      'status': 400,
      'data': {},
      'message': 'Invalid credentials',
      'errors': []
    })

  token_str = auth.encode(user_session)
  user_channels = client.get_channels(user_session)
  global_pulse = pulse.pulse_global(
    client.get_channels_messages(user_session)
  )

  return json_response({
    'status': 200,
    'data': {
      'token': token_str,
      'channels': user_channels,
      'pulse': global_pulse
    },
    'message': 'Success',
    'errors': []
  })
