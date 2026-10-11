from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path


CHUNK_SIZE = 4 * 1024 * 1024

# Fixed allowlist: the CLI cannot be used to invoke arbitrary Volatility plugins.
DEFAULT_PLUGINS = [
    "windows.info",
    "windows.pslist",
    "windows.pstree",
    "windows.cmdline",
    "windows.netscan",
    "windows.dlllist",
    "windows.filescan",
    "windows.registry.hivelist",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00", "Z"
    )


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


def checked_text(value: str, field: str) -> str:
    value = value.strip()
    if not value or len(value) > 200 or any(ord(char) < 32 for char in value):
        raise ValueError(f"{field} must be 1–200 printable characters.")
    return value


def resolve_image(path_text: str) -> Path:
    candidate = Path(path_text).expanduser()
    if candidate.is_symlink():
        raise ValueError("Refusing a symlink as the memory-image path.")
    path = candidate.resolve(strict=True)
    if not path.is_file():
        raise ValueError("Memory-image path is not a regular file.")
    return path


def find_volatility(bin_dir: str | None) -> str:
    names = ["vol.exe", "vol"] if os.name == "nt" else ["vol"]
    for name in names:
        # Try provided directory first
        if bin_dir:
            found = shutil.which(name, path=bin_dir)
            if found:
                return str(Path(found).resolve())
        
        # Try PATH
        found = shutil.which(name)
        if found:
            return str(found)
        
        # Try common Windows Volatility paths
        for base in [
            r"C:\Program Files\volatility3",
            r"C:\Users\antriksh\Downloads\volatility3",
            r"C:\Users\antriksh\Downloads\volatility3-win-exes-2.28.2",
        ]:
            found = shutil.which(name, path=base)
            if found:
                return str(Path(found).resolve())
    
    raise FileNotFoundError(
        "Could not find Volatility 3 command 'vol'/'vol.exe'. "
        "Install it using the official project instructions and ensure it is on PATH, "
        "or pass --vol-bin pointing to the directory containing vol.exe."
    )


def unique_run_dir(root_text: str) -> Path:
    root = Path(root_text).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    output = root / (
        f"memory-run-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"
    )
    output.mkdir(parents=False, exist_ok=False)
    return output


def run_plugin(
    executable: str,
    image: Path,
    output_dir: Path,
    plugin: str,
    allow_symbol_download: bool,
    timeout_seconds: int,
) -> dict:
    plugin_dir = output_dir / plugin.replace(".", "_")
    plugin_dir.mkdir(parents=False, exist_ok=False)

    cache_dir = output_dir / "volatility-cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    command = [executable, "--cache-path", str(cache_dir)]
    if not allow_symbol_download:
        command.append("--offline")

    command.extend(
        [
            "-f",
            str(image),
            "-o",
            str(plugin_dir),
            plugin,
        ]
    )

    stdout_path = plugin_dir / "stdout.txt"
    stderr_path = plugin_dir / "stderr.txt"
    started_at = utc_now()
    timer = time.monotonic()
    timed_out = False
    return_code = None

    try:
        with stdout_path.open("wb") as stdout_file, stderr_path.open("wb") as stderr_file:
            result = subprocess.run(
                command,
                shell=False,
                stdout=stdout_file,
                stderr=stderr_file,
                timeout=timeout_seconds,
                check=False,
            )
            return_code = result.returncode
    except subprocess.TimeoutExpired:
        timed_out = True
    finally:
        if not stdout_path.exists():
            stdout_path.write_bytes(b"")
        if not stderr_path.exists():
            stderr_path.write_bytes(b"")

    return {
        "plugin": plugin,
        "command": command,
        "started_at_utc": started_at,
        "duration_seconds": round(time.monotonic() - timer, 3),
        "return_code": return_code,
        "timed_out": timed_out,
        "stdout": {
            "file": str(stdout_path.relative_to(output_dir)),
            **hash_file(stdout_path),
        },
        "stderr": {
            "file": str(stderr_path.relative_to(output_dir)),
            **hash_file(stderr_path),
        },
        "status": (
            "timeout"
            if timed_out
            else "completed"
            if return_code == 0
            else "plugin_error"
        ),
    }


