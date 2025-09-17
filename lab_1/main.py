import random
import csv
from datetime import datetime, timedelta
import os
import faker
from faker.providers import person, phone_number, ssn  # for generating personal data
from typing import List, Dict

bank_names = ['GAZPROMBANK','MTS BANK','SBERBANK OF RUSSIA','TINKOFF BANK','VTB BANK']
painment_system_names = ['MIR','VISA','MASTERCARD']


def read_from_csv_file(file_path: str, delimiter: str = ';') -> List[List[str]]:
    data = []
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=delimiter)
        for row in reader:
            if row:
                data.append(row)
    return data



import random
import faker
from typing import List

def generate_personal_data(amount=1000) -> List[List[str]]:
    """
    Использует faker для генерации ФИО, паспортных данных и СНИЛС на русском языке.
    Возвращает список списков: [ ФИО ; паспорт ; СНИЛС ]
    """
    # Коды регионов основных фабрик Госзнака
    region_codes = [
        40,  # Москва (исторический)
        45,  # Москва
        50,  # Московская область
        77,  # Москва (современный)
        78,  # Санкт-Петербург
        59,  # Пермский край
        47,  # Ленинградская область
        66   # Свердловская область
    ]
    
    # Годы выпуска бланков (2007-2025)
    years = list(range(2007, 2026))
    
    fake = faker.Faker('ru_RU')
    personal_data = []
    
    for _ in range(amount):
        fio = fake.name()
        
        # Генерация серии паспорта: код региона + год выпуска
        region_code = random.choice(region_codes)
        year = random.choice(years)
        passport_series = f"{region_code:02d}{year % 100:02d}"  # Формат: 4023
        
        # Генерация номера паспорта (6 цифр)
        passport_number = f"{random.randint(100000, 999999):06d}"
        
        passport = f"{passport_series} {passport_number}"
        
        # СНИЛС - формат XXXXXXXXX XX
        snils_numbers = [random.randint(0, 9) for _ in range(9)]
        snils_control = [random.randint(0, 9) for _ in range(2)]
        snils = f"{snils_numbers[0]}{snils_numbers[1]}{snils_numbers[2]}{snils_numbers[3]}{snils_numbers[4]}{snils_numbers[5]}{snils_numbers[6]}{snils_numbers[7]}{snils_numbers[8]} {snils_control[0]}{snils_control[1]}"
        
        personal_data.append([fio, passport, snils])
    
    return personal_data


def generate_random_specialist(specialists_list: List[str]) -> str:
    # Считается, что первая специальность - самая популярная
    weights = [1/(i+1) for i in range(len(specialists_list))]
    total = sum(weights)
    normalized_weights = [w / total for w in weights]
    return random.choices(specialists_list, weights=normalized_weights)[0]


def choose_symptoms(specialist: str, symptoms_dict: Dict[str, List[str]]) -> List[str]:
    symptoms = symptoms_dict.get(specialist, [])
    count = random.randint(1, max(1, min(7, len(symptoms))))
    return random.sample(symptoms, count)


def check_realistic_and_seasonal_symptoms(
        symptoms: List[str], visit_date: datetime, seasonality_index: Dict[str, List[float]]
    ) -> List[str]:
    month = visit_date.month
    filtered_symptoms = []
    for symptom in symptoms:
        weights = seasonality_index.get(symptom, [1.0]*12)
        if random.random() < weights[month - 1]:
            filtered_symptoms.append(symptom)
    return filtered_symptoms if filtered_symptoms else symptoms


def generate_random_datetime(min_time="09:00", max_time="21:00") -> str:
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    random_date = start_date + timedelta(days=random_days)

    min_t = datetime.strptime(min_time, "%H:%M").time()
    max_t = datetime.strptime(max_time, "%H:%M").time()
    min_sec = min_t.hour*3600 + min_t.minute*60
    max_sec = max_t.hour*3600 + max_t.minute*60
    random_sec = random.randint(min_sec, max_sec)
    random_time = (datetime.min + timedelta(seconds=random_sec)).time()

    generated_datetime = datetime.combine(random_date, random_time)
    return generated_datetime.strftime("%Y-%m-%dT%H:%M")


