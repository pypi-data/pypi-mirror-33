from github_release import get_releases
import docker
import os


class DockerRelease(object):
    file = __file__

    def __init__(self, project, image=os.environ['IMAGE'], tag=os.environ['TAG'], context=None):
        self.image, self.tag, self.project = image, tag, project
        self.current_dir = os.path.normpath(
            os.path.join(os.path.abspath(self.file), os.pardir)
        )
        self.context = context or self.current_dir
        self.client = docker.from_env()
        self.latest = False
        self.args = self.get_args()
        self.default_kwargs = dict(stream=True)

    def docker_login(self, *args, **kwargs):
        self.client.login(*args, **kwargs)

    def get_args(self):
        builds_args = dict()
        for i in get_releases(self.project):
            if i['tag_name'] == self.tag:
                builds_args = dict(DOWNLOAD_URL=i['assets'][0]['browser_download_url'])
                break
            self.latest = True

        return builds_args

    def get_image_tag(self, image=None, tag=None):
        return "{image}:{tag}".format(
            image=image or self.image,
            tag=tag or self.tag
        )

    def log(self, line):
        print(line)

    def __execute(self, action, **kwargs):
        for line in getattr(self.client.images, action)(**kwargs):
            self.log(line)

    def build(self, image=None, tag=None):
        kwargs = dict(
            path=self.context, tag=self.get_image_tag(image, tag), buildargs=self.args,
            **self.default_kwargs
        )
        self.__execute('build', **kwargs)

    def push(self, image=None, tag=None):
        kwargs = dict(repository=self.get_image_tag(image, tag), **self.default_kwargs)
        self.__execute('push', **kwargs)

    def release(self, image=None, tag=None):
        self.build(image, tag)
        self.push(image, tag)

    def run(self, image=None):
        self.release(image)
        if self.latest:
            self.release(image, 'latest')
