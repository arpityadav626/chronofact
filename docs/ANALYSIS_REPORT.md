# ChronoFact – Analysis & v2 changes

## Bugs found in the uploaded version (all fixed in v2 unless marked OPEN)
**Security**
1. Auth was cosmetic: no route used `get_current_user`; `/api/upload`, `/api/reset` etc. were open to anyone. Security-header + rate-limit middleware were defined but never registered.
2. `login.html` checked passwords in the browser (visible in page source) and invented a fake "jwt-token-evaluator-…" token.
3. Hard-coded accounts (`SecurePassMin16Chars!`, `ChronoFact2026!`) and JWT secret fallback `CHANGE_THIS_IN_PRODUCTION`; login endpoint excluded from rate limiting; CORS `*` + credentials.
4. Path traversal: client filename joined into the vault path. No upload size limit. `uploaded_by` was client-supplied (spoofable audit actor).
5. `/inspect` fabricated file bytes when the exhibit was missing. `/api/reset` deleted audit-log rows (contradicts "immutable").
6. AES-GCM vault exists but is never used (files stored in plaintext) – **OPEN**. README claims it.
**Correctness**
7. Merkle: no leaf/node domain separation (second-preimage), odd-node duplication, false "RFC 6962" claim.
8. Audit genesis row stored `0` (SQL `'0'*64` is arithmetic); concurrent writes could fork the chain.
9. Alibi rule used the *earliest possible* chat time (14 h early) so the sample contradiction was never detected; window also started 30 min *before* the statement. Sample logs were labelled `Z` while chat/email are IST. Geographic rule had the same time bug.
10. CDR sample was parsed to `Unknown,,,` (all telecom fields lost). CDR facts still do not feed the geo rule – **OPEN**.
11. RAG: new empty engine per request → `/api/rag/*` always returned nothing, yet reported "sentence-transformers". FTS query could error silently.
12. Circular import `ml_model` ↔ `training_pipeline` (worked only by import order). requirements.txt missed PyJWT/jose/passlib/bcrypt/dotenv/cryptography; Dockerfile installed the wrong file.
13. Offline upload showed **random hex as the SHA-256**.
**Claims to remove/soften (docs fixed; slides/PDF/pptx you must edit)**
"0% hallucination guarantee", "100% court-admissible", "100% air-gapped" (pages load CDNs), "Round 2 Finalist" (only if true), README velocity 500 vs code 800 km/h, model card says §45 (BSA expert opinion is §39), model card numbers/CV method don't match metrics.json (ROC-AUC 1.0 on synthetic data = easy generator), IsolationForest `contamination=0.2` flags 20% by construction, Windows path `C:\Users\Arpit Yadav\…` leaked in metrics.json (scrubbed).
**Demo-day risk (OPEN):** speaker notes tell a 23:14 IST / Noida / tower story that the sample data does not contain; demo PDFs/pptx unchanged. Four demo cases in app.js use obviously fake Merkle roots (`d4e5f6a1b2c3…`).

## How it was verified
- Existing tests: 13/13 pass (+1 skipped only by my shim). New `tests/test_security_and_fixes.py`: 25/25 pass.
- Merkle proofs checked for every leaf, n = 1..40.
- ~45 end-to-end checks of main.py logic (auth, lockout, traversal, tamper, audit forgery, reset…) passed **using a stand-in for FastAPI** because the sandbox has no FastAPI/network. **Run `pip install -r requirements-dev.txt && pytest` and start `python run.py` once on your machine** before demo day; the HTML/JS edits were only syntax-checked, not browser-tested.
