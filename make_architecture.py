#!/usr/bin/env python3
"""Render the CSW <-> Kubernetes integration architecture diagram.

Produces ``csw-kubernetes-architecture.png`` in the same visual language as the
other connector guides (F5, Infoblox, NetScaler, vCenter): Cisco navy/blue
palette, rounded panels, labelled data-flow arrows. Text is drawn as real
vector text so every label stays crisp and accurate.

Unlike the label-import-only orchestrators, the Kubernetes integration is a
two-way path: the connector pulls pod/service metadata IN, and the DaemonSet
node agents push enforcement (iptables) DOWN onto the cluster.

Run:  python3 make_architecture.py
Requires: matplotlib
"""
from matplotlib import pyplot as plt
from matplotlib.patches import (FancyBboxPatch, FancyArrowPatch, Circle,
                                Polygon, Rectangle, Ellipse)

# ---- Cisco / Kubernetes palette --------------------------------------------
NAVY = "#00205B"
BLUE = "#007BC7"
CYAN = "#00BCEB"
K8S = "#326CE5"       # Kubernetes blue
K8S_D = "#1F3F87"
INK = "#1A1A2E"
GREY = "#555555"
LIGHT = "#F5F8FC"
K8SBG = "#EEF3FE"
BLUEBG = "#EAF4FB"
GREEN = "#2E8B57"
RED = "#B52C2C"

fig, ax = plt.subplots(figsize=(13.4, 8.6), dpi=100)
ax.set_xlim(0, 134)
ax.set_ylim(0, 86)
ax.axis("off")


def panel(x, y, w, h, edge, fc="white", lw=2.2, rounding=1.4, z=1, ls="solid"):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={rounding}",
        linewidth=lw, edgecolor=edge, facecolor=fc, zorder=z, linestyle=ls))


def box(x, y, w, h, edge, fc="white", lw=1.4, rounding=0.9, z=2, ls="solid"):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={rounding}",
        linewidth=lw, edgecolor=edge, facecolor=fc, zorder=z, linestyle=ls))


def text(x, y, s, size=11, color=INK, weight="normal", ha="center", va="center", z=5):
    ax.text(x, y, s, fontsize=size, color=color, fontweight=weight,
            ha=ha, va=va, zorder=z,
            fontfamily=["Helvetica Neue", "Arial", "DejaVu Sans"])


def helm(cx, cy, r, color):
    """Draw a small Kubernetes-style 7-spoke helm glyph."""
    import math
    ax.add_patch(Circle((cx, cy), r, facecolor=color, edgecolor="white", lw=1.0, zorder=4))
    ax.add_patch(Circle((cx, cy), r * 0.42, facecolor="white", edgecolor=color, lw=0.9, zorder=5))
    for k in range(7):
        a = math.pi / 2 + k * 2 * math.pi / 7
        x2 = cx + math.cos(a) * r * 0.86
        y2 = cy + math.sin(a) * r * 0.86
        ax.plot([cx + math.cos(a) * r * 0.42, x2],
                [cy + math.sin(a) * r * 0.42, y2],
                color="white", lw=1.1, zorder=5)


# ---- Title + Cisco wordmark -------------------------------------------------
text(60, 82, "Cisco Secure Workload  \u2013  Kubernetes / OpenShift Integration",
     size=21, color=NAVY, weight="bold")

# stylized Cisco "bars" logo (top-right)
lx = 118.0
heights = [1.6, 2.6, 3.6, 2.6, 1.6, 2.6, 3.6, 4.6, 3.6, 2.6, 1.6]
for i, hh in enumerate(heights):
    ax.add_patch(Rectangle((lx + i * 0.75, 81.0 - hh / 2), 0.32, hh,
                 facecolor=NAVY, edgecolor="none", zorder=5))
text(lx + len(heights) * 0.375, 76.9, "CISCO", size=10, color=NAVY, weight="bold")

# =============================================================================
# LEFT PANEL  --  Cisco Secure Workload (control / management plane)
# =============================================================================
panel(3, 20, 34, 52, BLUE)
text(20, 68.4, "Cisco Secure Workload", size=14, color=BLUE, weight="bold")
text(20, 65.4, "(SaaS tenant or on-prem cluster)", size=9, color=GREY)

# External orchestrator / K8s connector box
box(6, 58.0, 28, 5.6, BLUE, BLUEBG)
ax.add_patch(Circle((9.6, 60.8), 1.5, facecolor=BLUE, edgecolor="white", lw=0.8, zorder=4))
ax.add_patch(Circle((9.6, 60.8), 0.55, facecolor="white", zorder=5))
text(22.5, 61.4, "K8s Connector /", size=9.3, color=NAVY, weight="bold")
text(22.5, 59.6, "External Orchestrator", size=9.3, color=NAVY, weight="bold")

