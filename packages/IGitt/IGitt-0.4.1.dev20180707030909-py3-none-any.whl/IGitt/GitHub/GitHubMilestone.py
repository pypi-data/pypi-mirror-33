"""
This contains the Milestone implementation for GitHub
"""
from datetime import datetime

from IGitt.GitHub import GitHubMixin
from IGitt.Interfaces.Milestone import Milestone
from IGitt.Interfaces import MilestoneStates
from IGitt.GitHub import GitHubToken
from IGitt.Interfaces import post
from IGitt.Interfaces import patch
from IGitt.Interfaces import delete
from IGitt.Interfaces import get
from IGitt.GitHub.GitHubIssue import GitHubIssue
from IGitt.GitHub.GitHubMergeRequest import GitHubMergeRequest
from IGitt.GitHub.GitHubRepository import GitHubRepository


class GitHubMilestone(GitHubMixin, Milestone):
    """
    This class represents a milestone on GitHub.
    """

    def __init__(self, token: GitHubToken, repository: str, number: int):
        """
        Creates a new GitHubMilestone object with the given credentials.

        :param token: A Token object to be used for authentication.
        :param repository: The full name of the repository
                            eg. 'sils/repository'.
        :param number: The milestones number.
        :raises RuntimeError: If something goes wrong (network, auth, ...)
        """
        self._token = token
        self._repository = repository
        self._number = number
        self._url = '/repos/{repository}/milestones/{milestone_number}'\
            .format(repository=repository, milestone_number=number)
        self._issues_url = GitHubMixin.absolute_url(
            '/repos/{repository}/issues'.format(repository=self._repository))

    @staticmethod
    def create(token: GitHubToken,
               repository: str,
               title: str,
               state: MilestoneStates = MilestoneStates.OPEN,
               description: str = None,
               due_on: datetime = None):
        """
        Create a new milestone with given title
        :return: GitHubMilestone object of the newly created milestone.
        """
        url = '/repos/{repository}/milestones'.format(repository=repository)
        if due_on != None:
            due_on = datetime.strftime(due_on, '%Y-%m-%dT%H:%M:%SZ')
        milestone = post(
            token, GitHubMilestone.absolute_url(url), {
                'title': title,
                'state': str(state),
                'description': description,
                'due_on': due_on
            })
        return GitHubMilestone.from_data(milestone, token, repository,
                                         milestone['number'])

    @property
    def number(self) -> int:
        """
        Returns the milestone "number" or id.
        """
        return self._number

    @property
    def title(self) -> str:
        """
        Retrieves the title of the milestone.
        """
        return self.data['title']

    @title.setter
    def title(self, new_title):
        """
        Sets the title of the milestone.

        :param new_title: The new title.
        """
        self.data = patch(self._token, self.url, {'title': new_title})

    @property
    def description(self) -> str:
        """
        Retrieves the main description of the milestone.
        """
        return self.data['description']

    @description.setter
    def description(self, new_description):
        """
        Sets the description of the milestone

        :param new_description: The new description .
        """
        self.data = patch(self._token, self.url,
                          {'description': new_description})

    @property
    def state(self) -> MilestoneStates:
        """
        Get's the state of the milestone.

        :return: Either MilestoneStates.OPEN or MilestoneStates.CLOSED.
        """
        return MilestoneStates[self.data['state'].upper()]

    def close(self):
        """
        Closes the milestone.

        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        self.data = patch(self._token, self.url, {'state': 'closed'})

    def reopen(self):
        """
        Reopens the milestone.

        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        self.data = patch(self._token, self.url, {'state': 'open'})

    @property
    def created(self) -> datetime:
        """
        Retrieves a timestamp on when the milestone was created.
        """
        return datetime.strptime(self.data['created_at'], '%Y-%m-%dT%H:%M:%SZ')

    @property
    def updated(self) -> datetime:
        """
        Retrieves a timestamp on when the milestone was updated the last time.
        """
        return datetime.strptime(self.data['updated_at'], '%Y-%m-%dT%H:%M:%SZ')

    @property
    def due_date(self) -> datetime:
        """
        Retrieves a timestamp on when the milestone is due.
        """

        return datetime.strptime(
            self.data['due_on'],
            '%Y-%m-%dT%H:%M:%SZ') if self.data['due_on'] else None

    @due_date.setter
    def due_date(self, new_date: datetime):
        """
        Sets the due date of the milestone.
        It is not possible to set the time. GitHub will always set the time on
        the due date to 07:00:00

        :param new_date: The new due date.
        """
        self.data = patch(
            self._token, self.url, {
                'due_on':
                datetime.strftime(new_date, '%Y-%m-%dT%H:%M:%SZ')
                if new_date else None
            })

    def delete(self):
        """
        Deletes the milestone.
        This is not possible with GitLab api v4.

        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        delete(self._token, self.url)

    @property
    def issues(self) -> set:
        """
        Retrieves a set of issue objects that are assigned to this milestone.
        """
        return {
            GitHubIssue.from_data(res, self._token, self._repository,
                                  res['number'])
            for res in get(self._token, self._issues_url,
                           {'milestone': self._number})
            if 'pull_request' not in res
        }

    @property
    def merge_requests(self) -> set:
        """
        Retrieves a set of merge_request
        objects that are assigned to this milestone.
        """
        return {
            GitHubMergeRequest.from_data(res, self._token, self._repository,
                                         res['number'])
            for res in get(self._token, self._issues_url,
                           {'milestone': self._number})
            if 'pull_request' in res
        }

    @property
    def project(self) -> GitHubRepository:
        """
        Returns the repository this milestone is linked with.
        """
        return GitHubRepository(self._token, self._repository)

    @property
    def start_date(self) -> datetime:
        """
        Retrieves a timestamp on when the milestone was started.
        The start_date does not exist in GitHub.
        """
        return None
