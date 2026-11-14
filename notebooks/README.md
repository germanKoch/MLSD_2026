# Ноутбуки

[01_rcaeval_eda.ipynb](01_rcaeval_eda.ipynb) читает индекс RCAEval RE2-OB, строит разбиение 54/18/18 из дизайн-документа и показывает метрики, логи и трассы одного случая из части для разработки. Полноценный EDA пока не выполнен.

Из корня репозитория:

```bash
uv sync --locked --group eda
uv run --frozen --group eda python scripts/download_rcaeval.py
```

В VS Code откройте ноутбук и выберите `.venv/bin/python` как ядро. Затем выполните все ячейки по порядку. Ноутбук читает локальные файлы и не обращается к сети.

Данные находятся в `data/raw/rcaeval/`, которая исключена из Git. Загружаются 90 инцидентов RE2-OB и общий индекс `cases.parquet`, всего около 923 МБ. Скрипт фиксирует ревизию `afeacb11bcc94dadfd1c8f483ee4377b2b8b614e`, проверяет размеры и контрольные суммы файлов и сохраняет `download_manifest.json`. Повторный запуск использует кеш загрузки.

Источник: [RCAEval на Hugging Face](https://huggingface.co/datasets/phamquiluan/RCAEval/tree/afeacb11bcc94dadfd1c8f483ee4377b2b8b614e).
