"""
Contains a JIRA project implementation.
"""
from datetime import datetime
from urllib.parse import urljoin
from typing import Optional
from typing import Set
from typing import Union
import logging
import re

from IGitt.Interfaces import delete
from IGitt.Interfaces import get
from IGitt.Interfaces import post
from IGitt.Interfaces import AccessLevel
from IGitt.Interfaces import BasicAuthorizationToken
from IGitt.Interfaces import IssueStates
from IGitt.Interfaces.Repository import Repository
from IGitt.Interfaces.Repository import WebhookEvents
from IGitt.Jira import JiraMixin
from IGitt.Jira import JiraOAuth1Token
from IGitt.Jira import BASE_URL
from IGitt.Jira import JIRA_INSTANCE_URL
from IGitt.Jira.JiraIssue import JiraIssue


_HTTP_REGEX = re.compile(r'https?://')
JIRA_WEBHOOK_TRANSLATION = {
    WebhookEvents.PUSH: (None, ),
    WebhookEvents.ISSUE: ('jira:issue_created',
                          'jira:issue_updated',
                          'jira:issue_deleted',
                          'jira:worklog_updated'),
    WebhookEvents.MERGE_REQUEST: (None, ),
    WebhookEvents.COMMIT_COMMENT: (None, ),
    WebhookEvents.MERGE_REQUEST_COMMENT: (None, ),
    WebhookEvents.ISSUE_COMMENT: ('jira:comment_created',
                                  'jira:comment_updated',
                                  'jira:comment_deleted'),
}


