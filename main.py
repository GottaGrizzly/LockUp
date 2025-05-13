from tkinter import messagebox
from gui import AuthWindow, MainApp, CreatePasswordWindow
import tkinter as tk
from database import check_master_password_exists, verify_master_password

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        self.master_password = None
        self._main_app = None

        # Проверяем существование мастер-пароля
        if not self.check_master_password_exists():
            self.show_create_password_window()
        else:
            self.show_auth_window()

        self.mainloop()

    def show_auth_window(self):
        self.auth_win = AuthWindow(self, self.on_login_success)

    def show_create_password_window(self):
        self.create_password_win = CreatePasswordWindow(self, self.on_master_password_created)

    def on_master_password_created(self, password: str):
        self.master_password = password
        self.create_password_win.destroy()
        self.deiconify()
        self.show_main_app()

    def on_login_success(self, password: str):
        if verify_master_password(password):
            self.master_password = password
            self.auth_win.destroy()
            self.show_main_app()
        else:
            messagebox.showerror("Ошибка", "Неверный мастер-пароль!")
            self.auth_win.password_var.set("")

    def show_main_app(self):
        # Уничтожаем предыдущий экземпляр, если есть
        if self._main_app:
            self._main_app.root.destroy()

            # Создаем новый экземпляр MainApp
        self._main_app = MainApp(self, self.master_password)
        self._main_app.root.deiconify()

    def check_master_password_exists(self):
        return check_master_password_exists() 

if __name__ == "__main__":
    app = App()  
    app.mainloop()