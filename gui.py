import tkinter as tk
import requests
from tkinter import ttk, messagebox
from database import DatabaseManager, verify_master_password
from encryption import CryptoManager
import webbrowser

class MainApp:
    def __init__(self, root, master_password: str):
        self.root = root
        self.root.deiconify()
        self.root.configure(background="#2d2d2d")
        self.root.title("LockUp")
        self.root.geometry("800x600")
        
        self.db = DatabaseManager(master_password=master_password)
        self.crypto = CryptoManager(master_password)

        self.current_theme = "dark"
        
        self.setup_styles()
        self.create_widgets()
        self.load_data()

        self.current_version = "1.0.0"
        self.check_for_updates()

    def check_for_updates(self):
        """Проверяет наличие обновлений через удаленный JSON-файл."""
        try:
            response = requests.get(
                "https://raw.githubusercontent.com/GottaGrizzly/LockUp/main/version.json",
                timeout=5
            )
            data = response.json()
            
            if data["latest_version"] > self.current_version:
                self.show_update_dialog(data)
        except requests.exceptions.RequestException:
            messagebox.showerror("Ошибка", "Не удалось проверить обновления.")
        except Exception as e:
            print(f"Ошибка: {e}")

    def show_update_dialog(self, update_data):
        """Показывает диалоговое окно с предложением обновиться."""
        answer = messagebox.askyesno(
            "Доступно обновление",
            f"Версия {update_data['latest_version']}:\n{update_data['changelog']}\n\nСкачать сейчас?"
        )
        if answer:
            webbrowser.open(update_data["download_url"])

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self._configure_styles()

    def _configure_styles(self):
        self.style.configure("TButton", 
            background="#404040",
            foreground="#ffffff",
            width=12,
            padding=5,
            font=("Arial", 10)
        )

        # Стили для радиокнопок
        self.style.configure("TRadiobutton",
                            background="#2d2d2d",
                            foreground="#ffffff",
                            indicatorcolor="#ffffff")
        self.style.map("TRadiobutton",
                    background=[('active', '#404040')],
                    foreground=[('active', '#ffffff')])
        
        # Базовые стили для всех тем
        self.style.configure(".", 
                            background="#2d2d2d", 
                            foreground="#ffffff",
                            fieldbackground="#3d3d3d",
                            borderwidth=0)
        
        # Стили для кнопок
        self.style.configure("TButton",
                            background="#404040",
                            foreground="#ffffff",
                            bordercolor="#404040")
        self.style.map("TButton",
                    background=[('active', '#505050' if self.current_theme == "dark" else '#d0d0d0')],
                    foreground=[('active', '#ffffff' if self.current_theme == "dark" else '#000000')])
        
        self.style.configure("Treeview.Heading",
                        background="#2d2d2d",
                        foreground="#ffffff",
                        relief="flat")
        self.style.map("Treeview.Heading",
                  background=[('active', '#404040')])
        
        # Стили для чекбоксов
        self.style.configure("TCheckbutton",
                            background="#2d2d2d",
                            foreground="#ffffff")
        self.style.map("TCheckbutton",
                    background=[('active', '#3d3d3d' if self.current_theme == "dark" else '#e0e0e0')],
                    foreground=[('active', '#ffffff' if self.current_theme == "dark" else '#000000')])
        
        # Стиль для кнопки настроек
        self.style.configure("Settings.TButton",
                            borderwidth=0,
                            relief="flat",
                            highlightthickness=0)

    def create_widgets(self):
        # Заголовок
        self.header_frame = ttk.Frame(self.root)
        self.header_frame.pack(pady=20)
        
        self.logo = tk.PhotoImage(file="logo.png").subsample(2,2)
        ttk.Label(self.header_frame, image=self.logo).pack(side=tk.LEFT)
        ttk.Label(self.header_frame, text="LockUp", font=("Arial", 24, "bold")).pack(side=tk.LEFT, padx=10)

        # Иконка настроек (исправленная версия)
        self.settings_icon = tk.PhotoImage(file="settings_icon.png").subsample(5,5)
        self.settings_button = ttk.Button(
            self.header_frame,
            image=self.settings_icon,
            command=self.open_settings,
            style="Settings.TButton"
        )
        self.settings_button.pack(side=tk.RIGHT, padx=10)

        # Новая иконка "Информация"
        self.info_icon = tk.PhotoImage(file="info_icon.png").subsample(5,5)
        self.info_button = ttk.Button(
            self.header_frame,
            image=self.info_icon,
            command=self.open_info,
            style="Settings.TButton"
        )
        self.info_button.pack(side=tk.RIGHT, padx=10)

        # Treeview и кнопки управления (перенесено из open_info)
        self.tree_frame = ttk.Frame(self.root)
        self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.tree = ttk.Treeview(self.tree_frame, columns=("Service", "Username", "Password", "Date"), show="headings")
        for col in ["Service", "Username", "Password", "Date"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        self.controls = ttk.Frame(self.root)
        self.controls.pack(pady=10)
        
        ttk.Button(self.controls, text="Добавить", command=self.add_entry).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.controls, text="Редактировать", command=self.edit_entry, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.controls, text="Удалить", command=self.delete_entry).pack(side=tk.LEFT, padx=5)

    def open_info(self):
        InfoWindow(self.root)

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        records = self.db.get_all_passwords()
        for row in records:
            self.tree.insert("", tk.END, 
                        values=(row[1], row[2], "•"*12, row[4]),
                        tags=(row[0],))

    def open_settings(self):
        SettingsWindow(self.root, self)

    def change_theme(self, theme):
        self.style.theme_use("clam")
        self.root.update_idletasks()
        self.current_theme = theme
        bg_color = "#2d2d2d" if theme == "dark" else "#f0f0f0"
        fg_color = "#ffffff" if theme == "dark" else "#000000"
        field_bg = "#3d3d3d" if theme == "dark" else "#ffffff"
        button_bg = "#404040" if theme == "dark" else "#e0e0e0"
        
        # Обновление основных стилей
        self.style.configure(".", 
                            background=bg_color,
                            foreground=fg_color,
                            fieldbackground=field_bg)
        
        # Специфические стили для разных виджетов
        self.style.map("TButton",
                  background=[('active', '#505050' if theme == "dark" else '#d0d0d0')],
                  foreground=[('active', '#ffffff' if theme == "dark" else '#000000')])
        self.style.map("TCheckbutton",
                  background=[('active', '#3d3d3d' if theme == "dark" else '#e0e0e0')],
                  foreground=[('active', '#ffffff' if theme == "dark" else '#000000')])
        self.style.configure("Treeview.Heading",
                            background=bg_color,
                            foreground=fg_color)
        self.style.map("Treeview.Heading",
                    background=[('active', button_bg)])
        
        # Обновление стилей радиокнопок
        self.style.configure("TRadiobutton",
                            background=bg_color,
                            foreground=fg_color)
        self.style.map("TRadiobutton",
                    background=[('active', button_bg)],
                    foreground=[('active', fg_color)])
        
        # Принудительное обновление всех элементов
        self.root.config(bg=bg_color)
        self._refresh_all_windows(bg_color)

        # Принудительно обновляем все Entry-поля
        self.style.configure("Dynamic.TEntry",
                            fieldbackground=field_bg,
                            foreground=fg_color)
        self.root.update()

    def _refresh_all_windows(self, bg_color):
        for child in self.root.winfo_children():
            if isinstance(child, tk.Toplevel):
                child.configure(background=bg_color)
                # Принудительно обновляем все дочерние виджеты
                for widget in child.winfo_children():
                    if isinstance(widget, ttk.Entry):
                        widget.configure(style="TEntry")
                    elif isinstance(widget, ttk.Checkbutton):
                        widget.configure(style="TCheckbutton")
        self.tree.configure(style="Treeview")

    def _update_child_widgets(self, parent, bg_color):
        for widget in parent.winfo_children():
            if isinstance(widget, ttk.Frame):
                widget.configure(style="TFrame")
            elif isinstance(widget, ttk.Checkbutton):
                widget.configure(style="TCheckbutton")
            # Рекурсивное обновление
            self._update_child_widgets(widget, bg_color)

    def _update_widget_theme(self, widget, bg, fg):
        try:
            if isinstance(widget, (ttk.Entry, ttk.Combobox)):
                widget.configure(style="TEntry")
            elif isinstance(widget, ttk.Button):
                widget.configure(style="TButton")
            elif isinstance(widget, ttk.Checkbutton):
                widget.configure(style="TCheckbutton")
            
            # Для стандартных tkinter виджетов
            if isinstance(widget, tk.Entry):
                widget.configure(bg=self.style.lookup("TEntry", "fieldbackground"),
                                fg=self.style.lookup("TEntry", "foreground"))
            
            widget.update_idletasks()
        except Exception as e:
            pass

    def add_entry(self):
        EntryWindow(
            self.root,
            self.db,
            self.crypto,
            self.load_data
        )

    def edit_entry(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для редактирования")
            return
    
        try:
            # Получаем ID из первого столбца таблицы
            item = self.tree.item(selected[0])
            record_id = item['tags'][0]
            
            record = self.db.get_password_by_id(record_id)
            if not record:
                messagebox.showerror("Ошибка", "Запись не найдена")
                return
                
            EditWindow(
                self.root,
                self.db,
                self.crypto,
                self.load_data,
                record_id,
                record[1],  # service
                record[2],  # username
                self.crypto.decrypt(record[3])  # password
            )
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при редактировании: {str(e)}")

    def delete_entry(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления")
            return
            
        if messagebox.askyesno("Подтверждение", "Удалить выбранную запись?"):
            try:
                # Получаем ID из тегов
                item = self.tree.item(selected[0])
                record_id = item['tags'][0]
                self.db.delete_password(record_id)
                self.load_data()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при удалении: {str(e)}")

class SettingsWindow:
    def __init__(self, parent, main_app):
        if hasattr(parent, '_settings_win') and parent._settings_win.winfo_exists():
            parent._settings_win.destroy()

        self.parent = parent
        self.main_app = main_app

        # Создание нового окна
        self.window = tk.Toplevel(parent)
        parent._settings_win = self.window  # Сохраняем ссылку на окно
        
        self.window.configure(background=self.main_app.style.lookup(".", "background"))
        self.window.title("Настройки")
        self.window.geometry("300x260")
        
        self.theme_var = tk.StringVar(value=self.main_app.current_theme)
        self.create_widgets()
        
        self.window.transient(parent)
        self.window.grab_set()
        parent.wait_window(self.window)
        main_app.load_data()

    def create_widgets(self):
        main_frame = ttk.Frame(self.window)
        main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        # Выбор темы
        ttk.Label(main_frame, text="Тема оформления:").pack(anchor=tk.W)
        ttk.Radiobutton(
            main_frame, 
            text="Тёмная", 
            variable=self.theme_var, 
            value="dark",
             style="TRadiobutton",
            command=lambda: self.main_app.change_theme("dark")
        ).pack(anchor=tk.W)
        
        ttk.Radiobutton(
            main_frame, 
            text="Светлая", 
            variable=self.theme_var, 
            value="light", 
            command=lambda: self.main_app.change_theme("light")
        ).pack(anchor=tk.W)
        
        # Экспорт/Импорт
        ttk.Separator(main_frame).pack(fill=tk.X, pady=10)
        ttk.Button(main_frame, text="Экспорт данных", command=self.export_data, width=20).pack(pady=5, fill=tk.X)
        ttk.Button(main_frame, text="Импорт данных", command=self.import_data, width=20).pack(pady=5, fill=tk.X)

        ttk.Separator(main_frame).pack(fill=tk.X, pady=10)
        ttk.Button(
            main_frame, 
            text="Проверить обновления", 
            command=lambda: self.main_app.check_for_updates(),  # Вызов метода из MainApp
            width=20
        ).pack(pady=5, fill=tk.X)

    def export_data(self):
        # Реализация экспорта
        messagebox.showinfo("Экспорт", "Функция экспорта данных")

    def import_data(self):
        # Реализация импорта
        messagebox.showinfo("Импорт", "Функция импорта данных")

class EntryWindow:
    def __init__(self, parent, db, crypto, refresh_callback):
        self.parent = parent
        self.db = db
        self.crypto = crypto
        self.refresh = refresh_callback
        
        self.window = tk.Toplevel(parent)
        self.window.configure(background=self.parent.cget("background"))
        self.window.title("Новая запись")
        self.window.geometry("400x300")

        self.style = ttk.Style(self.window)
        
        self.service_var = tk.StringVar()
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.show_password = tk.BooleanVar(value=False)

        self.create_widgets()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.window)
        main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Автоматическое определение цвета текста
        bg_color = self.parent.cget("background")
        fg_color = "#000000" if bg_color == "#f0f0f0" else "#ffffff"
        field_bg = "#ffffff" if bg_color == "#f0f0f0" else "#3d3d3d"

        # Динамические стили
        self.style.configure("Dynamic.TEntry", 
                            fieldbackground=field_bg,
                            foreground=fg_color)
        
        # Поля ввода
        ttk.Label(main_frame, text="Сервис*:").grid(row=0, column=0, sticky=tk.W, pady=5)
        entry_service = ttk.Entry(main_frame, textvariable=self.service_var, style="Dynamic.TEntry")
        entry_service.grid(row=0, column=1, sticky=tk.EW, pady=5)
        
        ttk.Label(main_frame, text="Логин*:").grid(row=1, column=0, sticky=tk.W, pady=5)
        entry_username = ttk.Entry(main_frame, textvariable=self.username_var, style="Dynamic.TEntry")
        entry_username.grid(row=1, column=1, sticky=tk.EW, pady=5)
        
        ttk.Label(main_frame, text="Пароль*:").grid(row=2, column=0, sticky=tk.W, pady=5)
        password_entry = ttk.Entry(main_frame, textvariable=self.password_var, show="*", style="Dynamic.TEntry")
        password_entry.grid(row=2, column=1, sticky=tk.EW, pady=5)
        
        # Чекбокс показа пароля
        check_style = ttk.Style()
        check_style.configure("Light.TCheckbutton", 
                            background=self.parent.cget("background"),
                            foreground="#000000")
        
        ttk.Checkbutton(
            main_frame, 
            text="Показать пароль", 
            variable=self.show_password,
            style="TCheckbutton",
            command=lambda: self.toggle_password_visibility(password_entry)
        ).grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=15)
        
        ttk.Button(button_frame, text="Сохранить", command=self.save_entry).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Отмена", command=self.window.destroy).pack(side=tk.LEFT, padx=5)
        
        main_frame.columnconfigure(1, weight=1)
    
    def toggle_password_visibility(self, entry):
        entry.config(show="" if self.show_password.get() else "*")
    
    def save_entry(self):
        service = self.service_var.get().strip()
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        if not all([service, username, password]):
            messagebox.showerror("Ошибка", "Все поля обязательны для заполнения")
            return
        
        try:
            self.db.add_password(service, username, password)
            self.refresh()
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка базы данных", str(e))

