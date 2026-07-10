# Kubernetes / OpenShift integration — customer handoff checklist

**Purpose:** Give this page to your customer's **platform / Kubernetes / DevOps** team when scoping a Cisco Secure Workload (CSW) integration with their cluster(s).

**Integration summary:** CSW uses a **connector** to read pod/service/namespace metadata from the **Kubernetes API** (labels into CSW) and a **DaemonSet node agent** on every node to (a) report **network flows** and (b) **enforce** micro-segmentation by programming **iptables** in the node and pod network namespaces. An optional **scanner pod** reports container-image **CVEs**.

---

## Integration paths

| Path | What CSW does | Credential needed | Data direction |
|---|---|---|---|
| **Connector (inventory)** | Import pods/services/namespaces/nodes + labels → `orchestrator_*` | **Read-only** K8s ServiceAccount token | CSW → K8s API (poll) |
| **DaemonSet (visibility)** | Capture pod + node interface flows | Agent activation key (per tenant) | node → CSW (TLS) |
| **DaemonSet (enforcement)** | Program node/pod iptables from policy intent | same agent | CSW → node (TLS) |
| **Scanner (optional)** | Enumerate images → CVEs | registry creds (if private) | scanner → CSW (TLS) |

---

## What we need from the platform / Kubernetes team

### 1. Connector access (read-only)

| Item | Detail |
|------|--------|
| **ServiceAccount** | Dedicated read-only SA (see [`examples/connector-rbac.yaml`](../examples/connector-rbac.yaml)) |
| **RBAC** | `get/list/watch` on `pods, services, endpoints, namespaces, nodes` |
| **API endpoint** | Kubernetes **API server** FQDN/IP + port (usually 443) |
| **Auth** | kubeconfig or SA token + cluster CA (stored encrypted in CSW; kept in a secrets manager on your side) |

### 2. DaemonSet install (enforcement/visibility)

| Item | Detail |
|------|--------|
| **Privilege** | Cluster admin to apply namespace + RBAC + DaemonSet (`hostNetwork`, `NET_ADMIN`/`NET_RAW`/`SYS_ADMIN`) |
| **Installer** | Use the **CSW-generated** Kubernetes installer bundle (contains activation key + endpoints) |
| **Preserve rules** | **Must be enabled** so CSW coexists with the CNI's iptables rules |
| **Scheduling** | DaemonSet tolerations to also cover tainted/control-plane nodes if required |

### 3. Connectivity

| Direction | Source | Destination | Port |
|-----------|--------|-------------|------|
| Outbound | CSW cluster / SaaS Secure Connector VM | Kubernetes API server | **443/TCP** (HTTPS) |
| Outbound | Every worker node (agent) | CSW control/telemetry FQDNs | **TLS** (per tenant) |
| Outbound (SaaS) | Secure Connector VM | CSW SaaS FQDN | **443/TCP** |

### 4. Platform facts to confirm

- [ ] Distribution: EKS / AKS / GKE / OpenShift / unmanaged (OpenShift must be **SDN**, not OVN)
- [ ] Node OS mix: Linux / Windows
- [ ] Container runtime: containerd / Docker / CRI-O
- [ ] CNI: Calico / Cilium / Weave / cloud CNI (any — CNI rules are preserved)
- [ ] Overlay vs direct routing (affects inter-node flow records: VXLAN/Geneve → UDP, IPIP → TCP)
- [ ] Namespaces / apps that should map to CSW **scopes**

---

## What CSW will produce

| K8s source | CSW label | Example |
|------------|-----------|---------|
| Orchestrator type | `orchestrator_system/orch_type` | `kubernetes` |
| Namespace | `orchestrator_system/namespace` | `sock-shop` |
| Service | `orchestrator_system/service_name` | `carts` |
| Pod label/annotation | `orchestrator_<key>` | `orchestrator_app=payment` |

Use these labels in **inventory search**, **scopes**, and **policy**. Because labels track the pod, policy follows the workload even as pod IPs churn.

---

## Security & compliance talking points

- **Least privilege connector** — read-only SA; no write access to the cluster.
- **CNI-agnostic & non-destructive** — CSW **preserves** CNI iptables and inserts its filter rules with priority.
- **Staged rollout** — visibility first, analyze policy against live traffic, then enforce namespace-by-namespace.
- **Auditable enforcement** — every allow/deny is a versioned, analyzable policy; node/pod rules are inspectable (`iptables -S | grep ta_`).
- **Vulnerability context** — optional CVE scanning feeds risk-based segmentation.
- **Secrets hygiene** — activation keys/tokens live in Kubernetes Secrets / a secrets manager, never in source control.

---

## Validation (joint test)

| # | Test | Owner | Pass |
|---|------|-------|------|
| 1 | Connector **Connection Status: Success** | CSW admin | ☐ |
| 2 | Pods/services visible (`orchestrator_system/orch_type = kubernetes`) | CSW admin | ☐ |
| 3 | DaemonSet: `DESIRED == READY == node count` | Platform team | ☐ |
| 4 | East-west flows visible for a test app (pod↔pod, via service) | Security architect | ☐ |
| 5 | Policy analysis shows expected allows/denies (no enforcement) | Security architect | ☐ |
| 6 | Enforce one namespace → allowed flow works, disallowed flow blocked | Platform + CSW | ☐ |
| 7 | CNI still healthy after enforcement (Preserve rules) | Platform team | ☐ |
| 8 | (Optional) Scanner reports CVEs on the Vulnerability dashboard | CSW admin | ☐ |

---

## References

- Full guide: [CSW-Kubernetes-Integration-Guide.md](../CSW-Kubernetes-Integration-Guide.md)
- Enforcement/iptables reference: [examples/enforcement-iptables-reference.md](../examples/enforcement-iptables-reference.md)
- Cisco deep-dive: [Secure Workload and Kubernetes](https://secure.cisco.com/secure-workload/docs/secure-workload-and-k8s)
- Integration requirements: [Secure Workload integration requirements](https://www.cisco.com/go/secure-workload/requirements/integrations)
- Compatibility Matrix: [Secure Workload](https://www.cisco.com/c/m/en_us/products/security/secure-workload-compatibility-matrix.html)

---

*Generic template — no customer-specific names. Customize contacts and endpoints locally before sending.*
