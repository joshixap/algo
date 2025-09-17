import tkinter as tk
from tkinter import messagebox
from tkinter.ttk import Combobox
import os
from main import (
    bank_names, painment_system_names, create_personal_data, generate_dataset, write_into_csv_file,
    read_from_csv_file, parse_personal_data_file
)

# ===================== Загрузка и подготовка данных =====================
# Загрузка медицинских специальностей
med_specialities = read_from_csv_file('data/medical_specialities.csv')
specialists_list = [row[1].strip() for row in med_specialities]

# Загрузка тестов и цен
med_tests_prices = read_from_csv_file('data/medical_tests_and_prices.csv')
analyses_with_prices_dict = {}
for spec_row, tests_row in zip(med_specialities, med_tests_prices):
    spec = spec_row[1].strip()
    tests_with_prices = [item.strip() for item in tests_row if item.strip()]
    analyses = []
    for item in tests_with_prices:
        parts = [part.strip() for part in item.split(',', 1)]
        if len(parts) >= 2:
            analyses.append((parts[0], parts[1]))
        elif len(parts) == 1:
            analyses.append((parts[0], "0"))
    analyses_with_prices_dict[spec] = analyses

# Симптомы для каждой специальности
symptoms_dict = {}
for row in med_specialities:
    if len(row) >= 3:
        spec = row[1].strip()
        symptoms_dict[spec] = [s.strip() for s in row[2].split(',')]
    else:
        print(f"Предупреждение: нет симптомов для специальности {row[0]}")

# Словари для ФИО
names_dict = parse_personal_data_file("data/personal_data_name.csv")
surnames_dict = parse_personal_data_file("data/personal_data_surname.csv")
patronymics_dict = parse_personal_data_file("data/personal_data_patronymic.csv")

# ===================== GUI =====================
def on_generate():
    try:
        amount = int(txt_amount.get())
    except ValueError:
        messagebox.showerror("Ошибка", "Количество строк должно быть числом")
        return

    # Получаем веса банков и платёжных систем
    try:
        bank_weights = {
            'GAZPROMBANK': float(combo_bank1.get()),
            'MTS BANK': float(combo_bank2.get()),
            'SBERBANK OF RUSSIA': float(combo_bank3.get()),
            'TINKOFF BANK': float(combo_bank4.get()),
            'VTB BANK': float(combo_bank5.get())
        }
        pay_system_weights = {
            'MIR': float(combo_ps1.get()),
            'VISA': float(combo_ps2.get()),
            'MASTERCARD': float(combo_ps3.get())
        }
    except ValueError:
        messagebox.showerror("Ошибка", "Все веса должны быть числами")
        return

    # Проверка, что сумма весов не равна нулю
    if sum(bank_weights.values()) == 0 or sum(pay_system_weights.values()) == 0:
        messagebox.showerror("Ошибка", "Сумма весов не может быть нулевой")
        return

    # Генерация персональных данных
    personal_data = create_personal_data(amount, names_dict, surnames_dict, patronymics_dict)

    # Генерация датасета
    dataset = generate_dataset(
        amount,
        specialists_list,
        symptoms_dict,
        analyses_with_prices_dict,
        personal_data,
        bank_weights=bank_weights,
        pay_system_weights=pay_system_weights
    )

    # Запись в CSV
    output_path = 'output/medical_dataset.csv'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    write_into_csv_file(dataset, output_path)
    messagebox.showinfo("Готово", f"Датасет из {amount} записей сохранен в {output_path}")

# Создаем окно
window = tk.Tk()
window.title("Генератор медицинских данных")
window.geometry('650x400')

tk.Label(window, text="Количество строк:").pack()
txt_amount = tk.Entry(window)
txt_amount.insert(0, "1000")
txt_amount.pack()

# Веса банков
tk.Label(window, text="Веса банков (%):").pack()
frame_banks = tk.Frame(window)
frame_banks.pack(pady=5)
combo_bank1 = Combobox(frame_banks, values=list(range(0,101)), width=5)
combo_bank2 = Combobox(frame_banks, values=list(range(0,101)), width=5)
combo_bank3 = Combobox(frame_banks, values=list(range(0,101)), width=5)
combo_bank4 = Combobox(frame_banks, values=list(range(0,101)), width=5)
combo_bank5 = Combobox(frame_banks, values=list(range(0,101)), width=5)
for c in [combo_bank1, combo_bank2, combo_bank3, combo_bank4, combo_bank5]:
    c.pack(side='left', padx=5)
combo_bank1.set("5")
combo_bank2.set("1")
combo_bank3.set("1")
combo_bank4.set("2")
combo_bank5.set("4")

# Веса платёжных систем
tk.Label(window, text="Веса платёжных систем (%):").pack()
frame_ps = tk.Frame(window)
frame_ps.pack(pady=5)
combo_ps1 = Combobox(frame_ps, values=list(range(0,101)), width=5)
combo_ps2 = Combobox(frame_ps, values=list(range(0,101)), width=5)
combo_ps3 = Combobox(frame_ps, values=list(range(0,101)), width=5)
for c in [combo_ps1, combo_ps2, combo_ps3]:
    c.pack(side='left', padx=5)
combo_ps1.set("3")
combo_ps2.set("5")
combo_ps3.set("2")

# Кнопка генерации
tk.Button(window, text="Сгенерировать CSV", command=on_generate).pack(pady=20)

window.mainloop()
