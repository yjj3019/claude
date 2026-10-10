# GT004 synthetic OpenShift upgrade evidence

All identifiers and values below are fabricated lab snapshots. The versions and
notice are test inputs, not current official release/support claims.

## E1: cluster snapshot

```text
cluster: cluster-a
current: 4.18.24
requested target: 4.19.5
ClusterVersion Available=True, Progressing=False, Upgradeable=False
Upgradeable reason: AdminAckRequired (acknowledgment not recorded)
```

## E2: operator and disruption snapshot

```text
network: Available=True, Progressing=False, Degraded=True
network message: synthetic rollout diagnostic still pending
storage: Available=True, Progressing=False, Degraded=False
namespace-a/demo-api PDB: minAvailable=2, healthyPods=2, disruptionsAllowed=0
```

## E3: supplied lab change notice

The invented lab notice requires review of an API-removal inventory before
recording the administrator acknowledgment. Inventory and storage-vendor target
compatibility evidence are not supplied. A requested version string alone does
not establish an offered upgrade edge, entitlement or support status.

## E4: requested decision

Draft a release-impact brief for a maintenance decision. No upgrade, drain,
acknowledgment, force operation or production change is authorized. No cluster
URL, credentials, customer data, current official release note or live upgrade
graph is supplied. Treat external facts as unverified until primary evidence is
obtained; the exercise itself requires no network or infrastructure access.
