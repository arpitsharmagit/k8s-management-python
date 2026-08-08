"""QThread workers for each K8s panel — thin typed wrappers over BaseWorker."""
from __future__ import annotations

from app.application.k8s_service import k8s_service
from app.config import settings
from app.ui.workers.base_worker import BaseWorker


class ClusterHealthWorker(BaseWorker):
    """Fetches overall cluster health metrics."""
    def __init__(self, parent=None):
        super().__init__(
            fn=k8s_service.get_cluster_health,
            fn_kwargs={"namespace": settings.K8S_NAMESPACE},
            parent=parent,
        )


class PodsWorker(BaseWorker):
    """Fetches list of pods in the configured namespace."""
    def __init__(self, parent=None):
        super().__init__(
            fn=k8s_service.list_pods,
            fn_kwargs={"namespace": settings.K8S_NAMESPACE},
            parent=parent,
        )


class DeploymentsWorker(BaseWorker):
    """Fetches list of deployments in the configured namespace."""
    def __init__(self, parent=None):
        super().__init__(
            fn=k8s_service.list_deployments,
            fn_kwargs={"namespace": settings.K8S_NAMESPACE},
            parent=parent,
        )


class NodesWorker(BaseWorker):
    """Fetches list of cluster nodes."""
    def __init__(self, parent=None):
        super().__init__(fn=k8s_service.list_nodes, parent=parent)


class LogsWorker(BaseWorker):
    """Fetches logs for a specific pod."""
    def __init__(self, pod_name: str, namespace: str, parent=None):
        super().__init__(
            fn=k8s_service.get_node_log,
            fn_kwargs={"pod_name": pod_name, "namespace": namespace, "tail": 300},
            parent=parent,
        )
