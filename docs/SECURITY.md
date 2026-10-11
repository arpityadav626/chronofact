# CHRONOFACT Security Guide

## Security Architecture

### Phase 0: Safety Patches
- **Fail-closed**: Missing/corrupted evidence returns error, never sample data
- **Operator authentication**: All API endpoints require valid credentials
- **No default credentials**: Must configure CHRONOFACT_USER and CHRONOFACT_PASSWORD
- **Restricted filenames**: Only alphanumeric, dots, hyphens (no path traversal)
- **No demo/reset endpoints**: Removed `/api/load-sample` and `/api/reset`

### Phase 1: Vault Encryption
- **Algorithm**: AES-256-GCM (NIST FIPS 197)
- **Key size**: 32 bytes (256 bits)
- **Key management**: Base64-encoded, stored in environment variable
- **Nonces**: 12-byte random nonce per file
- **Associated data**: Evidence ID (prevents tampering)

### Phase 2: Artifact Parsers
- **Read-only**: No writes to original evidence files
- **Memory-based**: SQLite parsed in-memory (no temp files)
- **Limits**: Max 2000 records per parse, 4000 char text fields
- **Input validation**: Extension and header checks before parsing

### Phase 3-4: External Tool Wrappers
- **Pre/post hashing**: Hash verification before and after tool execution
- **No symlink execution**: Refuses symlinks as input paths
- **Command allowlisting**: Fixed plugin lists for Volatility
- **Timeout enforcement**: Hard timeout per command (6h for disk, 2h for memory)

### Phase 5: Report Export
- **Read-only database**: Opens SQLite with `?mode=ro` flag
- **Input hashing**: All input manifests hashed for audit trail
- **No automatic verification**: Exports note that quotations are not verified

---

## Key Management

### Vault Key (Critical!)
```powershell
# Generate new vault key
python -c "import base64,secrets; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"
```

**Storage:**
1. Save to encrypted file: `C:\backup\vault-key.txt`
2. Protect with Windows BitLocker or similar
3. NEVER commit to Git
4. Store separate from database backups

**If lost:**
- All encrypted evidence becomes unrecoverable
- System cannot decrypt or export evidence

### Audit Key
```powershell
# Generate audit key (must be 32+ characters)
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

**Purpose:** Creates hash-chained audit log
**Storage:** Same as vault key (encrypted, separate from database)

### Password
```powershell
# Generate secure password (16+ characters)
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Storage:** Environment variable `CHRONOFACT_PASSWORD`

---

## Configuration Checklist

| Variable | Required | Min Length | Notes |
|----------|----------|------------|-------|
| CHRONOFACT_USER | Yes | 3 chars | Username |
| CHRONOFACT_PASSWORD | Yes | 16 chars | Operator password |
| CHRONOFACT_AUDIT_KEY | Yes | 32 chars | Audit log HMAC key |
| CHRONOFACT_VAULT_KEY_B64 | Yes | 32 bytes | AES-256-GCM key |
| CHRONOFACT_DATA_DIR | Yes | - | Storage path |

**Generate all keys with:**
```powershell
$env:CHRONOFACT_USER = "examiner"
$env:CHRONOFACT_PASSWORD = (python -c "import secrets; print(secrets.token_urlsafe(32))")
$env:CHRONOFACT_AUDIT_KEY = (python -c "import secrets; print(secrets.token_urlsafe(48))")
$env:CHRONOFACT_VAULT_KEY_B64 = (python -c "import base64,secrets; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())")
```

---

## Security Limitations

### Not Protected By This System
1. **Host security**: If admin controls host, can bypass all protections
2. **Key compromise**: Vault key protects only at rest
3. **Physical access**: Does not enforce write-blocking
4. **Legal validity**: Does not establish provenance independently
5. **Trusted timestamps**: Does not provide certified timestamps

### Recommendations
1. **Run on isolated host**: Dedicated forensic workstation
2. **Full disk encryption**: BitLocker or VeraCrypt on vault volume
3. **Separate keys**: Store vault key on separate encrypted media
4. **Regular backups**: Test restoration of database AND vault key
5. **Network isolation**: Keep server on loopback (127.0.0.1)

---

## Incident Response

### Suspected Vault Key Exposure
1. **Revoke**: Generate new vault key
2. **Re-encrypt**: Decrypt and re-encrypt all evidence with new key
3. **Audit**: Check audit log for unauthorized access
4. **Document**: Record incident in case notes

### Integrity Failure Detected
```powershell
curl -u examiner:SecurePassMin16Chars! http://127.0.0.1:8007/api/integrity/verify
```

If `valid=false`:
1. Check `audit_issues` vs `evidence_issues`
2. For `file_missing`: Evidence may have been moved/deleted
3. For hash mismatches: Evidence may have been modified
4. Document findings in case notes

---

## Compliance Notes

### Not Sufficient For
- Court admissibility without external validation
- Independent chain-of-custody certification
- Trusted timestamping
- Multi-user role-based access control

### Does Provide
- Cryptographic evidence integrity
- Audit trail with hash chain
- Encrypted at-rest storage
- Operator authentication

---

**Version**: 2.0.0 | **Date**: 2026-10-11
