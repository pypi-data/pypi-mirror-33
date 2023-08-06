import os
from pathlib import Path
from contextlib import contextmanager
from tempfile import TemporaryDirectory

from .repo import GitRepo


class ResultArchiver:
    def as_ci(self):
        return "CI" in os.environ

    def __init__(self, repo, branch, results):
        if not self.as_ci():
            repo.set_authentication(system=True)

        self.repo = GitRepo(repo)
        self.result_branch = branch
        self.results = results
        self.destination = None

    def _get_build_number(self):
        raise NotImplementedError()

    def _get_branch_name(self):
        raise NotImplementedError()

    @property
    def _branch_name(self):
        return self._get_branch_name() if self.as_ci() else "NO_CI"

    @property
    def _build_number(self):
        return self._get_build_number() if self.as_ci() else "NO_CI"

    def commit(self, message=None, no_ci_push=False):
        if not message:
            message = "build #{build} on branch '{branch}'"
        with self._commit_to_repo(message, no_ci_push):
            self._add_results_files_to_index()
        return {
            "branch": self._branch_name
        }

    def _add_results_files_to_index(self):
        for result in self.results:
            added_files = result.to(self.destination)
            self.repo.add(added_files)

    @contextmanager
    def _commit_to_repo(self, message, no_ci_push):
        with TemporaryDirectory() as repo_dir:
            self._prepare_repo(Path(repo_dir))
            yield
            self._finish_repo(message, no_ci_push)

    def _prepare_repo(self, dir_):
        self.destination = dir_ / self._branch_name
        self.repo.clone(dir_, branch=self.result_branch)
        self.repo.rmdir(self.destination)
        self.destination.mkdir(exist_ok=True)

    def _finish_repo(self, message, no_ci_push):
        self.repo.commit(message.format(
            branch=self._branch_name,
            build=self._build_number,
        ))
        if self.as_ci() or no_ci_push:
            self.repo.push()
