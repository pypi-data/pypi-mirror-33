from kubernetes import client as k8s

from . import Kind


class Ingress(Kind):
    def delete(self, body: k8s.V1DeleteOptions):
        return k8s.ExtensionsV1beta1Api(self.client).delete_namespaced_ingress(
            body=body, namespace=self.namespace, name=self.name
        )

    def create(self):
        return k8s.ExtensionsV1beta1Api(self.client).create_namespaced_ingress(
            body=self.chart, namespace=self.namespace
        )
