"""Application Service — Kubernetes use cases.

All methods are synchronous (called from QThread workers).
Uses the k8s_client infrastructure adapter.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

from app.infrastructure.k8s_client import k8s_client

logger = logging.getLogger(__name__)


@dataclass
class ClusterHealth:
    node_count: int = 0
    ready_nodes: int = 0
    pod_count: int = 0
    running_pods: int = 0
    namespace_count: int = 0


@dataclass
class PodInfo:
    name: str = ""
    namespace: str = ""
    status: str = ""
    ready: str = ""
    restarts: int = 0
    node: str = ""
    age: str = ""


@dataclass
class DeploymentInfo:
    name: str = ""
    namespace: str = ""
    ready: str = ""
    up_to_date: int = 0
    available: int = 0
    desired: int = 0


@dataclass
class NodeInfo:
    name: str = ""
    status: str = ""
    roles: str = ""
    version: str = ""
    os_image: str = ""
    cpu: str = ""
    memory: str = ""


class K8sService:
    """Kubernetes management use cases."""

    def get_cluster_health(self, namespace: str = "") -> ClusterHealth:
        try:
            nodes = k8s_client.core_v1.list_node()
            pods = (
                k8s_client.core_v1.list_namespaced_pod(namespace)
                if namespace else k8s_client.core_v1.list_pod_for_all_namespaces()
            )
            namespaces = k8s_client.core_v1.list_namespace()

            ready_nodes = sum(
                1 for n in nodes.items
                for cond in n.status.conditions
                if cond.type == "Ready" and cond.status == "True"
            )
            running_pods = sum(
                1 for p in pods.items if p.status.phase == "Running"
            )
            return ClusterHealth(
                node_count=len(nodes.items),
                ready_nodes=ready_nodes,
                pod_count=len(pods.items),
                running_pods=running_pods,
                namespace_count=len(namespaces.items),
            )
        except Exception as exc:
            logger.error("get_cluster_health failed: %s", exc)
            raise

    def list_pods(self, namespace: str = "") -> list[PodInfo]:
        try:
            if namespace:
                pods = k8s_client.core_v1.list_namespaced_pod(namespace)
            else:
                pods = k8s_client.core_v1.list_pod_for_all_namespaces()

            result = []
            for p in pods.items:
                restarts = 0
                ready_count = 0
                total = len(p.spec.containers)
                if p.status.container_statuses:
                    restarts = sum(c.restart_count for c in p.status.container_statuses)
                    ready_count = sum(1 for c in p.status.container_statuses if c.ready)
                result.append(PodInfo(
                    name=p.metadata.name,
                    namespace=p.metadata.namespace,
                    status=p.status.phase or "Unknown",
                    ready=f"{ready_count}/{total}",
                    restarts=restarts,
                    node=p.spec.node_name or "—",
                    age=str(p.metadata.creation_timestamp)[:10] if p.metadata.creation_timestamp else "—",
                ))
            return result
        except Exception as exc:
            logger.error("list_pods failed: %s", exc)
            raise

    def list_deployments(self, namespace: str = "") -> list[DeploymentInfo]:
        try:
            if namespace:
                deps = k8s_client.apps_v1.list_namespaced_deployment(namespace)
            else:
                deps = k8s_client.apps_v1.list_deployment_for_all_namespaces()

            return [
                DeploymentInfo(
                    name=d.metadata.name,
                    namespace=d.metadata.namespace,
                    ready=f"{d.status.ready_replicas or 0}/{d.spec.replicas or 0}",
                    up_to_date=d.status.updated_replicas or 0,
                    available=d.status.available_replicas or 0,
                    desired=d.spec.replicas or 0,
                )
                for d in deps.items
            ]
        except Exception as exc:
            logger.error("list_deployments failed: %s", exc)
            raise

    def scale_deployment(self, name: str, namespace: str, replicas: int) -> bool:
        try:
            k8s_client.apps_v1.patch_namespaced_deployment_scale(
                name=name,
                namespace=namespace,
                body={"spec": {"replicas": replicas}},
            )
            logger.info("Scaled %s/%s to %d replicas", namespace, name, replicas)
            return True
        except Exception as exc:
            logger.error("scale_deployment failed: %s", exc)
            raise

    def list_nodes(self) -> list[NodeInfo]:
        try:
            nodes = k8s_client.core_v1.list_node()
            result = []
            for n in nodes.items:
                status = "Unknown"
                for cond in n.status.conditions:
                    if cond.type == "Ready":
                        status = "Ready" if cond.status == "True" else "NotReady"

                labels = n.metadata.labels or {}
                roles = [
                    k.split("/")[-1]
                    for k in labels if k.startswith("node-role.kubernetes.io/")
                ] or ["worker"]

                result.append(NodeInfo(
                    name=n.metadata.name,
                    status=status,
                    roles=", ".join(roles),
                    version=n.status.node_info.kubelet_version,
                    os_image=n.status.node_info.os_image,
                    cpu=n.status.capacity.get("cpu", "—"),
                    memory=n.status.capacity.get("memory", "—"),
                ))
            return result
        except Exception as exc:
            logger.error("list_nodes failed: %s", exc)
            raise

    def get_node_log(self, pod_name: str, namespace: str, tail: int = 200) -> str:
        """Fetch pod logs as a proxy for 'node logs' (pod's stdout)."""
        try:
            return k8s_client.core_v1.read_namespaced_pod_log(
                name=pod_name,
                namespace=namespace,
                tail_lines=tail,
                timestamps=True,
            )
        except Exception as exc:
            logger.error("get_node_log failed: %s", exc)
            return f"[Error fetching logs: {exc}]"


k8s_service = K8sService()
