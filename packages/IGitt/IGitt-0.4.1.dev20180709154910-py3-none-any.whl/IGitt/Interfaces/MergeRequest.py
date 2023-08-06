"""
Contains a class that represents a request to merge something into some git
branch.
"""
from datetime import datetime
from typing import List
from typing import Set

from IGitt.Interfaces import MergeRequestStates
from IGitt.Interfaces.Commit import Commit
from IGitt.Interfaces.CommitStatus import Status
from IGitt.Interfaces.Issue import Issue
from IGitt.Interfaces.User import User
from IGitt.Interfaces.Milestone import Milestone


class MergeRequest(Issue):
    """
    A request to merge something into the main codebase. Can be a patch in a
    mail or a pull request on GitHub.
    """

    def close(self):
        """
        Closes the merge request.

        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        raise NotImplementedError

    def reopen(self):
        """
        Reopens the merge request.

        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        raise NotImplementedError

    @property
    def state(self) -> MergeRequestStates:
        """
        Get's the state of the merge request.

        :return: A MergeRequestStates object indicating current state.
        """
        raise NotImplementedError

    @property
    def base(self) -> Commit:
        """
        Retrieves the base commit of the merge request, i.e. the one it should
        be merged into.

        :return: A Commit object.
        """
        raise NotImplementedError

    @property
    def base_branch_name(self) -> str:
        """
        Retrieves the base branch name of the merge request, i.e. the one it
        should be merged into.

        :return: A string.
        """
        raise NotImplementedError

    @property
    def head(self) -> Commit:
        """
        Retrieves the head commit of the merge request, i.e. the one which
        would be merged.

        :return: A Commit object.
        """
        raise NotImplementedError

    @property
    def head_branch_name(self) -> str:
        """
        Retrieves the head branch name of the merge request, i.e. the one that
        will be merged.

        :return: A string.
        """
        raise NotImplementedError

    @property
    def commits(self) -> List[Commit]:
        """
        Retrieves all commits that are contained in this request.

        :return: A list of Commits.
        """
        raise NotImplementedError

    @property
    def repository(self):
        """
        Retrieves the repository where this PR is opened at.

        :return: A Repository object.
        """
        raise NotImplementedError

    @property
    def target_repository(self):
        """
        Retrieves the repository where this PR is opened at. An alias to
        ``self.repository`` property.

        :return: A Repository object.
        """
        return self.repository

    @property
    def source_repository(self):
        """
        Retrieves the repository where this PR's head branch is located at.

        :return: A Repository object.
        """
        raise NotImplementedError

    @property
    def affected_files(self):
        """
        Retrieves the affected files.

        :return: A set of filenames relative to repo root.
        """
        raise NotImplementedError

    @property
    def diffstat(self):
        """
        Gets additions and deletions of a merge request.

        :return: An (additions, deletions) tuple.
        """
        raise NotImplementedError

    @property
    def created(self) -> datetime:
        """
        Retrieves a timestamp on when the merge request was created.
        """
        raise NotImplementedError

    @property
    def updated(self) -> datetime:
        """
        Retrieves a timestamp on when the merge request was updated the last
        time.
        """
        raise NotImplementedError

    @property
    def number(self) -> int:
        """
        Returns the MR "number" or id.
        """
        raise NotImplementedError

    @property
    def closes_issues(self) -> Set[Issue]:
        """
        Returns a set of Issue objects which would be closed upon merging this
        pull request.
        """
        raise NotImplementedError

    @property
    def tests_passed(self) -> bool:
        """
        Returns True if all commits of the merge request have a success state.
        If you wish to only get the head state, use mr.head.combined_status.
        """
        statuses = set(map(lambda commit: commit.combined_status,
                           self.commits))
        if Status.PENDING in statuses or Status.FAILED in statuses:
            return False
        return True

    @property
    def mentioned_issues(self) -> Set[Issue]:
        """
        Returns a set of Issue objects which are related to the pull request.
        """
        raise NotImplementedError

    @property
    def author(self) -> User:
        """
        Returns the author of the MR wrapped in a User object.
        """
        raise NotImplementedError

    def merge(self, message: str=None, sha: str=None,
              should_remove_source_branch: bool=False,
              _github_merge_method: str=None,
              _gitlab_merge_when_pipeline_succeeds: bool=False):
        """
        Merges the merge request.

        :param message:                     The commit message.
        :param sha:                         The commit sha that the HEAD must
                                            match in order to merge.
        :param should_remove_source_branch: Whether the source branch should be
                                            removed upon a successful merge.
        :param _github_merge_method:        On GitHub, the merge method to use
                                            when merging the MR. Can be one of
                                            `merge`, `squash` or `rebase`.
        :param _gitlab_wait_for_pipeline:   On GitLab, whether the MR should be
                                            merged immediately after the
                                            pipeline succeeds.
        :raises RuntimeError:        If something goes wrong (network, auth...).
        :raises NotImplementedError: If an unused parameter is passed.
        """
        raise NotImplementedError

    @property
    def milestone(self) -> Milestone:
        """
        Retrieves the milestone.
        """
        raise NotImplementedError

    @milestone.setter
    def milestone(self, new_milestone) -> Milestone:
        """
        Setter for the Milestone.
        """
        raise NotImplementedError

    @property
    def mergeable(self) -> bool:
        """
        Returns true if there is no merge conflict.
        """
        raise NotImplementedError
