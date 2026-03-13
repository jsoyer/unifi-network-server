# UniFi Network Server in Docker 🐳

[![Build](https://github.com/jsoyer/unifi-network-server/actions/workflows/build.yml/badge.svg)](https://github.com/jsoyer/unifi-network-server/actions/workflows/build.yml)
[![Publish](https://github.com/jsoyer/unifi-network-server/actions/workflows/docker.yml/badge.svg)](https://github.com/jsoyer/unifi-network-server/actions/workflows/docker.yml)
[![Docker Pulls](https://img.shields.io/docker/pulls/jsoyer/unifi-network-server)](https://hub.docker.com/r/jsoyer/unifi-network-server)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./license)

A production-ready Docker image for [Ubiquiti's UniFi Network Server](https://ui.com/), built for `amd64`, `arm64`, and `armhf`. Runs on Linux, macOS, Windows, and Raspberry Pi.

> **Note:** This project was previously known as `unifi-docker` / `jsoyer/unifi`. It has been renamed to `unifi-network-server` / `jsoyer/unifi-network-server`. Please update your `docker-compose.yml` or `docker run` commands accordingly.

This is a fork of [jacobalberty/unifi-docker](https://github.com/jacobalberty/unifi-docker). Huge thanks to **Jacob Alberty** for his foundational work. 🙌

---

## 📦 Current Version

| Tag | Description | Changelog |
|---------------------------------------------------------------------------------------------|---------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|
| [`latest` `v10.2.93`](https://github.com/jsoyer/unifi-network-server/blob/master/Dockerfile) | Current Stable: Version 10.2.93 as of 2026-03-12 | [Change Log 10.2.93](https://community.ui.com/releases/UniFi-Network-Application-10-2-93/6124ef35-ce93-47d9-8f9d-fa44ab02c587) |
| [`stable-6`](https://github.com/jsoyer/unifi-network-server/blob/stable-6/Dockerfile) | Final stable version 6 (6.5.55) | [Change Log 6.5.55](https://community.ui.com/releases/UniFi-Network-Application-6-5-55/48c64137-4a4a-41f7-b7e4-3bee505ae16e) |
| [`stable-5`](https://github.com/jsoyer/unifi-network-server/blob/stable-5/Dockerfile) | Final stable version 5 (5.14.23) | [Change Log 5.14.23](https://community.ui.com/releases/UniFi-Network-Controller-5-14-23/daf90732-30ad-48ee-81e7-1dcb374eba2a) |

Images are available on:
- **GitHub Container Registry:** `ghcr.io/jsoyer/unifi-network-server`
- **Docker Hub:** `jsoyer/unifi-network-server`

A GitHub Actions workflow checks the UniFi RSS feed daily and opens a pull request automatically whenever a new stable release is available.

### 🖥️ Multi-architecture support

| Architecture | Status | Notes |
|---|---|---|
| `amd64` | ✅ | Fully supported |
| `arm64` (v8) | ✅ | Raspberry Pi 4/5 (64-bit OS), Apple Silicon via QEMU |
| `armhf` (v7) | ⚠️ | Raspberry Pi 4 (32-bit OS). MongoDB 3.6 only — no upgrade path to 7.0 available |

---

## 🚀 Quick Start

### With Docker Compose (recommended)

```bash
# Copy the example env file and adjust as needed
cp .env.example .env

# Start all services
docker compose up -d
```

The `docker-compose.yml` in this repository starts a MongoDB container and the UniFi controller together. Access the web UI at `https://<docker-host-ip>:8443` once the controller is healthy (allow ~2 minutes on first boot).

### With Docker Run

```bash
docker run -d --init \
  --restart=unless-stopped \
  -p 8080:8080 -p 8443:8443 -p 3478:3478/udp -p 10001:10001/udp \
  -e TZ='Europe/Paris' \
  -e SYSTEM_IP='<your-docker-host-ip>' \
  -v ~/unifi:/unifi \
  --user unifi \
  --name unifi \
  jsoyer/unifi-network-server
```

---

## ⚙️ Configuration

### Environment Variables

Copy `.env.example` to `.env` to get a documented template of all available variables.

| Variable | Default | Description |
|---|---|---|
| `TZ` | unset | Timezone (e.g. `Europe/Paris`, `America/New_York`) |
| `SYSTEM_IP` | unset | IP advertised to devices for adoption. **Must match your Docker host IP.** |
| `UNIFI_HTTP_PORT` | `8080` | HTTP port for device communication |
| `UNIFI_HTTPS_PORT` | `8443` | HTTPS port for the web UI and API |
| `PORTAL_HTTP_PORT` | `80` | HTTP captive portal redirect port |
| `PORTAL_HTTPS_PORT` | `8843` | HTTPS captive portal redirect port |
| `JVM_MAX_HEAP_SIZE` | `1024M` | JVM max heap. Increase for large deployments. |
| `JVM_INIT_HEAP_SIZE` | unset | JVM initial heap size |
| `JVM_MAX_THREAD_STACK_SIZE` | unset | JVM thread stack size (e.g. `1280k`) |
| `JVM_EXTRA_OPTS` | unset | Additional JVM arguments |
| `LOTSOFDEVICES` | unset | Set to `true` to enable G1GC and reduce MongoDB I/O for 50+ device deployments |
| `UNIFI_STDOUT` | unset | Set to `true` to forward application logs to Docker stdout |
| `UNIFI_ECC_CERT` | `false` | Set to `true` if using an Elliptic Curve certificate |
| `SMTP_STARTTLS_ENABLED` | unset | Set to `false` to disable StartTLS for SMTP |
| `RUNAS_UID0` | `true` | Set to `false` to run as the `unifi` user (recommended) |
| `UNIFI_UID` | `999` | UID for the `unifi` user inside the container |
| `UNIFI_GID` | `999` | GID for the `unifi` group inside the container |
| `DB_URI` | unset | External MongoDB URI (e.g. `mongodb://mongo/unifi`) |
| `STATDB_URI` | unset | External MongoDB stats URI |
| `DB_NAME` | unset | External MongoDB database name |

### 🔌 Exposed Ports

| Port | Protocol | Purpose |
|---|---|---|
| `8080` | TCP | Device communication (required) |
| `8443` | TCP | Web UI and API (required) |
| `3478` | UDP | STUN service (required) |
| `10001` | UDP | Device discovery (required) |
| `8880` | TCP | HTTP captive portal _(optional)_ |
| `8843` | TCP | HTTPS captive portal _(optional)_ |
| `6789` | TCP | Speed test _(optional)_ |

See [UniFi — Ports Used](https://help.ubnt.com/hc/en-us/articles/218506997-UniFi-Ports-Used) for details.

---

## 💾 Volumes

| Path | Description |
|---|---|
| `/unifi/data` | Controller configuration and database (persist this!) |
| `/unifi/log` | Application log files |
| `/unifi/cert` | Custom SSL certificates |
| `/unifi/init.d` | Custom scripts run on every container start |
| `/var/run/unifi` | PID and runtime files |

> **Legacy paths** `/var/lib/unifi` and `/var/log/unifi` still work via symlinks for backwards compatibility.

---

## 🔌 Adopting Access Points and UniFi Devices

For your devices to find the controller running in Docker, set `SYSTEM_IP` to the IP address of your Docker host. Without this, devices will try to reach the container's internal Docker IP (e.g. `172.17.x.x`) and fail.

```yaml
environment:
  SYSTEM_IP: 192.168.1.100  # your Docker host IP
```

Alternatively, in the UniFi web UI go to **UniFi Devices → Device Settings → Inform Host Override**, enable it and enter your Docker host IP.

> 💡 Port `10001/udp` must be forwarded for device discovery to work.

See [Side Projects](https://github.com/jsoyer/unifi-network-server/blob/master/Side-Projects.md#other-techniques-for-adoption) for Layer 2 adoption and SSH adoption methods.

---

## 👤 Running as Non-root (Recommended)

The recommended way to run this container is as the `unifi` user (UID/GID 999):

```yaml
# docker-compose.yml
user: unifi
sysctls:
  net.ipv4.ip_unprivileged_port_start: 0  # allows binding to ports < 1024
```

Or with `docker run`:
```bash
docker run ... --user unifi --sysctl net.ipv4.ip_unprivileged_port_start=0 ...
```

---

## 💾 Backup and Restore

### Backup directory permissions

The `docker-compose.yml` mounts `./backup` on your host to `/unifi/data/backup` inside the container. The entrypoint creates this directory automatically with the correct permissions on first boot.

If you create the directory manually before starting the container, ensure it is owned by `999:999`:

```bash
mkdir -p backup
chown -R 999:999 backup/
```

### Importing a backup

1. Upload the `.unf` backup file via the UniFi web UI (**System → Backup → Restore**)
2. UniFi will restore the data and restart internally
3. The container will exit and Docker will restart it automatically (`restart: always`)
4. On the next boot the controller resumes with the restored configuration

> ⚠️ After importing a backup from a **standalone install** (non-Docker), the external MongoDB settings are automatically re-applied from environment variables on restart — no manual intervention needed.

---

## 🔒 Certificate Support

Mount your certificates to `/unifi/cert`. Expected file names:

```
cert.pem      # Certificate
privkey.pem   # Private key
chain.pem     # Full certificate chain (optional)
```

Use `CERTNAME` and `CERT_PRIVATE_NAME` environment variables if your files have different names.

**Let's Encrypt:** Automatically detected. The required Identrust X3 CA cert is added automatically. If your cert is already a chained certificate, set `CERT_IS_CHAIN=true`.

**Elliptic Curve certificates:** Set `UNIFI_ECC_CERT=true`. You can verify your cert type with:

```bash
openssl x509 -text < cert.pem | grep 'Public Key Algorithm'
# id-ecPublicKey → set UNIFI_ECC_CERT=true
```

---

## 🛠️ Init Scripts

Place executable scripts in `/unifi/init.d` (mounted as a volume) to run custom logic on every container start. Useful for certificate imports, custom configuration, etc.

An example certificate import script is available at `/usr/unifi/init.d/import_cert` inside the container.

---

## ⬆️ Upgrading UniFi Controller

All configuration is stored in the mounted volumes — nothing is retained inside the container itself. Upgrading is simply a matter of pulling a new image:

```bash
docker compose pull
docker compose down
docker compose up -d
```

> ⚠️ **Always make a backup before upgrading**, stored on a separate machine — not just the Docker host.

---

## ℹ️ Additional Information

See [Side Projects and Background Info](https://github.com/jsoyer/unifi-network-server/blob/master/Side-Projects.md) for external MongoDB setup, Layer 2 adoption, beta builds, and more.

---

## 📝 Roadmap

### 🔴 High priority

- **Upgrade base image from Ubuntu 20.04 to 24.04** — Ubuntu 20.04 reached EOL in April 2025 and no longer receives security patches. This is a prerequisite for the MongoDB upgrade below. Note: `temurin-25-jdk` (required by UniFi 10.1.x) is confirmed available in the Adoptium repo for Ubuntu 20.04 focal on arm64, so the Java setup will carry over cleanly to 24.04.

- **Upgrade external MongoDB from 3.6 to 7.0** — MongoDB 3.6 is EOL since April 2022. MongoDB 7.0 brings journaling improvements, better crash recovery, and long-term support. Findings:
  - ✅ **UniFi 10.1.85 officially supports MongoDB 7.0** — the `.deb` package declares `mongodb-org-server (>= 3.6.0, < 8.1.0)`, so 7.0 is within the supported range.
  - ✅ **aarch64 (arm64/v8) confirmed** — `mongo:7.0` ships an official `linux/arm64/v8` image. Covers Pi 4 and Pi 5 running a 64-bit OS.
  - ❌ **armhf (32-bit ARM) is a blocker** — MongoDB dropped official armhf support after 3.x. Pi 4 users running a 32-bit OS are affected. Options: find a community build for MongoDB 7.0 on armhf, or officially drop armhf support and document it.
  - ⚠️ **Incremental upgrade required** — MongoDB does not support jumping directly from 3.6 to 7.0. The upgrade path must go through each major version: 3.6 → 4.0 → 4.2 → 4.4 → 5.0 → 6.0 → 7.0, with `setFeatureCompatibilityVersion` run at each step before moving to the next. A migration guide and/or helper script will be needed.

### 🟡 Medium priority

- ~~**Migrate CI from Travis CI to GitHub Actions**~~ ✅ — `build.yml` (PR) and `docker.yml` (publish) fully rewritten with modern action versions, fixed deprecated syntax, and multi-platform builds on `main`.
- ~~**Add image vulnerability scanning (Trivy)**~~ ✅ — Trivy runs on every PR and every push to `main`, results uploaded to the GitHub Security tab as SARIF.
- ~~**Replace deprecated `apt-key adv` with signed keyring**~~ ✅ — Ubiquiti repo key now fetched via `curl | gpg --dearmor` into `/etc/apt/trusted.gpg.d/ubiquiti.gpg`.
- ~~**Automate UniFi version updates**~~ ✅ — Implemented via `.github/workflows/update.yml` and `.github/scripts/unifi-updater.py`, which poll the UniFi RSS feed daily and open a PR automatically when a new stable version is released.
- ~~**Sign released images with cosign**~~ ✅ — Keyless cosign signing via Sigstore/Fulcio on every push to `main`.
- ~~**Add log rotation for `/unifi/log/`**~~ ✅ — `logrotate` runs daily via an init.d script. Config: daily rotation, 7-day retention, compressed, `copytruncate` (safe for Java open file descriptors). State file persisted at `/unifi/log/.logrotate.state`.

### 🟢 Low priority

- ~~**Add memory limits in docker-compose**~~ ✅ — `mem_limit: 2g` on the controller, `mem_limit: 512m` on MongoDB.
- ~~**Add `depends_on` healthcheck for MongoDB**~~ ✅ — MongoDB healthcheck with `db.adminCommand('ping')`, controller uses `condition: service_healthy`.
- ~~**Improve healthcheck to use UniFi API**~~ ✅ — Healthcheck now hits `/status` and checks for `"up":true`.
- ~~**Document `./backup` directory permissions**~~ ✅ — Entrypoint creates the directory automatically with correct permissions. See [Backup and Restore](#-backup-and-restore) above.
- ~~**Add `.env.example` file**~~ ✅ — Copy `.env.example` to `.env` and uncomment the variables you need.
- ~~**Add SBOM generation**~~ ✅ — `syft` generates an SPDX-JSON SBOM on every publish, attached to the image via `cosign attach sbom`.
- **Document MongoDB authentication** — The mongo container runs without credentials. Isolated on an internal Docker network, but adding `MONGO_INITDB_ROOT_USERNAME/PASSWORD` and updating `DB_URI` would harden deployments exposed beyond localhost.

For other suggestions, please [open an issue](https://github.com/jsoyer/unifi-network-server/issues).
