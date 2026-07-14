# Работа с Git-ветками

## Цель

Безопасно переносить изменения между ветками и публиковать их без потери
истории или чужих изменений.

## Перед изменением веток

```powershell
git branch --show-current
git status --short
git branch --verbose --verbose
git remote --verbose
git log --oneline --decorate --graph -10
```

- Не добавлять, не удалять и не прятать несвязанные файлы.
- Не выполнять `git reset --hard`, `git checkout --`, `rebase` или force-push
  без явного запроса пользователя.
- Если рабочее дерево содержит изменения, способные быть перезаписанными,
  остановиться и запросить решение.

## Перенос текущей ветки в master

1. Определить имя текущей ветки `<source>`.
2. Проверить, что `master` является её предком:

   ```powershell
   git merge-base --is-ancestor master <source>
   ```

3. При успехе выполнить fast-forward:

   ```powershell
   git checkout master
   git merge --ff-only <source>
   ```

4. При расхождении веток не выбирать стратегию самостоятельно. Сообщить
   коммиты с обеих сторон и запросить решение: merge commit или rebase.

## Публикация

Публиковать только по явному запросу и только после проверки remote:

```powershell
git remote --verbose
git push <remote> master
```

При отсутствии remote локальный merge считается завершённым, но требуется имя
или URL удалённого репозитория для публикации.

## После операции

```powershell
git status --short
git log -1 --oneline --decorate
git branch --verbose --verbose
```

Зафиксировать итоговый commit, факт публикации и несвязанные файлы, которые не
были изменены.
