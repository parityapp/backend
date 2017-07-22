from typing import List, Tuple, Dict

import pydash as _


def most_active_n_users(messages: List[Dict], n: int) -> List[str]:

  def user_scorer(users_with_ranks: Dict, message):
    user = message.get('userid')
    return _.assign(users_with_ranks,
                    {user: users_with_ranks.get(user, 0) + 1})

  users_with_ranks: Dict = _.reduce_(messages, user_scorer, {})
  sorted_users_by_rank: List[Tuple[str, int]] = sorted(
    users_with_ranks,
    key=users_with_ranks.get
  )

  return _.take(sorted_users_by_rank, min(len(users_with_ranks), n))
