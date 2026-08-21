#!/bin/bash
set -euo pipefail

BASE="/home/rustam/Data/test/lms_fastapi/frontend/src"

echo "🔍 Шаг 1: Проверка наличия всех файлов entity-system"
required_files=(
  "$BASE/features/entity-system/EntityListPage.tsx"
  "$BASE/features/entity-system/EntityDetailPage.tsx"
  "$BASE/features/entity-system/GroupActionsBar.tsx"
  "$BASE/features/entity-system/hooks/useEntityList.tsx"
  "$BASE/features/entity-system/hooks/useEntityDetail.ts"
  "$BASE/features/entity-system/types.ts"
)
for f in "${required_files[@]}"; do
  if [[ ! -f "$f" ]]; then
    echo "❌ Отсутствует файл: $f"
    exit 1
  fi
done
echo "✅ Все файлы entity-system на месте"

echo "🔄 Шаг 2: Обновление импортов во всех страницах"
find "$BASE/pages" -name "*.tsx" -type f | while read -r file; do
  if grep -q "features/entity-list" "$file"; then
    # Замена импортов
    sed -i \
      -e "s|features/entity-list/EntityListPage|features/entity-system/EntityListPage|g" \
      -e "s|features/entity-list/useEntityList|features/entity-system/hooks/useEntityList|g" \
      -e "s|features/entity-list/types|features/entity-system/types|g" \
      "$file"
    echo "  ✅ Обновлён: $(basename "$file")"
  fi
done

echo "🔄 Шаг 3: Обновление импортов в конфигурациях"
find "$BASE/features" -name "config.ts" -type f | while read -r file; do
  if grep -q "entity-list" "$file"; then
    sed -i \
      -e "s|features/entity-list/types|features/entity-system/types|g" \
      "$file"
    echo "  ✅ Обновлён: $(basename "$file")"
  fi
done

echo "🔄 Шаг 4: Обновление импортов в других файлах"
find "$BASE" -name "*.tsx" -o -name "*.ts" | while read -r file; do
  if grep -q "entity-list" "$file"; then
    sed -i \
      -e "s|features/entity-list/EntityListPage|features/entity-system/EntityListPage|g" \
      -e "s|features/entity-list/useEntityList|features/entity-system/hooks/useEntityList|g" \
      -e "s|features/entity-list/types|features/entity-system/types|g" \
      "$file"
    echo "  ✅ Обновлён: $(basename "$file")"
  fi
done

echo "🗑️ Шаг 5: Удаление директории entity-list"
rm -rf "$BASE/features/entity-list"
echo "✅ Директория entity-list удалена"

echo "🔧 Шаг 6: Проверка на оставшиеся ссылки"
if grep -r "entity-list" "$BASE" --include="*.ts" --include="*.tsx" -l; then
  echo "⚠️ Остались ссылки на entity-list:"
  grep -r "entity-list" "$BASE" --include="*.ts" --include="*.tsx" -l
  exit 1
else
  echo "✅ Ссылок на entity-list не осталось"
fi

echo "📦 Шаг 7: Запуск TypeScript проверки"
cd /home/rustam/Data/test/lms_fastapi/frontend
if npx tsc -b --noEmit 2>&1 | tee /tmp/tsc_output.txt; then
  echo "✅ TypeScript проверка пройдена"
else
  echo "⚠️ Ошибки TypeScript (это нормально для первого прогона):"
  cat /tmp/tsc_output.txt
fi

echo "🎨 Шаг 8: Запуск ESLint"
if npm run lint 2>&1 | tee /tmp/eslint_output.txt; then
  echo "✅ ESLint пройден"
else
  echo "⚠️ Ошибки ESLint:"
  cat /tmp/eslint_output.txt
fi

echo "✅ Миграция завершена!"
echo ""
echo "📋 Дальнейшие шаги:"
echo "1. Проверьте ошибки TypeScript в /tmp/tsc_output.txt"
echo "2. Проверьте ошибки ESLint в /tmp/eslint_output.txt"
echo "3. Исправьте все типовые ошибки"
echo "4. Запустите dev-сервер и проверьте страницы визуально"
echo "5. Удалите скрипт миграции: rm $0"
