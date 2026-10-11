from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path


ALLOWED_RAW_SUFFIXES = {".dd", ".img", ".raw"}
CHUNK_SIZE = 4 * 1024 * 1024


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00", "Z"
    )


def validate_case_text(value: str, field: str) -> str:
    value = value.strip()
    if not value or len(value) > 160 or any(ord(ch) < 32 for ch in value):
        raise ValueError(f"{field} must be 1–160 printable characters.")
    return value


def resolve_raw_image(path_text: str) -> Path:
    candidate = Path(path_text).expanduser()

    if candidate.is_symlink():
        raise ValueError("Refusing a symlink as the image path.")
    path = candidate.resolve(strict=True)

    if not path.is_file():
        raise ValueError("Image path is not a regular file.")
    if path.suffix.lower() not in ALLOWED_RAW_SUFFIXES:
        raise ValueError(
            f"Only single-file raw images are accepted: {sorted(ALLOWED_RAW_SUFFIXES)}. "
            "E01, split images, and physical devices are not supported."
        )
    return path


def hash_file(path: Path) -> dict:
    sha256 = hashlib.sha256()
    sha3 = hashlib.sha3_256()
    size = 0

    with path.open("rb") as stream:
        while True:
            chunk = stream.read(CHUNK_SIZE)
            if not chunk:
                break
            size += len(chunk)
            sha256.update(chunk)
            sha3.update(chunk)

    return {
        "bytes": size,
        "sha256": sha256.hexdigest(),
        "sha3_256": sha3.hexdigest(),
    }


def resolve_tool(name: str, bin_dir: str | None) -> str:
    # Try provided directory first, then PATH, then Windows-specific locations
    if bin_dir:
        found = shutil.which(name, path=bin_dir)
        if found:
            return str(Path(found).resolve())
    
    # Try PATH
    found = shutil.which(name)
    if found:
        return str(Path(found).resolve())
    
    # Try common Windows Sleuth Kit paths
    for base in [
        r"C:\Program Files\Sleuth Kit\bin",
        r"C:\Users\antriksh\Downloads\sleuthkit-4.14.0-win32\sleuthkit-4.14.0-win32\bin",
    ]:
        found = shutil.which(name, path=base)
        if found:
            return str(Path(found).resolve())
    
    raise FileNotFoundError(
        f"Could not find {name!r}. Install The Sleuth Kit and add its bin "
        "directory to PATH, or pass --tsk-bin."
    )


def run_command(
    command: list[str],
    output_dir: Path,
    label: str,
    timeout_seconds: int,
) -> dict:
    started = utc_now()
    start_clock = time.monotonic()

    try:
        result = subprocess.run(
            command,
            cwd=str(output_dir),
            shell=False,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
        )
        stdout = result.stdout or ""
        stderr = result.stderr or ""
        return_code = result.returncode
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        return_code = None
        timed_out = True

    (output_dir / f"{label}.stdout.txt").write_text(
        stdout, encoding="utf-8", errors="replace"
    )
    (output_dir / f"{label}.stderr.txt").write_text(
        stderr, encoding="utf-8", errors="replace"
    )

    return {
        "label": label,
        "command": command,
        "started_at": started,
        "duration_seconds": round(time.monotonic() - start_clock, 3),
        "return_code": return_code,
        "timed_out": timed_out,
        "stdout_file": f"{label}.stdout.txt",
        "stderr_file": f"{label}.stderr.txt",
    }


def write_manifest(output_dir: Path, manifest: dict) -> None:
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    digest = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    (output_dir / "manifest.json.sha256").write_text(
        f"{digest}  manifest.json\n",
        encoding="ascii",
    )


def hash_recovered_files(recovery_dir: Path, output_dir: Path) -> int:
    manifest_path = output_dir / "recovered_files.jsonl"
    count = 0

    with manifest_path.open("w", encoding="utf-8") as manifest:
        for path in sorted(recovery_dir.rglob("*")):
            if path.is_symlink():
                continue
            if not path.is_file():
                continue

            record = {
                "relative_path": str(path.relative_to(recovery_dir)),
                **hash_file(path),
            }
            manifest.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1

    return count


def base_manifest(args, image_path: Path, pre_hash: dict) -> dict:
    return {
        "schema": "chronofact-phase3-disk-run-v1",
        "created_at_utc": utc_now(),
        "status": "started",
        "case_id": args.case_id,
        "examiner": args.examiner,
        "source_image": str(image_path),
        "source_image_hash_before": pre_hash,
        "acquisition_reference": args.acquisition_reference,
        "write_blocker_statement": args.write_blocker_statement,
        "write_blocker_statement_note": (
            "Operator-provided statement only; this program cannot detect or "
            "validate whether a write blocker was used."
        ),
        "image_format": "raw",
        "tools": [],
        "notes": [
            "Analysis is performed on a previously acquired image, not a source device.",
            "The image is re-hashed after tool execution.",
            "This manifest hash is a local checksum, not an external signature "
            "or trusted timestamp.",
        ],
    }


def create_output_dir(root_text: str) -> Path:
    root = Path(root_text).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)

    run_dir = root / f"disk-run-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"
    run_dir.mkdir(parents=False, exist_ok=False)
    return run_dir


