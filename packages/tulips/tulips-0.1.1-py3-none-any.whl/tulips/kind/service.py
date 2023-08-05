import typing as t

import yaml
from kubernetes import client as k8s

from . import Kind


class Service(Kind):
    def __init__(self, client: k8s.ApiClient, namespace: str) -> None:
        self.client = client
        self.namespace: str = namespace

    def delete(self, name: t.AnyStr, body: k8s.V1DeleteOptions):
        return k8s.CoreV1Api(self.client).delete_namespaced_service(
            body=body, namespace=self.namespace, name=name
        )

    def create(self, body: yaml.YAMLObject):
        return k8s.CoreV1Api(self.client).create_namespaced_service(
            body=body, namespace=self.namespace
        )
