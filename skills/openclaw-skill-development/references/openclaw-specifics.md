# OpenClaw-специфика разработки навыков

Используй эту справку вместе с `openclaw-skill-development`, когда нужно
создать, перенести, проверить или улучшить OpenClaw skill.

## Проверяемые основания корпуса

Минимальные утверждения корпуса для этой справки:

- `OCDOC-001`: OpenClaw skill хранится как markdown instruction file в каталоге
  с `SKILL.md`, YAML frontmatter и markdown body.
- `OCDOC-002`: порядок загрузки начинается с workspace skills, затем project
  agent skills, personal agent skills, managed local skills, bundled skills,
  extra directories или plugin skills.
- `OCDOC-003`: `$CODEX_HOME/skills` не является OpenClaw skill root.
- `OCDOC-004`: agent allowlists ограничивают видимость навыков независимо от
  места загрузки.
- `OCDOC-005`: сторонние навыки нужно считать недоверенным кодом и читать перед
  включением.
- `OCDOC-006` - `OCDOC-008`: Skill Workshop является управляемым путём для
  создания и обновления workspace skills через proposal-first lifecycle.
- `OCDOC-009` - `OCDOC-012`: workspace skills живут в `skills/`, frontmatter
  требует `name` и `description`, локальные файлы можно ссылать через
  `{baseDir}`, а agent-drafted skills с review-before-live должны идти через
  Skill Workshop proposals.
- `OCDOC-013` - `OCDOC-015`: конфигурация навыков живёт в OpenClaw config,
  видимость задаётся `agents.defaults.skills` и `agents.list[].skills`,
  install policy может запускать локальную trusted policy command.
- `AGFOC-001` - `AGFOC-004`: AgentForge является внешним примером пайплайна
  создания OpenClaw skills, но его структура и подходы не становятся правилом
  проекта без отдельного решения.

## Формат OpenClaw skill

Проверяй:

- каталог навыка находится внутри нужного OpenClaw skill root;
- имя каталога и `name` в frontmatter согласованы;
- `name` использует lowercase letters, digits и hyphens;
- `description` является коротким маршрутизирующим описанием для агента и
  discovery, а не пересказом внутренней процедуры;
- frontmatter содержит только однострочные ключи;
- body объясняет, когда применять навык, обязательный порядок, ограничения и
  проверку результата;
- локальные материалы подключены через `{baseDir}`.

## Загрузка, видимость и конфликт имён

Проверяй не только файл, но и runtime-поверхность:

- какой skill root содержит целевой навык;
- не перекрывается ли он одноимённым навыком из root с более высоким
  приоритетом;
- видит ли нужный агент навык с учётом `agents.defaults.skills` и
  `agents.list[].skills`;
- нужен ли `metadata.openclaw.requires` для бинарников, env, config или OS;
- нужен ли `user-invocable: false`, если навык не должен быть slash-командой;
- не является ли `$CODEX_HOME/skills` ошибочно выбранным root для OpenClaw.

## Skill Workshop или прямая правка

Используй Skill Workshop proposal, если:

- навык создаётся или обновляется агентом в live OpenClaw workspace;
- оператор хочет review-before-apply;
- изменение должно пройти scanner, hash-bound update и rollback metadata.

Правь tracked files напрямую, если:

- работа идёт в исходном Git-репозитории коллекции;
- пользователь просит изменить кодовую базу проекта;
- результат должен попасть в VCS как обычный артефакт разработки.

В отчёте явно назови выбранный путь, чтобы не смешивать proposal-first workflow
OpenClaw и сопровождение исходной коллекции.

## Безопасность

Для навыков с командами, установкой, секретами или сторонними источниками
проверяй:

- навык прочитан перед включением, если он сторонний;
- shell-команды не позволяют произвольную инъекцию из пользовательского ввода;
- секреты не попадают в prompt, логи, tracked файлы или sandbox без явной
  политики;
- install policy, sandbox и gating соответствуют риску;
- режим доступа источников корпуса разрешает перенос сведений в публичные
  файлы.

## Минимальные проверки

Для нового OpenClaw-навыка нужны:

- `SKILL.md` с валидным frontmatter;
- trigger eval с положительными, отрицательными и пограничными случаями;
- result-сценарий, который проверяет OpenClaw-совместимость, использование
  корпуса и отличает применение навыка от общей рекомендации;
- проверка JSON/YAML/Markdown доступными локальными инструментами;
- явная фиксация отсутствующих проверок, если нет OpenClaw CLI, project runner
  или live workspace.
