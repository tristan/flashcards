"""Collection of namedtuples for various database constructs"""

from collections import namedtuple

User = namedtuple('User', ['user_id', 'username', 'name'])

Frame = namedtuple('Frame', ['frame_id', 'kanji', 'keyword', 'primative'])

UserFrame = namedtuple('UserFrame', ['user_id', 'frame_id', 'weight', 'last_seen',
                                     'success_count', 'failure_count', 'active'])
