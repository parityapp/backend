from aiohttp.web import Request, Response, json_response
from cerberus import Validator
import pydash as _

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

  user_session = auth.UserSession()
  user_session.username = request_body.get('username')
  user_session.password = request_body.get('password')

  try:
    mattermost = client.Client(user_session)
  except:
    return json_response({
      'status': 400,
      'data': {},
      'message': 'Invalid credentials',
      'errors': []
    })

  token_str = auth.encode(user_session)
  user_channels = mattermost.get_channels()
  all_messages = mattermost.get_channels_messages()
  global_pulse = _.map_(
    pulse.pulse_global(all_messages),
    lambda pulse: _.assign(
      pulse,
      {'time': pulse.get('time').isoformat()}
    )
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
