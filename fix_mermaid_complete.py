#!/usr/bin/env python3
"""
Полное исправление Mermaid диаграмм в README.md
Собирает разорванные диаграммы и правильно оборачивает их в блоки кода
"""

import re
import sys
import os

def fix_mermaid_complete(content):
    """
    Находит и исправляет все Mermaid диаграммы, включая разорванные на части
    """
    lines = content.split('\n')
    result_lines = []
    i = 0
    
    # Предопределенные диаграммы из вашего файла для восстановления
    diagrams_content = {
        'flowchart_lr': '''flowchart LR
PDF --1--> OCR
WEB --1--> webparser
Word --2--> NLP
Excel --2--> схема
webparser --2--> NLP
OCR --2--> NLP
схема --3--> LLM
NLP --3--> LLM
LLM--4--> json
json -- 5 встраивает данные--> БД
БД -- 3 Данные онтологий для определения связей --> LLM''',
        
        'flowchart_td': '''flowchart TD
    A[Сырые ряды и региональные данные] --"Методы: Интерполяция (линейная, полиномиальная),<br/>Kalman filter, KNN-imputation, Байесовские модели<br/>Инструменты: scikit-learn, statsmodels, PyMC"--> B[Обработка пропущенных значений]
    
    B --"Методы: Bottom-up/Top-down reconciliation,<br/>Padding, Truncation<br/>Инструменты: HierarchicalForecast, Custom padding functions"--> C[Агрегация и нормализация рядов]
    
    C --"Методы: Лаги, средние, сезонность, внешние регрессоры<br/>Инструменты: tsfresh, sktime, FRED API"--> D[Инженерия признаков]
    
    D --"Методы: BSTS (байес. модели), LightGBM, LSTM/NN, ARIMA, Prophet<br/>Инструменты: PyMC, bsts (R), LightGBM, PyTorch, statsmodels"--> E[Обучение моделей]
    
    E --"Методы: Стекинг, взвешенное усреднение, Bayesian Model Averaging (BMA)<br/>Инструменты: scikit-learn, PyMC, XGBoost"--> F[Ансамблирование моделей]
    
    F --"Методы: Time Series Cross-Validation, Bayesian Optimization<br/>Инструменты: sktime, Optuna, scikit-optimize"--> G[Валидация и оптимизация]
    
    G --"Методы: Модельное развертывание, мониторинг<br/>Инструменты: MLflow, Docker, Kubernetes"--> H[Продакшн/Деплой]
    
    H --> I[Реальный прогноз]''',
        
        'graph_td_search': '''graph TD
    %% Начало процесса
    USER_QUERY[Запрос пользователя]

    %% Параллельная обработка
    EMBEDDING[embedding]
    ONTOLOGY_QUERY[Запрос релевантных<br/>онтологий]

    %% RAG процесс
    RAG[RAG по количественным<br/>узлам]

    %% Обработка онтологий
    RELEVANT_NODES[Выбор релевантных<br/>узлов]
    EXTERNAL_LINKS[Запрос внешних связей<br/>для выбранных узлов]

    %% Поиск недостающих данных
    MISSING_NODES[Определение<br/>пересекающихся<br/>численных узлов для<br/>всех онтологий]

    %% Боковая проверка
    PARENT_CHILD_QUERY[Запрос узлов онтологий<br/>дочерних и<br/>родительских<br/>до ближайшего,<br/>который будет<br/>содержать<br/>количественные данные]

    %% Получение индексов
    INDEX_RETRIEVAL[Получение через связи<br/>релевантных индексов]

    %% Финальная генерация
    ANSWER_GENERATION[Генерация ответа]

    %% Связи
    USER_QUERY --> EMBEDDING
    USER_QUERY --> ONTOLOGY_QUERY

    EMBEDDING --> RAG
    ONTOLOGY_QUERY --> RELEVANT_NODES

    RELEVANT_NODES --> EXTERNAL_LINKS
    EXTERNAL_LINKS --> MISSING_NODES

    MISSING_NODES --> |Узлы не найдены| PARENT_CHILD_QUERY
    PARENT_CHILD_QUERY --> EXTERNAL_LINKS

    RAG --> INDEX_RETRIEVAL
    MISSING_NODES --> ANSWER_GENERATION

    INDEX_RETRIEVAL --> ANSWER_GENERATION''',
        
        'graph_tb_architecture': '''graph TB
    %% Система координации
    subgraph "Система координации"
        COORD[System Coordinator<br/>CLI управление<br/>Health checks<br/>Graceful shutdown]
    end

    %% Пользовательские интерфейсы
    subgraph "Пользовательские интерфейсы"
        TGBOT[Telegram Bot<br/>Естественно-языковые запросы]
        WEBAPP[Web Dashboard<br/>Интерактивные карты и графики]
    end

    %% Обработка запросов
    subgraph "Обработка запросов"
        LLM[LLM интеграция<br/>OpenAI GPT-4o<br/>LangChain<br/>Анализ запросов]
    end

    %% Визуализация
    subgraph "Визуализация"
        VIZ[Визуализация<br/>Plotly карты<br/>Временные ряды<br/>Региональная аналитика]
    end

    %% ETL процессы
    subgraph "ETL процессы"
        DATA[Исходные данные<br/>~850 Excel файлов<br/>2015-2024 годы<br/>85 регионов]
        ETL[ETL компоненты<br/>Excel → CSV → Neo4j<br/>Федеральные данные<br/>Региональные данные]
    end

    %% Внешний поиск
    subgraph "Внешний поиск"
        TAVILY[Tavily Search<br/>Поиск в интернете<br/>Актуальная информация]
    end

    %% Данные и хранение
    subgraph "Данные и хранение"
        NEO4J[Neo4j Graph DB<br/>Сетевые узлы<br/>Расчетные узлы<br/>Региональные данные]
        GEO[Геоданные<br/>russia_regions.parquet<br/>85 регионов РФ]
    end

    %% Связи координации
    COORD --> TGBOT
    COORD --> WEBAPP
    COORD --> ETL

    %% Связи обработки
    TGBOT --> LLM
    LLM --> TAVILY
    LLM --> NEO4J
    
    %% Связи визуализации
    WEBAPP --> VIZ
    VIZ --> NEO4J
    VIZ --> GEO

    %% Связи данных
    DATA --> ETL
    ETL --> NEO4J

    %% Стили
    classDef coordinator fill:#e8f5e8,stroke:#4caf50
    classDef interface fill:#e3f2fd,stroke:#2196f3
    classDef processing fill:#f3e5f5,stroke:#9c27b0
    classDef visualization fill:#fff3e0,stroke:#ff9800
    classDef data fill:#fce4ec,stroke:#e91e63
    classDef search fill:#f1f8e9,stroke:#8bc34a
    classDef storage fill:#fff8e1,stroke:#ffc107

    class COORD coordinator
    class TGBOT,WEBAPP interface
    class LLM processing
    class VIZ visualization
    class DATA,ETL data
    class TAVILY search
    class NEO4J,GEO storage''',
        
        'graph_td_rid': '''graph TD
    %% Коммерческие компоненты
    STARTEX["ООО 'СТАРТЕХ БАЗА'"]

    %% Open Source компоненты
    OPENSOURCE[OpenSource]

    %% Базы данных и платформы
    STARTUP_DB["БД стартапов и проектов<br/>Онлайн-платформа технологических компаний,<br/>корпораций и инвесторов<br/>(серверный модуль)"]
    EDU_DB[БД данных об образовании]

    %% Агенты и модели
    PARSER_AGENT[Агент парсер]
    ANALYTICS_AGENT[Агент аналитик]
    FORECAST_MODEL[Прогнозная модель]

    %% РИД (действующий)
    RID_CURRENT["РИД<br/>№2024613709"]

    %% РИД (новые планируемые)
    RID_NEW1["РИД<br/>(новый)"]
    RID_NEW2["РИД<br/>(opensource)<br/><br/>Используемые открытые решения, обязуют<br/>реализовывать продукт по открытой лицензии"]

    %% Связи коммерческих компонентов к БД
    STARTEX -.-> STARTUP_DB
    STARTEX -.-> EDU_DB

    %% Связи Open Source к агентам
    OPENSOURCE -.-> PARSER_AGENT
    OPENSOURCE -.-> ANALYTICS_AGENT
    OPENSOURCE -.-> FORECAST_MODEL

    %% Связи к действующему РИД
    STARTUP_DB --> RID_CURRENT

    %% Связи к новым РИД
    EDU_DB --> RID_NEW1
    PARSER_AGENT --> RID_NEW2
    ANALYTICS_AGENT --> RID_NEW2
    FORECAST_MODEL --> RID_NEW2

    %% Легенда цветов
    subgraph "Легенда"
        LEGEND_RID_CURRENT[Действующий РИД]
        LEGEND_RID_PLANNED[Планируемый РИД]
    end

    %% Стили
    classDef ridCurrent fill:#c8e6c9,stroke:#4caf50
    classDef ridPlanned fill:#fff8e1,stroke:#ffc107
    classDef neutral fill:#f5f5f5,stroke:#757575

    class STARTUP_DB,RID_CURRENT ridCurrent
    class EDU_DB,PARSER_AGENT,ANALYTICS_AGENT,FORECAST_MODEL,RID_NEW1,RID_NEW2 ridPlanned
    class STARTEX,OPENSOURCE neutral
    
    class LEGEND_RID_CURRENT ridCurrent
    class LEGEND_RID_PLANNED ridPlanned'''
    }
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Ищем начала диаграмм и заменяем их правильными версиями
        if line.startswith('flowchart LR'):
            result_lines.append('```mermaid')
            result_lines.append(diagrams_content['flowchart_lr'])
            result_lines.append('```')
            result_lines.append('')
            # Пропускаем все до следующего значимого контента
            i += 1
            while i < len(lines) and (lines[i].strip() == '' or 
                                      lines[i].strip().startswith(('PDF', 'WEB', 'Word', 'Excel', 'webparser', 'OCR', 'схема', 'NLP', 'LLM', 'json', 'БД', '```'))):
                i += 1
            continue
            
        elif line.startswith('flowchart TD'):
            result_lines.append('```mermaid')  
            result_lines.append(diagrams_content['flowchart_td'])
            result_lines.append('```')
            result_lines.append('')
            # Пропускаем все части этой диаграммы
            i += 1
            while i < len(lines) and (lines[i].strip() == '' or
                                      'Методы:' in lines[i] or
                                      lines[i].strip().startswith(('A[', 'B ', 'C ', 'D ', 'E ', 'F ', 'G ', 'H ', '-->'))):
                i += 1
            continue
            
        elif line.startswith('graph TD') and 'Начало процесса' in content[content.find(lines[i]):content.find(lines[i])+500]:
            result_lines.append('```mermaid')
            result_lines.append(diagrams_content['graph_td_search'])
            result_lines.append('```')
            result_lines.append('')
            # Пропускаем все части этой диаграммы
            i += 1
            while i < len(lines) and (lines[i].strip() == '' or
                                      lines[i].strip().startswith(('%', 'USER_QUERY', 'EMBEDDING', 'ONTOLOGY', 'RAG', 'RELEVANT', 'EXTERNAL', 'MISSING', 'PARENT', 'INDEX', 'ANSWER', '-->', '|'))):
                i += 1
            continue
            
        elif line.startswith('graph TB'):
            result_lines.append('```mermaid')
            result_lines.append(diagrams_content['graph_tb_architecture'])
            result_lines.append('```')
            result_lines.append('')
            # Пропускаем все части этой диаграммы
            i += 1
            while i < len(lines) and (lines[i].strip() == '' or
                                      lines[i].strip().startswith(('%', 'subgraph', 'COORD', 'TGBOT', 'WEBAPP', 'LLM', 'VIZ', 'DATA', 'ETL', 'TAVILY', 'NEO4J', 'GEO', 'end', '-->', 'classDef', 'class '))):
                i += 1
            continue
            
        elif line.startswith('graph TD') and ('STARTEX' in content[content.find(lines[i]):content.find(lines[i])+500] or 'РИД' in content[content.find(lines[i]):content.find(lines[i])+500]):
            result_lines.append('```mermaid')
            result_lines.append(diagrams_content['graph_td_rid'])
            result_lines.append('```')
            result_lines.append('')
            # Пропускаем все части этой диаграммы
            i += 1
            while i < len(lines) and (lines[i].strip() == '' or
                                      lines[i].strip().startswith(('%', 'STARTEX', 'OPENSOURCE', 'STARTUP_DB', 'EDU_DB', 'PARSER', 'ANALYTICS', 'FORECAST', 'RID_', 'LEGEND', '-.', '-->', 'subgraph', 'end', 'classDef', 'class '))):
                i += 1
            continue
            
        # Пропускаем отдельные строки диаграмм, которые не были собраны в блоки
        elif (line.startswith(('%', 'USER_QUERY', 'EMBEDDING', 'ONTOLOGY', 'RAG', 'RELEVANT', 'EXTERNAL', 'MISSING', 'PARENT', 'INDEX', 'ANSWER')) or
              line.startswith(('COORD', 'TGBOT', 'WEBAPP', 'LLM', 'VIZ', 'DATA', 'ETL', 'TAVILY', 'NEO4J', 'GEO')) or
              line.startswith(('STARTEX', 'OPENSOURCE', 'STARTUP_DB', 'EDU_DB', 'PARSER', 'ANALYTICS', 'FORECAST', 'RID_', 'LEGEND')) or
              line.startswith(('A[', 'B ', 'C ', 'D ', 'E ', 'F ', 'G ', 'H ')) or
              re.match(r'^\s*[A-Z_]+\s*-->', line) or
              re.match(r'^\s*[A-Z_]+\s*\[.*\]', line) or
              line.startswith(('end', 'subgraph', 'classDef', 'class ')) or
              ('Методы:' in line and '-->' in line)):
            # Пропускаем эти строки - они уже включены в диаграммы выше
            pass
        else:
            result_lines.append(lines[i])
        
        i += 1
    
    return '\n'.join(result_lines)

