"""Сервис FTP."""

from __future__ import annotations

import os


class FTPService:
    """Работа с FTP. Поддерживает контекстный менеджер."""
    """Работа с FTP."""

    def __init__(self, host: str, username: str, password: str):
        self.host = host
        self.username = username
        self.password = password
        self._ftp = None

    def connect(self):
        from ftplib import FTP

        self._ftp = FTP(self.host)
        self._ftp.login(self.username, self.password)
        return self

    def __enter__(self):
        """Вход в контекстный менеджер."""
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Выход из контекстного менеджера — всегда закрываем соединение."""
        self.disconnect()
        return False

    def disconnect(self):
        if self._ftp:
            self._ftp.quit()
            self._ftp = None

    def list_files(self, remote_path: str) -> list[str]:
        self._ftp.cwd(remote_path)
        files = []
        self._ftp.retrlines("LIST", files.append)
        return [f.split()[-1] for f in files if f.startswith("-")]

    def download(self, remote_path: str, local_dir: str) -> str:
        filename = os.path.basename(remote_path)
        local_path = os.path.join(local_dir, filename)
        with open(local_path, "wb") as f:
            self._ftp.retrbinary(f"RETR {remote_path}", f.write)
        return local_path

    def delete(self, remote_path: str):
        self._ftp.delete(remote_path)
