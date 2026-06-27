# Rook-Ceph & VolSync Troubleshooting (June 2026)

This document details the resolution of cluster-wide storage instability and VolSync backup failures following the Rook-Ceph v1.20 upgrade.

## Issue 1: CSI RBD Attachment Failures
**Symptoms:** Pods stuck in `ContainerCreating` or `Init` with `AttachVolume.Attach failed ... timed out waiting for external-attacher`.
**Root Cause:** Missing RBAC permissions for CSI components in Rook-Ceph v1.20. Specifically, ServiceAccounts lacked permissions to update `volumeattachments/status` and list `csinodes`.
**Resolution:**
- Created `kubernetes/apps/rook-ceph/app/csi-rbac.yaml` to define `rbd-ctrlplugin-sa` and `rbd-nodeplugin-sa` with correct ClusterRoles.
- Added permissions for:
    - `storage.k8s.io/volumeattachments` (and `/status`)
    - `storage.k8s.io/csinodes`
    - `coordination.k8s.io/leases`
- Restarted `rook-ceph.rbd.csi.ceph.com-ctrlplugin` and `nodeplugin` components.
- Manually cleared stuck leader election `Lease` objects in the `rook-ceph` namespace.

## Issue 2: VolSync Backup/Restore Hangs
**Symptoms:** ReplicationSource/Destination objects stuck in `Synchronizing` or `Pending`.
**Root Cause:**
1.  VolSync operator was scaled to 0 replicas.
2.  CSI attachment failures (see Issue 1) prevented mover pods from starting.
3.  Multi-Attach errors due to stuck VolumeAttachments from previous failed attempts.
**Resolution:**
- Scaled `volsync` deployment in `storage` namespace to 1 replica.
- Force-deleted failed `VolumeAttachment` objects to clear the CSI attacher queue.
- Scaled down VolSync, deleted all hung mover jobs/pods, and scaled back up to reset the state.

## Issue 3: Resource Starvation (Scheduling Deadlocks)
**Symptoms:** `Insufficient cpu` warnings on `rook-ceph-osd-prepare` pods; Flux reconciliations hanging.
**Root Cause:** High CPU requests on OSD prepare jobs (1000m) and RGW gateways caused scheduling saturation.
**Resolution:**
- Updated `kubernetes/apps/rook-ceph/cluster/helmrelease.yaml` to lower `prepareosd` CPU requests to `100m`.
- Lowered `ceph-objectstore` gateway CPU requests to `100m`.

## Issue 4: Dragonfly Connectivity
**Symptoms:** Paperless/Immich unable to connect to Dragonfly (Redis).
**Root Cause:** Dragonfly operator lacked RBAC to manage `networkpolicies`, causing it to crash and fail to properly configure the Dragonfly service selector (resulting in no endpoints).
**Resolution:**
- Patched `dragonfly-operator` ClusterRole to include `networking.k8s.io/networkpolicies` and `policy/poddisruptionbudgets`.
- Restarted `dragonfly-operator`, which then correctly labeled pods and populated the `dragonfly` service endpoints.

## Issue 5: Frigate Crashloop (GPU/OpenVINO)
**Symptoms:** Frigate stuck in `CrashLoopBackOff` with `[GPU] Context was not initialized for 0 device`. `/dev/dri` missing from the node.
**Root Cause:**
- Talos image on `talos1` was a base image missing the `i915` and `intel-ucode` system extensions.
- Raptor Lake (UHD 770) GPU required specific kernel arguments (`i915.force_probe`) and GuC/HuC firmware loading to initialize.
**Resolution:**
- Updated `talos/talconfig.yaml` to include a custom `schematic` for `talos1` with `siderolabs/i915` and `siderolabs/intel-ucode`.
- Added `extraKernelArgs` to `talos1`: `i915.force_probe=a780` and `i915.enable_guc=3`.
- Performed a `talosctl upgrade` using the new schematic-based image URL.

## Issue 6: Kopia HTTP Server Read-Only Permission Error (v0.23.0 Upgrade)
**Symptoms:** After upgrading Kopia to v0.23.0, the server pods crash loop with write permission errors.
**Root Cause:** The Kopia container attempts to write configuration updates to its default configuration path on startup, which is mounted on a read-only filesystem.
**Resolution:**
- Configured `KOPIA_CONFIG_PATH: /tmp/repository.config` environment variable in the HelmRelease values for Kopia.
- Enforced password authentication on the Kopia HTTP server and updated the Homepage dashboard widget settings to use the updated credentials, ensuring secure connection and preventing authentication failures.

## Issue 7: Kopia Repository Blob Accumulation (Too Many Blobs)
**Symptoms:** Storage warnings indicating too many unmaintained blobs in the Kopia repository.
**Root Cause:** Automated repository garbage collection and maintenance were not scheduled or executed.
**Resolution:**
- Created and registered `kopiamaintenance.yaml` under `kubernetes/apps/storage/kopia/app/` to schedule automated repository cleanup (blob pruning, indexing, garbage collection) to run regularly.

## Issue 8: Telegram Alert Spam from OCIRepositories
**Symptoms:** Spammy notifications on Telegram reporting `OCIRepository/<namespace>/<name> configured` during routine reconciliation intervals, even when no configuration changes had been made.
**Root Cause:** Multi-app configurations or multiple Kustomizations referencing/applying the same OCIRepository trigger frequent `Progressing` events, which were captured by the cluster-wide Alert config.
**Resolution:**
- Added `".*OCIRepository/.*configured.*"` to the `exclusionList` in the shared component [telegram-alert.yaml](file:///home/jason/projects/talos/iac/kubernetes/components/telegram-alert/telegram-alert.yaml). This suppresses routine configuration notices while preserving actual warnings/failures.

## Issue 9: Renovate Auto-Merge failing for Minor and Digest Updates
**Symptoms:** Minor and digest pull requests opened by `renovate[bot]` are not merged automatically.
**Root Cause:** Renovate was only configured to auto-merge patch updates. Additionally, the `.github/workflows/renovate-approve.yaml` workflow was hardcoded to only trigger for the `type/patch` label.
**Resolution:**
- Configured `automerge: true` and `automergeType: "pr"` for both `minor` and `digest` update types in `.renovaterc.json5`.
- Updated `.github/workflows/renovate-approve.yaml` to trigger for `type/patch`, `type/minor`, and `type/digest` labels.
