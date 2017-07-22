from typing import List, Dict, Union, Tuple
from datetime import datetime, timedelta
import functools
import math
import pydash as _


def round_to_nearest_n_minutes(
    minute_interval_size: int,
    actual_time: datetime = datetime.now(),
    rounder_func=round
) -> datetime:
  nth_minute_interval = actual_time.minute // minute_interval_size
  leftover = rounder_func(actual_time.minute
                          % minute_interval_size
                          / minute_interval_size)

  established_minute = (
    nth_minute_interval * minute_interval_size +
    leftover * minute_interval_size
  )
  if established_minute > 59:
    return actual_time.replace(
      hour=actual_time.hour + 1,
      minute=0,
      second=0,
      microsecond=0
    )

  return actual_time.replace(
    minute=established_minute,
    second=0,
    microsecond=0
  )


def pulse(messages: List[Dict], interval: int=5) -> Union[
  List[Dict],
  None
]:
  """
  Representative Pulse for a stream of messages
  :param messages: List[{userid:str, content:str, timestamp:datetime}]
  :param interval: Size of a pulse point, in minutes
  :return: List[{rate, time}]
  """
  if len(messages) < 2:
    return None

  round_to_nearest_interval_minutes = functools.partial(
    round_to_nearest_n_minutes, interval, rounder_func=math.ceil
  )

  def datetime_clusterer(tuplet: Tuple[List[Dict], int],
                         message: Dict) -> Tuple[List, int]:

    message_anchored_time = round_to_nearest_interval_minutes(
      message.get('timestamp')
    )

    # No cluster: create a cluster
    if not tuplet:
      return [{
        'rate': 1,
        'time': message_anchored_time
      }], 1

    pulse_clusters, max_pulse_rate = tuplet
    latest_pulse = pulse_clusters.pop()

    # Message fits in cluster - cluster it up!
    if latest_pulse.get('time') == message_anchored_time:

      new_pulse_rate = latest_pulse.get('rate') + 1
      new_pulse_clusters = _.push(
        pulse_clusters,
        _.assign(latest_pulse, {'rate': new_pulse_rate})
      )

      if max_pulse_rate >= new_pulse_rate:
        return new_pulse_clusters, max_pulse_rate
      return new_pulse_clusters, new_pulse_rate

    # Message doesn't fit in cluster
    # lock in latest cluster, create new cluster but also fill
    # in missing clusters in between
    old_pulse_cluster = _.push(pulse_clusters, latest_pulse)
    minutes_difference = message_anchored_time - latest_pulse.get('time')
    intervals_difference = \
      ((minutes_difference.seconds // 60) // interval) - 1
    if intervals_difference > 0:
      for x in range(0, intervals_difference):
        old_pulse_cluster = _.push(old_pulse_cluster, {
          'rate': 0,
          'time': latest_pulse.get('time') + timedelta(minutes=interval * (x + 1))
        })

    return _.push(
      old_pulse_cluster,
      _.assign({}, {'rate': 1, 'time': message_anchored_time})
    ), max_pulse_rate

  pulse_clusters, max_pulse_rate = _.reduce_(
    messages, datetime_clusterer, ()
  )

  def rate_normalizer(max_rate: int):
    return lambda pulse_dict: _.assign(pulse_dict, {
      'rate': pulse_dict.get('rate') / max_rate
    })
  return _.map_(pulse_clusters, rate_normalizer(max_pulse_rate))
