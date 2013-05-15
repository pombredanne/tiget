from git_orm.testcases import GitTestCase


class TigetTestCase(GitTestCase):
    def setup(self):
        super().setup()
        from tiget.conf import settings
        settings.core.repository = self.repo.path
