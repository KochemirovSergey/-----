#!/usr/bin/env python3
"""
Скрипт для исправления Mermaid диаграмм в Markdown файлах для GitHub
Автоматически оборачивает диаграммы в правильные блоки кода с указанием языка mermaid
"""

import re
import sys
import os

def fix_mermaid_diagrams(content):
    """
    Исправляет Mermaid диаграммы в тексте
    
    Ищет паттерны:
    1. flowchart TD/LR/TB/RL (без блока кода)
    2. graph TD/TB/LR/RL (без блока кода)  
    3. Блоки кода без указания mermaid
    
    И оборачивает их в правильные блоки ```mermaid
    """
    
    # Паттерн для поиска незакрытых Mermaid диаграмм
    # Ищем строки, начинающиеся с flowchart или graph, которые не находятся в блоке кода
    mermaid_patterns = [
        r'^(flowchart\s+(?:TD|TB|LR|RL|BT))',
        r'^(graph\s+(?:TD|TB|LR|RL|BT))',
    ]
    
    lines = content.split('\n')
    result_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Проверяем, является ли текущая строка началом Mermaid диаграммы
        is_mermaid_start = False
        for pattern in mermaid_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                is_mermaid_start = True
                break
        
        if is_mermaid_start:
            # Проверяем, не находится ли уже в блоке кода
            # Ищем предыдущие строки на наличие ```mermaid
            in_code_block = False
            for j in range(max(0, i-10), i):  # Проверяем последние 10 строк
                prev_line = lines[j].strip()
                if prev_line.startswith('```mermaid'):
                    in_code_block = True
                    break
                elif prev_line.startswith('```') and prev_line != '```mermaid':
                    break
            
            if not in_code_block:
                # Добавляем открывающий блок
                result_lines.append('```mermaid')
                result_lines.append(lines[i])
                
                # Ищем конец диаграммы
                i += 1
                while i < len(lines):
                    current_line = lines[i].rstrip()
                    result_lines.append(current_line)
                    
                    # Проверяем условия окончания диаграммы
                    if (current_line.strip() == '' and 
                        i + 1 < len(lines) and 
                        not lines[i + 1].strip().startswith(('    ', '-', '|', '%', 'subgraph', 'classDef', 'class '))):
                        # Пустая строка и следующая строка не относится к диаграмме
                        break
                    elif (current_line.strip().startswith('```') and 
                          current_line.strip() != '```mermaid'):
                        # Встретили закрывающий блок кода
                        result_lines.pop()  # Убираем неправильный закрывающий блок
                        break
                    
                    i += 1
                
                # Добавляем закрывающий блок
                result_lines.append('```')
                result_lines.append('')  # Пустая строка после блока
            else:
                result_lines.append(lines[i])
        else:
            result_lines.append(lines[i])
        
        i += 1
    
    return '\n'.join(result_lines)

def fix_existing_code_blocks(content):
    """
    Исправляет существующие блоки кода, добавляя mermaid где необходимо
    """
    # Паттерн для блоков кода без указания языка, содержащих Mermaid
    pattern = r'```\n((?:flowchart|graph)\s+(?:TD|TB|LR|RL|BT).*?)\n```'
    
    def replace_block(match):
        diagram_content = match.group(1)
        return f'```mermaid\n{diagram_content}\n```'
    
    return re.sub(pattern, replace_block, content, flags=re.DOTALL | re.MULTILINE)

def main():
    if len(sys.argv) != 2:
        print("Использование: python fix_mermaid.py <путь_к_файлу.md>")
        print("Пример: python fix_mermaid.py readme.md")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"Ошибка: файл {file_path} не найден")
        sys.exit(1)
    
    if not file_path.endswith('.md'):
        print("Предупреждение: файл не имеет расширения .md")
    
    # Создаем резервную копию
    backup_path = file_path + '.backup'
    
    try:
        # Читаем исходный файл
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Создаем резервную копию
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"Создана резервная копия: {backup_path}")
        
        # Исправляем содержимое
        print("Исправляем Mermaid диаграммы...")
        fixed_content = fix_mermaid_diagrams(original_content)
        fixed_content = fix_existing_code_blocks(fixed_content)
        
        # Записываем исправленный файл
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print(f"Файл {file_path} успешно исправлен!")
        print("\nИсправления:")
        print("- Добавлены блоки ```mermaid для незащищенных диаграмм")
        print("- Исправлены существующие блоки кода")
        print("- Добавлены закрывающие блоки ```")
        
        # Показываем статистику
        original_mermaid_count = original_content.count('```mermaid')
        fixed_mermaid_count = fixed_content.count('```mermaid')
        
        print(f"\nСтатистика:")
        print(f"- Блоков ```mermaid до: {original_mermaid_count}")
        print(f"- Блоков ```mermaid после: {fixed_mermaid_count}")
        print(f"- Добавлено блоков: {fixed_mermaid_count - original_mermaid_count}")
        
    except Exception as e:
        print(f"Ошибка при обработке файла: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()