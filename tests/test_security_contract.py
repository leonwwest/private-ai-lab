from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_application_container_runs_as_a_non_root_user() -> None:
    dockerfile = (ROOT / "Dockerfile").read_text()

    assert "USER 10001:10001" in dockerfile
    assert "--uid 10001" in dockerfile


def test_namespace_enforces_the_restricted_pod_security_standard() -> None:
    namespace = (ROOT / "deploy" / "k8s" / "base" / "namespace.yaml").read_text()

    assert "pod-security.kubernetes.io/enforce: restricted" in namespace
    assert "pod-security.kubernetes.io/audit: restricted" in namespace
    assert "pod-security.kubernetes.io/warn: restricted" in namespace


def test_kubernetes_workloads_define_explicit_security_boundaries() -> None:
    manifests = "\n".join(
        (ROOT / "deploy" / "k8s" / "base" / name).read_text()
        for name in ("app.yaml", "postgres.yaml")
    )

    assert manifests.count("automountServiceAccountToken: false") == 2
    assert manifests.count("runAsNonRoot: true") == 2
    assert manifests.count("allowPrivilegeEscalation: false") == 2
    assert manifests.count('drop: ["ALL"]') == 2
    assert manifests.count("readOnlyRootFilesystem: true") == 2
    assert manifests.count("type: RuntimeDefault") == 2


def test_network_policies_default_to_isolation_and_allow_only_required_paths() -> None:
    manifest_dir = ROOT / "deploy" / "k8s" / "base"
    default_deny = (manifest_dir / "default-deny-network-policy.yaml").read_text()
    api_policy = (manifest_dir / "api-network-policy.yaml").read_text()
    postgres_policy = (manifest_dir / "postgres-network-policy.yaml").read_text()
    kustomization = (manifest_dir / "kustomization.yaml").read_text()

    assert "podSelector: {}" in default_deny
    assert "- Ingress" in default_deny
    assert "- Egress" in default_deny
    assert "port: 53" in api_policy
    assert "port: 5432" in api_policy
    assert "port: 11434" in api_policy
    assert "app: private-ai-lab-api" in postgres_policy
    assert "port: 5432" in postgres_policy
    assert kustomization.count("network-policy.yaml") == 3