def generate_analyses(specialist: str, analyses_with_prices_dict: Dict[str, List[tuple]]) -> List[str]:
    """
    Генерирует список анализов для специалиста
    analyses_with_prices_dict содержит кортежи: (название_анализа, цена)
    """
    analyses_with_prices = analyses_with_prices_dict.get(specialist, [])
    
    # Извлекаем только названия анализов (первый элемент кортежа)
    analyses_names = [analysis[0] for analysis in analyses_with_prices]
    
    count = random.randint(1, max(1, min(5, len(analyses_names))))
    selected_analyses = random.sample(analyses_names, count)
    
    return selected_analyses

def calculate_cost_based_on_analyses(analyses: List[str], analyses_with_prices_dict: Dict[str, List[tuple]], specialist: str) -> float:
    """
    Вычисляет стоимость на основе выбранных анализов
    """
    total_cost = 0
    available_analyses = analyses_with_prices_dict.get(specialist, [])
    
    # Создаем словарь для быстрого поиска цен
    price_dict = {analysis[0]: float(analysis[1]) for analysis in available_analyses}
    
    for analysis in analyses:
        if analysis in price_dict:
            total_cost += price_dict[analysis]
        else:
            # Если цена не найдена, добавляем случайную стоимость
            total_cost += random.uniform(500, 5000)
    
    return round(total_cost, 2)

def generate_one_card_2(pay_system, bank):
    card_format = '{fig12} {fig3} {fig4}'
    if pay_system == 'MIR':
        if bank == 'SBERBANK OF RUSSIA':
            figures = '2202 20'
        elif bank == 'TINKOFF BANK':
            figures = '2200 70'
        elif bank == 'VTB BANK':
            figures = '2200 40'
        else:
            figures = '2200 56'  # GAZPROMBANK
    elif pay_system == 'MASTERCARD':
        if bank == 'SBERBANK OF RUSSIA':
            figures = '5228 60'
        elif bank == 'TINKOFF BANK':
            figures = '5389 94'
        elif bank == 'VTB BANK':
            figures = '5211 94'
        else:
            figures = '5112 23'  # GAZPROMBANK
    else:  # VISA
        if bank == 'SBERBANK OF RUSSIA':
            figures = '4039 33'
        elif bank == 'TINKOFF BANK':
            figures = '4377 73'
        elif bank == 'VTB BANK':
            figures = '4986 29'
        else:
            figures = '4306 43'  # GAZPROMBANK
    argz = {'fig12': figures + str(random.randint(10, 99)),
            'fig3': str(random.randint(1000, 9999)),
            'fig4': str(random.randint(1000, 9999))}
    return card_format.format(**argz)


def generate_one_card(
        personal: List[str], specialist: str, symptoms: List[str], visit_date: str,
        analyses: List[str], analysis_date: str, cost: float, payment_card: str
    ) -> Dict:
    # Собираем все данные в словарь для одной записи
    return {
        "ФИО": personal[0],
        "Паспорт": personal[1],
        "СНИЛС": personal[2],
        "Симптомы": ", ".join(symptoms),
        "Врач": specialist,
        "Дата_посещения": visit_date,
        "Анализы": ", ".join(analyses), 
        "Дата_анализов": analysis_date,
        "Стоимость": cost,
        "Карта_оплаты": payment_card
    }


def generate_one_output(card: Dict) -> List[str]:
    # Форматируем словарь в список по нужному порядку
    return [
        card["ФИО"],
        card["Паспорт"],
        card["СНИЛС"],
        card["Симптомы"],
        card["Врач"],
        card["Дата_посещения"],
        card["Анализы"],
        card["Дата_анализов"],
        str(int(card['Стоимость'])),
        card["Карта_оплаты"]
    ]


