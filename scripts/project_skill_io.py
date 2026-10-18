"""Local AGENTS transactions. No network, installs, or implicit authorization.

The lock serializes these tools; unrelated editors do not honor advisory locks.
Snapshots detect external changes up to the final pre-replace check. A pending
journal requires explicit review after interruption; it never authorizes rollback.
"""
import contextlib
import fcntl
import hashlib
import json
import os
from pathlib import Path
import stat
import tempfile


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def markers(text, start, end):
    if text.count(start) != text.count(end) or text.count(start) > 1:
        raise ValueError('malformed managed markers')
    if start in text and text.index(start) > text.index(end):
        raise ValueError('reversed managed markers')
    if start in text:
        before, tail = text.split(start, 1)
        _, after = tail.split(end, 1)
        return before, after
    return None


def root_path(path):
    # abspath preserves symlink components, unlike resolve(). macOS /tmp itself
    # is a system symlink: callers must use its canonical /private/tmp spelling.
    root = Path(os.path.abspath(Path(path).expanduser()))
    for part in (root, *root.parents):
        if part.is_symlink():
            raise ValueError('symlink directory component')
    if not root.is_dir():
        raise ValueError('root is not a directory')
    return root


def snapshot(root):
    target = root / 'AGENTS.md'
    try:
        fd = os.open(target, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except FileNotFoundError:
        return None, b''
    st = os.fstat(fd)
    if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1:
        os.close(fd)
        raise ValueError('AGENTS.md must be a single-link regular file')
    with os.fdopen(fd, 'rb') as stream:
        raw = stream.read()
        now = os.fstat(stream.fileno())
        signature = lambda s: (s.st_dev, s.st_ino, s.st_mode, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
        if signature(st) != signature(now) or target.lstat().st_ino != st.st_ino:
            raise ValueError('concurrent read change')
        return signature(st), raw


def read(path):
    root = root_path(path)
    return root, snapshot(root)


def _durable(path, raw, mode=0o600):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, mode)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def _sync(root):
    fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


@contextlib.contextmanager
def locked(root):
    path = root / '.sdkit-agents.lock'
    fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600)
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1:
            raise ValueError('unsafe lock file')
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ValueError('another updater holds lock') from exc
        yield
    finally:
        os.close(fd)
    # Do not unlink lock: waiters could otherwise lock different inodes.


def apply(root, original, new, authorized, expected, hook=None):
    if not authorized or expected != digest(original[1]):
        raise ValueError('apply requires authorization and matching dry-run SHA')
    root = root_path(root)
    with locked(root):
        pending = root / '.sdkit-agents-pending.json'
        if pending.exists() or pending.is_symlink():
            raise ValueError('pending transaction: review journal, target and backup before retry')
        if snapshot(root) != original:
            raise ValueError('concurrent change')
        if new == original[1]:
            return {'status': 'unchanged', 'sha256': digest(new)}
        # One private directory retains exact preimage and proposed bytes. For a
        # previously missing target, absence is recorded rather than an empty backup.
        recovery = Path(tempfile.mkdtemp(prefix='.sdkit-agents-recovery-', dir=root))
        recovery.chmod(0o700)
        backup = recovery / 'before.md'
        if original[0] is not None:
            _durable(backup, original[1])
        temp = recovery / 'after.md'
        _durable(temp, new)
        os.chmod(temp, stat.S_IMODE(original[0][2]) if original[0] else 0o600)
        record = {'before_sha256': digest(original[1]), 'after_sha256': digest(new),
                  'existed': original[0] is not None, 'mode': stat.S_IMODE(original[0][2]) if original[0] else None,
                  'backup': str(backup) if original[0] else None, 'recovery': str(recovery)}
        _durable(pending, json.dumps(record, ensure_ascii=False).encode())
        _sync(root)
        if hook:
            hook()
        if root_path(root) != root or snapshot(root) != original:
            raise ValueError('concurrent change; pending evidence retained')
        os.replace(temp, root / 'AGENTS.md')
        _sync(root)
        if snapshot(root)[1] != new:
            raise ValueError('post-write verification failed; pending evidence retained')
        pending.unlink()
        _sync(root)
        return {'status': 'updated', 'sha256': digest(new), **record}


def restore(root, backup, authorized, expected):
    """Restoration is a new authorized transaction, never an automatic rollback."""
    root, original = read(root)
    backup = Path(backup)
    if backup.is_symlink() or not backup.is_file():
        raise ValueError('invalid backup')
    # Explicit content to restore is still guarded by current target SHA.
    return apply(root, original, backup.read_bytes(), authorized, expected)
