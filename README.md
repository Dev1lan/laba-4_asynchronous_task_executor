# Лабораторная работа №4 — Асинхронный исполнитель задач

**Тема:** Реализация пользовательской коллекции задач с поддержкой итерации и ленивой фильтрации  
**Студент:** Шамшетов Арыслан Жаксыбаевич  
**Группа:** М8О-106БВ-25  
**Преподаватель:** Самир Ахмед Халид  

---

## Структура проекта

```text
laba-4_asynchronous_task_executor/
├── src/
│   ├── async_processing/          
│   │   ├── __init__.py
│   │   ├── async_queue.py        
│   │   ├── executor.py           
│   │   ├── handler_protocols.py   
│   │   ├── handlers.py            
│   │   └── logger.py              
│   │
│   ├── domain/                    
│   │   ├── __init__.py
│   │   ├── descriptors.py         
│   │   ├── exceptions.py          
│   │   └── task.py               
│   │
│   ├── queue/                      
│   │   ├── __init__.py
│   │   └── task_queue.py          
│   │
│   ├── sources/                   
│   │   ├── __init__.py
│   │   ├── receiver.py           
│   │   ├── source_protocols.py    
│   │   └── sources.py             
│   │
│   └── main.py                    
│
├── tests/
│   └── general_test.py            
│
├── pyproject.toml                 
├── uv.lock                       
├── README.md                      
└── .pre-commit-config.yaml 
```
---

## Описание проекта

В рамках данной лабораторной работы реализована подсистема асинхронной обработки задач. Проект демонстрирует применение паттернов проектирования, контрактного программирования и современного стека асинхронного Python (`asyncio`).

Система позволяет конкурентно обрабатывать задачи из очереди с использованием пула асинхронных воркеров (рабочих корутин), обеспечивая при этом корректное управление ресурсами и перехват ошибок.

---

## Реализованная функциональность и архитектура

В соответствии с функциональными и техническими требованиями в проекте реализовано:

- **Асинхронная очередь (`AsyncTaskQueue`):** Потокобезопасная (в контексте event loop) обертка над `asyncio.Queue`, управляющая передачей задач воркерам.
- **Расширяемые обработчики (Handlers):**
  - Описание контракта обработчика строго через `typing.Protocol` (`AsyncTaskHandler`).
  - Реализация паттерна **Компоновщик (Composite)** через класс `CompositeHandler`, что позволяет строить сложные пайплайны обработки (цепочки обязанностей) и прерывать их при возникновении ошибок (статус `failed`).
- **Исполнитель (`AsyncTaskExecutor`):** - Запуск пула воркеров без блокирующих операций в event loop.
  - Централизованное логирование всех этапов жизненного цикла задачи (старт, успешное завершение, ошибка).
  - Использование **асинхронных контекстных менеджеров** (`__aenter__` / `__aexit__`) для безопасного старта и гарантированного изящного завершения (graceful shutdown) всех корутин.

---

## Пример использования

```python
import asyncio
from src.async_processing import AsyncTaskExecutor, AsyncTaskQueue
from src.async_processing.handlers import CompositeHandler, MarkDoneHandler, FailableHandler
from src.sources import GeneratorSource
from src.sources.receiver import receive_tasks

async def demo():
    # 1. Получаем задачи из источника
    tasks = receive_tasks(GeneratorSource(5))
    tasks[2].description = "fail this task"

    # 2. Помещаем их в асинхронную очередь
    queue = AsyncTaskQueue(tasks)

    # 3. Настраиваем цепочку обработчиков
    handler = CompositeHandler([
        FailableHandler(fail_on_substring="fail"),
        MarkDoneHandler(delay_seconds=0.5)
    ])

    # 4. Запускаем экзекутор через контекстный менеджер
    async with AsyncTaskExecutor(queue=queue, handler=handler, workers_count=3) as executor:
        await executor.run()

if __name__ == "__main__":
    asyncio.run(demo())
```

---

## Запуск

Проект использует современный пакетный менеджер uv для строгой фиксации зависимостей (uv.lock).

Установка зависимостей

```Bash
uv sync
```
### Запуск демонстрационного примера

```Bash
uv run python -m src.main
```
---

## Тестирование

### Запуск тестов

```bash
python -m pytest
```

### Результат

- Все тесты проходят успешно  
- Покрытие кода: **95%**  
- Минимальный порог покрытия **80%** выполнен  

---

Made by Dev1lan
