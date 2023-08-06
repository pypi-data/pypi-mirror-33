from git import Repo


class GitRepo:
    def __init__(self, url):
        self.url = url
        self.repo = None
        self.base = None
        self.branch = None

    def clone(self, dest, branch):
        self.base = dest
        self.branch = branch
        self.repo = Repo.clone_from(str(self.url), dest, branch=branch)

    def rmdir(self, dir_):
        if dir_.is_dir():
            self.repo.index.remove([str(dir_)],
                                   working_tree=True,
                                   r=True)  # delete recursively

    def add(self, files):
        self.repo.index.add([str(f.relative_to(self.base))
                             for f in files])

    def commit(self, message):
        self.repo.index.commit(message)

    def push(self):
        self.repo.remote("origin").push()


class GitHub:
    def __init__(self, user, repo, token):
        self.name = repo
        self.user = user
        self._authentication = None
        self.set_authentication(token=token)

    def set_authentication(self, token=None, system=False):
        if system:
            self._authentication = ""
        elif token:
            self._authentication = "{}:x-oauth-basic@".format(token)

    def __str__(self):
        return "https://{}github.com/{}/{}.git".format(self._authentication,
                                                       self.user, self.name)
