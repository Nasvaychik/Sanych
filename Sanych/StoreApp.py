import tkinter as tk
from tkinter import messagebox, ttk, Menu, simpledialog, filedialog
import mysql.connector
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import random
from datetime import datetime
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from customstyle import CustomStyle

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Спортпит")
        self.geometry("1200x600")

        self.products = []
        self.order_items = []

        self.load_products()
        self.load_orders()

        self.create_widgets()

        # Создаем экземпляр класса CustomStyle
        custom_style = CustomStyle()

        # Применяем стили к текущему корневому окну (self)
        custom_style.configure_styles(self)

    def load_products(self):
        # Загрузка товаров из базы данных
        try:
            with mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="1488",
                    database="sanych",
            ) as db_connection:
                cursor = db_connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM products")
                self.products = cursor.fetchall()
        except mysql.connector.Error as err:
            messagebox.showerror("Ошибка", f"Произошла ошибка при загрузке товаров: {err}")

    def load_orders(self):
        # Загрузка заказов из базы данных
        try:
            with mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="1488",
                    database="sanych",
            ) as db_connection:
                cursor = db_connection.cursor(dictionary=True)
                cursor.execute("SELECT COUNT(*) AS count FROM orders")
                order_count = cursor.fetchone()["count"]
                if order_count is not None:
                    self.order_number = order_count + 1
                else:
                    self.order_number = 1
        except mysql.connector.Error as err:
            messagebox.showerror("Ошибка", f"Произошла ошибка при загрузке заказов: {err}")

    def create_widgets(self):
        self.treeview = ttk.Treeview(self)
        self.treeview["columns"] = ("name", "manufacturer", "price", "quantity")
        self.treeview.heading("name", text="Название")
        self.treeview.heading("manufacturer", text="Город")
        self.treeview.heading("price", text="Цена")
        self.treeview.heading("quantity", text="Количество")
        for product in self.products:
            self.treeview.insert("", "end", text=product["id"],
                                 values=(product["name"], product["manufacturer"], product["price"], 1))
        self.treeview.pack(fill="both", expand=True)

        self.popup_menu = Menu(self, tearoff=0)
        self.popup_menu.add_command(label="Добавить к заказу", command=self.add_to_order)

        self.treeview.bind("<ButtonRelease-1>", self.on_quantity_change)
        self.treeview.bind("<Button-3>", self.show_popup_menu)

        self.view_order_button = tk.Button(self, text="Просмотр заказа", command=self.view_order, state=tk.DISABLED)
        self.view_order_button.pack()

    def show_popup_menu(self, event):
        item = self.treeview.identify("item", event.x, event.y)
        if item:
            self.treeview.selection_set(item)
            self.popup_menu.post(event.x_root, event.y_root)

    def add_to_order(self):
        selected_item = self.treeview.selection()[0]
        product_id = int(self.treeview.item(selected_item, "text"))
        product = next((p for p in self.products if p["id"] == product_id), None)
        if product:
            quantity = simpledialog.askinteger("Введите количество", f'Укажите количество товара "{product["name"]}"')
            if quantity is not None and quantity > 0:
                product["quantity"] = quantity
                self.order_items.append(product)
                self.view_order_button.config(state=tk.NORMAL)
                messagebox.showinfo("Добавление к заказу", f'Товар "{product["name"]}" добавлен к заказу.')
            else:
                messagebox.showwarning("Ошибка", "Введите корректное количество товара (больше нуля).")

    def view_order(self):
        order_window = tk.Toplevel(self)
        order_window.title("Просмотр заказа")

        treeview = ttk.Treeview(order_window)
        treeview["columns"] = ("name", "manufacturer", "price", "quantity")
        treeview.heading("name", text="Наименование")
        treeview.heading("manufacturer", text="Производитель")
        treeview.heading("price", text="Цена")
        treeview.heading("quantity", text="Количество")
        total_price = 0
        for item in self.order_items:
            treeview.insert("", "end", text=item["id"],
                            values=(item["name"], item["manufacturer"], item["price"], item["quantity"]))
            total_price += item["price"] * item["quantity"]
        treeview.pack(fill="both", expand=True)

        total_price_label = tk.Label(order_window, text=f"Общая сумма заказа: {total_price}")
        total_price_label.pack()

        generate_pdf_button = tk.Button(order_window, text="Сформировать талон заказа",
                                        command=lambda: self.choose_delivery_method(total_price))
        generate_pdf_button.pack()

        def change_quantity():
            nonlocal total_price
            selected_item = treeview.selection()[0]
            item_id = int(treeview.item(selected_item, "text"))
            product = next((p for p in self.order_items if p["id"] == item_id), None)
            if product:
                new_quantity = simpledialog.askinteger("Изменить количество",
                                                       f'Текущее количество: {product["quantity"]}\nВведите новое количество товара "{product["name"]}"')
                if new_quantity is not None:
                    if new_quantity > 0:
                        product["quantity"] = new_quantity
                        treeview.item(selected_item,
                                      values=(product["name"], product["manufacturer"], product["price"], new_quantity))
                        total_price = sum(int(item["price"]) * int(item["quantity"]) for item in self.order_items)
                        total_price_label.config(text=f"Общая сумма заказа: {total_price}")
                    elif new_quantity == 0:
                        self.order_items.remove(product)
                        treeview.delete(selected_item)
                        total_price = sum(int(item["price"]) * int(item["quantity"]) for item in self.order_items)
                        total_price_label.config(text=f"Общая сумма заказа: {total_price}")
                else:
                    messagebox.showwarning("Ошибка", "Введите корректное количество товара (больше нуля).")

        change_quantity_button = tk.Button(order_window, text="Изменить количество", command=change_quantity)
        change_quantity_button.pack()

    def choose_delivery_method(self, total_price):
        delivery_methods = ["Почта России", "СДЭК"]

        def generate_order_pdf_with_delivery(delivery_method):
            self.generate_order_pdf(total_price, delivery_method)
            delivery_method_window.destroy()

        delivery_method_window = tk.Toplevel(self)
        delivery_method_window.title("Выберите способ доставки")

        selected_method = tk.StringVar()
        selected_method.set(delivery_methods[0])

        for method in delivery_methods:
            tk.Radiobutton(delivery_method_window, text=method, variable=selected_method, value=method).pack(anchor="w")

        confirm_button = tk.Button(delivery_method_window, text="Подтвердить",
                                   command=lambda: generate_order_pdf_with_delivery(selected_method.get()))
        confirm_button.pack()

    def generate_order_pdf(self, total_price, delivery_method):
        try:
            # Сгенерировать случайный номер заказа
            order_number = random.randint(1000, 9999)

            delivery_point = ""
            if delivery_method != "Самовывоз":
                delivery_point = simpledialog.askstring(f"Пункт выдачи для {delivery_method}",
                                                        f"Введите пункт выдачи для {delivery_method}:")

            filename = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
            if filename:
                c = canvas.Canvas(filename, pagesize=letter)
                pdfmetrics.registerFont(TTFont('DejaVuSans', 'fonts/DejaVuSans.ttf'))
                pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'fonts/DejaVuSans-Bold.ttf'))
                c.setFont("DejaVuSans", 12)
                c.drawString(100, 750, f"Дата заказа: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                c.drawString(100, 730, f"Номер заказа: {order_number}")
                c.setFont("DejaVuSans-Bold", 12)
                c.drawString(100, 710, "Код получения: " + str(random.randint(100, 999)))
                c.setFont("DejaVuSans", 12)
                c.drawString(100, 690, f"Способ доставки: {delivery_method}")
                if delivery_method != "Самовывоз":
                    c.drawString(100, 670, f"Пункт выдачи: {delivery_point}")
                c.drawString(100, 650, "Срок доставки: " + str(3 if len(self.order_items) >= 3 else 6) + " дней")
                c.drawString(100, 630, "Состав заказа:")
                y = 610
                for item in self.order_items:
                    c.drawString(120, y, f'{item["name"]} - {item["price"]} руб. x {item["quantity"]}')
                    y -= 20
                c.drawString(100, y, f"Общая сумма заказа: {total_price} руб.")

                c.setFillColorRGB(0, 0, 0)
                c.save()
                messagebox.showinfo("PDF сформирован", f"PDF-файл успешно создан: {filename}")

                self.create_order(order_number, total_price, delivery_point)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Возникла ошибка при формировании PDF-файла: {str(e)}")

    def create_order(self, order_number, total_price, delivery_point):
            try:
                with mysql.connector.connect(
                        host="localhost",
                        user="root",
                        password="1488",
                        database="sanych",
                ) as db_connection:
                    cursor = db_connection.cursor()
                    order_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    cursor.execute(
                        "INSERT INTO orders (order_number, order_date, delivery_point, total_price) VALUES (%s, %s, %s, %s)",
                        (order_number, order_date, delivery_point, total_price))
                    db_connection.commit()
                    messagebox.showinfo("Успех", "Заказ успешно сохранен в базе данных.")
            except mysql.connector.Error as err:
                messagebox.showerror("Ошибка", f"Произошла ошибка при сохранении заказа: {err}")

    def on_quantity_change(self, event):
            item = self.treeview.selection()
            if item:
                item = item[0]
                quantity = int(self.treeview.item(item, "values")[3])
                if quantity == 0:
                    self.treeview.delete(item)
                    self.update_total_price()

    def update_total_price(self):
            total_price = sum(
                int(self.treeview.item(child, "values")[2]) * int(self.treeview.item(child, "values")[3]) for
                child in
                self.treeview.get_children())
            total_price_label = tk.Label(self, text=f"Общая сумма заказа: {total_price}")
            total_price_label.pack()


if __name__ == "__main__":
    app = Application()
    app.mainloop()