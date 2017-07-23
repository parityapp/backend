from aiohttp.web import Request, Response, json_response
import pydash as _

from .utils.mattermost import client
from .utils.messages import pulse, most_active
from .utils import route_helpers

async def pulse_route(request: Request) -> Response:
  user_session = await route_helpers.get_session_from_request(request)
  if user_session is None:
    return json_response({
      'status': 400,
      'data': [],
      'message': 'No authentication token provided',
      'errors': []
    })

  try:
    mattermost = client.Client(user_session)
  except:
    return json_response({
      'status': 400,
      'data': {},
      'message': 'Invalid credentials',
      'errors': []
    })

  pulse_beat = _.map_(
    pulse.pulse_global(
      mattermost.get_channels_messages()
    ),
    lambda pulse: _.assign(
      pulse,
      {'time': pulse.get('time').isoformat()}
    )
  )
  if pulse_beat is None:
    return json_response({
      'status': 400,
      'data': [],
      'message': 'No pulse obtained',
      'errors': []
    })

  return json_response({
    'status': 200,
    'data': pulse_beat,
    'message': 'Success',
    'errors': []
  })

async def pulse_by_channel_route(request: Request) -> Response:
  user_session = await route_helpers.get_session_from_request(request)
  if user_session is None:
    return json_response({
      'status': 400,
      'data': [],
      'message': 'No authentication token provided',
      'errors': []
    })

  try:
    mattermost = client.Client(user_session)
  except:
    return json_response({
      'status': 400,
      'data': {},
      'message': 'Invalid credentials',
      'errors': []
    })

  channel_id = request.match_info['channel_id']

  pulse_beat = _.map_(
    pulse.pulse(
      mattermost.get_channel_messages(channel_id)
    ),
    lambda pulse: _.assign(
      pulse,
      {'time': pulse.get('time').isoformat()}
    )
  )

  if pulse_beat is None:
    return json_response({
      'status': 400,
      'data': [],
      'message': 'No pulse obtained',
      'errors': []
    })

  return json_response({
    'status': 200,
    'data': pulse_beat,
    'message': 'Success',
    'errors': []
  })

async def most_active_by_channel_route(request: Request) -> Response:
  user_session = await route_helpers.get_session_from_request(request)
  if user_session is None:
    return json_response({
      'status': 400,
      'data': [],
      'message': 'No authentication token provided',
      'errors': []
    })

  try:
    mattermost = client.Client(user_session)
  except:
    return json_response({
      'status': 400,
      'data': {},
      'message': 'Invalid credentials',
      'errors': []
    })

  channel_id = request.match_info['channel_id']

  most_active_users = _.map_(most_active.most_active_n_users(
    mattermost.get_channel_messages(channel_id),
    5
  ), lambda user_id: mattermost.get_username_by_id(user_id))

  return json_response({
    'status': 200,
    'data': most_active_users,
    'message': 'Success',
    'errors': []
  })


async def hot_topics_by_channel_route(request: Request) -> Response:
  user_session = await route_helpers.get_session_from_request(request)
  if user_session is None:
    return json_response({
      'status': 400,
      'data': [],
      'message': 'No authentication token provided',
      'errors': []
    })

  channel_id = request.match_info['channel_id']

  return json_response({
    'status': 200,
    'data': [],
    'message': 'Success',
    'errors': []
  })


async def representative_messages_by_channel_route(request: Request) -> Response:
  user_session = await route_helpers.get_session_from_request(request)
  if user_session is None:
    return json_response({
      'status': 400,
      'data': [],
      'message': 'No authentication token provided',
      'errors': []
    })

  channel_id = request.match_info['channel_id']

  return json_response({
    'status': 200,
    'data': [],
    'message': 'Success',
    'errors': []
  })


async def summary_by_channel_route(request: Request) -> Response:
  user_session = await route_helpers.get_session_from_request(request)
  if user_session is None:
    return json_response({
      'status': 400,
      'data': [],
      'message': 'No authentication token provided',
      'errors': []
    })

  channel_id = request.match_info['channel_id']

  return json_response({
    'status': 200,
    'data': [],
    'message': 'Success',
    'errors': []
  })
