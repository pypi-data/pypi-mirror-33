"""
Contains the GitHub Team implementation.
"""
from typing import Set

from IGitt.GitHub import GH_INSTANCE_URL
from IGitt.GitHub import GitHubMixin
from IGitt.GitHub.GitHubUser import GitHubUser
from IGitt.GitHub.GitHubOrganization import GitHubOrganization
from IGitt.Interfaces.Team import Team
from IGitt.Interfaces import get


class GitHubTeam(GitHubMixin, Team):
    """
    Represents a team on GitHub.
    """

    def __init__(self, token, team_id):
        """
        :param team_id: The id of the team.
        """
        self._token = token
        self._id = team_id
        self._url = '/teams/{team_id}'.format(team_id=team_id)


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
    def web_url(self):
        return '{}/orgs/{}/teams/{}'.format(GH_INSTANCE_URL,
                                            self.get_organization.name,
                                            self.name)

    @property
    def members(self) -> Set[GitHubUser]:
        """
        Returns the user handles of all members of this team.
        """
        return {
            GitHubUser.from_data(user, self._token, user['login'])
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
        Returns parent organization.
        """
        return GitHubOrganization.from_data(self.data['organization'],
                                            self._token,
                                            self.data['organization']['login'])
