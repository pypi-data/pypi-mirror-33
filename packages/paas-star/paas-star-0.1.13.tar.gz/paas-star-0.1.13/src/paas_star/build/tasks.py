import re
import getpass

from star_builder.build.tasks import Task, Model as _Model, \
    Project as _Project, ModuleTask
from os.path import join, exists, abspath, dirname, isdir, basename


__all__ = ["Project", "Model", "Backend", "Service"]


class Project(_Project):
    """
    项目
    """
    @classmethod
    def enrich_parser(cls, sub_parser):
        super().enrich_parser(sub_parser)
        reg = "hub.yiducloud.cn/library"
        sub_parser.add_argument(
            "-r", "--registry", help=f"镜像仓库地址 默认：{reg}", default=reg)
        sub_parser.add_argument("-v", "--version", help="版本", default="0.1.0")
        index = "http://devpi.intra.yiducloud.cn/root/yiducloud/+simple/"
        sub_parser.add_argument(
            "-i", "--index-url", help=f"Pip源 默认：{index}", default=index)
        t = "devpi.intra.yiducloud.cn"
        sub_parser.add_argument(
            "-th", "--trusted-host", help=f"信任的域名 默认：{t}", default=t)
        user = getpass.getuser()
        sub_parser.add_argument(
            "-a", "--author", help=f"作者 默认：{user}", default=user)


class Service(ModuleTask):
    """
    服务
    """

    def enrich_kwargs(self, words):
        super().enrich_kwargs(words)
        father = None

        if exists("__init__.py"):
            regex = re.compile(r"class\s+(\w*?Service)\(\w*Service\):")
            mth = regex.search(open("__init__.py").read())
            if mth:
                father = mth.group(1)
        self.kwargs["father"] = father or "Service"

    @classmethod
    def enrich_parser(cls, sub_parser):
        sub_parser.add_argument("name", nargs="+", help="服务模块名称")


class Drivable(Task):

    def enrich_kwargs(self, name):
        super().enrich_kwargs(name)
        driver = self.kwargs.get("driver")
        if driver and driver.count(":") == 1:
            module, cls = driver.split(":")
        else:
            module, cls = None, None
        self.kwargs["module"] = module
        self.kwargs["cls"] = cls

    @classmethod
    def enrich_parser(cls, sub_parser):
        super().enrich_parser(sub_parser)
        sub_parser.add_argument(
            "-d", "--driver", help="驱动 eg：pymongo:MongoClient")


class Model(Drivable, _Model):
    """
    model。
    """


class Backend(Drivable, ModuleTask):
    """
    后台服务驱动
    """

    def validate_name(self, name):
        words = re.findall(r"([A-Za-z0-9]+)", name)
        if words[0][0].isdigit():
            words.insert(0, "backend")
        self.kwargs["name"] = name
        return words

    def enrich_kwargs(self, name):
        super(Backend, self).enrich_kwargs(name)
        self.kwargs["dirname"] = "backend"

    @classmethod
    def enrich_parser(cls, sub_parser):
        super().enrich_parser(sub_parser)
        sub_parser.add_argument("name", nargs="+", help="后台服务名称")

