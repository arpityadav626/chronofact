# Changelog

## 2.0.0 (this hardening release)
- Auth enforced on every API route; removed hard-coded accounts/JWT secret; scrypt hashes; login lockout; PyJWT.
- Security headers + rate limiting actually registered; CORS no longer `*` with credentials.
- Upload: filename sanitisation, path confinement, size limit, no orphan files, authenticated uploader recorded.
- Audit log: genesis hash bug fixed (SQL `'0'*64` was numeric), transactional appends, append-only triggers, `/api/audit/verify`.
- Merkle tree: domain separation + odd-node promotion (RFC 6962 style); inclusion proofs re-verified for n=1..40.
- Alibi rule: assumed-timezone reference instant, forward-looking window (was missing the sample contradiction entirely).
- CDR parser keeps telecom fields; RAG endpoints share one engine and verify hits verbatim; FTS input escaped.
- Removed fabricated fallback bytes in `/inspect`; offline UI hashes with real SHA-256; login no longer trusts client-side passwords.
- Fixed ml_model <-> training_pipeline circular import; one consolidated requirements.txt; hardened Docker.
