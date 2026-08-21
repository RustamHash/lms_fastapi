"""Утилита для пересборки Pydantic моделей с циклическими зависимостями."""

import importlib
import inspect
import logging
from typing import Type, Set

from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Список всех модулей со схемами
SCHEMA_MODULES = [
    'app.files.schemas',
    'app.api.v1.accounts.schemas',
    'app.api.v1.orders.schemas',
    'app.api.v1.integration.schemas',
    'app.api.v1.parties.schemas',
    'app.api.v1.documents.schemas',
    'app.api.v1.warehouse.schemas',
    'app.api.v1.delivery.schemas',
    'app.api.v1.notifications.schemas',
]


def get_all_models() -> list:
    """Получает все Pydantic модели из всех модулей схем."""
    all_models = []
    seen_models = set()
    
    for module_name in SCHEMA_MODULES:
        try:
            module = importlib.import_module(module_name)
            
            # Находим все модели BaseModel в модуле
            for name, obj in inspect.getmembers(module):
                if (isinstance(obj, type) and 
                    issubclass(obj, BaseModel) and 
                    obj.__module__ == module_name and
                    obj not in seen_models):
                    all_models.append(obj)
                    seen_models.add(obj)
                    
        except ImportError as e:
            logger.warning(f"Не удалось импортировать модуль {module_name}: {e}")
        except Exception as e:
            logger.error(f"Ошибка при обработке модуля {module_name}: {e}")
    
    return all_models


def rebuild_all_models():
    """Пересобирает все Pydantic модели для решения циклических зависимостей."""
    models = get_all_models()
    logger.info(f"Найдено {len(models)} моделей для пересборки")
    
    # Пересобираем модели несколько раз, так как зависимости могут быть сложными
    for iteration in range(5):  # 5 итераций для надежности
        success_count = 0
        fail_count = 0
        
        for model in models:
            try:
                if hasattr(model, 'model_rebuild'):
                    model.model_rebuild(force=True)
                    success_count += 1
            except Exception as e:
                fail_count += 1
                if iteration == 4:  # Логируем только на последней итерации
                    logger.debug(f"Не удалось пересобрать модель {model.__name__}: {e}")
        
        logger.debug(f"Итерация {iteration + 1}: успешно {success_count}, с ошибками {fail_count}")
        
        # Если все модели пересобраны успешно, выходим
        if fail_count == 0:
            break
    
    logger.info("Пересборка моделей завершена")
    return models
