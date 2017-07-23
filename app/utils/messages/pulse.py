from typing import List, Dict, Union, Tuple, Union
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


def zero_pulses(start_time: datetime,
                end_time: datetime,
                interval: int) -> List[Dict]:
  minutes_difference = end_time - start_time
  intervals_difference = \
    ((minutes_difference.seconds // 60) // interval) - 1

  if intervals_difference > 0:
    pulses = []
    for x in range(0, intervals_difference):
      pulses = _.push([], {
        'rate': 0,
        'time': start_time + timedelta(minutes=interval * (x + 1))
      })
    return pulses

  return []


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
    old_pulse_cluster = _.concat(zero_pulses(
      start_time=latest_pulse.get('time'),
      end_time=message_anchored_time,
      interval=interval
    ), old_pulse_cluster)

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


def pulse_global(message_groups: List[List[Dict]],
                 interval: int=5) -> Union[
  List[Dict],
  None
]:
  if not message_groups:
    return []

  pulses: List[List[Dict]] = _.map_(
    message_groups,
    lambda message: pulse(message, interval)
  )

  def remove_nones(pulses: List[Union[List[Dict], None]],
                   pulse: Union[List[Dict], None]) -> List[List[Dict]]:
    if pulse is None:
      return pulses

    return _.push(pulses, pulse)
  pulses = _.reduce_(pulses, remove_nones, [])

  def pulses_align(pulses: List[List[Dict]]) -> List[List[Dict]]:
    earliest_time = _.min_by(
      pulses,
      lambda pulse: pulse[0].get('time')
    )[0].get('time')
    latest_time = _.max_by(
      pulses,
      lambda pulse: pulse[-1].get('time')
    )[0].get('time')

    return _.map_(
      pulses,
      lambda pulse: _.concat(zero_pulses(
        start_time=earliest_time,
        end_time=pulse[0].get('time'),
        interval=interval
      ), pulse, zero_pulses(
        start_time=pulse[-1].get('time'),
        end_time=latest_time,
        interval=interval
      ))
    )
  pulses = pulses_align(pulses)

  def collapser(collapsed_pulses: List[Dict],
                pulses: List[Dict]) -> List[Dict]:
    if not collapsed_pulses:
      return pulses

    def message_adder(index):
      collapsed_pulse = collapsed_pulses[index]
      pulse = pulses[index]

      return _.assign(
        collapsed_pulse, {
          'rate': collapsed_pulse.get('rate') + pulse.get('rate')
        }
      )

    return _.map_(
      _.range_(len(collapsed_pulses)),
      message_adder
    )
  pulse_clusters = _.reduce_(
    pulses,
    collapser,
    []
  )
  max_pulse_rate = _.max_by(pulse_clusters, 'rate').get('rate')

  def rate_normalizer(max_rate: int):
    return lambda pulse_dict: _.assign(pulse_dict, {
      'rate': pulse_dict.get('rate') / max_rate
    })

  return _.map_(
    pulse_clusters,
    rate_normalizer(max_pulse_rate)
  )
