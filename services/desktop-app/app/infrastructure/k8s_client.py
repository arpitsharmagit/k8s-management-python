"""Domain — Kubernetes infrastructure client wrapper.

Handles kubeconfig auto-detection (local kubeconfig or in-cluster)
and provides access to the core API objects used by the service layer.
"""
from __future__ import annotations

import logging
import os

from kubernetes import client, config
from kubernetes.client.rest import ApiException

from app.config import settings

logger = logging.getLogger(__name__)


class K8sClient:
    """Thin wrapper around the kubernetes Python SDK.

    Auto-detects configuration:
      1. In-cluster (KUBERNETES_SERVICE_HOST env set) → load_incluster_config()
      2. Local kubeconfig (KUBECONFIG env or ~/.kube/config) → load_kube_config()
    """

    def __init__(self) -> None:
        self._configured = False
        self._v1: client.CoreV1Api | None = None
        self._apps_v1: client.AppsV1Api | None = None

    def _ensure_configured(self) -> None:
        if self._configured:
            return
        try:
            if os.environ.get("KUBERNETES_SERVICE_HOST"):
                config.load_incluster_config()
                logger.info("K8s client: loaded in-cluster config")
            else:
                kubeconfig = settings.KUBECONFIG or None
                config.load_kube_config(config_file=kubeconfig)
                logger.info("K8s client: loaded local kubeconfig")
            self._configured = True
            self._v1 = client.CoreV1Api()
            self._apps_v1 = client.AppsV1Api()
        except Exception as exc:
            logger.error("Failed to configure Kubernetes client: %s", exc)
            raise

    @property
    def core_v1(self) -> client.CoreV1Api:
        self._ensure_configured()
        return self._v1

    @property
    def apps_v1(self) -> client.AppsV1Api:
        self._ensure_configured()
        return self._apps_v1


k8s_client = K8sClient()
