import abc
import typing as t

import yaml
from kubernetes import client as k8s


class Kind(metaclass=abc.ABCMeta):
    """Kind is interface that describes Kubernetes Resource defintion."""

    @abc.abstractmethod
    def __init__(
        self, client: t.Callable[[], k8s.ApiClient], namespace: t.AnyStr
    ) -> None:
        pass

    @abc.abstractmethod
    def create(self, body: yaml.YAMLObject):
        pass

    @abc.abstractmethod
    def delete(self, name: t.AnyStr, body: k8s.V1DeleteOptions):
        pass
