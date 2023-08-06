"""
Contains the GitLab Team implementation.
"""
from typing import Set

from IGitt.GitLab import GitLabMixin
from IGitt.GitLab.GitLabUser import GitLabUser
from IGitt.Interfaces import get

class GitLabTeam(GitLabMixin):
    """
    Represents a Team on GitLab.
    """

    def __init__(self, token, group_id):
        """
        :param group_id: The id of the group.
        """
        self._token = token
        self._id = group_id
        self._url = '/groups/{group_id}'.format(group_id=group_id)

    @property
    def name(self) -> str:
        """
        Name of the team.
        """
        return self.data['name']

    @property
    def id(self) -> int:
        """
        Retrieves the id of the team.
        """
        return self._id

    @property
    def description(self) -> str:
        """
        Returns the description of this team.
        """
        return self.data['description']

    @property
    def members(self) -> Set[GitLabUser]:
        """
        Returns the user handles of all members of this team.
        """
        return {
            GitLabUser.from_data(user, self._token, user['id'])
            for user in get(
                self._token, self.url + '/members'
            )
        }

    def is_member(self, username):
        """
        Checks if given username is member of this team.
        """
        usernames = [user.username for user in self.members]
        return True if username in usernames else False

    @property
    def get_organization(self):
        """
        Returns parent team.
        """
        if self.data['parent_id']:
            return GitLabTeam(self._token, self.data['parent_id'])
        return None
