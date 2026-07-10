# Enforcement & iptables reference — how CSW programs Kubernetes policy

When a workspace is **enforced**, the Cisco Secure Workload policy engine translates each
label-based **intent** into two rule tiers, applied by the DaemonSet agent:

- **Concrete (node) rules** → node-namespace `iptables` (e.g. NodePort pre-routing, health checks, forward).
- **Container (pod) rules** → each pod's network-namespace `iptables` (ingress/egress for that pod).

CNI chains (e.g. `cali-*`, `KUBE-*`) are **preserved**; CSW inserts its `ta_*` filter chains
with **priority**. This requires the agent's **Preserve rules** option to be enabled.

> These are **illustrative** representations of the auto-generated rules — CSW manages the real
> chains. Use them to reason about behavior and to verify on a node.

---

## Pattern A — Direct pod → pod (no service)

Intent: allow `app=payment` → `app=user-db` on **TCP/27017**.

```text
# payment pod netns (EGRESS)
-A ta_egress  -p tcp -m tcp --dport 27017 -m comment --comment "csw:allow payment->user-db" -j ACCEPT
# user-db pod netns (INGRESS)
-A ta_ingress -p tcp -m tcp --dport 27017 -m comment --comment "csw:allow payment->user-db" -j ACCEPT
# node netns: (none — CNI forward chain handles inter-node routing)
```

## Pattern B — Pod → pod via ClusterIP service

Intent: allow `app=frontend` → `svc/carts` (ClusterIP `10.100.135.136`) on **TCP/80**; carts pod also on 80.

```text
# frontend pod netns (EGRESS) — destination is the ClusterIP
-A ta_egress  -d 10.100.135.136/32 -p tcp --dport 80 -m comment --comment "csw:allow frontend->carts-svc" -j ACCEPT
# carts pod netns (INGRESS) — service IP is DNAT'd to pod IP in node ns; engine auto-adds the pod-IP allow
-A ta_ingress -p tcp --dport 80 -m comment --comment "csw:allow frontend->carts-pod (auto)" -j ACCEPT
# node netns: (none)
```

## Pattern C — Node → pod (health / readiness probe)

Intent: allow Kubernetes health checks → `app=frontend` on **TCP/80**.

```text
# node netns (EGRESS): node IP -> pods:80
-A ta_egress  -p tcp --dport 80 -m comment --comment "csw:allow node->frontend healthcheck" -j ACCEPT
# frontend pod netns (INGRESS): from node IPs
-A ta_ingress -s <NODE_IP_SET> -p tcp --dport 80 -m comment --comment "csw:allow node->frontend healthcheck" -j ACCEPT
```

## Pattern D — External → pod via NodePort / LoadBalancer

Intent: allow **any** → `frontend` NodePort service; pod listens **8079**, NodePort **31095**.

```text
# node netns (PREROUTING / INGRESS): any -> node pool IP on the NodePort (auto pre-routing allow)
-A ta_ingress -p tcp --dport 31095 -m comment --comment "csw:allow any->frontend nodeport" -j ACCEPT
# frontend pod netns (INGRESS): any -> pod IP on the pod port (auto pod-port allow)
-A ta_ingress -p tcp --dport 8079  -m comment --comment "csw:allow any->frontend podport" -j ACCEPT
```

> **Split-scope note:** if nodes and app pods/services are in different parent/child scopes,
> add the allow to **both** scopes.

## Pattern E — Pod → external IP

Intent: allow `app=frontend` pod IPs → external IP on **TCP/666**.

```text
# frontend pod netns (EGRESS)
-A ta_egress  -d <EXTERNAL_IP>/32 -p tcp --dport 666 -m comment --comment "csw:allow frontend->external" -j ACCEPT
# node netns: (none — SNAT'd to node IP, allowed by default forward allow-all)
```

---

## Verify on a node

```bash
# From the node host (or exec into the agent pod):
sudo iptables -S | grep -i ta_             # CSW/Tetration filter chains
sudo iptables -t nat -S | grep -i ta_      # NAT / NodePort pre-routing
sudo iptables -S | grep -Ei 'cali-|KUBE-'  # CNI chains still present == Preserve rules OK
```
