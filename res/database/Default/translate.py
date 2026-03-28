import pandas as pd
import re
import os

# --- НАСТРОЙКИ ---
excel_file = 'Films.xlsx'  # Имя твоего файла Excel
sheet_name = 'Лист5'               # Имя листа с переводом
xml_file = 'database_programmes.xml' # Оригинальный файл игры
output_file = 'database_programmes_translated.xml' # Куда сохранить результат

def translate_xml():
    # 1. Загружаем переводы из Excel
    print("Загружаем Excel...")
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    
    # Создаем словарь для быстрого поиска по GUID
    # Предполагаем колонки: A (GUID), B (Title RU), C (Desc RU)
    # Если колонки называются иначе, поправь названия ниже
    translations = {}
    for _, row in df.iterrows():
        guid = str(row[5]).strip()
        title_ru = str(row[3]).strip()
        desc_ru = str(row[4]).strip()
        translations[guid] = {'title': title_ru, 'desc': desc_ru}
        if guid != 'nan' and len(guid) > 10:
            translations[guid] = {'title': title_ru, 'desc': desc_ru}

    # 2. Читаем XML
    print("Читаем XML...")
    with open(xml_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 3. Улучшенная функция замены
    def replace_func(match):
        block = match.group(0)
        guid = match.group(1)
        
        if guid in translations:
            t_data = translations[guid]
            
            # 1. Вставляем <ru> в блок <title> (именно в первый, не путая с title_original)
            # Ищем <title>, за которым следуют другие теги, но НЕ </title_original>
            if f'<ru>{t_data["title"]}</ru>' not in block:
                # Меняем только внутри ПЕРВОГО встреченного тега <title>
                block = re.sub(r'(<title>.*?</title>)', 
                               rf'\1\n\t\t\t\t<ru>{t_data["title"]}</ru>', 
                               block, count=1, flags=re.DOTALL)
            
            # 2. Вставляем <ru> в блок <description>
            if f'<ru>{t_data["desc"]}</ru>' not in block:
                block = re.sub(r'(<description>.*?</description>)', 
                               rf'\1\n\t\t\t\t<ru>{t_data["desc"]}</ru>', 
                               block, count=1, flags=re.DOTALL)
            return block
        
        return block

    # Новая регулярка: ищет guid внутри тега, у которого могут быть любые атрибуты
    pattern = r'<programme guid="(.*?)" .*?>.*?</programme>'
    
    print("Внедряем перевод...")
    new_content = re.sub(pattern, replace_func, content, flags=re.DOTALL)
    # 4. Сохраняем результат
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Готово! Файл сохранен как: {output_file}")

if __name__ == "__main__":
    translate_xml()