import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.ttk import Combobox, Progressbar
import os
from main import (
    bank_names, painment_system_names, create_personal_data, generate_dataset, write_into_csv_file,
    read_from_csv_file, parse_personal_data_file
)
import threading

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

    # Блокируем кнопку во время генерации
    btn_generate.config(state='disabled')
    progress_bar['value'] = 0
    progress_label.config(text="0%")
    window.update()

    # Запускаем генерацию в отдельном потоке
    thread = threading.Thread(target=generate_data_thread, args=(amount, bank_weights, pay_system_weights))
    thread.daemon = True
    thread.start()

def generate_data_thread(amount, bank_weights, pay_system_weights):
    try:
        # Генерация персональных данных (25%)
        personal_data = create_personal_data(amount, names_dict, surnames_dict, patronymics_dict)
        update_progress(25, "Генерация персональных данных...")

        # Генерация датасета (50%)
        dataset = generate_dataset(
            amount,
            specialists_list,
            symptoms_dict,
            analyses_with_prices_dict,
            personal_data,
            bank_weights=bank_weights,
            pay_system_weights=pay_system_weights
        )
        update_progress(75, "Генерация медицинских данных...")

        # Запись в CSV (25%)
        output_path = 'output/medical_dataset.csv'
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        write_into_csv_file(dataset, output_path)
        update_progress(100, "Завершено!")

        # Показываем сообщение об успехе
        window.after(0, lambda: messagebox.showinfo("Готово", f"Датасет из {amount} записей сохранен в {output_path}"))
        
    except Exception as e:
        window.after(0, lambda: messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}"))
    finally:
        window.after(0, lambda: btn_generate.config(state='normal'))

def update_progress(value, text):
    window.after(0, lambda: progress_bar.config(value=value))
    window.after(0, lambda: progress_label.config(text=f"{int(value)}% - {text}"))
    window.after(0, window.update)

# ===================== Создание окна =====================
window = tk.Tk()
window.title("Генератор медицинских данных")
window.geometry('700x550')
window.configure(bg="#2b2b2b")  # Тёмный фон

# Стили для тёмной темы
label_bg = "#2b2b2b"
label_fg = "#ffffff"
entry_bg = "#3c3f41"
entry_fg = "#ffffff"

# Количество строк
tk.Label(window, text="Количество строк:", bg=label_bg, fg=label_fg).pack(pady=5)
txt_amount = tk.Entry(window, bg=entry_bg, fg=entry_fg, insertbackground='white')
txt_amount.insert(0, "1000")
txt_amount.pack(pady=5)

# Веса банков
tk.Label(window, text="Веса банков (%):", bg=label_bg, fg=label_fg).pack(pady=(10, 0))

# Фрейм для названий банков
frame_bank_labels = tk.Frame(window, bg=label_bg)
frame_bank_labels.pack()

bank_labels = ["GAZPROMBANK", "MTS BANK", "SBERBANK", "TINKOFF", "VTB BANK"]
for lbl in bank_labels:
    tk.Label(frame_bank_labels, text=lbl, bg=label_bg, fg=label_fg, width=12).pack(side='left', padx=5)

# Фрейм для комбобоксов банков
frame_bank_combos = tk.Frame(window, bg=label_bg)
frame_bank_combos.pack(pady=(0, 10))

combo_bank1 = Combobox(frame_bank_combos, values=list(range(0,101)), width=10)
combo_bank2 = Combobox(frame_bank_combos, values=list(range(0,101)), width=10)
combo_bank3 = Combobox(frame_bank_combos, values=list(range(0,101)), width=10)
combo_bank4 = Combobox(frame_bank_combos, values=list(range(0,101)), width=10)
combo_bank5 = Combobox(frame_bank_combos, values=list(range(0,101)), width=10)

for c in [combo_bank1, combo_bank2, combo_bank3, combo_bank4, combo_bank5]:
    c.pack(side='left', padx=5)

combo_bank1.set("5")
combo_bank2.set("1")
combo_bank3.set("1")
combo_bank4.set("2")
combo_bank5.set("4")

# Веса платёжных систем
tk.Label(window, text="Веса платёжных систем (%):", bg=label_bg, fg=label_fg).pack(pady=(10, 0))

# Фрейм для названий платёжных систем
frame_ps_labels = tk.Frame(window, bg=label_bg)
frame_ps_labels.pack()

ps_labels = ["MIR", "VISA", "MASTERCARD"]
for lbl in ps_labels:
    tk.Label(frame_ps_labels, text=lbl, bg=label_bg, fg=label_fg, width=12).pack(side='left', padx=5)

# Фрейм для комбобоксов платёжных систем
frame_ps_combos = tk.Frame(window, bg=label_bg)
frame_ps_combos.pack(pady=(0, 20))

combo_ps1 = Combobox(frame_ps_combos, values=list(range(0,101)), width=10)
combo_ps2 = Combobox(frame_ps_combos, values=list(range(0,101)), width=10)
combo_ps3 = Combobox(frame_ps_combos, values=list(range(0,101)), width=10)

for c in [combo_ps1, combo_ps2, combo_ps3]:
    c.pack(side='left', padx=5)

combo_ps1.set("3")
combo_ps2.set("5")
combo_ps3.set("2")

# Прогрессбар
progress_frame = tk.Frame(window, bg=label_bg)
progress_frame.pack(pady=10, fill='x', padx=20)

progress_label = tk.Label(progress_frame, text="0% - Ожидание", bg=label_bg, fg=label_fg)
progress_label.pack()

progress_bar = Progressbar(progress_frame, orient='horizontal', length=600, mode='determinate')
progress_bar.pack(pady=5, fill='x')

# Кнопка генерации
btn_generate = tk.Button(window, text="Сгенерировать CSV", command=on_generate, bg="#3c3f41", fg="#ffffff")
btn_generate.pack(pady=20)

window.mainloop()