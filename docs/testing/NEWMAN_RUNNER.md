# Newman Runner

Docker Newman is the canonical runner for this repository.

Host `newman.cmd` is optional and is not required for backend correctness. The
host wrapper may use it when explicitly requested, but the default runner is:

```powershell
.\scripts\ci\run_newman_docker.ps1
```

## Image

The Docker runner uses a version-pinned image tag:

```text
postman/newman:6.1.3
```

The current tag resolves to digest
`sha256:d9b5e780ead0026bbb37f3759cd7b10fc8a88cd4030c8266a7c5e343d75a5198`.
If CI upgrades Newman, update this document and the runner intentionally after
verifying the replacement version locally.

## Mount Policy

- Postman collection is mounted read-only.
- Postman environment is mounted read-only.
- Reports are written only under `tests/postman/reports/`.
- Reports are ignored by Git except `.gitkeep`.

## No External Providers

The local collection uses fake-provider flows only. It must not call Daraja,
email providers, or production storage.