def execute(args) -> int:
    case_id = validate_case_text(args.case_id, "case_id")
    examiner = validate_case_text(args.examiner, "examiner")
    acquisition_reference = validate_case_text(
        args.acquisition_reference, "acquisition_reference"
    )
    write_blocker_statement = validate_case_text(
        args.write_blocker_statement, "write_blocker_statement"
    )

    image_path = resolve_raw_image(args.image)
    pre_hash = hash_file(image_path)
    output_dir = create_output_dir(args.output_root)

    manifest = base_manifest(args, image_path, pre_hash)
    manifest["case_id"] = case_id
    manifest["examiner"] = examiner
    manifest["acquisition_reference"] = acquisition_reference
    manifest["write_blocker_statement"] = write_blocker_statement
    manifest["output_directory"] = str(output_dir)
    manifest["source_image_stat_before"] = {
        "size": image_path.stat().st_size,
        "mtime_ns": image_path.stat().st_mtime_ns,
    }

    try:
        mmls = resolve_tool("mmls.exe" if os.name == "nt" else "mmls", args.tsk_bin)
        recover = resolve_tool(
            "tsk_recover.exe" if os.name == "nt" else "tsk_recover",
            args.tsk_bin,
        )

        version_mmls = run_command(
            [mmls, "-V"], output_dir, "mmls_version", args.timeout_seconds
        )
        version_recover = run_command(
            [recover, "-V"], output_dir, "tsk_recover_version",
            args.timeout_seconds
        )
        manifest["tools"].extend([version_mmls, version_recover])

        layout_command = [mmls, "-i", "raw", "-B", str(image_path)]
        layout_result = run_command(
            layout_command, output_dir, "partition_layout", args.timeout_seconds
        )
        manifest["tools"].append(layout_result)

        if layout_result["return_code"] != 0 or layout_result["timed_out"]:
            manifest["status"] = "failed_partition_listing"
            return 2

        if args.mode == "recover":
            recovery_dir = output_dir / "recovered"
            if recovery_dir.exists():
                raise FileExistsError("Recovery output directory already exists.")

            command = [recover, "-i", "raw"]
            if args.include_allocated:
                command.append("-e")
            command.extend(["-o", str(args.offset_sectors)])
            command.extend([str(image_path), str(recovery_dir)])

            recovery_result = run_command(
                command, output_dir, "tsk_recover", args.timeout_seconds
            )
            manifest["tools"].append(recovery_result)
            manifest["recovery"] = {
                "offset_sectors": args.offset_sectors,
                "includes_allocated_and_unallocated": bool(args.include_allocated),
                "output_directory": str(recovery_dir),
            }

            if recovery_result["return_code"] != 0 or recovery_result["timed_out"]:
                manifest["status"] = "failed_recovery"
                return 3

            if not recovery_dir.is_dir():
                manifest["status"] = "failed_no_recovery_directory"
                return 4

            manifest["recovered_file_count"] = hash_recovered_files(
                recovery_dir, output_dir
            )

        post_hash = hash_file(image_path)
        manifest["source_image_hash_after"] = post_hash
        manifest["source_image_stat_after"] = {
            "size": image_path.stat().st_size,
            "mtime_ns": image_path.stat().st_mtime_ns,
        }

        if pre_hash != post_hash:
            manifest["status"] = "failed_source_image_changed"
            return_code = 5
        else:
            manifest["status"] = "completed"
            return_code = 0

        return return_code

    except Exception as exc:
        manifest["status"] = "failed"
        manifest["error_type"] = type(exc).__name__
        manifest["error_message"] = str(exc)[:1000]
        return_code = 10
        return return_code

    finally:
        try:
            post_hash = hash_file(image_path)
            manifest.setdefault("source_image_hash_after", post_hash)
            manifest["source_image_changed"] = (
                manifest["source_image_hash_before"] != post_hash
            )
        except Exception as exc:
            manifest["source_image_postcheck_error"] = type(exc).__name__

        write_manifest(output_dir, manifest)
        print(f"Run directory: {output_dir}")
        print(f"Status: {manifest['status']}")
        print(f"Manifest: {output_dir / 'manifest.json'}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read-only wrapper for The Sleuth Kit on a raw disk image."
    )
    parser.add_argument("--image", required=True, help="Single-file raw image path.")
    parser.add_argument("--output-root", required=True, help="Protected output root.")
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--examiner", required=True)
    parser.add_argument("--acquisition-reference", required=True)
    parser.add_argument(
        "--write-blocker-statement",
        required=True,
        help="Operator note only; this is not verified by the program.",
    )
    parser.add_argument(
        "--tsk-bin",
        default=None,
        help="Optional directory containing mmls and tsk_recover.",
    )
    parser.add_argument(
        "--timeout-seconds", type=int, default=21600,
        help="Per-command timeout; default is six hours.",
    )

    modes = parser.add_subparsers(dest="mode", required=True)

    modes.add_parser("inspect", help="List the partition layout only.")

    recover = modes.add_parser(
        "recover",
        help="Recover unallocated files from the selected partition offset.",
    )
    recover.add_argument(
        "--offset-sectors",
        type=int,
        required=True,
        help="Partition start sector selected by the examiner from mmls output.",
    )
    recover.add_argument(
        "--include-allocated",
        action="store_true",
        help="Pass -e to recover allocated and unallocated files.",
    )
    return parser


if __name__ == "__main__":
    args = build_parser().parse_args()
    if args.timeout_seconds <= 0:
        print("timeout-seconds must be positive.", file=sys.stderr)
        raise SystemExit(2)
    if args.mode == "recover" and args.offset_sectors < 0:
        print("offset-sectors must be non-negative.", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(execute(args))