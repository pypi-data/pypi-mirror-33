from kubernetes import client as k8s

from . import Kind


class Secret(Kind):
    def delete(self, body: k8s.V1DeleteOptions):
        return k8s.CoreV1Api(self.client).delete_namespaced_secret(
            body=body, namespace=self.namespace, name=self.name
        )

    def create(self):
        return k8s.CoreV1Api(self.client).create_namespaced_secret(
            body=self.chart, namespace=self.namespace
        )