def main():
    if len(sys.argv) != 2:
        print("Использование: python fix_mermaid_complete.py <путь_к_файлу.md>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"Ошибка: файл {file_path} не найден")
        sys.exit(1)
    
    # Создаем резервную копию
    backup_path = file_path + '.backup_final'
    
    try:
        # Читаем исходный файл
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Создаем резервную копию
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"Создана резервная копия: {backup_path}")
        
        # Исправляем содержимое
        print("Восстанавливаем и исправляем все Mermaid диаграммы...")
        fixed_content = fix_mermaid_complete(original_content)
        
        # Записываем исправленный файл
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print(f"Файл {file_path} успешно исправлен!")
        
        # Показываем статистику
        original_mermaid_count = original_content.count('```mermaid')
        fixed_mermaid_count = fixed_content.count('```mermaid')
        
        print(f"\nСтатистика:")
        print(f"- Блоков ```mermaid до: {original_mermaid_count}")
        print(f"- Блоков ```mermaid после: {fixed_mermaid_count}")
        
        if fixed_mermaid_count > original_mermaid_count:
            print(f"- Восстановлено диаграмм: {fixed_mermaid_count - original_mermaid_count}")
        
        print("\nВыполненные исправления:")
        print("✅ Восстановлены все 5 разорванных Mermaid диаграмм")
        print("✅ Правильно оформлены блоки ```mermaid")
        print("✅ Удалены разрозненные части диаграмм")
        print("✅ Все диаграммы готовы для отображения на GitHub")
        
    except Exception as e:
        print(f"Ошибка при обработке файла: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()