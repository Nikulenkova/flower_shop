import tkinter as tk
from tkinter import messagebox
import requests
import threading

# Менеджер страниц
class PageManager:
    def __init__(self, root):
        self.root = root
        self.frames = {}

    def add_page(self, name, frame):
        self.frames[name] = frame
        frame.pack(fill="both", expand=True)

    def show_page(self, name):
        for frame in self.frames.values():
            frame.pack_forget()
        frame = self.frames.get(name)
        if frame:
            frame.pack(fill="both", expand=True)
            frame.tkraise()

# Главный класс приложения
class FlowerShopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Интернет-магазин цветов")
        self.root.geometry("700x400")

        self.page_manager = PageManager(root)
        self.current_user = None  # ID текущего пользователя

        self.create_menu()
        self.create_pages()

    # Создаём главное меню
    def create_menu(self):
        profile_frame = tk.Frame(self.root)
        profile_frame.pack(side=tk.TOP, fill=tk.X, pady=10)

        tk.Button(profile_frame, text="Корзина", font=("Arial", 12),
                  command=lambda: self.page_manager.show_page("cart")).pack(side=tk.RIGHT, padx=(0, 15))
        tk.Button(profile_frame, text="Личный кабинет", font=("Arial", 12),
                  command=lambda: self.page_manager.show_page(
                      "profile") if self.current_user else self.page_manager.show_page("login")).pack(side=tk.RIGHT, padx=(0, 15))

        menu_frame = tk.Frame(self.root)
        menu_frame.pack(pady=10)

        tk.Button(menu_frame, text="О нас", font=("Arial", 12),
                  command=lambda: self.page_manager.show_page("about")).pack(side=tk.LEFT, padx=20)
        tk.Button(menu_frame, text="Букеты", font=("Arial", 12),
                  command=lambda: self.page_manager.show_page("bouquets")).pack(side=tk.LEFT, padx=20)

    # Создаём все страницы
    def create_pages(self):
        self.create_about_page()
        self.create_bouquets_page()
        self.create_cart_page()
        self.create_login_page()
        self.create_registration_page()
        self.create_profile_page()
        self.page_manager.show_page("about")

    # Страница "О нас"
    def create_about_page(self):
        frame = tk.Frame(self.root)
        tk.Label(frame, text='''Добро пожаловать в наш цветочный магазин!
У нас вы найдете букеты с уникальным дизайном.
Будем рады Вашему заказу!''', font=("Arial", 16)).pack(pady=20)
        self.page_manager.add_page("about", frame)

    # Страница входа
    def create_login_page(self):
        frame = tk.Frame(self.root)

        tk.Label(frame, text="Логин", font=("Arial", 16)).pack(pady=10)
        username_entry = tk.Entry(frame)
        username_entry.pack()

        tk.Label(frame, text="Пароль", font=("Arial", 16)).pack(pady=10)
        password_entry = tk.Entry(frame, show='*')
        password_entry.pack()
        login_button = tk.Button(frame, text="Войти", font=("Arial", 16),
                                 command=lambda: self.login_user(username_entry.get(), password_entry.get()))
        login_button.pack(pady=10)
        registration_button = tk.Button(frame, text="Регистрация", font=("Arial", 16),
                                        command=lambda: self.page_manager.show_page("registration"))
        registration_button.pack(pady=10)
        self.page_manager.add_page("login", frame)

    # Логика входа
    def login_user(self, login, password):
        try:
            response = requests.post("http://localhost:5000/login", json={"login": login, "password": password})
            response.raise_for_status()
            user = response.json()
            self.current_user = user["id"]
            messagebox.showinfo("Успешный вход", "Вы вошли в личный кабинет!")
            self.page_manager.show_page("about")
            self.update_cart_page()
        except requests.RequestException as e:
            messagebox.showerror("Ошибка", f"Ошибка входа: {e}")

    # Страница регистрации
    def create_registration_page(self):
        frame = tk.Frame(self.root)
        tk.Label(frame, text="Логин", font=("Arial", 16)).pack(pady=10)
        username_entry = tk.Entry(frame)
        username_entry.pack()
        tk.Label(frame, text="Пароль", font=("Arial", 16)).pack(pady=10)
        password_entry = tk.Entry(frame, show='*')
        password_entry.pack()
        register_button = tk.Button(frame, text="Зарегистрироваться", font=("Arial", 16),
                                    command=lambda: self.register_user(username_entry.get(), password_entry.get()))
        register_button.pack(pady=10)
        self.page_manager.add_page("registration", frame)

    # Логика регистрации
    def register_user(self, login, password):
        try:
            response = requests.post("http://localhost:5000/register", json={"login": login, "password": password})
            response.raise_for_status()
            messagebox.showinfo("Регистрация", "Успешная регистрация!")
            self.page_manager.show_page("login")
        except requests.RequestException as e:
            messagebox.showerror("Ошибка", f"Ошибка регистрации: {e}")

    # Страница профиля
    def create_profile_page(self):
        frame = tk.Frame(self.root)
        logout_button = tk.Button(frame, text="Выйти из аккаунта", font=("Arial", 16),
                                  command=self.logout_user)
        logout_button.pack(pady=10)
        self.page_manager.add_page("profile", frame)

    # Логика выхода из аккаунта
    def logout_user(self):
        self.current_user = None
        messagebox.showinfo("Выход из аккаунта", "Вы вышли из аккаунта")
        self.page_manager.show_page("login")

    # Страница каталога букетов
    def create_bouquets_page(self):
        frame = tk.Frame(self.root)
        frame.pack()

        def fetch_bouquets():
            try:
                response = requests.get("http://localhost:5002/catalog")
                response.raise_for_status()
                bouquets = response.json()
                display_bouquets(bouquets)
            except requests.RequestException as e:
                messagebox.showerror("Ошибка", f"Ошибка загрузки каталога: {e}")
            except ValueError as e:
                messagebox.showerror("Ошибка", f"Некорректный ответ от сервера: {e}")

        def display_bouquets(bouquets):
            for i, bouquet in enumerate(bouquets):
                name_label = tk.Label(frame, text=bouquet["name"])
                price_label = tk.Label(frame, text=f"{bouquet['price']} руб.")
                add_button = tk.Button(frame, text="Добавить в корзину",
                                       command=lambda b=bouquet["id"]: self.add_to_cart(b))
                name_label.grid(row=i, column=0, padx=10, pady=10)
                price_label.grid(row=i, column=1, padx=10, pady=10)
                add_button.grid(row=i, column=2, padx=10, pady=10)

        threading.Thread(target=fetch_bouquets).start()
        self.page_manager.add_page("bouquets", frame)

    # Логика добавления букета в корзину
    def add_to_cart(self, bouquet_id):
        if not self.current_user:
            messagebox.showwarning("Ошибка", "Вы должны войти в аккаунт, чтобы добавить букет в корзину")
            return
        try:
            payload = {
                "user_id": self.current_user,
                "bouquet_id": bouquet_id
            }
            response = requests.post("http://localhost:5002/cart", json=payload)
            response.raise_for_status()
            messagebox.showinfo("Корзина", "Букет добавлен в корзину")
            self.update_cart_page()
        except requests.RequestException as e:
            messagebox.showerror("Ошибка", f"Ошибка добавления в корзину: {e}")
            
    # Страница корзины
    def create_cart_page(self):
        frame = tk.Frame(self.root)
        self.page_manager.add_page("cart", frame)
        self.update_cart_page()

    # Обновление корзины
    def update_cart_page(self):
        frame = self.page_manager.frames["cart"]
        for widget in frame.winfo_children():
            widget.destroy()
        if not self.current_user:
            tk.Label(frame, text="Войдите в аккаунт, чтобы увидеть корзину", font=("Arial", 16)).pack()
            return

        def fetch_cart():
            try:
                response = requests.get(f"http://localhost:5002/cart/{self.current_user}")
                response.raise_for_status()
                cart_items = response.json()
                display_cart(cart_items)
            except requests.RequestException as e:
                messagebox.showerror("Ошибка", f"Ошибка загрузки корзины: {e}")

        def display_cart(cart_items):
            total_cost = 0
            for idx, item in enumerate(cart_items):
                name, price, quantity = item["name"], item["price"], item["quantity"]
                total_price = price * quantity
                total_cost += total_price

                tk.Label(frame, text=f"{idx + 1}. {name} - {price} руб. (x{quantity}) = {total_price} руб.").pack()
                delete_button = tk.Button(frame, text="Удалить",
                                          command=lambda idx=idx: self.delete_from_cart(idx))
                delete_button.pack()
            tk.Label(frame, text=f"Итого: {total_cost} руб.", font=("Arial", 16)).pack()
        threading.Thread(target=fetch_cart).start()

    # Логика удаления из корзины
    def delete_from_cart(self, item_id):
        try:
            response = requests.delete(f"http://localhost:5002/cart/{item_id}")
            response.raise_for_status()
            messagebox.showinfo("Корзина", "Товар удалён из корзины")
            self.update_cart_page()
        except requests.RequestException as e:
            messagebox.showerror("Ошибка", f"Ошибка удаления из корзины: {e}")

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = FlowerShopApp(root)
    root.mainloop()