import os
from typing import Dict, List
from datetime import datetime

from mattermostdriver import Driver
import pydash as _

from ..auth import UserSession


def construct_driver(user_session: UserSession) -> Driver:
  driver = Driver({
    'login_id': user_session.username,
    'password': user_session.password,
    'verify': False,
    'scheme': os.getenv('MATTERMOST_SCHEME'),
    'url': os.getenv('MATTERMOST_URL_WITH_PORT')
  })
  driver.login()
  return driver


def get_channels(user_session: UserSession) -> List[Dict]:
  driver: Driver = construct_driver(user_session)
  teams_list = driver.api['teams'].get_teams()

  def channels_per_team(team: Dict) -> List[Dict]:
    team_id = team.get('id')
    channels_list = \
      driver.api['teams'].get_public_channels(team_id)

    def channel_transformer(channel: Dict) -> Dict:
      return {
        'id': channel.get('id'),
        'name': channel.get('display_name')
      }
    return _.map_(channels_list, channel_transformer)

  return _.flatten(_.map_(teams_list, channels_per_team))


def get_channel_messages(user_session: UserSession,
                         channel_id: str) -> List[Dict]:
  driver: Driver = construct_driver(user_session)
  channel_messages: Dict = \
    driver.api['posts'].get_posts_for_channel(channel_id)

  def message_transformer(post_id: str) -> Dict:
    return {
      'userid': channel_messages.get('posts', {})
        .get(post_id, {})
        .get('user_id'),
      'content': channel_messages.get('posts', {})
        .get(post_id, {})
        .get('message'),
      'timestamp': datetime.fromtimestamp(
        float(
          channel_messages.get('posts', {})
            .get(post_id, {})
            .get('create_at')
        ) / 1000
      )
    }

  return sorted(_.map_(
    _.reverse(channel_messages.get('order')),
    message_transformer
  ), key=lambda message: message.get('timestamp'))


def get_channels_messages(user_session: UserSession) -> List[
  List[Dict]
]:
  return _.map_(
    get_channels(user_session),
    lambda channel: get_channel_messages(
      user_session,
      channel.get('id')
    )
  )


def get_username_by_id(user_session: UserSession, id: str) -> str:
  driver: Driver = construct_driver(user_session)
  return driver.api['users'].get_user(id).get('username')
