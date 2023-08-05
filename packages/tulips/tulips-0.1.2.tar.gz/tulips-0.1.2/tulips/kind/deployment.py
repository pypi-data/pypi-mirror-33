from kubernetes import client as k8s

from . import Kind


class Deployment(Kind):
    def delete(self, body: k8s.V1DeleteOptions):
        return k8s.AppsV1Api(self.client).delete_namespaced_deployment(
            body=body, namespace=self.namespace, name=self.name
        )

    def create(self):
        return k8s.AppsV1Api(self.client).create_namespaced_deployment(
            body=self.chart, namespace=self.namespace
        )
