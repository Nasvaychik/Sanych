from tkinter import ttk


class CustomStyle:
    @staticmethod
    def configure_styles(root):
        # Настройка цветов и шрифтов для приложения
        root.configure(bg='#40E0D0')
        root.option_add('*TCombobox*Listbox*Background', '#40E0D0')
        root.option_add('*TCombobox*Listbox*Foreground', '#40E0D0')
        root.option_add('*TCombobox*Listbox*Font', ('123Marker', 13))

        # Настройка стилей для ttk виджетов
        style = ttk.Style(root)

        # Основные цвета
        style.theme_create("custom_theme", parent="clam", settings={
            "TNotebook": {"configure": {"tabmargins": [2, 5, 2, 0]}},
            "TNotebook.Tab": {"configure": {"padding": [10, 5], "background": "#40E0D0"},
                              "map": {"background": [("selected", "#40E0D0")],
                                      "foreground": [("selected", "#40E0D0")]}}
        })
        style.theme_use("custom_theme")

        # Настройка цветов для отдельных виджетов
        style.configure("Treeview", background="#40E0D0", foreground="#8B0000")
        style.configure("TButton", background="#40E0D0", foreground="#8B0000", font=('Gothic', 13))
        style.configure("TLabel", background="#40E0D0", foreground="#8B0000", font=('Gothic', 13))
        style.configure("TEntry", background="#40E0D0", foreground="#8B0000", font=('Gothic', 13))