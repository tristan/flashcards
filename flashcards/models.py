"""Collection of namedtuples for various database constructs"""

from collections import namedtuple

User = namedtuple('User', ['user_id', 'username', 'name'])

UserCard = namedtuple('UserCard', ['user_id', 'card_id', 'weight', 'last_seen',
                                   'success_count', 'failure_count', 'active'])
