
import io
import re
import typing as t

import structlog
import yaml
from kubernetes import client as k8s
from kubernetes import config
from passlib import pwd

from tulips import class_for_kind
from tulips.kind import Kind

log = structlog.get_logger("helm")

__version__ = "0.0.2"


class Helm:
    def __init__(
        self, conf: str, namespace: str, meta: t.Dict, spec_path: str
    ) -> None:
        """Manages deployment.

        Args:
            conf (t.AnyStr): Path to Kubernetes config.
            namespace (t.AnyStr): Kubernetes namespace.
            meta (t.Dict): Spec variables
            spec_path (t.AnyStr): Location of chart to deploy.
        """

        self.meta: dict = meta
        self.namespace: str = namespace
        self.spec_path: str = spec_path
        self.client: k8s.ApiClient = config.new_client_from_config(conf)

    def specs(self) -> t.Iterator[Kind]:
        """Deployment specification.

        Returns:
            t.Iterator[Kind]: Iterator over specifications
        """

        pattern = re.compile(r"^(.*)<%=(?:\s+)?(\S*)(?:\s+)?=%>(.*)$")
        yaml.add_implicit_resolver("!meta", pattern)
        maps = {"@pwd": lambda: pwd.genword(length=16)}
        maps.update(self.meta)

        def meta_constructor(loader, node):
            value = loader.construct_scalar(node)
            start, name, end = pattern.match(value).groups()
            val = maps[name]
            if name.startswith("@"):
                val = val()
            return start + val + end

        yaml.add_constructor("!meta", meta_constructor)
        with io.open(self.spec_path) as f:
            for spec in yaml.load_all(f.read()):
                yield class_for_kind(spec["kind"])(
                    self.client, self.namespace, spec
                )