def generate_dataset(
    n: int,
    specialists_list: List[str],
    symptoms_dict: Dict[str, List[str]],
    analyses_with_prices_dict: Dict[str, List[tuple]],
    seasonality_index: Dict[str, List[float]],
    personal_data: List[List[str]]
) -> List[List[str]]:
    dataset = []
    for _ in range(n):
        person = random.choice(personal_data)
        specialist = generate_random_specialist(specialists_list)
        visit_dt = generate_random_datetime()
        symptoms = choose_symptoms(specialist, symptoms_dict)

        symptoms_checked = check_realistic_and_seasonal_symptoms(
            symptoms,
            datetime.strptime(visit_dt, "%Y-%m-%dT%H:%M"),
            seasonality_index
        )
        analyses = generate_analyses(specialist, analyses_with_prices_dict)
        analysis_dt = generate_random_datetime()
        cost = calculate_cost_based_on_analyses(analyses, analyses_with_prices_dict, specialist)

        pay_sys = random.choice(painment_system_names)
        bank = random.choice(bank_names)
        card = generate_one_card_2(pay_sys, bank)

        card_data = generate_one_card(person, specialist, symptoms_checked, visit_dt, analyses, analysis_dt, cost, card)
        output_row = generate_one_output(card_data)
        dataset.append(output_row)
    return dataset



def write_into_csv_file(data: List[List[str]], path: str = 'output/medical_dataset.csv'):
    headers = ['ФИО', 'Паспорт', 'СНИЛС', 'Симптомы', 'Врач', 'Дата_посещения', 'Анализы', 'Дата_анализов', 'Стоимость', 'Карта_оплаты']
    file_exists = os.path.isfile(path)
    with open(path, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        if not file_exists:
            writer.writerow(headers)
        writer.writerows(data)


if __name__ == "__main__":
    # Пример загрузки данных
    med_specialities = read_from_csv_file('data/medical_specialities.csv')
    
    # Разбор спец. в список строк для генерации
    specialists_list = [row[0].strip() for row in med_specialities]

    # Загрузить тесты и цены
    med_tests_prices = read_from_csv_file('data/medical_tests_and_prices.csv')
    
    # Словарь для анализов с ценами
    analyses_with_prices_dict = {}

    for spec_row, tests_row in zip(med_specialities, med_tests_prices):
        spec = spec_row[0].strip()
        
        tests_with_prices = [item.strip() for item in tests_row if item.strip()]
        
        analyses = []
        for item in tests_with_prices:
            parts = [part.strip() for part in item.split(',', 1)]
            if len(parts) >= 2:
                # Сохраняем как кортеж (название, цена)
                analyses.append((parts[0], parts[1]))
            elif len(parts) == 1:
                # Только название, без цены
                analyses.append((parts[0], "0"))
        
        analyses_with_prices_dict[spec] = analyses
    
    symptoms_dict = {}
    for row in med_specialities:
        if len(row) >= 2:  # Проверяем, что есть симптомы
            spec = row[0].strip()
            symptoms = [s.strip() for s in row[1].split(',')]
            symptoms_dict[spec] = symptoms
        else:
            print(f"Предупреждение: нет симптомов для специальности {row[0]}")


    # Сезонность (простой пример, коэффициенты для каждого месяца)
    seasonality_index = {symptom: [1.0]*12 for symptom in ['симптом1', 'симптом2', 'симптом3']}  # простая заглушка

    # Генерация персональных данных (пример)
    personal_data = generate_personal_data(1000)

    # Генерация датасета на 10 записей
    dataset = generate_dataset(
        10,
        specialists_list,
        symptoms_dict,
        analyses_with_prices_dict,
        seasonality_index,
        personal_data
    )

    # Запись в CSV
    write_into_csv_file(dataset)