# inventory database cylinder
cx, cy, cw, ch = 8.5, 47.5, 11, 7.5
ax.add_patch(Rectangle((cx, cy), cw, ch, facecolor="white", edgecolor=NAVY, lw=1.7, zorder=3))
ax.add_patch(Ellipse((cx + cw / 2, cy + ch), cw, 2.0, facecolor="white", edgecolor=NAVY, lw=1.7, zorder=4))
ax.add_patch(Ellipse((cx + cw / 2, cy), cw, 2.0, facecolor="white", edgecolor=NAVY, lw=1.7, zorder=3))
text(cx + cw / 2, cy + ch / 2 + 0.4, "Inventory", size=9, color=NAVY, weight="bold")
text(cx + cw / 2, cy + ch / 2 - 1.5, "(pods/svcs)", size=8, color=NAVY)
text(31, 51.6, "orchestrator_*", size=8, color=GREY, ha="center")
text(31, 49.8, "pod / ns / svc", size=8, color=GREY, ha="center")
text(31, 48.0, "labels", size=8, color=GREY, ha="center")

# scopes + policies pills
box(6, 39.5, 12, 5.2, BLUE, BLUE)
text(12, 42.1, "Scopes", size=9.5, color="white", weight="bold")
box(22, 39.5, 12, 5.2, NAVY, NAVY)
text(28, 42.1, "Policies", size=9.5, color="white", weight="bold")

# policy engine translate note
box(6, 31.0, 28, 6.6, "#BBD3F2", "#F3F7FE")
text(20, 35.4, "Policy engine translates intent", size=8.7, color=NAVY, weight="bold")
text(20, 33.4, "\u2192 concrete (node) + container (pod)", size=8.2, color=GREY)
text(20, 31.8, "iptables rules", size=8.2, color=GREY)

# vuln dashboard pill
box(6, 22.5, 28, 6.0, GREEN, "#EAF6EF")
text(20, 26.3, "Vulnerability dashboard (CVEs)", size=8.7, color=GREEN, weight="bold")
text(20, 24.3, "from optional scanner pod", size=8.2, color=GREY)

# =============================================================================
# RIGHT PANEL  --  Kubernetes / OpenShift cluster
# =============================================================================
panel(58, 12, 73, 60, K8S)
text(94.5, 68.6, "Kubernetes / OpenShift Cluster", size=14, color=K8S_D, weight="bold")
text(94.5, 65.8, "(EKS · AKS · GKE · OpenShift · unmanaged)", size=9, color=GREY)

# --- kube-apiserver box (top) ---
box(61, 58.5, 30, 5.8, K8S_D, K8SBG)
helm(64.6, 61.4, 1.7, K8S)
text(78.5, 62.3, "kube-apiserver", size=9.6, color=K8S_D, weight="bold")
text(78.5, 60.2, "pod / service / label metadata", size=8.0, color=GREY)

# vuln scanner pod (top right)
box(98, 58.5, 30, 5.8, GREEN, "#EAF6EF")
ax.add_patch(Circle((101.6, 61.4), 1.6, facecolor=GREEN, edgecolor="white", lw=0.8, zorder=4))
text(101.6, 61.4, "CVE", size=6.6, color="white", weight="bold", z=6)
text(115.5, 62.3, "Scanner pod (optional)", size=9.2, color=GREEN, weight="bold")
text(115.5, 60.2, "scans container images \u2192 CVEs", size=8.0, color=GREY)

# --- Worker node 1 ---
def worker(nx, ny, nw, nh, label):
    box(nx, ny, nw, nh, K8S, "white", lw=1.7)
    text(nx + nw / 2, ny + nh - 2.4, label, size=9.6, color=K8S_D, weight="bold")
    # DaemonSet agent pill
    box(nx + 1.6, ny + nh - 6.6, nw - 3.2, 3.4, NAVY, "#EDF2FB")
    ax.add_patch(Circle((nx + 4.2, ny + nh - 4.9), 1.15, facecolor=NAVY, edgecolor="white", lw=0.6, zorder=4))
    text(nx + nw / 2 + 1.2, ny + nh - 4.9, "CSW agent (DaemonSet)", size=8.0, color=NAVY, weight="bold")
    # pods
    pw = (nw - 5.2) / 3
    for i in range(3):
        px = nx + 1.9 + i * (pw + 0.7)
        box(px, ny + 1.6, pw, 3.4, K8S, K8SBG, lw=1.1, rounding=0.5)
        helm(px + pw / 2, ny + 3.3, 0.95, K8S)
    text(nx + nw / 2, ny + 0.6, "pods  \u00b7  pod-namespace iptables (container rules)", size=7.4, color=GREY)


worker(61, 40.5, 32.5, 15.5, "Worker node 1")
worker(97.5, 40.5, 30.5, 15.5, "Worker node 2")

