"""
Contains the Team abstraction class.
"""
from typing import Set

from IGitt.Interfaces import IGittObject
from IGitt.Interfaces.User import User


class Team(IGittObject):
    """
    Represents a team on GitHub or GitLab.
    """
    @property
    def name(self) -> str:
        """
        Name of the team.
        """
        raise NotImplementedError

    @property
    def id(self) -> int:
        """
        Retrieves the id of the team.
        """
        raise NotImplementedError

    @property
    def description(self) -> str:
        """
        Returns the description of this team.
        """
        raise NotImplementedError

    @property
    def members(self) -> Set[User]:
        """
        Returns the user handles of all members of this team.
        """
        raise NotImplementedError

    def is_member(self, username: str):
        """
        Checks if given username is member of this team.
        """
        raise NotImplementedError

    @property
    def get_organization(self):
        """
        Returns parent organization.
        """
        raise NotImplementedError