def write_manifest(output_dir: Path, manifest: dict) -> None:
    path = output_dir / "manifest.json"
    path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    (output_dir / "manifest.json.sha256").write_text(
        f"{digest}  manifest.json\n", encoding="ascii"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run an allowlisted Volatility 3 plugin set on a memory image."
    )
    parser.add_argument("--memory-image", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--examiner", required=True)
    parser.add_argument("--acquisition-reference", required=True)
    parser.add_argument(
        "--acquisition-note",
        required=True,
        help="Operator-provided acquisition note; not independently verified.",
    )
    parser.add_argument("--vol-bin", default=None)
    parser.add_argument("--timeout-seconds", type=int, default=7200)
    parser.add_argument(
        "--allow-symbol-download",
        action="store_true",
        help=(
            "Allow Volatility to use its online symbol mechanisms. "
            "Default is offline and may produce incomplete analysis."
        ),
    )
    parser.add_argument(
        "--plugins",
        nargs="+",
        choices=DEFAULT_PLUGINS,
        default=DEFAULT_PLUGINS,
        help="Select from the fixed allowlist.",
    )
    args = parser.parse_args()

    if args.timeout_seconds <= 0:
        parser.error("--timeout-seconds must be positive.")

    image = resolve_image(args.memory_image)
    case_id = checked_text(args.case_id, "case-id")
    examiner = checked_text(args.examiner, "examiner")
    acquisition_reference = checked_text(
        args.acquisition_reference, "acquisition-reference"
    )
    acquisition_note = checked_text(args.acquisition_note, "acquisition-note")

    output_dir = unique_run_dir(args.output_root)
    manifest = {
        "schema": "chronofact-phase4-memory-run-v1",
        "created_at_utc": utc_now(),
        "status": "started",
        "case_id": case_id,
        "examiner": examiner,
        "acquisition_reference": acquisition_reference,
        "acquisition_note": acquisition_note,
        "acquisition_note_is_verified": False,
        "memory_image": str(image),
        "memory_image_hash_before": hash_file(image),
        "memory_image_stat_before": {
            "size": image.stat().st_size,
            "mtime_ns": image.stat().st_mtime_ns,
        },
        "offline_mode": not args.allow_symbol_download,
        "symbol_download_warning": (
            "Online symbol resolution was explicitly enabled."
            if args.allow_symbol_download
            else "Offline mode: plugins may fail if required symbols are unavailable."
        ),
        "outputs": [],
        "notes": [
            "This program analyzes an existing memory image; it does not acquire RAM.",
            "Plugin output is raw tool output, not an examiner conclusion.",
            "Manifest checksum is local and is not a digital signature or trusted timestamp.",
        ],
    }

    exit_code = 0
    try:
        executable = find_volatility(args.vol_bin)
        manifest["volatility_executable"] = executable

        for plugin in args.plugins:
            result = run_plugin(
                executable=executable,
                image=image,
                output_dir=output_dir,
                plugin=plugin,
                allow_symbol_download=args.allow_symbol_download,
                timeout_seconds=args.timeout_seconds,
            )
            manifest["outputs"].append(result)
            if result["status"] != "completed":
                exit_code = 2

        manifest["status"] = (
            "completed" if exit_code == 0 else "completed_with_plugin_errors"
        )

    except Exception as exc:
        manifest["status"] = "failed"
        manifest["error_type"] = type(exc).__name__
        manifest["error_message"] = str(exc)[:1000]
        exit_code = 1

    finally:
        try:
            after = hash_file(image)
            manifest["memory_image_hash_after"] = after
            manifest["memory_image_changed"] = (
                manifest["memory_image_hash_before"] != after
            )
            manifest["memory_image_stat_after"] = {
                "size": image.stat().st_size,
                "mtime_ns": image.stat().st_mtime_ns,
            }
            if manifest["memory_image_changed"]:
                manifest["status"] = "failed_memory_image_changed"
                exit_code = 3
        except Exception as exc:
            manifest["memory_image_postcheck_error"] = type(exc).__name__
            manifest["status"] = "failed_postcheck"
            exit_code = 4

        write_manifest(output_dir, manifest)

    print(f"Run directory: {output_dir}")
    print(f"Status: {manifest['status']}")
    print(f"Manifest: {output_dir / 'manifest.json'}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())