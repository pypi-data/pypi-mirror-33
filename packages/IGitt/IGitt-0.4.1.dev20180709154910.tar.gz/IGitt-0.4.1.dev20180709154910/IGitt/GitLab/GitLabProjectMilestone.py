"""
This contains the Milestone implementation for GitLab
"""
import re
from datetime import datetime
from urllib.parse import quote_plus

from IGitt.GitLab import GitLabMixin
from IGitt.GitLab import get
from IGitt.Interfaces import put
from IGitt.Interfaces import post
from IGitt.Interfaces import delete
from IGitt.GitLab import GitLabOAuthToken, GitLabPrivateToken
from IGitt.Interfaces.Milestone import Milestone
from IGitt.GitLab.GitLabIssue import GitLabIssue
from IGitt.GitLab.GitLabMergeRequest import GitLabMergeRequest
from IGitt.Interfaces import MilestoneStates
from IGitt.GitLab.GitLabRepository import GitLabRepository

state_translation_dict = {
    'active': MilestoneStates.OPEN,
    'closed': MilestoneStates.CLOSED,
}


class GitLabProjectMilestone(GitLabMixin, Milestone):
    """
    This class represents a project level milestone on GitLab.
    This class does not support group level milestones.
    """

    def __init__(self, token: (GitLabOAuthToken, GitLabPrivateToken), project,
                 number: int):
        """
        Creates a new GitLabProjectMilestone with the given credentials.

        :param token: A Token object to be used for authentication.
        :param project: The full name of the project. Including the owner
                        e.g. ``owner/project``.
        :param number: The unique milestone identification number (id).
                        Not The clear text number given on the Web UI
                        See also https://docs.gitlab.com/ee/api/README.html#id-vs-iid
        :raises RuntimeError: If something goes wrong (network, auth, ...)
        """
        self._token = token
        self._project = project
        self._id = number
        self._url = '/projects/{project}/milestones/{milestone_id}'.format(
            project=quote_plus(project), milestone_id=number)

    @staticmethod
    def create(token: (GitLabOAuthToken, GitLabPrivateToken),
               project,
               title: str,
               description: str = None,
               due_date=None,
               start_date=None):
        """
        Create a new milestone with given title and body.

        >>> from os import environ
        >>> milestone = GitLabProjectMilestone.create(
        ...     GitLabOAuthToken(environ['GITLAB_TEST_TOKEN']),
        ...     'gitmate-test-user/test',
        ...     'test milestone title',
        ...     'sample description'
        ... )
        >>> milestone.state
        'active'

        Delete the milestone to avoid filling the test repo with milestones.

        >>> milestone.close()

        :return: GitLabProjectMilestone object of the newly created milestone.
        """
        url = '/projects/{project}/milestones'.format(
            project=quote_plus(project))
        if due_date is not None:
            due_date = datetime.strftime(due_date, '%Y-%m-%d')
        if start_date is not None:
            start_date = datetime.strftime(start_date, '%Y-%m-%d')
        milestone = post(
            token, GitLabProjectMilestone.absolute_url(url), {
                'title': title,
                'description': description,
                'due_date': due_date,
                'start_date': start_date
            })

        return GitLabProjectMilestone.from_data(milestone, token, project,
                                                milestone['id'])

    @property
    def number(self) -> int:
        """
        Returns the milestone "number" or id.
        """
        return self._id

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
        self.data = put(self._token, self.url, {'title': new_title})

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
        self.data = put(self._token, self.url,
                        {'description': new_description})

    @property
    def state(self) -> MilestoneStates:
        """
        Get's the state of the milestone.

        :return: Either MilestoneStates.OPEN or MilestoneStates.CLOSED.
        """

        return state_translation_dict[self.data['state']]

    def close(self):
        """
        Closes the milestone.

        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        self.data = put(self._token, self.url, {'state_event': 'close'})

    def reopen(self):
        """
        Reopens the milestone.

        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        self.data = put(self._token, self.url, {'state_event': 'activate'})

    @property
    def created(self) -> datetime:
        """
        Retrieves a timestamp on when the milestone was created.
        """
        return datetime.strptime(self.data['created_at'],
                                 '%Y-%m-%dT%H:%M:%S.%fZ')

    @property
    def updated(self) -> datetime:
        """
        Retrieves a timestamp on when the milestone was updated the last time.
        """
        return datetime.strptime(self.data['updated_at'],
                                 '%Y-%m-%dT%H:%M:%S.%fZ')

    @property
    def start_date(self) -> datetime:
        """
        Retrieves a timestamp on when the milestone was started.
        """

        return datetime.strptime(
            self.data['start_date'],
            '%Y-%m-%d') if self.data['start_date'] else None

    @start_date.setter
    def start_date(self, new_date: datetime):
        """
        Sets the start date of the milestone.

        :param new_date: The new start date.
        """
        self.data = put(
            self._token, self.url, {
                'start_date':
                datetime.strftime(new_date, '%Y-%m-%d') if new_date else None,
            })

    @property
    def due_date(self) -> datetime:
        """
        Retrieves a timestamp on when the milestone is due.
        """

        return datetime.strptime(self.data['due_date'],
                                 '%Y-%m-%d') if self.data['due_date'] else None

    @due_date.setter
    def due_date(self, new_date: datetime):
        """
        Sets the due date of the milestone.

        :param new_date: The new due date.
        """

        self.data = put(
            self._token, self.url, {
                'due_date':
                datetime.strftime(new_date, '%Y-%m-%d') if new_date else None
            })

    @staticmethod
    def extract_repo_full_name(web_url):
        """
        Extracts the repository name from the web_url of the issue
        """
        return re.sub(r'https?://gitlab\.com/|/issues/\d', '', web_url)

    @property
    def issues(self) -> set:
        """
        Retrieves a set of issue objects that are assigned to this milestone.
        """
        return {
            GitLabIssue.from_data(res, self._token,
                                  self.extract_repo_full_name(res['web_url']),
                                  res['iid'])
            for res in get(self._token, self.url + '/issues')
        }

    @property
    def merge_requests(self) -> set:
        """
        Retrieves a set of merge request objects that are assigned to this
        milestone.
        """
        return {
            GitLabMergeRequest.from_data(res, self._token,
                                         self.extract_repo_full_name(
                                             res['web_url']), res['iid'])
            for res in get(self._token, self.url + '/merge_requests')
        }

    @property
    def project(self) -> GitLabRepository:
        """
        Returns the repository this milestone is linked with.
        """
        return GitLabRepository(self._token, self._project)

    def delete(self):
        """
        Deletes the milestone.
        This is not possible with GitLab api v4.

        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        delete(self._token, self.url)
