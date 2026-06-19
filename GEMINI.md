# Gemini CLI Instructions - Talos IaC

Foundational mandates for AI agents working in this repository.

## Operational Standards

- **GitOps First:** All changes to cluster state MUST be made by modifying YAML manifests in `kubernetes/` or `talos/` and reconciling via Flux. Avoid manual `kubectl` edits except for transient troubleshooting.
- **Resource Discipline:** Always specify reasonable CPU/Memory requests and limits. CPU requests should be kept minimal (e.g., `10m` or `100m`) for non-critical path components to avoid scheduling deadlocks on this cluster.
- **Validation:** After any change to `kubernetes/`, always run `task reconcile` (if available) or manual `flux reconcile` commands to verify the change.

## Storage (Rook-Ceph)

- **CSI RBAC:** Rook-Ceph v1.20+ requires explicit RBAC for CSI components if not handled by the operator. See `kubernetes/apps/rook-ceph/app/csi-rbac.yaml` for required permissions.
- **Storage Troubleshooting:** If volumes fail to attach, check `VolumeAttachment` status and clear stuck `Lease` objects in the `rook-ceph` namespace to force leader re-election.

## VolSync (Backups/Restore)

- **Mover Lifecycle:** If backups hang, check the `storage/volsync` operator logs. You may need to scale the operator to 0, cleanup hung jobs/pods, and scale back up to clear the queue.
- **Multi-Attach Errors:** VolSync mover pods often trigger Multi-Attach errors if a previous pod didn't detach correctly. Force-deleting the `VolumeAttachment` for the affected PVC is usually required.
- **Kopia Config Path:** Kopia (v0.23.0+) requires a writable configuration path. Always configure `KOPIA_CONFIG_PATH: /tmp/repository.config` to prevent startup write permission errors.
- **Kopia Authentication:** Keep password authentication configured on Kopia HTTP server and ensure Homepage dashboard widget settings align with those credentials.

## Databases (Dragonfly/CloudNative-PG)

- **Dragonfly Operator:** Requires cluster-wide permission for `networkpolicies` and `poddisruptionbudgets`. If the operator crashes with "forbidden" errors, verify the `dragonfly-operator` ClusterRole.
- Postgres (CNPG): Managed by CloudNative-PG. Ensure `postgres18` cluster status is healthy before deploying dependent apps.

## Talos Image Customization (Schematics)

- **System Extensions:** Hardware-specific drivers (like `i915` for Intel GPUs) are NOT in the base Talos image. Use the `schematic` block in `talconfig.yaml` to include them.
- **Intel GPU (Raptor Lake):** For UHD 770 passthrough, ensure the `i915` and `intel-ucode` extensions are included. Required kernel args: `i915.force_probe=a780` and `i915.enable_guc=3`.
- **Applying Changes:** After updating `schematic` or `extraKernelArgs`, run `task talos:generate-config` and then a `talosctl upgrade` with the new image URL.

## Alerts & Notifications

- **Telegram Noise Suppression:** To avoid notification spam from routine reconciliations (e.g. OCI repositories), add regex patterns to the `exclusionList` in the shared component `kubernetes/components/telegram-alert/telegram-alert.yaml` instead of hardcoding namespaces.

