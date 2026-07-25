# Talos Migration

- cert-manager issuer for jw2.org domains
- cloudflare-dns (externald-dns)  needs a dns01 challenge with a valid token

## Apps to Migrate

- storage
  - minio
- 65t01
- three14
- brody

## PVC migration steps

 - Deploy the app to talos
 - Let volsync create the normal PVCs (smokeping-data)
 - Create the kopia secret on the k3s app namespace
 - Create the RS on the k3s side and get it into the kopia UI
 - Create RD on talos
   - Use the destinationPVC option put the data into the existing pvc
   - Use the repository secret from the talos NS:  volsync-xxx-secret or something

## Postgres permission fix

If apps need permission after restore and switching to initContainer method

```bash
```bash
 k exec -it -n database postgres16-1 -c postgres -- bash
 postgres@postgres16-1:/$ psql -d paperless
 psql (16.3 (Debian 16.3-1.pgdg110+1))
 Type "help" for help.
 
  paperless=# GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "paperless-q6xJPh";
  GRANT
  paperless=# GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO "paperless-q6xJPh";
  GRANT
```
```


## Postgres Immich Nightmware

 - pgvectors to vectorchord
 - trying to use a immich specific postgres16 image that has both to do the migration
    - but this has uid 26 vs uid 999 permission problems
 - then I can use a vectorcord-only postgrs18 maybe

## Completed

- default
  - wishlist
  - paperless (cnpg)
  - esphome
  - openspeedtest
  - karakeep
  - silverbullet
- home
  - mosquitto
  - frigate
  - zigbee2mqtt
- database
  - postgres/cnpg
- media
  - immich (cnpg)
  - jellyfin
  - jellyseerr
  - prowlarr
  - sabnzbd
  - radarr
  - sonarr
  - qbittorrent
- monitoring
  - smokeping
  - kube-prom-stack
  - grafana
  - snmp-exporter-brocade
- database
  - dragonfly
- security
  - authentik (cnpg, dragonfly)
- networking
  - omada-controller

## Apps Not Migrating

default
 - gitea
