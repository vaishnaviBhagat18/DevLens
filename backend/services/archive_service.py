"""Safely unpack a limited ZIP upload into a temporary repository directory."""

import shutil
import stat
import zipfile
from pathlib import Path, PurePosixPath


class ArchiveService:
    MAX_UPLOAD_BYTES = 25 * 1024 * 1024
    MAX_EXTRACTED_BYTES = 100 * 1024 * 1024
    MAX_FILES = 2000
    MAX_ENTRIES = 3000
    SKIP_DIRECTORIES = {
        "__MACOSX", ".git", "node_modules", ".venv", "venv",
        "__pycache__", "dist", "build", ".next",
    }

    def extract_zip(self, uploaded_file, destination: str) -> Path:
        """Return the extracted project root; never trust archive paths."""
        target_root = Path(destination).resolve()
        target_root.mkdir(parents=True, exist_ok=True)

        uploaded_file.seek(0, 2)
        compressed_size = uploaded_file.tell()
        uploaded_file.seek(0)
        if compressed_size == 0:
            raise ValueError("The uploaded ZIP file is empty.")
        if compressed_size > self.MAX_UPLOAD_BYTES:
            raise ValueError("ZIP file exceeds the 25 MB upload limit.")

        try:
            with zipfile.ZipFile(uploaded_file) as archive:
                entries = archive.infolist()
                if len(entries) > self.MAX_ENTRIES:
                    raise ValueError("ZIP archive contains too many entries.")

                accepted = []
                file_count = 0
                declared_total = 0
                for info in entries:
                    name = info.filename
                    if (
                        not name or name.startswith(("/", "\\"))
                        or "\\" in name or ":" in name or "\x00" in name
                    ):
                        raise ValueError("ZIP contains an unsafe file path.")
                    parts = PurePosixPath(name).parts
                    if ".." in parts:
                        raise ValueError("ZIP contains a path traversal entry.")
                    if any(part in self.SKIP_DIRECTORIES for part in parts):
                        continue
                    if any(part in {"", "."} for part in parts):
                        continue

                    mode = stat.S_IFMT(info.external_attr >> 16)
                    if mode not in {0, stat.S_IFREG, stat.S_IFDIR}:
                        raise ValueError("ZIP contains a symlink or unsupported file type.")

                    relative = Path(*parts)
                    path = (target_root / relative).resolve()
                    if not path.is_relative_to(target_root):
                        raise ValueError("ZIP contains an unsafe file path.")

                    if not info.is_dir():
                        file_count += 1
                        declared_total += info.file_size
                        if file_count > self.MAX_FILES:
                            raise ValueError("ZIP contains more than 2,000 files.")
                        if declared_total > self.MAX_EXTRACTED_BYTES:
                            raise ValueError("Uncompressed ZIP exceeds the 100 MB limit.")
                    accepted.append((info, path))

                if not file_count:
                    raise ValueError("ZIP contains no project files.")

                # Ensure no archive entry can become an unexpected parent-file collision.
                file_destinations = {p for info, p in accepted if not info.is_dir()}
                for _, p in accepted:
                    if any(parent in file_destinations for parent in p.parents if parent != p):
                        raise ValueError("ZIP has conflicting file and directory paths.")

                extracted_total = 0
                for info, path in accepted:
                    if info.is_dir():
                        path.mkdir(parents=True, exist_ok=True)
                        continue
                    path.parent.mkdir(parents=True, exist_ok=True)
                    with archive.open(info) as source, path.open("wb") as output:
                        while True:
                            block = source.read(1024 * 1024)
                            if not block:
                                break
                            extracted_total += len(block)
                            if extracted_total > self.MAX_EXTRACTED_BYTES:
                                raise ValueError("Extracted ZIP exceeds the 100 MB limit.")
                            output.write(block)
        except (zipfile.BadZipFile, zipfile.LargeZipFile, EOFError, OSError) as exc:
            raise ValueError("Invalid or unreadable ZIP archive.") from exc

        # A GitHub-downloaded ZIP commonly contains one enclosing folder.
        visible = [p for p in target_root.iterdir() if p.name not in {".DS_Store", "Thumbs.db"}]
        if len(visible) == 1 and visible[0].is_dir():
            return visible[0]
        return target_root
