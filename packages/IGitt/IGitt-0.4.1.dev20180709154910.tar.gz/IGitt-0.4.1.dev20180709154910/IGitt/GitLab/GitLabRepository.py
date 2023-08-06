"""
Contains the GitLab Repository implementation.
"""
from datetime import datetime
from typing import List
from typing import Optional
from typing import Set
from typing import Union
from urllib.parse import quote_plus
from functools import lru_cache

from IGitt import ElementAlreadyExistsError, ElementDoesntExistError
from IGitt.GitLab import GitLabMixin
from IGitt.GitLab import GitLabOAuthToken, GitLabPrivateToken
from IGitt.GitLab.GitLabIssue import GitLabIssue
from IGitt.GitLab.GitLabOrganization import GitLabOrganization
from IGitt.Interfaces import delete, get, post
from IGitt.Interfaces import BasicAuthorizationToken
from IGitt.Interfaces import AccessLevel
from IGitt.Interfaces import IssueStates
from IGitt.Interfaces import MergeRequestStates
from IGitt.Interfaces.Repository import Repository
from IGitt.Interfaces.Repository import WebhookEvents
from IGitt.Utils import eliminate_none


GL_WEBHOOK_TRANSLATION = {
    WebhookEvents.PUSH: 'push_events',
    WebhookEvents.ISSUE: 'issues_events',
    WebhookEvents.MERGE_REQUEST: 'merge_requests_events',
    WebhookEvents.COMMIT_COMMENT: 'note_events',
    WebhookEvents.MERGE_REQUEST_COMMENT: 'note_events',
    WebhookEvents.ISSUE_COMMENT: 'note_events',
}

GL_WEBHOOK_EVENTS = {'tag_push_events', 'job_events', 'pipeline_events',
                     'wiki_events', 'confidential_issues_events',
                    } | set(GL_WEBHOOK_TRANSLATION.values())

GL_MR_STATE_TRANSLATION = {MergeRequestStates.MERGED: 'merged',
                           MergeRequestStates.OPEN: 'opened',
                           MergeRequestStates.CLOSED: 'closed'}

GL_ISSUE_STATE_TRANSLATION = {IssueStates.OPEN: 'opened',
                              IssueStates.CLOSED: 'closed'}


def date_in_range(data,
                  created_after: Optional[datetime]=None,
                  created_before: Optional[datetime]=None,
                  updated_after: Optional[datetime]=None,
                  updated_before: Optional[datetime]=None):
    """
    Returns true if issue/MR is in the given range.
    """
    is_created_after = not created_after
    is_created_before = not created_before
    is_updated_after = not updated_after
    is_updated_before = not updated_before
    if created_after and data['created_at']>str(created_after):
        is_created_after = True
    if created_before and data['created_at']<str(created_before):
        is_created_before = True
    if updated_after and data['updated_at']>str(updated_after):
        is_updated_after = True
    if updated_before and data['updated_at']<str(updated_before):
        is_updated_before = True
    return (is_created_after and is_created_before and is_updated_after and
            is_updated_before)


