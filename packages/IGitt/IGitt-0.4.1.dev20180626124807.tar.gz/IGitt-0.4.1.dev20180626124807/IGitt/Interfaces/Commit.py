"""
This module contains the actual commit object.
"""
from typing import Optional
from typing import Set
from typing import List
from itertools import chain
import re

from IGitt.Interfaces import IGittObject
from IGitt.Interfaces import Comment
from IGitt.Interfaces.CommitStatus import CommitStatus, Status
from IGitt.Interfaces.Repository import Repository
from IGitt.Interfaces.Issue import Issue


SUPPORTED_HOST_KEYWORD_REGEX = {
    'github': (r'[Cc]lose[sd]?'
               r'|[Rr]esolve[sd]?'
               r'|[Ff]ix(?:e[sd])?'),
    'gitlab': (r'[Cc]los(?:e[sd]?|ing)'
               r'|[Rr]esolv(?:e[sd]?|ing)'
               r'|[Ff]ix(?:e[sd]|ing)?')
    }
CONCATENATION_KEYWORDS = [r',', r'\sand\s']


class Commit(IGittObject):
    """
    An abstraction representing a commit. This especially exposes functions to
    place comments and manipulate the status.
    """

    def ack(self):
        """
        Acknowledges the commit by setting the manual review GitMate status to
        success.

        >>> CommitMock = type('CommitMock', (Commit,),
        ...                   {'set_status': lambda self, s: print(s.status)})
        >>> CommitMock().ack()
        Status.SUCCESS

        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        status = CommitStatus(Status.SUCCESS, 'This commit was acknowledged.',
                              'review/gitmate/manual', 'http://gitmate.io/')
        self.set_status(status)

    def unack(self):
        """
        Unacknowledges the commit by setting the manual review GitMate status to
        failed.

        >>> CommitMock = type('CommitMock', (Commit,),
        ...                   {'set_status': lambda self, s: print(s.status)})
        >>> CommitMock().unack()
        Status.FAILED

        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        status = CommitStatus(Status.FAILED, 'This commit needs work.',
                              'review/gitmate/manual', 'http://gitmate.io/')
        self.set_status(status)

    def pending(self):
        """
        Sets the commit to a pending manual review state if there is no manual
        review state yet.

        Given a commit with an unrelated status:

        >>> CommitMock = type(
        ...     'CommitMock', (Commit,),
        ...     {'set_status': lambda self, s: self.statuses.append(s),
        ...      'get_statuses': lambda self: self.statuses,
        ...      'statuses': []})
        >>> commit = CommitMock()
        >>> commit.set_status(CommitStatus(Status.FAILED, context='unrelated'))
        >>> len(commit.get_statuses())
        1

        The invocation of pending will now add a pending status:

        >>> commit.pending()
        >>> len(commit.get_statuses())
        2
        >>> commit.get_statuses()[1].context
        'review/gitmate/manual'

        However, if there is already a manual review state, the invocation of
        pending won't affect the status:

        >>> commit.get_statuses().clear()
        >>> commit.ack()
        >>> commit.pending()  # Won't do anything
        >>> len(commit.get_statuses())
        1
        >>> commit.get_statuses()[0].status
        <Status.SUCCESS: 1>

        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        for status in self.get_statuses():
            if status.context == 'review/gitmate/manual':
                return

        status = CommitStatus(Status.PENDING, 'This commit needs review.',
                              'review/gitmate/manual', 'http://gitmate.io')
        self.set_status(status)

    def comment(self, message: str, file: Optional[str]=None,
                line: Optional[int]=None,
                mr_number: Optional[int]=None) -> Comment:
        """
        Puts a comment on the new version of the given line. If the file or
        line is None, the comment will be placed at the bottom of the commit.

        :param message:   The message to comment.
        :param file:      Filename or None
        :param line:      Line number or None
        :param mr_number: The number of a merge request if this should end up in
                          the review UI of the merge request.

        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        raise NotImplementedError

    def set_status(self, status: CommitStatus):
        """
        Adds the given status to the commit. If a status with the same context
        already exists, it will be bluntly overridden.

        :param status: The CommitStatus to set to this commit.

        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        raise NotImplementedError

    def get_statuses(self) -> Set[CommitStatus]:
        """
        Retrieves the all commit statuses.

        :return: A (frozen)set of CommitStatus objects.
        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        raise NotImplementedError

    @property
    def combined_status(self) -> Status:
        """
        Retrieves a combined status of all the commits.

        :return:
            Status.FAILED if any of the commits report as error or failure or
            canceled
            Status.PENDING if there are no statuses or a commit is pending or a
            test is running
            Status.SUCCESS if the latest status for all commits is success
        """
        raise NotImplementedError

    @property
    def sha(self) -> str:
        """
        Retrieves the sha of the commit.

        :return: A string holding the SHA of the commit.
        """
        raise NotImplementedError

    @property
    def parent(self):
        """
        Retrieves the parent commit if possible.

        :return: A Commit object.
        """
        raise NotImplementedError

    @property
    def repository(self) -> Repository:
        """
        Retrieves the repository that holds this commit.

        :return: A Repository object.
        """
        raise NotImplementedError

    @property
    def message(self) -> str:
        """
        Retrieves the commit message.

        :return: Commit message as string.
        """
        raise NotImplementedError

    @property
    def unified_diff(self):
        """
        Retrieves the unified diff for the commit excluding the diff index.
        """
        raise NotImplementedError

    def get_keywords_issues(self, keyword: str, body_list: List) -> Set[int]:
        """
        Returns a set of tuples(issue number, name of the repository the issue
        is contained in), which are mentioned with given ``keyword``.
        """
        results = set()
        hoster = self.repository.hoster
        repo_name = self.repository.full_name

        identifier_regex = r'[\w\.-]+'
        namespace_regex = r'(?:{0})/(?:{0})(?:/(?:{0}))?'.format(
            identifier_regex)
        concat_regex = '|'.join(kw for kw in CONCATENATION_KEYWORDS)
        issue_no_regex = r'[1-9][0-9]*'
        issue_url_regex = r'https?://{}\S+/issues/{}'.format(
            hoster, issue_no_regex)
        c_joint_regex = re.compile(
            r'((?:{0})'         # match keywords expressed via ``keyword``

            r'(?:(?:{3})?\s*'   # match conjunctions
                                # eg: ',', 'and' etc.

            r'(?:(?:\S*)#{2}|'  # match short references
                                # eg: #123, coala/example#23

            r'(?:{1})))+)'      # match full length issue URLs
                                # eg: https://github.com/coala/coala/issues/23

            r''.format(keyword,
                       issue_url_regex, issue_no_regex, concat_regex))
        c_issue_capture_regex = re.compile(
            r'(?:(?:\s+|^)({2})?#({0}))|(?:https?://{1}\S+?/({2})/issues/({0}))'
            ''.format(
                issue_no_regex, hoster, namespace_regex))

        for body in body_list:
            matches = c_joint_regex.findall(body.replace('\r', ''))
            refs = list(chain(*[c_issue_capture_regex.findall(match)
                                for match in matches]))
            for ref in refs:
                if ref[0] != '':
                    repo_name = ref[0]
                if ref[1] != '':
                    results.add((ref[1], repo_name))
                if ref[2] != '' and ref[3] != '':
                    results.add((ref[3], ref[2]))

        return results

    def _get_closes_issues(self) -> Set[int]:
        """
        Returns a set of tuples(issue number, name of the repository the issue
        is contained in), which would be closed upon merging this commit.
        """
        hoster = self.repository.hoster

        # If the hoster does not support auto closing issues with matching
        # keywords, just return an empty set. At the moment, we only have
        # support for GitLab and GitHub. And both of them support autoclosing
        # issues with matching keywords.
        if hoster not in SUPPORTED_HOST_KEYWORD_REGEX: # dont cover
            return set()
        return self.get_keywords_issues(
            SUPPORTED_HOST_KEYWORD_REGEX[self.repository.hoster],
            [self.message]
        )

    def _get_mentioned_issues(self):
        """
        Returns a set of tuples(issue number, name of the repository the issue
        is contained in), which are related to this commit.
        """
        return self.get_keywords_issues(r'', [self.message])

    @property
    def closes_issues(self) -> Set[Issue]:
        """
        Returns a set of Issue objects which would be closed upon merging this
        commit.
        """
        raise NotImplementedError

    @property
    def mentioned_issues(self) -> Set[Issue]:
        """
        Returns a set of Issue objects which are related to the commit.
        """
        raise NotImplementedError

    @property
    def will_fix_issues(self) -> Set[Issue]:
        """
        Returns a set of Issue objects which would be fixed as stated in
        this commit message.
        """

    @property
    def will_close_issues(self) -> Set[Issue]:
        """
        Returns a set of Issue objects which would be closed as stated in
        this commit message.
        """
        raise NotImplementedError

    @property
    def will_resolve_issues(self) -> Set[Issue]:
        """
        Returns a set of Issue objects which would be resolved as stated
        in this commit message.
        """
        raise NotImplementedError
