import typing as t

import yaml
from kubernetes import client as k8s

from . import Kind


class Issuer(Kind):
    """A `cert-manager` Issuer resource."""

    version = "v1alpha1"
    group = "certmanager.k8s.io"
    plural = "issuers"

    def __init__(self, client: k8s.ApiClient, namespace: str) -> None:
        self.client = client
        self.namespace: str = namespace

    def delete(self, name: t.AnyStr, body: k8s.V1DeleteOptions):
        return k8s.CustomObjectsApi(
            self.client
        ).delete_namespaced_custom_object(
            body=body,
            namespace=self.namespace,
            version=self.version,
            group=self.group,
            plural=self.plural,
            name=name,
        )

    def create(self, body: yaml.YAMLObject):
        return k8s.CustomObjectsApi(
            self.client
        ).create_namespaced_custom_object(
            body=body,
            namespace=self.namespace,
            version=self.version,
            group=self.group,
            plural=self.plural,
        )