class GitLabRepository(GitLabMixin, Repository):
    """
    Represents a repository on GitLab.
    """

    def __init__(self, token: Union[GitLabOAuthToken, GitLabPrivateToken],
                 repository: Union[str, int]):
        """
        Creates a new GitLabRepository object with the given credentials.

        :param token: A Token object to be used for authentication.
        :param repository: Full name or unique identifier of the repository,
                           e.g. ``sils/baritone``.
        """
        self._token = token
        self._repository = repository
        try:
            repository = int(repository)
            self._repository = None
            self._url = '/projects/{}'.format(repository)
        except ValueError:
            self._url = '/projects/' + quote_plus(repository)

    @property
    def identifier(self):
        """
        Returns the id of the repository.
        """
        return self.data['id']

    @property
    def top_level_org(self):
        """
        Returns the topmost organization, e.g. for `gitmate/open-source/IGitt`
        this is `gitmate`.
        """
        return GitLabOrganization(self._token,
                                  self.full_name.split('/', maxsplit=1)[0])

    @property
    def full_name(self) -> str:
        """
        Retrieves the full name of the repository, e.g. "sils/baritone".

        >>> from os import environ
        >>> repo = GitLabRepository(
        ...     GitLabOAuthToken(environ['GITLAB_TEST_TOKEN']),
        ...     'gitmate-test-user/test'
        ... )
        >>> repo.full_name
        'gitmate-test-user/test'

        :return: The full repository name as string.
        """
        return self._repository or self.data['path_with_namespace']

    @lru_cache(None)
    def filter_commits(self, author: Optional[str]=None):
        """
        Filter commits based on properties.

        :author: Author username of the commit.
        :return: A set of GitLabCommit objects.
        """
        # Don't move to module, leads to circular imports
        from IGitt.GitLab.GitLabCommit import GitLabCommit

        commits = get(self._token, self.url + '/repository/commits')
        if author is not None:
            data =  {'username': author}
            user = get(self._token, self.absolute_url('/users'), data)
            if user:
                author_name = user[0]['name']
            else:
                return None
            commits = [commit for commit in commits
                       if commit['author_name'] == author_name]
        return {GitLabCommit.from_data(commit,
                                       self._token,
                                       self.full_name,
                                       commit['id'])
                for commit in commits}

    @property
    def commits(self):
        """
        Retrieves the set of commits in this repository.

        :return: A set of GitLabCommit objects.
        """
        return self.filter_commits()

    @property
    def clone_url(self) -> str:
        """
        Retrieves the URL of the repository.

        >>> from os import environ as env
        >>> repo = GitLabRepository(
        ...     GitLabOAuthToken(environ['GITLAB_TEST_TOKEN']),
        ...     'gitmate-test-user/test'
        ... )
        >>> expected = 'https://{}@gitlab.com/gitmate-test-user/test.git'
        >>> assert repo.clone_url == expected.format(env['GITLAB_TEST_TOKEN'])

        :return: A URL that can be used to clone the repository with Git.
        """
        return self.data['http_url_to_repo'].replace(
            '://', '://oauth2:' + self._token.value + '@', 1)

    def get_labels(self) -> Set[str]:
        """
        Retrieves the labels of the repository.

        >>> from os import environ
        >>> repo = GitLabRepository(
        ...     GitLabOAuthToken(environ['GITLAB_TEST_TOKEN']),
        ...     'gitmate-test-user/test'
        ... )
        >>> sorted(repo.get_labels())
        ['a', 'b', 'c']

        :return: A set of strings containing the label captions.
        """
        return {label['name']
                for label in get(self._token, self.url + '/labels')}

    def create_label(self, name: str, color: str='', **kwargs):
        """
        Creates a new label with the given color. For an example,
        see delete_label.

        If a label that already exists is attempted to be created, that throws
        an exception:

        >>> from os import environ
        >>> repo = GitLabRepository(
        ...     GitLabOAuthToken(environ['GITLAB_TEST_TOKEN']),
        ...     'gitmate-test-user/test'
        ... )
        >>> sorted(repo.get_labels())
        ['a', 'b', 'c']
        >>> repo.create_label('c', '#555555')
        Traceback (most recent call last):
         ...
        IGitt.ElementAlreadyExistsError: c already exists.

        :param name: The name of the label to create.
        :param color: A HTML color value with a leading #.
        :raises ElementAlreadyExistsError: If the label name already exists.
        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        if name in self.get_labels():
            raise ElementAlreadyExistsError(name + ' already exists.')

        self.data = post(
            self._token,
            self.url + '/labels',
            {'name': name, 'color': color}
        )

    def delete_label(self, name: str):
        """
        Deletes a label.

        Take a given repository:

        >>> from os import environ
        >>> repo = GitLabRepository(
        ...     GitLabOAuthToken(environ['GITLAB_TEST_TOKEN']),
        ...     'gitmate-test-user/test'
        ... )
        >>> sorted(repo.get_labels())
        ['a', 'b', 'c']

        Let's create a label 'd':

        >>> repo.create_label('d', '#555555')
        >>> sorted(repo.get_labels())
        ['a', 'b', 'c', 'd']

        >>> repo.delete_label('d')
        >>> sorted(repo.get_labels())
        ['a', 'b', 'c']

        If the label doesn't exist it won't get silently dropped - no! You will
        get an exception.

        >>> repo.delete_label('d')
        Traceback (most recent call last):
         ...
        IGitt.ElementDoesntExistError: d doesnt exist.

        :param name: The caption of the label to delete.
        :raises ElementDoesntExistError: If the label doesn't exist.
        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        if name not in self.get_labels():
            raise ElementDoesntExistError(name + ' doesnt exist.')

        delete(self._token, self.url + '/labels', params={'name': name})

    def get_issue(self, issue_number: int) -> GitLabIssue:
        """
        Retrieves an issue:

        >>> from os import environ
        >>> repo = GitLabRepository(
        ...     GitLabOAuthToken(environ['GITLAB_TEST_TOKEN']),
        ...     'gitmate-test-user/test'
        ... )
        >>> repo.get_issue(1).title
        'Take it serious, son!'

        :param issue_number: The issue IID of the issue on GitLab.
        :return: An Issue object.
        :raises ElementDoesntExistError: If the issue doesn't exist.
        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        return GitLabIssue(self._token, self.full_name, issue_number)

    def get_mr(self, mr_number: int):
        """
        Retrieves an MR.

        :param mr_number: The MR IID of the merge_request on GitLab.
        :return: A MergeRequest object.
        :raises ElementDoesntExistError: If the MR doesn't exist.
        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        from IGitt.GitLab.GitLabMergeRequest import GitLabMergeRequest
        return GitLabMergeRequest(self._token, self.full_name, mr_number)

    @property
    def hooks(self) -> Set[str]:
        """
        Retrieves all URLs this repository is hooked to.

        :return: Set of URLs (str).
        """
        hook_url = self.url + '/hooks'
        hooks = get(self._token, hook_url)

        return {hook['url'] for hook in hooks}

    def register_hook(self,
                      url: str,
                      secret: Optional[str]=None,
                      events: Optional[Set[WebhookEvents]]=None):
        """
        Registers a webhook to the given URL. Use it as simple as:

        >>> from os import environ
        >>> repo = GitLabRepository(environ['GITLAB_TEST_TOKEN'],
        ...                         'gitmate-test-user/test')
        >>> repo.register_hook("http://some.url/in/the/world")

        It does nothing if the hook is already there:

        >>> repo.register_hook("http://some.url/in/the/world")

        To register a secret token with the webhook, simply add
        the secret param:

        >>> repo.register_hook("http://some.url/i/have/a/secret",
        ...     "mylittlesecret")

        To delete it simply run:

        >>> repo.delete_hook("http://some.url/in/the/world")
        >>> repo.delete_hook("http://some.url/i/have/a/secret")

        :param url: The URL to fire the webhook to.
        :param secret:
            An optional secret token to be registered with the webhook.
        :param events:
            The events for which the webhook is to be registered against.
            Defaults to all possible events.
        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        if url in self.hooks:
            return

        config = {
            'url': url,
            'enable_ssl_verification': False,
        }

        if secret:
            config['token'] = secret

        if events and len(events):
            config.update({GL_WEBHOOK_TRANSLATION[event]: True
                           for event in events})
        else:
            config.update({event: True for event in GL_WEBHOOK_EVENTS})

        self.data = post(self._token, self.url + '/hooks', config)

    def delete_hook(self, url: str):
        """
        Deletes all webhooks to the given URL.

        :param url: The URL to not fire the webhook to anymore.
        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        hook_url = self.url + '/hooks'
        hooks = get(self._token, hook_url)

        # Do not use self.hooks since id of the hook is needed
        for hook in hooks:
            if hook['url'] == url:
                delete(self._token, hook_url + '/' + str(hook['id']))

    def create_issue(self, title: str, body: str='') -> GitLabIssue:
        """
        Create a new issue in the repository.
        """
        return GitLabIssue.create(self._token, self.full_name, title, body)

    def filter_merge_requests(self, state: str='opened') -> set:
        """
        Filters the merge requests from the repository based on the state
        of the merge requests.

        :param state: 'opened' or 'closed', or 'merged', or 'all'.
        """
        from IGitt.GitLab.GitLabMergeRequest import GitLabMergeRequest
        return {GitLabMergeRequest.from_data(mr, self._token,
                                             self.full_name, mr['iid'])
                for mr in get(self._token,
                              self.url + '/merge_requests',
                              {'state': state})}

    @property
    def merge_requests(self) -> set:
        """
        Retrieves a set of open merge request objects.

        >>> from os import environ
        >>> repo = GitLabRepository(
        ...     GitLabOAuthToken(environ['GITLAB_TEST_TOKEN']),
        ...     'gitmate-test-user/test'
        ... )
        >>> len(repo.merge_requests)
        4
        """
        return self.filter_merge_requests(state='opened')

    def filter_issues(self, state: str='opened') -> set:
        """
        Filters the issues from the repository based on properties.

        :param state: 'opened' or 'closed' or 'all'.
        """
        return {GitLabIssue.from_data(res, self._token,
                                      self.full_name, res['iid'])
                for res in get(self._token,
                               self.url + '/issues',
                               {'state': state})}

    @property
    def issues(self) -> set:
        """
        Retrieves a set of issue objects.

        >>> from os import environ
        >>> repo = GitLabRepository(environ['GITLAB_TEST_TOKEN'],
        ...                         'gitmate-test-user/test')
        >>> len(repo.issues)
        13
        """
        return self.filter_issues()

    def create_fork(self, organization: Optional[str]=None,
                    namespace: Optional[str]=None):
        """
        Create a fork of Repository
        """
        url = self.url + '/fork'
        data = {
            'id': self.full_name,
            'namespace': namespace
        }
        res = post(self._token, url=url, data=data)

        return GitLabRepository(self._token, res['path_with_namespace'])

    def create_file(self, path: str, message: str, content: str,
                    branch: Optional[str]=None, committer: Optional[str]=None,
                    author: Optional[dict]=None, encoding: Optional[str]=None):
        """
        Create a new file in Repository
        """
        url = self.url + '/repository/files/' + path
        data = {
            'file_path' : path,
            'commit_message' : message,
            'content' : content,
            'branch' : branch,
            'encoding' : encoding
        }

        if author:
            data['author_name'] = author['name']
            data['author_email'] = author['email']

        data = eliminate_none(data)
        post(token=self._token, url=url, data=data)

        from IGitt.GitLab.GitLabContent import GitLabContent
        return GitLabContent(self._token, self.full_name, path=path)

    def create_merge_request(self, title:str, base:str, head:str,
                             body: Optional[str]=None,
                             target_project_id: Optional[int]=None,
                             target_project: Optional[str]=None):
        """
        Create a new merge request in Repository
        """
        url = self.url + '/merge_requests'
        data = {
            'title' : title,
            'target_branch' : base,
            'source_branch' : head,
            'id' : quote_plus(self.full_name),
            'target_project_id' : target_project_id
        }
        json = post(self._token, url=url, data=data)

        from IGitt.GitLab.GitLabMergeRequest import GitLabMergeRequest
        return GitLabMergeRequest.from_data(json, self._token,
                                            repository=target_project,
                                            number=json['iid'])

    def delete(self):
        """
        Delete the Repository
        """
        delete(token=self._token, url=self.url)

    def _search(self,
                search_type,
                state: Union[MergeRequestStates, IssueStates, None]):
        """
        Retrives a list of all issues or merge requests.
        :param search_type: A string for type of object i.e. issues for issue
                            and merge_requests for merge requests.
        :param state: A string for MR/issue state (opened or closed)
        :return: List of issues/merge requests.
        """
        url = self.url + '/{}'.format(search_type)
        if state is None:
            return get(self._token, url)
        elif isinstance(state, IssueStates):
            state = GL_ISSUE_STATE_TRANSLATION[state]
        elif isinstance(state, MergeRequestStates):
            state = GL_MR_STATE_TRANSLATION[state]
        return get(self._token, url, {'state': state})

    def search_issues(self,
                      created_after: Optional[datetime]=None,
                      created_before: Optional[datetime]=None,
                      updated_after: Optional[datetime]=None,
                      updated_before: Optional[datetime]=None,
                      state: Optional[IssueStates] = None):
        """
        Searches for issues based on created and updated date.
        """
        for issue_data in filter(lambda data: date_in_range(data,
                                                            created_after,
                                                            created_before,
                                                            updated_after,
                                                            updated_before),
                                 self._search('issues', state)):
            issue = self.get_issue(issue_data['iid'])
            issue.data = issue_data
            yield issue

    def search_mrs(self,
                   created_after: Optional[datetime]=None,
                   created_before: Optional[datetime]=None,
                   updated_after: Optional[datetime]=None,
                   updated_before: Optional[datetime]=None,
                   state: Optional[MergeRequestStates]=None):
        """
        Searches for merge request based on created and updated date.
        """
        for mr_data in filter(lambda data: date_in_range(data,
                                                         created_after,
                                                         created_before,
                                                         updated_after,
                                                         updated_before),
                              self._search('merge_requests', state)):
            merge_request = self.get_mr(mr_data['iid'])
            merge_request.data = mr_data
            yield merge_request

    def get_permission_level(self, user) -> AccessLevel:
        """
        Retrieves the permission level for the specified user on this
        repository.
        """
        members = get(self._token, self.url + '/members')
        if user.username not in map(lambda m: m['username'], members):
            return (AccessLevel.CAN_VIEW
                    if self.data['visibility'] != 'private'
                    else AccessLevel.NONE)
        curr_member_idx = next(i for (i, d) in enumerate(members)
                               if d['username'] == user.username)
        return AccessLevel(members[curr_member_idx]['access_level'])

    @property
    def parent(self):
        """
        Returns the repository from which this repository is forked from.
        Returns `None` if it has no fork relationship.
        """
        try:
            return GitLabRepository.from_data(
                self.data['forked_from_project'],
                self._token,
                self.data['forked_from_project']['id'])
        except KeyError:
            return None

    @staticmethod
    def create(token: Union[BasicAuthorizationToken,
                            GitLabPrivateToken,
                            GitLabOAuthToken],
               name: str,
               path: Optional[str]=None,
               visibility: str='public',
               namespace_id: Optional[int]=None,
               default_branch: Optional[str]='master',
               description: Optional[str]=None,
               has_issues: bool=True,
               has_merge_requests: bool=True,
               has_jobs: bool=True,
               has_wiki: bool=True,
               has_snippets: bool=True,
               has_container_registry: bool=True,
               has_shared_runners: bool=True,
               has_lfs: bool=False,
               resolve_outdated_diff_discussions: bool=False,
               import_url: Optional[str]=None,
               public_jobs: bool=False,
               only_allow_merge_if_pipeline_succeeds: bool=False,
               only_allow_merge_if_all_discussions_are_resolved: bool=False,
               allow_request_access: bool=True,
               allow_printing_merge_request_link: bool=True,
               tag_list: Optional[List[str]]=None,
               avatar: Optional[object]=None,
               ci_config_path: Optional[str]=None,
               repository_storage: Optional[str]=None,
               approvals_before_merge: Optional[int]=None,
               **kwargs):
        """
        Creates a new repository and returns the associated GitLabRepository
        instance.

        :param token:
            The credentials to be used for authentication.
        :param name:
            The name of the new project. Equals ``path`` if not provided.
        :param path:
            Repository name for new project. Generated based on name if not
            provided (generated lowercased with dashes).
        :param visibility:
            Either of ``private``, ``public`` or ``internal``.
            Reference: https://docs.gitlab.com/ee/api/projects.html#project-visibility-level
        :param namespace_id:
            Namespace for the new project (defaults to the current user's
            namespace)
        :param default_branch:
            The default branch to be used.
        :param description:
            A short description of the repository.
        :param has_issues:
            Either ``True`` to enable issues for this project or ``False`` to
            disable them.
        :param has_merge_requests:
            Either ``True`` to enable merge requests for this project or
            ``False`` to disable them.
        :param has_jobs:
            Either ``True`` to enable jobs for this project or ``False`` to
            disable them.
        :param has_wiki:
            Either ``True`` to enable wiki for this project or ``False`` to
            disable it.
        :param has_snippets:
            Either ``True`` to enable snippets for this project or ``False`` to
            disable them.
        :param has_container_registry:
            Either ``True`` to enable container registry or ``False`` to
            disable it.
        :param has_lfs:
            Either ``True`` to enable Git Large File Sharing or ``False`` to
            disable it.
        :param resolve_outdated_diff_discussions:
            Either ``True`` to automatically resolve merge request diff
            discussions on lines changed with a push of ``False`` to disable
            it.
        :param import_url:
            URL to import repository from.
        :param public_jobs:
            If ``True``, jobs can be viewed by non-project-members.
        :param only_allow_merge_if_pipeline_succeeds:
            Set whether merge requests can only be merged with successful jobs.
        :param only_allow_merge_if_all_discussions_are_resolved:
            Set whether merge requests can only be merged when all the
            discussions are resolved.
        :param allow_request_access:
            Allow users to request member access.
        :param allow_printing_merge_request_link:
            Show link to create/view merge request when pushing from the
            command line.
        :param tag_list:
            The list of tags for a project that should be finally assigned to a
            project.
        :param avatar:
            Image file for avatar of the project (base64 encoded png).
        :param ci_config_path:
            The path to CI config file.
        :param repository_storage:
            Which storage shard the repository is on. Available only to admins.
        :param approvals_before_merge:
            How many approvers should approve merge request by default before
            allowing it to be merged.
        """
        data = eliminate_none({
            'name': name,
            'path': path,
            'visibility': visibility,
            'namespace_id': namespace_id,
            'default_branch': default_branch,
            'description': description,
            'has_issues': has_issues,
            'has_merge_requests': has_merge_requests,
            'has_jobs': has_jobs,
            'has_wiki': has_wiki,
            'has_snippets': has_snippets,
            'has_container_registry': has_container_registry,
            'has_shared_runners': has_shared_runners,
            'has_lfs': has_lfs,
            'resolve_outdated_diff_discussions':
                resolve_outdated_diff_discussions,
            'import_url': import_url,
            'public_jobs': public_jobs,
            'only_allow_merge_if_pipeline_succeeds':
                only_allow_merge_if_pipeline_succeeds,
            'only_allow_merge_if_all_discussions_are_resolved':
                only_allow_merge_if_all_discussions_are_resolved,
            'allow_request_access': allow_request_access,
            'allow_printing_merge_request_link':
                allow_printing_merge_request_link,
            'tag_list': tag_list,
            'avatar': avatar,
            'ci_config_path': ci_config_path,
            'repository_storage': repository_storage,
            'approvals_before_merge': approvals_before_merge
        })
        repo = post(token, GitLabRepository.absolute_url('/projects'), data)
        return GitLabRepository.from_data(repo, token, repo['id'])
