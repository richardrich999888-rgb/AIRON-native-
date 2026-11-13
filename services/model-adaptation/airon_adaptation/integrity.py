"""Data-only artifact import and canonical signed-record encoding."""
import hashlib
import json
import os
import stat
from pathlib import Path


class Rejected(ValueError):
    pass


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                      allow_nan=False).encode("ascii")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def file_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_path(root, relative, *, exists=True):
    root = Path(root).absolute()
    if not isinstance(relative, (str, Path)):
        raise Rejected("Invalid path")
    rel = Path(relative)
    if rel.is_absolute() or not rel.parts or ".." in rel.parts:
        raise Rejected("Relative contained path required")
    for parent in [*root.parents, root]:
        if parent.is_symlink():
            raise Rejected("Symlink root")
    current = root
    for part in rel.parts:
        current = current / part
        if current.is_symlink():
            raise Rejected("Symlink path")
    if os.path.commonpath([os.path.realpath(root), os.path.realpath(current)]) != str(root):
        raise Rejected("Path outside root")
    if exists and not current.exists():
        raise Rejected("Missing local artifact")
    return current


def manifest(root, *, model=False):
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise Rejected("Artifact must be a real directory")
    safe_path(root.parent, root.name)
    result = {}
    total = 0
    for p in sorted(root.rglob("*")):
        mode = p.lstat().st_mode
        if stat.S_ISLNK(mode) or not (stat.S_ISREG(mode) or stat.S_ISDIR(mode)):
            raise Rejected("Links and special files forbidden")
        if p.is_dir():
            continue
        if p.stat().st_nlink != 1:
            raise Rejected("Hard links forbidden")
        name = p.relative_to(root).as_posix()
        if model and (p.suffix not in {".json", ".safetensors", ".txt", ".model", ".md"}
                      or any(part.startswith(".") for part in p.relative_to(root).parts)):
            raise Rejected("Only data-only model files are accepted")
        if model and p.suffix == ".json":
            if p.stat().st_size > 32 * 1024 * 1024:
                raise Rejected("Metadata too large")
            value = json.loads(p.read_text())
            if isinstance(value, dict) and (value.get("auto_map") or value.get("custom_pipelines")):
                raise Rejected("Custom model code forbidden")
        total += p.stat().st_size
        if total > 2 * 1024**3 or len(result) >= 10000:
            raise Rejected("Artifact limit exceeded")
        result[name] = {"sha256": file_hash(p), "bytes": p.stat().st_size}
    if not result or (model and not any(n.endswith(".safetensors") for n in result)):
        raise Rejected("Nonempty safetensors model required" if model else "Empty artifact")
    return result


def verify_tree(path, expected, *, model=False):
    if manifest(path, model=model) != expected:
        raise Rejected("Artifact integrity mismatch")


def write_json(path, value):
    path = Path(path)
    temp = path.with_name(path.name + ".new")
    fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(canonical(value))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
        dfd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    finally:
        temp.unlink(missing_ok=True)
