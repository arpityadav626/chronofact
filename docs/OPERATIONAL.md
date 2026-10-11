# CHRONOFACT Operational Guide

## Real-Life Deployment Checklist

### Pre-Deployment

- [ ] **Hardware Write-Blockers**: Acquire and test forensic write-blockers
- [ ] **Physical Security**: Dedicated forensic workstation in secure location
- [ ] **Legal Review**: Agency counsel approves workflow and certificate templates
- [ ] **Key Management**: Vault key stored on encrypted removable media
- [ ] **Backup Plan**: Database AND vault key backed up separately

### Training & Validation

- [ ] **Model Training**: Train Phase 6 model on agency-authorized data
- [ ] **False Positive Review**: Document benign explanations for all flags
- [ ] **False Negative Analysis**: Review missed events
- [ ] **Validation Testing**: Independent examiner reviews flagged events

### Operational Use

- [ ] **Documentation**: Standard operating procedures documented
- [ ] **Chain of Custody**: Physical custody records separate from software
- [ ] **Examiner Review**: All findings manually reviewed before reporting
- [ ] **Audit Trail**: Preserve audit keys separately from evidence

---

## Data Preparation (Phase 6)

### Labeling Guidelines

| Label | Meaning | When to Use |
|-------|---------|-------------|
| 1 | Confirmed target event | Evidence adjudicated as malicious/data exfiltration |
| 0 | Confirmed benign event | Evidence adjudicated as legitimate/authorized |

**Do NOT use:**
- Unknown status (must review and decide)
- Unlabeled data (must review all events)

### Training Data Requirements

```csv
event_id,scenario_id,timestamp,source,action,bytes,label
E001,SCENARIO-A,2026-10-01T09:00:00Z,logon,login,0,0
E002,SCENARIO-A,2026-10-01T09:05:00Z,file,download,2048,0
E003,SCENARIO-B,2026-10-02T21:00:00Z,http,upload,9500000,1
E004,SCENARIO-B,2026-10-02T21:05:00Z,http,upload,9200000,1
```

**Requirements:**
- **Grouped split**: `scenario_id` prevents leakage (entire scenario in train OR test)
- **Minimum groups**: 4 distinct scenarios for valid training
- **Both labels**: Training data must contain both label=0 and label=1
- **Timezone**: All timestamps must include offset (e.g., `+00:00`, `+05:30`, `Z`)

### Evaluation

```powershell
python phase6_ml.py train ^
  --input "./training.csv" ^
  --output-root "./model-runs" ^
  --group-column "scenario_id" ^
  --label-column "label" ^
  --positive-label-definition "Adjudicated data exfiltration events"
```

**Output metrics:**
- Precision: True positives / all positive predictions
- Recall: True positives / all actual positives
- Average Precision: Area under precision-recall curve
- Confusion matrix: TP, FP, TN, FN counts

---

## Operational Limitations

### What CHRONOFACT Does NOT Do

1. **Evidence Acquisition**
   - Does not acquire from physical devices
   - Does not enforce write-blocking
   - Requires separate acquisition workflow

2. **Chain of Custody**
   - Records receipt but not physical custody
   - Does not generate BSA §63(4) certificates
   - Legal review required for statutory compliance

3. **Full Forensic Analysis**
   - SQLite parser does not decrypt SQLCipher
   - Generic Registry parser (no ShellBags/UserAssist)
   - Chat/email parsers limited to basic formats

4. **Model Validation**
   - Performance on synthetic data does not establish real accuracy
   - Requires operational validation with agency data
   - Requires independent examiner review

### Required External Validation

| Component | Validation Required |
|-----------|---------------------|
| ML Model | False positive/negative analysis on agency data |
| Parsers | Tested against known-good test fixtures |
| Acquisition | Validated with hardware write-blockers |
| Certificate | Legal review per BSA §63(4) |

---

## Reporting Requirements

### Case Documentation

Must include:
- Evidence acquisition details (who, when, where, how)
- Tools used (with version numbers)
- Hash values (SHA-256, SHA-3-256)
- Custody chain (physical, separate from software)
- Examiner findings (with benign explanations)
- Model scores (with "NOT probability of guilt" warning)

### Certificate Notes

**Do NOT use CHRONOFACT to generate BSA §63(4) certificates.**

This system does:
- Hash verification
- Custody event recording
- Audit trail

But **NOT**:
- Legal declaration of device operation
- Independent acquisition verification
- Court-ready statutory certificate

---

## Deployment Checklist

### Phase 0: Security
- [ ] Operator credentials configured
- [ ] Default/demo endpoints removed
- [ ] Fail-closed behavior tested

### Phase 1: Vault
- [ ] Vault key generated and backed up
- [ ] Key stored separately from database
- [ ] Full disk encryption enabled

### Phase 2: Parsers
- [ ] Parsers tested on known-good files
- [ ] Input validation working
- [ ] Record limits enforced

### Phase 3: Disk
- [ ] Sleuth Kit installed and tested
- [ ] Image hashes verified before/after
- [ ] Write-blocker statement recorded

### Phase 4: Memory
- [ ] Volatility 3 installed and tested
- [ ] Plugin allowlist reviewed
- [ ] Symbol download policy defined

### Phase 5: Reports
- [ ] Report template reviewed
- [ ] Exhibits hash-verified in report
- [ ] Benign explanations included

### Phase 6: ML
- [ ] Training data labeled by examiner
- [ ] Grouped holdout verified
- [ ] Operational validation completed

---

## Maintenance

### Weekly
- [ ] Verify vault integrity
- [ ] Check audit log for anomalies
- [ ] Review failed authentication attempts

### Monthly
- [ ] Restore test from backups
- [ ] Test key recovery procedures
- [ ] Review new CVEs for dependencies

### Quarterly
- [ ] Review and rotate vault key (requires re-encryption)
- [ ] Update dependencies
- [ ] Training data refresh

---

**Version**: 2.0.0 | **Date**: 2026-10-11
