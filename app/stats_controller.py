from aiohttp.web import Request, Response, json_response

from .utils.mattermost import client
from .utils.messages import pulse, most_active
from .utils import route_helpers

async def pulse_route(request: Request) -> Response:
  user_session = route_helpers.get_session_from_request(request)
  if user_session is None:
    return json_response({
      'status': 400,
      'data': [],
      'message': 'No authentication token provided',
      'errors': []
    })

  pulse_beat = pulse.pulse_global(client.get_channels_messages(user_session))
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
  user_session = route_helpers.get_session_from_request(request)
  if user_session is None:
    return json_response({
      'status': 400,
      'data': [],
      'message': 'No authentication token provided',
      'errors': []
    })

  channel_id = request.match_info['channel_id']

  pulse_beat = pulse.pulse(
    client.get_channel_messages(user_session, channel_id),
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
  user_session = route_helpers.get_session_from_request(request)
  if user_session is None:
    return json_response({
      'status': 400,
      'data': [],
      'message': 'No authentication token provided',
      'errors': []
    })

  channel_id = request.match_info['channel_id']

  most_active_users = most_active.most_active_n_users(
    client.get_channel_messages(user_session, channel_id),
    5
  )

  return json_response({
    'status': 200,
    'data': most_active_users,
    'message': 'Success',
    'errors': []
  })


async def hot_topics_by_channel_route(request: Request) -> Response:
  user_session = route_helpers.get_session_from_request(request)
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
  user_session = route_helpers.get_session_from_request(request)
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
  user_session = route_helpers.get_session_from_request(request)
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