# node-namespace iptables strip under nodes
box(61, 33.5, 67, 5.2, K8S_D, "#E4ECFB")
text(94.5, 36.9, "Node-namespace iptables  \u2014  concrete rules (NodePort / health-check / forward)", size=8.6, color=K8S_D, weight="bold")
text(94.5, 34.8, "CNI rules preserved (Calico · Cilium · Weave · AWS/Azure CNI) \u2014 CSW filter rules take priority", size=7.7, color=GREY)

# flows captured note
box(61, 24.5, 67, 6.6, BLUE, BLUEBG)
text(94.5, 29.4, "DaemonSet captures flows at pod + node interfaces", size=8.8, color=NAVY, weight="bold")
text(94.5, 27.4, "pod\u2194pod (intra/inter-node) \u00b7 via ClusterIP \u00b7 external\u2194NodePort/LB \u00b7 pod\u2192external", size=7.6, color=GREY)
text(94.5, 25.6, "conversation mode (15s summaries) or detailed mode (per-packet, 1s)", size=7.6, color=GREY)

# =============================================================================
# CONNECTING ARROWS between the two planes
# =============================================================================
# 1. Connector pulls inventory/metadata IN  (apiserver -> CSW)  HTTPS
ax.add_patch(FancyArrowPatch((61, 61.2), (37, 61.0),
             arrowstyle="-|>", mutation_scale=22, linewidth=3.2, color=BLUE, zorder=6))
text(49, 63.0, "K8s API (HTTPS/443)", size=8.6, color=BLUE, weight="bold")
text(49, 61.1, "pull pod/svc metadata \u2192 labels", size=7.6, color=GREY)

# 2. Agents report flow telemetry IN (node -> CSW)  TLS
ax.add_patch(FancyArrowPatch((61, 27.6), (37, 44.0),
             arrowstyle="-|>", mutation_scale=20, linewidth=2.6, color=CYAN, zorder=6))
text(49, 39.0, "flow telemetry (TLS)", size=8.2, color="#0891b2", weight="bold")

# 3. Policy pushed DOWN (CSW -> agents) enforcement
ax.add_patch(FancyArrowPatch((34, 33.4), (61, 35.8),
             arrowstyle="-|>", mutation_scale=20, linewidth=2.6, color=NAVY, zorder=6))
text(48, 32.0, "enforcement: iptables", size=8.2, color=NAVY, weight="bold")
text(48, 30.2, "pushed to node + pod ns", size=7.4, color=GREY)

# 4. Scanner CVEs up
ax.add_patch(FancyArrowPatch((104, 58.4), (30, 28.6),
             arrowstyle="-|>", mutation_scale=14, linewidth=1.6, color=GREEN,
             linestyle=(0, (5, 3)), zorder=5,
             connectionstyle="arc3,rad=-0.12"))

# =============================================================================
# Secure Connector tunnel (dashed) note bottom-left
# =============================================================================
box(3, 12.5, 34, 5.6, BLUE, "white", lw=1.5, ls=(0, (4, 3)))
from matplotlib.patches import Arc
ax.add_patch(Arc((7.2, 15.9), 1.5, 1.7, theta1=0, theta2=180,
             linewidth=1.4, edgecolor=BLUE, zorder=6))
ax.add_patch(FancyBboxPatch((6.15, 13.6), 2.1, 1.9,
             boxstyle="round,pad=0,rounding_size=0.25",
             facecolor=BLUE, edgecolor="none", zorder=6))
ax.add_patch(Circle((7.2, 14.5), 0.3, facecolor="white", zorder=7))
text(23.5, 16.0, "Secure Connector tunnel", size=8.8, color=NAVY, weight="bold")
text(23.5, 14.0, "(SaaS / private clusters)", size=8.0, color=GREY)

# ---- bottom gradient bar + caption -----------------------------------------
grad_y = 5.5
for i in range(200):
    frac = i / 199
    if frac < 0.6:
        t = frac / 0.6
        r = int(0x00); g = int(0x20 + t * (0x7b - 0x20)); b = int(0x5b + t * (0xc7 - 0x5b))
    else:
        t = (frac - 0.6) / 0.4
        r = int(0x00); g = int(0x7b + t * (0xbc - 0x7b)); b = int(0xc7 + t * (0xeb - 0xc7))
    ax.add_patch(Rectangle((3 + frac * 128, grad_y), 128 / 200 + 0.2, 1.0,
                 facecolor=f"#{r:02x}{g:02x}{b:02x}", edgecolor="none", zorder=2))

text(67, 2.4,
     "Connector imports pod/service labels  \u00b7  DaemonSet reports flows & enforces iptables  \u00b7  scanner reports CVEs",
     size=10.5, color=NAVY, weight="bold")

plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
out = "csw-kubernetes-architecture.png"
plt.savefig(out, dpi=100, facecolor="white", bbox_inches="tight", pad_inches=0.15)
print("wrote", out)
