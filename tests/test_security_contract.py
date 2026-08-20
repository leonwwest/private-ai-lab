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
