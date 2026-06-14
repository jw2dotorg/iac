# AGENTS.md

This file contains guidelines for AI agents working in this Talos Kubernetes Infrastructure as Code repository.

## Project Overview

This is a Talos OS Kubernetes cluster managed via GitOps using Flux CD. The infrastructure is declared as code using:
- **Talos OS** for Kubernetes cluster management
- **Flux CD** for GitOps deployment
- **Helmfile** for Helm chart management
- **SOPS** for secrets encryption with Age keys
- **Kustomize** for Kubernetes resource management

## Build/Lint/Test Commands

### Primary Commands (via Task runner)
```bash
task --list                    # List all available tasks
task reconcile                 # Force Flux to pull changes from Git
task bootstrap:talos          # Bootstrap Talos cluster
task bootstrap:apps           # Bootstrap apps into cluster
task talos:generate-config    # Generate Talos configuration
task talos:apply-node IP=x.x.x.x  # Apply config to specific node
task talos:upgrade-node IP=x.x.x.x  # Upgrade Talos on node
task talos:upgrade-k8s        # Upgrade Kubernetes
task talos:reset              # Reset nodes to maintenance mode
```

### Validation and Testing
```bash
flux-local test --path ./kubernetes --enable-helm --all-namespaces
# Validate with standard and custom CRD schemas (skipping missing ones)
kubeconform -summary -kubernetes-version 1.35.0 -schema-location default -schema-location 'https://kubernetes-schemas.pages.dev/{{.Group}}/{{.ResourceKind}}_{{.ResourceAPIVersion}}.json' -ignore-missing-schemas ./kubernetes/**/*.yaml
```

### Tool Management
```bash
mise install                  # Install all required tools
mise exec <tool> -- <command> # Run specific tool
```

## Code Style Guidelines

### Shell Scripts
- Use `#!/usr/bin/env bash` shebang
- Strict error handling: `set -Eeuo pipefail`
- 4-space indentation
- Environment variables in UPPER_CASE
- Function names in snake_case
- Structured logging with key-value pairs
- Explicit exit codes for error handling

### YAML Files
- 2-space indentation
- LF line endings
- UTF-8 encoding
- Trim trailing whitespace
- Use SOPS for encrypted secrets: `sops --encrypt --encrypted-regex '^(data|stringData)$'`

### General Conventions
- Follow GitOps principles: all changes committed to Git
- Use semantic versioning for cluster upgrades
- Maintain backward compatibility for Kubernetes APIs
- Encrypt all secrets using SOPS with Age keys
- Use structured naming for resources: `app-environment-component`

## Directory Structure

```
/
├── talos/           # Talos cluster configuration and patches
├── kubernetes/      # Kubernetes manifests and applications
├── bootstrap/       # Bootstrap scripts and Helmfile configurations
├── scripts/         # Utility scripts for cluster management
├── .sops.yaml/      # SOPS encryption configuration
└── Taskfile.yaml    # Task runner configuration
```

## Error Handling

### Shell Scripts
- Always use `set -Eeuo pipefail`
- Check command exit codes explicitly
- Provide meaningful error messages
- Use cleanup traps for temporary resources

### Kubernetes Resources
- Use resource requests/limits
- Implement health checks (readiness/liveness probes)
- Use proper restart policies
- Validate manifests with kubeconform

## Security Guidelines

- Never commit unencrypted secrets
- Use SOPS for all sensitive data
- Rotate Age keys regularly
- Use RBAC for Kubernetes access
- Validate all external images
- Use network policies where applicable

## Testing Strategy

This is an IaC project - testing focuses on:
1. **Manifest validation** - Use kubeconform for Kubernetes resources
2. **Flux validation** - Use flux-local for GitOps configuration
3. **Integration testing** - Deploy to staging environment first
4. **Configuration testing** - Validate Talos config generation

## Common Patterns

### Flux Kustomizations
```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: app-name
  namespace: flux-system
spec:
  interval: 10m
  path: ./kubernetes/apps/app-name
  prune: true
  sourceRef:
    kind: GitRepository
    name: flux-system
```

### HelmReleases
```yaml
apiVersion: helm.toolkit.fluxcd.io/v2
kind: HelmRelease
metadata:
  name: app-name
  namespace: apps
spec:
  interval: 5m
  chart:
    spec:
      chart: app-name
      version: "x.x.x"
      sourceRef:
        kind: HelmRepository
        name: app-name-repo
```

## Tools and Dependencies

All tools are managed via Mise (.mise.toml):
- Python 3.14.2
- Containerized CLI tools via Aqua
- Flux CLI, Helm, Kubectl, Talos CLI
- SOPS for secrets management
- Task for task running

## Before Making Changes

1. Read existing configurations to understand patterns
2. Test changes in staging environment first
3. Validate all YAML manifests
4. Encrypt secrets with SOPS
5. Run `task reconcile` to test Flux configuration

## Troubleshooting

- Check Flux logs: `kubectl logs -n flux-system deployment/flux-controller`
- Validate Talos config: `talhelper validate -c .`
- Decrypt secrets: `sops --decrypt file.yaml`
- Check cluster status: `kubectl get nodes -o wide`