class JiraRepository(JiraMixin, Repository):
    """
    Represents a project resource on JIRA.
    """
    def __init__(self,
                 token: Union[JiraOAuth1Token, BasicAuthorizationToken],
                 identifier: Union[str, int]):
        """
        Instantiates a new JiraRepository object with the given details.

        :param token:
            The OAuth v1.0 token to be used for authentication.
        :param identifier:
            The unique identifier or key of the project.
        """
        self._identifier = identifier
        self._token = token
        self._url = '/project/{}'.format(identifier)
        self._hook_url = urljoin(JIRA_INSTANCE_URL,
                                 '/rest/webhooks/1.0/webhook')

    @property
    def identifier(self) -> int:
        """
        Returns the unique identifier of the corresponding repository.
        """
        try:
            return int(self._identifier)
        except ValueError:
            return int(self.data['id'])

    @property
    def web_url(self) -> str:
        """
        Returns a human accessible web url for the corresponding project.
        """
        return urljoin(JIRA_INSTANCE_URL,
                       '/projects/{}'.format(self.data['key']))

    @property
    def top_level_org(self):
        """
        JIRA doesn't support organizations.
        """
        raise NotImplementedError

    @property
    def full_name(self):
        """
        JIRA doesn't have an account based naming scheme like GitHub. So, this
        property returns just the project name.
        """
        return self.data['name']

    @property
    def commits(self):
        """
        JIRA projects don't actually hold a codebase and hence has no commits.
        """
        raise NotImplementedError

    @property
    def clone_url(self):
        """
        JIRA projects don't actually hold a codebase which can be cloned.
        """
        raise NotImplementedError

    def get_labels(self):
        """
        Retrieves the list of available labels for this project.
        """
        raise NotImplementedError

    def create_label(self,
                     name: str,
                     description: Optional[str]=None,
                     label_type: Optional[str]=None,
                     **kwargs):
        """
        Creates a new label.
        """
        raise NotImplementedError

    def delete_label(self, name: str):
        """
        Deletes the specified label.

        :raises: ElementDoesntExistError if no such label exists.
        """
        raise NotImplementedError

    def get_issue(self, issue_number: int):
        """
        Retrieves the specified issue from the project.

        :return:    A JiraIssue object representing the specified issue.
        """
        return JiraIssue(self._token, issue_number)

    def get_mr(self, mr_number: int):
        """
        JIRA doesn't actually hold a codebase and doesn't support sending merge
        requests.
        """
        raise NotImplementedError

    @property
    def hooks(self):
        """
        Retrieves all the webhooks this project is hooked to.

        :return:    A set of URLs.
        """
        params = {'jqlFilter': 'project = {}'.format(self.data['key'])}
        return {hook['url']
                for hook in get(self._token, self._hook_url, params)}

    def register_hook(self,
                      url: str,
                      _: Optional[str]=None,
                      events: Optional[Set[WebhookEvents]]=None):
        """
        Registers a webhook to the given URL.
        """
        if url in self.hooks:
            return

        reg_events = [x for event in events
                      for x in JIRA_WEBHOOK_TRANSLATION[event]
                      if x is not None]
        config = {
            'name': 'An IGitt webhook',
            'url': url,
            'events': reg_events,
            'jqlFilter': 'project = {}'.format(self.data['key']),
            'excludeIssueDetails': False
        }

        post(self._token, self._hook_url, config)
        logging.warning('Be careful with JIRA webhooks as they are system '
                        'wide. i.e. Every single project sends a webhook for '
                        'one registration.')

    def delete_hook(self, url: str):
        """
        Deletes all the webhooks to the specified URL.
        """
        for hook in get(self._token, self._hook_url):
            if hook['url'] == url:
                delete(self._token, hook['self'])

    def filter_issues(self, state: str='opened') -> set:
        """
        Filters issues from a repository based on the chosen properties.
        """
        raise NotImplementedError

    @property
    def issues(self) -> set:
        """
        Retrieves the set of JiraIssue objects for this project.
        """
        params = {'jql': 'Project="{}"'.format(self.data['key'])}
        return {JiraIssue.from_data(iss, self._token, iss['id'])
                for iss in get(self._token,
                               self.absolute_url('/search'),
                               params)['issues']
               }

    @property
    def merge_requests(self) -> set:
        """
        JIRA projects don't actually hold a codebase, so merge requests do not
        exist.
        """
        raise NotImplementedError

    def create_issue(self,
                     issue_type: str,
                     title: str,
                     body: str='') -> JiraIssue:
        """
        Creates a new issue in the project.
        """
        return JiraIssue.create(
            self._token, self.identifier, title, body, issue_type=issue_type)

    def create_fork(self, *args, **kwargs):
        """
        JIRA projects don't actually have a codebase to be forked.
        """
        raise NotImplementedError

    def delete(self):
        """
        Deletes the JIRA project.
        """
        delete(self._token, self.url)

    def create_merge_request(self, *args, **kwargs):
        """
        JIRA projects don't actually hold a codebase to merge changes into.
        """
        raise NotImplementedError

    def create_file(self, *args, **kwargs):
        """
        JIRA projects don't actually hold a codebase. So, new files can't be
        created.
        """
        raise NotImplementedError

    def search_mrs(self, *args, **kwargs):
        """
        JIRA doesn't support a merge request resource.
        """
        raise NotImplementedError

    def search_issues(self,
                      created_after: Optional[datetime]=None,
                      created_before: Optional[datetime]=None,
                      updated_after: Optional[datetime]=None,
                      updated_before: Optional[datetime]=None,
                      state: Optional[IssueStates] = None):
        """
        List open issues in the repository.
        """
        raise NotImplementedError

    def get_permission_level(self, *args, **kwargs) -> AccessLevel:
        """
        JIRA provides support for custom permission schemes for users which
        cannot be therefore generalized into an ``AccessLevel`` enum.
        """
        raise NotImplementedError

    @property
    def parent(self):
        """
        JIRA projects do not support or maintain a fork relationship between
        each other.
        """
        return None

    @staticmethod
    def create(token: Union[JiraOAuth1Token, BasicAuthorizationToken],
               name: str,
               project_type: Optional[str]=None,
               project_key: Optional[str]=None,
               project_lead: Optional[str]=None,
               **kwargs):
        """
        Creates a new JIRA project and returns it.

        :param name:
            The name of the project.
        :param project_type:
            The type of the project.
        :param project_key:
            The key identifier of the project to be set.
        :param project_lead:
            The project lead.
        """
        repo = post(token,
                    BASE_URL + '/project',
                    {
                        'key': project_key,
                        'name': name,
                        'projectTypeKey': project_type,
                        'lead': project_lead
                    })
        return JiraRepository.from_data(repo, token, repo['id'])