class EditWindow:
    def __init__(self, parent, db, crypto, refresh_callback, record_id, service, username, password):
        self.parent = parent
        self.db = db
        self.crypto = crypto
        self.refresh = refresh_callback
        self.record_id = record_id
        
        self.window = tk.Toplevel(parent)
        self.window.configure(background=parent.cget("background"))
        self.window.title("Редактирование записи")
        self.window.geometry("400x300")
        
        self.service_var = tk.StringVar(value=service)
        self.username_var = tk.StringVar(value=username)
        self.password_var = tk.StringVar(value=password)
        self.show_password = tk.BooleanVar(value=False)

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.window)
        main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Стили для элементов
        entry_style = ttk.Style()
        entry_style.configure("TEntry",
                            fieldbackground=self.parent.cget("background"),
                            foreground="#000000" if self.parent.cget("background") == "#f0f0f0" else "#ffffff")

        # Поля ввода
        ttk.Label(main_frame, text="Сервис*:").grid(row=0, column=0, sticky=tk.W, pady=5)
        entry_service = ttk.Entry(main_frame, textvariable=self.service_var, style="TEntry")
        entry_service.grid(row=0, column=1, sticky=tk.EW, pady=5)
        
        ttk.Label(main_frame, text="Логин*:").grid(row=1, column=0, sticky=tk.W, pady=5)
        entry_username = ttk.Entry(main_frame, textvariable=self.username_var, style="TEntry")
        entry_username.grid(row=1, column=1, sticky=tk.EW, pady=5)
        
        ttk.Label(main_frame, text="Пароль*:").grid(row=2, column=0, sticky=tk.W, pady=5)
        password_entry = ttk.Entry(main_frame, textvariable=self.password_var, show="*", style="TEntry")
        password_entry.grid(row=2, column=1, sticky=tk.EW, pady=5)

        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=15)
        
        ttk.Button(button_frame, 
                 text="Сохранить", 
                 command=self.save_changes,
                 style="TButton").pack(side=tk.LEFT, padx=5)
                 
        ttk.Button(button_frame, 
                 text="Отмена", 
                 command=self.window.destroy,
                 style="TButton").pack(side=tk.LEFT, padx=5)

        main_frame.columnconfigure(1, weight=1)
    
    def save_changes(self):
        service = self.service_var.get().strip()
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        if not all([service, username, password]):
            messagebox.showerror("Ошибка", "Все поля обязательны для заполнения")
            return
            
        try:
            self.db.update_password(
                self.record_id,
                service,
                username,
                password
            )
            self.refresh()
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

