import os
from typing import Dict, List
from datetime import datetime

from mattermostdriver import Driver
import pydash as _

from ..auth import UserSession


class Client:

  def __init__(self, user_session: UserSession):
    self.user_session = user_session
    self.driver = Driver({
      'login_id': self.user_session.username,
      'password': self.user_session.password,
      'verify': False,
      'scheme': os.getenv('MATTERMOST_SCHEME'),
      'url': os.getenv('MATTERMOST_URL_WITH_PORT')
    })
    self.driver.login()

  def get_channels(self) -> List[Dict]:
    teams_list = self.driver.api['teams'].get_teams()

    def channels_per_team(team: Dict) -> List[Dict]:
      team_id = team.get('id')
      channels_list = \
        self.driver.api['teams'].get_public_channels(team_id)

      def channel_transformer(channel: Dict) -> Dict:
        return {
          'id': channel.get('id'),
          'name': channel.get('display_name')
        }
      return _.map_(channels_list, channel_transformer)

    return _.flatten(_.map_(teams_list, channels_per_team))

  def get_channel_messages(self, channel_id: str) -> List[Dict]:
    channel_messages: Dict = \
      self.driver.api['posts'].get_posts_for_channel(channel_id)

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

  def get_channels_messages(self) -> List[
    List[Dict]
  ]:
    return _.map_(
      self.get_channels(),
      lambda channel: self.get_channel_messages(
        channel.get('id')
      )
    )

  def get_username_by_id(self, id: str) -> str:
    return self.driver.api['users'].get_user(id).get('username')
