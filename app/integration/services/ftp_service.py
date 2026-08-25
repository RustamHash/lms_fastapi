"""Сервис FTP."""

from __future__ import annotations

import os

FTP_TIMEOUT_SEC = 15


class FTPService:
    """Работа с FTP."""

    def __init__(self, host: str, username: str, password: str):
        self.host = host
        self.username = username
        self.password = password
        self._ftp = None

    def connect(self):
        from ftplib import FTP

        self._ftp = FTP(timeout=FTP_TIMEOUT_SEC)
        self._ftp.connect(self.host, timeout=FTP_TIMEOUT_SEC)
        self._ftp.login(self.username, self.password)
        return self

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        return False

    def disconnect(self):
        if not self._ftp:
            return
        try:
            self._ftp.quit()
        except Exception:
            try:
                self._ftp.close()
            except Exception:
                pass
        self._ftp = None

    def list_files(self, remote_path: str) -> list[str]:
        if self._ftp is None:
            raise RuntimeError("FTP не подключён")
        self._ftp.cwd(remote_path)
        files: list[str] = []
        self._ftp.retrlines("LIST", files.append)
        return [f.split()[-1] for f in files if f.startswith("-")]

    def download(self, remote_path: str, local_dir: str) -> str:
        if self._ftp is None:
            raise RuntimeError("FTP не подключён")
        filename = os.path.basename(remote_path)
        local_path = os.path.join(local_dir, filename)
        with open(local_path, "wb") as f:
            self._ftp.retrbinary(f"RETR {remote_path}", f.write)
        return local_path

    def delete(self, remote_path: str):
        if self._ftp is None:
            raise RuntimeError("FTP не подключён")
        self._ftp.delete(remote_path)