class CreatePasswordWindow(tk.Toplevel):
    def __init__(self, parent, on_success_callback):
        super().__init__(parent)
        self.configure(background="#2d2d2d")
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.style.configure("TButton",  # Единый стиль для всех кнопок
            background="#404040",
            foreground="#ffffff",
            padding=5,
            font=("Arial", 12),
            width=12
        )
        self.style.map("TButton",
            background=[('active', '#505050')],
            foreground=[('active', '#ffffff')]
        )

        # Стиль для поля ввода
        self.style.configure("Dark.TFrame", background="#2d2d2d")
        self.style.configure("Dark.TLabel", background="#2d2d2d", foreground="white")
        self.style.configure("Dark.TEntry",
            fieldbackground="#3d3d3d",
            foreground="#ffffff"
        )
        self.title("Создание мастер-пароля")
        self.geometry("450x400")
        self.on_success = on_success_callback
        
        # Главный контейнер
        main_frame = ttk.Frame(self, style="Dark.TFrame")
        main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        # Логотип
        try:
            self.logo_img = tk.PhotoImage(file="logo.png").subsample(2)
            ttk.Label(main_frame, image=self.logo_img, background="#2d2d2d").pack(pady=10)
        except Exception as e:
            ttk.Label(main_frame, text="LOCKUP", font=("Arial", 24), background="#2d2d2d", foreground="white").pack(pady=10)

        ttk.Label(main_frame, text="Создайте мастер-пароль:", style="Dark.TLabel", background="#2d2d2d", foreground="white").pack()
        # Поле ввода с применением стиля
        self.password_entry = ttk.Entry(
            main_frame, 
            show="•", 
            font=("Arial", 12),
            style="Dark.TEntry"  # Применяем стиль
        )
        self.password_entry.pack(pady=10, ipady=5, fill=tk.X)
        
        ttk.Button(main_frame, text="Создать", command=self._create, style="TButton").pack(pady=10, fill=tk.X, ipady=5)

    def _create(self):
        password = self.password_entry.get()
        if password:
            from database import save_master_password
            save_master_password(password)  # Сохранение в БД
            self.on_success(password)
        else:
            messagebox.showerror("Ошибка", "Введите пароль!")

