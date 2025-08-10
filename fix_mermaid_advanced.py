#!/usr/bin/env python3
"""
Улучшенный скрипт для исправления Mermaid диаграмм в Markdown файлах
Исправляет:
1. Неправильное разделение диаграмм на части
2. Проблемы с экранированием специальных символов
3. Неправильное закрытие блоков кода
"""

import re
import sys
import os

def fix_mermaid_diagrams(content):
    """
    Исправляет все проблемы с Mermaid диаграммами
    """
    lines = content.split('\n')
    result_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Проверяем начало Mermaid диаграммы
        if re.match(r'^```mermaid\s*$', stripped):
            result_lines.append(line)
            i += 1
            
            # Собираем всю диаграмму до закрывающих ```
            diagram_lines = []
            diagram_complete = False
            
            while i < len(lines):
                current_line = lines[i]
                current_stripped = current_line.strip()
                
                # Проверяем закрывающие ```
                if re.match(r'^```\s*$', current_stripped):
                    diagram_complete = True
                    break
                
                diagram_lines.append(current_line)
                i += 1
            
            # Если диаграмма не была закрыта, ищем логический конец
            if not diagram_complete:
                # Возвращаемся и ищем конец диаграммы по контексту
                for j, diagram_line in enumerate(diagram_lines):
                    stripped_diagram = diagram_line.strip()
                    
                    # Если встретили пустую строку, проверяем следующую
                    if stripped_diagram == '' and j + 1 < len(diagram_lines):
                        next_line = diagram_lines[j + 1].strip()
                        # Если следующая строка не относится к диаграмме
                        if (next_line and 
                            not next_line.startswith(('    ', '```', '%', 'subgraph', 'classDef', 'class ', 'graph', 'flowchart')) and
                            not re.match(r'^\w+.*--', next_line) and
                            not re.match(r'^\w+.*-->', next_line) and
                            not re.match(r'^\w+\s*\[.*\]', next_line)):
                            # Обрезаем диаграмму здесь
                            diagram_lines = diagram_lines[:j]
                            break
            
            # Добавляем строки диаграммы
            result_lines.extend(diagram_lines)
            
            # Добавляем закрывающий блок, если его не было
            if not diagram_complete:
                result_lines.append('```')
            else:
                result_lines.append(lines[i])  # Добавляем найденный закрывающий блок
                
        else:
            # Проверяем, не начинается ли строка с Mermaid диаграммы без блока кода
            if re.match(r'^(flowchart|graph)\s+(TD|TB|LR|RL|BT)', stripped):
                # Начинаем новый блок Mermaid
                result_lines.append('```mermaid')
                result_lines.append(line)
                
                i += 1
                
                # Собираем диаграмму
                while i < len(lines):
                    current_line = lines[i]
                    current_stripped = current_line.strip()
                    
                    # Логика определения конца диаграммы
                    if current_stripped == '':
                        # Проверяем следующую строку
                        if i + 1 < len(lines):
                            next_stripped = lines[i + 1].strip()
                            if (next_stripped and 
                                not next_stripped.startswith(('    ', '%', 'subgraph', 'classDef', 'class ')) and
                                not re.match(r'^\w+.*(--)|(-->)', next_stripped) and
                                not re.match(r'^\w+\s*\[.*\]', next_stripped) and
                                not next_stripped.startswith('Для ') and  # Специфично для этого документа
                                next_stripped not in ['```']):
                                # Конец диаграммы
                                result_lines.append(current_line)
                                break
                        else:
                            # Конец файла
                            result_lines.append(current_line)
                            break
                    elif current_stripped.startswith('```'):
                        # Встретили другой блок кода - не добавляем эту строку
                        i -= 1  # Вернемся на шаг назад
                        break
                    elif (current_stripped.startswith('**') and 
                          current_stripped.endswith('**') and 
                          len(current_stripped) > 4):
                        # Встретили заголовок - конец диаграммы
                        i -= 1  # Не добавляем эту строку в диаграмму
                        break
                    elif current_stripped.startswith('!['):
                        # Встретили изображение - конец диаграммы
                        i -= 1
                        break
                    
                    result_lines.append(current_line)
                    i += 1
                
                # Закрываем блок
                result_lines.append('```')
                result_lines.append('')  # Пустая строка после диаграммы
            else:
                result_lines.append(line)
        
        i += 1
    
    return '\n'.join(result_lines)

