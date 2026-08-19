"""Импорт заказов с FTP Зиландии."""

import asyncio
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

import app.accounts.models  # noqa
import app.parties.models  # noqa
import app.warehouse.models  # noqa
import app.integration.models  # noqa
import app.documents.models  # noqa

from app.core.database import async_session_factory
from app.infrastructure.uow import UnitOfWork
from app.integration.adapters.zln_adapter import ZLNAdapter
from app.integration.services.integration_service import IntegrationService
from app.integration.services.ftp_service import FTPService


async def import_from_ftp(profile_id: int = 1):
    # Подключаемся к FTP
    async with UnitOfWork(async_session_factory) as session:
        from app.integration.models import IntegrationProfile
        profile = await session.get(IntegrationProfile, profile_id)
        if not profile:
            print(f"Профиль {profile_id} не найден")
            return

        ftp_config = profile.config.get("ftp", {})
        print(f"Подключение к {ftp_config.get('host')}...")

        ftp = FTPService(
            host=ftp_config["host"],
            username=ftp_config["username"],
            password=ftp_config["password"],
        )
        ftp.connect()
        print("Подключено")

        try:
            out_path = ftp_config.get("out_path", "/out")
            files = ftp.list_files(out_path)
            print(f"Найдено файлов: {len(files)}")

            adapter = ZLNAdapter()
            integration = IntegrationService(session)

            with tempfile.TemporaryDirectory() as tmp_dir:
                for filename in files:
                    print(f"\nОбработка: {filename}")
                    remote_path = f"{out_path}/{filename}"
                    local_path = ftp.download(remote_path, tmp_dir)

                    universal_doc, errors = adapter.parse(local_path)
                    if errors:
                        print("Ошибки парсинга:")
                        for err in errors:
                            print(f"  - {err}")
                        continue

                    print(f"Документ: {universal_doc['document_type']} {universal_doc['document_number']}")

                    document, errors = await integration.process_document(
                        universal_doc=universal_doc,
                        depositor_id=profile.depositor_id,
                        user_id=1,
                    )

                    if errors:
                        print("Ошибки импорта:")
                        for err in errors:
                            print(f"  - {err}")
                        continue

                    if document:
                        print(f"Создан: id={document.id}")
                        ftp.delete(remote_path)
                        print("Файл удалён с FTP")
        finally:
            ftp.disconnect()
            print("\nОтключено")
    # UoW закоммитит при выходе из with


if __name__ == "__main__":
    asyncio.run(import_from_ftp())