class AuthWindow(tk.Toplevel):
    def __init__(self, parent, on_success):
        super().__init__(parent)
        self.configure(background="#2d2d2d")
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.style.configure("Dark.TFrame", background="#2d2d2d")
        self.style.configure("Dark.TLabel", background="#2d2d2d", foreground="white")
        self.style.configure("TEntry", fieldbackground="#3d3d3d", foreground="white")

        # Настройка стилей
        self.title("LockUp - Вход")
        self.geometry("450x400")

        # Стиль кнопки "Войти" как в основном интерфейсе
        self.style.configure("Auth.TButton", 
            background="#404040",
            foreground="#ffffff",
            padding=10,
            font=("Arial", 12),
            width=15
        )
        self.style.map("Auth.TButton",
            background=[('active', '#505050')],
            foreground=[('active', '#ffffff')]
        )

        self.parent = parent
        self.on_success = on_success

        self.main_frame = ttk.Frame(self, style="Dark.TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)

        # Обработка закрытия окна
        self.protocol("WM_DELETE_WINDOW", self.quit_app)

        # Логотип
        try:
            self.logo_img = tk.PhotoImage(file="logo.png").subsample(2)
            self.logo_label = tk.Label(
                self.main_frame, 
                image=self.logo_img, 
                background="#2d2d2d"
            )
        except Exception:
            self.logo_label = tk.Label(
                self.main_frame, 
                text="LOCKUP", 
                font=("Arial", 24), 
                background="#2d2d2d", 
                foreground="white"
            )
        self.logo_label.pack(pady=(20, 30))

        # Текст и поле ввода пароля
        ttk.Label(
            self.main_frame, 
            text="Введите мастер-пароль", 
            font=("Arial", 14), 
            style="Dark.TLabel"
        ).pack(pady=5)

        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(
            self.main_frame,
            textvariable=self.password_var,
            show="•",
            font=("Arial", 12),
            width=25
        )
        self.password_entry.pack(pady=15, ipady=5, fill=tk.X, padx=20)

        # Кнопка входа
        self.style.configure(
            "Auth.TButton", 
            padding=10, 
            font=("Arial", 12), 
            width=15
        )
        self.login_btn = ttk.Button(
            self.main_frame,
            text="Войти",
            command=self.authenticate,
            style="Auth.TButton"
        )
        self.login_btn.pack(pady=10, ipady=5, fill=tk.X, padx=20)

        # Привязка Enter
        self.password_entry.bind('<Return>', lambda e: self.authenticate())

        # Центрирование и фокус
        self.center_window()
        self.password_entry.focus_force()

    def center_window(self):
        self.update_idletasks()
        width = 450  
        height = 460
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def authenticate(self):
        password = self.password_var.get().strip()
        if not password:
            messagebox.showerror("Ошибка", "Введите пароль!")
            return
            
        if verify_master_password(password):
            self.destroy()
            self.on_success(password)
        else:
            messagebox.showerror("Ошибка", "Неверный мастер-пароль!")
            self.password_var.set("")

    def quit_app(self):
        self.parent.destroy()

class InfoWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("О программе")
        self.geometry("400x250")
        self.configure(background=parent.cget("background"))
        
        main_frame = ttk.Frame(self)
        main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        info_text = (
            "LockUp - Менеджер паролей\n\n"
            "Автор: GottaGrizzly\n"
            "Email: gottagrizzlyproject@tuta.io\n"
        )
        
        ttk.Label(
            main_frame,
            text=info_text,
            font=("Arial", 12),
            justify="center"
        ).pack(expand=True)

        # Добавляем кликабельную ссылку
        self.github_btn = ttk.Button(
            main_frame,
            text="GitHub",
            command=lambda: webbrowser.open("https://github.com/GottaGrizzly"),
            style="TButton"
        )
        self.github_btn.pack(pady=10)
        
        ttk.Button(
            main_frame,
            text="Закрыть",
            command=self.destroy
        ).pack(pady=10)