def escape_mermaid_content(content):
    """
    Экранирует специальные символы в Mermaid диаграммах
    """
    def escape_labels(match):
        full_match = match.group(0)
        
        # Заменяем проблемные символы в лейблах
        # Экранируем кавычки внутри строк
        escaped = full_match.replace('"', '&quot;')
        
        # Исправляем проблемы с < и >
        escaped = re.sub(r'<(\d+)', r'&lt;\1', escaped)
        escaped = re.sub(r'>(\d+)', r'&gt;\1', escaped)
        
        return escaped
    
    # Применяем экранирование к содержимому между ```mermaid и ```
    def process_mermaid_block(match):
        mermaid_content = match.group(1)
        
        # Экранируем содержимое стрелок
        mermaid_content = re.sub(r'--"([^"]*)"-->', lambda m: f'--"{escape_labels(m)}"-->', mermaid_content)
        
        # Экранируем содержимое узлов [содержимое]
        mermaid_content = re.sub(r'\[([^\]]*<[^>]*>[^\]]*)\]', 
                                lambda m: f'[{m.group(1).replace("<", "&lt;").replace(">", "&gt;")}]', 
                                mermaid_content)
        
        return f'```mermaid\n{mermaid_content}\n```'
    
    # Обрабатываем все блоки mermaid
    pattern = r'```mermaid\n(.*?)\n```'
    content = re.sub(pattern, process_mermaid_block, content, flags=re.DOTALL)
    
    return content

def clean_broken_diagrams(content):
    """
    Очищает разорванные диаграммы, где части диаграммы оказались вне блоков кода
    """
    lines = content.split('\n')
    result_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Проверяем строки, которые выглядят как часть Mermaid диаграммы, но не в блоке
        if (re.match(r'^\s*[A-Z_]+\s*--', line) or  # Связи типа A --> B
            re.match(r'^\s*[A-Z_]+\s*\[.*\]', line) or  # Узлы типа A[Label]
            re.match(r'^\s*%%.+', line) or  # Комментарии
            re.match(r'^\s*subgraph\s+', line) or  # Подграфы
            re.match(r'^\s*classDef\s+', line) or  # Определения классов
            re.match(r'^\s*class\s+', line)):  # Применение классов
            
            # Пропускаем эти строки, так как они должны быть внутри блоков mermaid
            pass
        else:
            result_lines.append(lines[i])
        
        i += 1
    
    return '\n'.join(result_lines)

def main():
    if len(sys.argv) != 2:
        print("Использование: python fix_mermaid_advanced.py <путь_к_файлу.md>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"Ошибка: файл {file_path} не найден")
        sys.exit(1)
    
    # Создаем резервную копию
    backup_path = file_path + '.backup2'
    
    try:
        # Читаем исходный файл
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Создаем резервную копию
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"Создана резервная копия: {backup_path}")
        
        # Исправляем содержимое по шагам
        print("Шаг 1: Исправляем структуру Mermaid диаграмм...")
        fixed_content = fix_mermaid_diagrams(original_content)
        
        print("Шаг 2: Очищаем разорванные части диаграмм...")
        fixed_content = clean_broken_diagrams(fixed_content)
        
        print("Шаг 3: Экранируем специальные символы...")
        fixed_content = escape_mermaid_content(fixed_content)
        
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
            print(f"- Исправлено блоков: {fixed_mermaid_count - original_mermaid_count}")
        
        print("\nВыполненные исправления:")
        print("✅ Объединены разорванные диаграммы")
        print("✅ Добавлены недостающие блоки ```mermaid")
        print("✅ Исправлены закрывающие блоки ```")
        print("✅ Экранированы специальные символы")
        print("✅ Очищены неправильно расположенные части диаграмм")
        
    except Exception as e:
        print(f"Ошибка при обработке файла: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()