import abc

from kubernetes import client as k8s


class Kind(metaclass=abc.ABCMeta):
    """Kind is interface that describes Kubernetes Resource defintion."""

    chart: dict
    client: k8s.ApiClient
    namespace: str

    def __init__(
        self, client: k8s.ApiClient, namespace: str, chart: dict
    ) -> None:
        """Initializes chart or CRD.

        Args:
            client (k8s.ApiClient): Instance of the Kubernetes client.
            namespace (str): Namespace where Workload should be deployed.
            chart (dict): Kubernetes chart or CRD.
        """

        self.client = client
        self.namespace = namespace
        self.chart = chart

    @abc.abstractmethod
    def create(self):
        pass

    @abc.abstractmethod
    def delete(self, options: k8s.V1DeleteOptions):
        pass

    @property
    def name(self):
        return self.chart["metadata"]["name"]
