# Импортирование модулей
from tkinter import messagebox
from tkinter import *
import pymongo
import sqlite3
import platform
import datetime
from docxtpl import DocxTemplate
from tkcalendar import Calendar

try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:
    import Tkinter as tk
    import ttk


# Время сейчас
time = datetime.datetime.now()
time_now = time.strftime("%d-%m-%Y %H:%M:%S")
# Характеристики ПК
system = (
    "Система: "
    + platform.system()
    + "; Cетевое имя компьютера: "
    + platform.node()
    + "; Процессор: "
    + platform.processor()
)

# Класс подключения к MongoDB
class Connect_MongoDB:
    def __init__(self, conn):
        self.mongo_connector = pymongo.MongoClient(conn)

    def connect_database(self, db):
        self.db_connector = getattr(self.mongo_connector, db)

    def connect_coll(self, coll):
        self.coll_connector = getattr(self.db_connector, coll)


connections = Connect_MongoDB(
    "mongodb://dron2026:55555@dron2026-shard-00-00-x59g6.mongodb.net:27017,dron2026-shard-00-01-x59g6.mongodb.net:27017,dron2026-shard-00-02-x59g6.mongodb.net:27017/test?ssl=true&replicaSet=dron2026-shard-0&authSource=admin&retryWrites=true&w=majority"
)
connections.connect_database("polyclinic")

# Класс подключения к SQLite
class Connect_SQLite:
    def __init__(self, conn_sql):
        self.conn_sql = sqlite3.connect(conn_sql)
        self.cursor = self.conn_sql.cursor
        self.commit = self.conn_sql.commit


connection_SQL = Connect_SQLite("mydatabase.db")
cursor = connection_SQL.cursor()

# Класс авторизации
class Auth(Connect_MongoDB, Connect_SQLite):
    def __init__(self, log, pas):
        self.log = log
        self.pas = pas

    # Функция главного окна авторизации
    @staticmethod
    def main():
        global enter_login, enter_password, root
        root = Tk()
        root.geometry("300x250")
        root.title("Войти в систему")
        root.config(background="#fff44f")
        root.resizable(width=False, height=False)
        text_log = Label(text="Вход в систему", background="#fff44f", font="times 12")
        text_enter_login = Label(
            text="Введите ваш логин:", background="#fff44f", font="times 12"
        )
        enter_login = Entry()
        text_enter_pass = Label(
            text="Введите ваш пароль:", background="#fff44f", font="times 12"
        )
        enter_password = Entry(show="*")
        button_enter = Button(
            text="Войти",
            command=lambda: Auth(
                enter_login.get(), enter_password.get()
            ).log_pas_registrator(),
            background="#71bc78",
            foreground="white",
            font="times 12",
        )
        text_log.pack()
        text_enter_login.pack()
        enter_login.pack()
        text_enter_pass.pack()
        enter_password.pack()
        button_enter.pack()
        root.mainloop()

    # Функция проверки логина и пароля в бд
    # Открытие соответсвуюшего окна пользователя
    def log_pas_registrator(self):
        global specialization, name, id_docs
        connections.connect_coll("registrator")
        for log in connections.coll_connector.find(
            {"login": self.log, "password": self.pas}
        ):
            if log["specialization"] == "Регистратор":
                specialization = log["specialization"]
                name = log["name"]
                params = (name, specialization, time_now, system)
                cursor.execute("INSERT INTO staff_session VALUES (?,?,?,?)", params)
                connection_SQL.commit()
                root.destroy()
                Registrator.main_reg()
            else:
                messagebox.showerror("Ошибка", "Попопробуйте еще раз!")
            break
        else:
            connections.connect_coll("app_doctor")
            for log in connections.coll_connector.find(
                {"login": self.log, "password": self.pas}
            ):
                specialization = log["specialization"]
                name = log["name"]
                id_docs = log["id"]
                params = (name, specialization, time_now, system)
                cursor.execute("INSERT INTO staff_session VALUES (?,?,?,?)", params)
                connection_SQL.commit()
                root.destroy()
                Doctors.doctors_main()
                break
            else:
                connections.connect_coll("auth_user")
                for log in connections.coll_connector.find(
                    {"username": self.log, "password": self.pas}
                ):
                    root.destroy()
                    Admin.main_admin_window()
                    break
                else:
                    messagebox.showerror("Ошибка", "Попопробуйте еще раз!")


# Класс администратора
class Admin:
    def __init__(self):
        pass

    # Функция главного окна администратора
    @staticmethod
    def main_admin_window():
        root_admin = Tk()
        root_admin.geometry("500x400")
        root_admin.title("Окно администратора")
        btn_add_registrator = Button(
            root_admin,
            text="Добавить регистратора",
            command=lambda: Admin.add_reg(),
            font="times12",
        )
        btn_add_registrator.place(x=1, y=1)
        root_admin.config(background="#FFAAA8")
        root_admin.mainloop()

    # Функция окна добавления регистратора
    @staticmethod
    def add_reg():
        global entry_name_reg, entry_login_reg, entry_password_reg, root_add_reg
        root_add_reg = Tk()
        root_add_reg.geometry("300x300")
        root_add_reg.title("Окно добавления регистратора")
        lbl_name_reg = Label(
            root_add_reg, text="ФИО:", background="#FFAAA8", font="times 14",
        )
        lbl_name_reg.place(x=1, y=1)
        entry_name_reg = Entry(root_add_reg)
        entry_name_reg.place(x=70, y=5)
        lbl_login_reg = Label(
            root_add_reg, text="Логин:", background="#FFAAA8", font="times 14",
        )
        lbl_login_reg.place(x=1, y=50)
        entry_login_reg = Entry(root_add_reg)
        entry_login_reg.place(x=70, y=55)
        lbl_password_reg = Label(
            root_add_reg, text="Пароль:", background="#FFAAA8", font="times 14",
        )
        lbl_password_reg.place(x=1, y=100)
        entry_password_reg = Entry(root_add_reg)
        entry_password_reg.place(x=70, y=105)
        btn_add_ = Button(
            root_add_reg,
            text="Добавить регистратора",
            command=lambda: Admin.add_reg_check(),
            font="times12",
        )
        btn_add_.place(x=1, y=150)
        root_add_reg.config(background="#FFAAA8")
        root_add_reg.mainloop()

    # Функция добавления регистратора и запись в бд
    @staticmethod
    def add_reg_check():
        if (
            entry_name_reg.get() == ""
            or entry_login_reg.get() == ""
            or entry_password_reg.get() == ""
        ):
            messagebox.showerror("Ошибка", "Заолните все поля!")
        else:
            connections.connect_coll("registrator")
            registrator_content = {
                "name": entry_name_reg.get(),
                "login": entry_login_reg.get(),
                "password": entry_password_reg.get(),
                "specialization": "Регистратор",
            }
            connections.coll_connector.insert_one(registrator_content)
            messagebox.showinfo("Успешно", "Регистратор добавлен")
            root_add_reg.destroy()


# Класс регистратора
class Registrator:
    def __init__(self):
        pass

    # функция окна регистратора
    @staticmethod
    def main_reg():
        global var, root1
        root1 = Tk()
        root1.geometry("700x400")
        root1.title("Окно регистратора")
        root1.config(background="#FFAAA8")
        var = IntVar()
        var.set(0)
        window_main_reg = Registrator()
        window_main_reg.main_reg_window()
        root1.mainloop()

    # функция выбора врача по id и заданному времени
    # открытие окна соотвествующего врача
    @staticmethod
    def choose():
        global doctor, id_, array_zapis_fio, array_zapis_worry, array_time, sortedArray1, array_zapis_id
        id_ = -1
        doctor = -1
        try:
            if first_date_date == "":
                ""
        except NameError:
            messagebox.showerror("Ошибка", "Выберите дату")
        if var.get() == 0:
            messagebox.showerror("Ошибка", "Выберите врача!")
        else:
            while id_ < (len(array_doc_id)):
                id_ += 1
                doctor += 1
                if var.get() == array_doc_id[id_]:
                    array_doc[doctor]
                    array_zapis_fio = []
                    array_zapis_worry = []
                    array_zapis_id = []
                    array_time = []
                    end = datetime.datetime.today()
                    start = datetime.datetime.today() + datetime.timedelta(days=-1)
                    connections.connect_coll("app_reception")
                    iii = 0
                    while iii < len(array_doc[doctor]):
                        for time_poisk in connections.coll_connector.find(
                            {
                                "date": {"$gt": start, "$lt": end},
                                "doctor_id": array_doc_id[id_],
                            }
                        ):
                            array_time.append(time_poisk["time"])
                        iii += 1
                        break
                    break
            sortedArray1 = sorted(
                array_time, key=lambda x: datetime.datetime.strptime(x, "%H:%M")
            )
            ccc = 0
            while ccc < len(sortedArray1):
                for zapis in connections.coll_connector.find(
                    {
                        "date": {"$gt": start, "$lt": end},
                        "doctor_id": array_doc_id[id_],
                        "time": sortedArray1[ccc],
                    }
                ):
                    array_zapis_fio.append(zapis["patient_name"])
                    array_zapis_worry.append(zapis["patient_info"])
                    array_zapis_id.append(zapis["id"])
                ccc += 1
            Registrator.raspis_doc()

    # Функция главного окна врача у регистратора
    @staticmethod
    def raspis_doc_window():
        global patinet_informations
        i = 0
        entr_place = 0
        lbl_place = 0
        worry_place = 0
        # Если записей нет, то выводить в лейбл "Записей нет!"
        if len(array_zapis_fio) == 0:
            label_dont = Label(
                doctor_main, text="Записей нет!", background="#FFAAA8", font="times 14",
            )
            label_dont.place(x=400, y=370)
        # Иначе,записывать лейбл ФИО и Беспокойства
        else:
            lbl_fio_pat = Label(
                doctor_main, text="ФИО пациента", background="#FFAAA8", font="times 12",
            )
            lbl_worry_pat = Label(
                doctor_main, text="Беспокойства", background="#FFAAA8", font="times 12",
            )
            lbl_fio_pat.place(x=100, y=20)
            lbl_worry_pat.place(x=400, y=20)
            # Цикл вывода всех пациентов записанных к выбраному врачу
            while i < len(array_zapis_fio):
                connections.connect_coll("patient")
                # Цикл поиска, если пациент уже получил услуги, чтобы распечатать чек
                for patinet_informations in connections.coll_connector.find(
                    {"patient_id": array_zapis_id[i], "id_check": "1"}
                ):
                    btn_chek_reg = Button(
                        doctor_main,
                        text="Распечатать чек",
                        command=lambda: Registrator.print_check(),
                        font="times 12",
                    )
                    btn_chek_reg.place(x=650, y=55 + entr_place)
                time1 = Label(
                    doctor_main,
                    text=sortedArray1[i],
                    background="#FFAAA8",
                    font="times 14",
                )
                time1.place(x=1, y=55 + lbl_place)
                lbl_name = Entry(doctor_main, font="times 12")
                lbl_name.insert(END, array_zapis_fio[i])
                lbl_name.configure(
                    disabledbackground="white",
                    state=DISABLED,
                    disabledforeground="black",
                    width=30,
                )
                lbl_name.place(x=80, y=60 + entr_place)
                lbl_worry = Entry(doctor_main, font="times 12")
                lbl_worry.insert(END, array_zapis_worry[i])
                lbl_worry.configure(
                    disabledbackground="white",
                    state=DISABLED,
                    disabledforeground="black",
                    width=30,
                )
                lbl_worry.place(x=350, y=60 + worry_place)
                worry_place += 50
                entr_place += 50
                lbl_place += 50
                i += 1

    # Функция вывода чека
    @staticmethod
    def print_check():
        array_work = []
        array_price = []
        i = 0
        # Цикл поиска данных пациента и добавления в чек
        while i < (len(patinet_informations["service"])):
            array_work.append(patinet_informations["service"][i][0])
            array_price.append(patinet_informations["service"][i][1])
            price = patinet_informations["service"][i][0]
            print(array_work[i])
            print(price)
            context = {
                "doctor": patinet_informations["doc_name"],
                "rabota": array_work[i],
                "price": array_price[i],
                "summ": array_price[i],
                "itogo": array_price[i],
            }
            doc = DocxTemplate("Чек.docx")
            doc.render(context)
            doc.save("чек_покупка.docx")
            i += 1
        messagebox.showinfo("Успешно", "Заберите чек")

    # Функция главного окна регистратора
    @staticmethod
    def main_reg_window():
        global array_doc_id, array_doc, doc
        connections.connect_coll("app_doctor")
        btn1 = Button(
            text="Перейти к расписанию",
            command=lambda: Registrator.choose(),
            font="times 12",
        )
        btn2 = Button(
            text="Редактирование услуг врача",
            command=lambda: Registrator.edit_price(),
            font="times 12",
        )
        btn3 = Button(
            text="Журнал пациентов",
            command=lambda: Registrator.patient_journal(),
            font="times 12",
        )
        btn4 = Button(
            text="Выбор даты",
            command=lambda: Registrator.date_entry_main(),
            font="times 12",
        )
        btn6 = Button(
            text="Отчет за период",
            command=lambda: Registrator.period_main(),
            font="times 12",
        )
        i = 0
        radio_place = 0
        btn_place = 0
        array_doc_id = []
        array_doc = []
        array_var = []
        # Цикл поиска всех врачей и вывод в нлавнео окно регистратора
        for doc in connections.coll_connector.find({}):
            array_doc.append(doc["specialization"])
            array_doc_id.append(doc["id"])
            while i < len(array_doc):
                radio = Radiobutton(
                    text=array_doc[i] + "(" + doc["name"] + ")",
                    variable=var,
                    value=1 + i,
                    background="#FFAAA8",
                    font="times 14",
                )
                radio.place(x=1, y=1 + radio_place)
                btn1.place(x=1, y=120 + btn_place)
                btn2.place(x=1, y=170 + btn_place)
                btn3.place(x=1, y=220 + btn_place)
                btn4.place(x=480, y=10)
                btn6.place(x=1, y=270 + btn_place)
                array_var.append(var.get())
                i += 1
                radio_place += 30
                btn_place += 10

    # Функция составления отчетов по обменам
    @staticmethod
    def period_main():
        time1 = datetime.datetime.today()
        time_now1 = time1.strftime("%H:%M:%S.%f")
        print(time_now1)
        root_date = Tk()
        root_date.geometry("825x650")
        root_date.title("Отчет по обменам")
        root_date.config(background="#FFAAA8")
        root_date.resizable(width=False, height=False)
        lbl_poisk = Label(
            root_date, text="Выберите даты:", background="#FFAAA8", font="times14"
        )
        btn1 = Button(
            root_date, text="Первая дата", command=lambda: search1(), font="times12"
        )
        btn2 = Button(
            root_date, text="Вторая дата", command=lambda: search2(), font="times12"
        )
        btn_poisk = Button(
            root_date, text="Поиск", command=lambda: search(), font="times12"
        )
        text = Text(root_date, width=100, height=30, wrap=WORD,)
        btn_delete = Button(
            root_date, text="Очистить", command=lambda: clear(), font="times12"
        )
        lbl_poisk.place(x=1, y=1)
        btn1.place(x=1, y=30)
        btn2.place(x=250, y=30)
        btn_poisk.place(x=1, y=100)
        btn_delete.place(x=100, y=100)
        text.place(x=1, y=150)

        # функция открытия первого календаря
        def search1():
            first_date = ""

            def print_sel():
                global first_date
                a = datetime.datetime.now().time()
                first_date = datetime.datetime.combine(cal.selection_get(), a)
                root.destroy()
                lbl_first_date = Label(
                    root_date,
                    text=first_date.strftime("%d-%m-%Y"),
                    background="#FFAAA8",
                    font="times12",
                )
                lbl_first_date.place(x=135, y=35)

            root = Tk()
            root.title("Выбор первой даты")
            a = datetime.datetime.today().year
            b = datetime.datetime.today().month
            c = datetime.datetime.today().day

            cal = Calendar(
                root,
                font="Arial 14",
                selectmode="day",
                locale="Ru",
                cursor="hand1",
                year=a,
                month=b,
                day=c,
            )

            cal.pack(fill="both", expand=True)
            Button(root, text="ok", command=print_sel).pack()

        # функция второго первого календаря
        def search2():
            second_date = ""

            def print_sel():
                global second_date
                a = datetime.datetime.now().time()
                second_date = datetime.datetime.combine(cal.selection_get(), a)
                root.destroy()
                lbl_second_date = Label(
                    root_date,
                    text=second_date.strftime("%d-%m-%Y"),
                    background="#FFAAA8",
                    font="times12",
                )
                lbl_second_date.place(x=385, y=35)

            root = Tk()
            root.title("Выбор второй даты")
            a = datetime.datetime.today().year
            b = datetime.datetime.today().month
            c = datetime.datetime.today().day
            cal = Calendar(
                root,
                font="Arial 14",
                selectmode="day",
                locale="Ru",
                cursor="hand1",
                year=a,
                month=b,
                day=c,
            )

            cal.pack(fill="both", expand=True)
            Button(root, text="ok", command=print_sel).pack()

        # функция поиска всех данных пациентов в выбранный период
        def search():
            connections.connect_coll("patient")
            try:
                if first_date == "" or second_date == "":
                    messagebox.showerror("Ошибка", "Выберите период!!")
                else:
                    array_array = []
                    for pat_inf in connections.coll_connector.find(
                        {"date": {"$gt": first_date, "$lt": second_date}}
                    ):
                        for inf_search in range(len(pat_inf["service"])):
                            array_array.append(
                                str(pat_inf["service"][inf_search][0])
                                + " "
                                + str(pat_inf["service"][inf_search][1])
                            )
                            info = (
                                "Имя врача: "
                                + pat_inf["doc_name"]
                                + " , "
                                + "Cпециализация: "
                                + pat_inf["doc_spec"]
                                + " , "
                                + "ФИО пациента: "
                                + pat_inf["patient_name"]
                                + " ,"
                                + "Информация о пациенте: "
                                + pat_inf["patient_info"]
                                + " , "
                                + "Дата посещения: "
                                + str(pat_inf["date"])
                                + " , "
                                + "Время посещения: "
                                + pat_inf["time"]
                                + " , "
                                + "Полис:"
                                + pat_inf["polis"]
                                + " , "
                                + "Услуги: "
                                + " ".join(array_array)
                                + " , "
                                + "Комментарий врача: "
                                + pat_inf["comment"]
                                + "\n"
                                + "--------------------------------------------------------------------------------------------"
                                "----------------------------------------------------------------------------------------"
                                + "\n"
                            )
                            text.insert(1.0, info)
                    else:
                        messagebox.showerror("Ошибка", "Отчета за выбранную дату нет")
            except NameError:
                messagebox.showerror("Ошибка", "Выберите дату")

        def clear():
            text.delete(1.0, END)

    # функция выбора даты в главном меню регистратора
    @staticmethod
    def date_entry_main():
        first_date_date = ""

        def print_sel():
            global first_date_date
            first_date_date = str(cal.selection_get())
            label_date = Label(
                root1, text=first_date_date, background="#FFAAA8", font="times14"
            )
            label_date.place(x=480, y=50)
            root.destroy()

        root = Tk()
        root.title("Выбор даты")
        a = datetime.date.today().year
        b = datetime.date.today().month
        c = datetime.date.today().day

        cal = Calendar(
            root,
            font="Arial 14",
            selectmode="day",
            locale="Ru",
            cursor="hand1",
            year=a,
            month=b,
            day=c,
        )

        cal.pack(fill="both", expand=True)
        Button(root, text="ok", command=print_sel).pack()

    # функция главного окна регистратора
    @staticmethod
    def raspis_doc():
        global doctor_main
        time_now_doc = time.strftime("%d-%m-%Y")
        doctor_main = Tk()
        doctor_main.geometry("1000x800")
        doctor_main.title("Расписание " + (str(array_doc[doctor]).lower()))
        doctor_main.config(background="#FFAAA8")
        doctor_main.resizable(width=False, height=False)
        date = Label(
            doctor_main, text=time_now_doc, background="#FFAAA8", font="times 12"
        )
        name_label = Label(doctor_main, text="", background="#FFAAA8", font="times 14",)
        name_label.place(x=1, y=780)
        date.place(x=10, y=1)
        btn_update_window = Button(
            doctor_main,
            text="Обновить",
            command=lambda: Registrator.update_window(),
            font="times 14",
        )
        btn_update_window.place(x=850, y=750)
        window_main = Registrator()
        window_main.raspis_doc_window()
        doctor_main.mainloop()

    # функция обновления окна врача
    @staticmethod
    def update_window():
        doctor_main.destroy()
        Registrator.raspis_doc()

    # функция окна редактирования услуг
    @staticmethod
    def main_edit_price():
        global price_main
        price_main = Tk()
        price_main.geometry("800x700")
        price_main.title("Редактирование услуг " + (str(array_doc[doctor_]).lower()))
        price_main.config(background="#FFAAA8")
        price_main.resizable(width=False, height=False)
        lbl_nomen = Label(
            price_main, text="Наиминование", background="#FFAAA8", font="times 12"
        )
        lbl_nomen.place(x=100, y=1)
        lbl_price = Label(
            price_main, text="Цена", background="#FFAAA8", font="times 12"
        )
        lbl_price.place(x=390, y=1)
        btn_add = Button(
            price_main,
            text="Добавить услугу",
            command=lambda: Registrator.add_nomen(),
            font="times 12",
        )
        btn_add.place(x=300, y=600)
        Registrator.edit_price_fucnk()
        price_main.mainloop()

    # функция проверки и выбор по id нужного врача
    @staticmethod
    def edit_price():
        global doctor_, id__
        id__ = -1
        doctor_ = -1
        if var.get() == 0:
            messagebox.showerror("Ошибка", "Выберите врача!")
        else:
            while id__ < (len(array_doc_id)):
                id__ += 1
                doctor_ += 1
                if var.get() == array_doc_id[id__]:
                    array_doc[doctor_]
                    Registrator.main_edit_price()
                    break

    # функция редактирования услуг
    @staticmethod
    def edit_price_fucnk():
        global ax
        price_i = 0
        lbl_number_i = 1
        sql = "SELECT officium FROM price WHERE doctor_id=?"
        cursor.execute(sql, [(str(array_doc_id[id__]))])
        abc = cursor.fetchall()
        sql1 = "SELECT price FROM price WHERE doctor_id=?"
        cursor.execute(sql1, [(str(array_doc_id[id__]))])
        abc1 = cursor.fetchall()
        sql2 = "SELECT rowid FROM price WHERE doctor_id=?"
        cursor.execute(sql2, [(str(array_doc_id[id__]))])
        abc2 = cursor.fetchall()
        lbl_number_place = 0
        # Цикл записи в окно редактирования услуг имеющиейся записи из бд
        while price_i < len(abc):
            lbl_number = Label(
                price_main,
                text=str(lbl_number_i),
                font="times 12",
                background="#FFAAA8",
            )
            ax = abc2[price_i]
            lbl_number.place(x=1, y=25 + lbl_number_place)
            entry_nomen = Entry(price_main)
            entry_nomen.insert(END, abc[price_i])
            entry_nomen.place(x=100, y=25 + lbl_number_place)
            entry_price = Entry(price_main)
            entry_price.insert(END, abc1[price_i])
            entry_price.place(x=350, y=25 + lbl_number_place)
            btn_delete = Button(
                price_main,
                text="Удалить",
                command=lambda ax=ax: Registrator.delete_price(ax),
                font="times 11",
            )
            btn_delete.place(x=550, y=21 + lbl_number_place)
            lbl_number_i += 1
            lbl_number_place += 35
            price_i += 1

    # Функция удаления услуги
    @staticmethod
    def delete_price(klo):
        answer = messagebox.askyesno(title="Вопрос", message="Точно хотите удалить?")
        if answer == True:
            cursor.execute("""DELETE FROM price WHERE rowid = ?""", (klo))
            connection_SQL.commit()
            messagebox.showinfo("Успешно", "Услуга удалена!")
            price_main.destroy()
            Registrator.main_edit_price()

    # Функция окна добавления услуги
    @staticmethod
    def add_nomen():
        global entry_nome_add, entry_price_add, add_nomen_main
        add_nomen_main = Tk()
        add_nomen_main.geometry("400x250")
        add_nomen_main.title("Добавление услуги")
        lbl_nomen = Label(
            add_nomen_main, text="Введите услугу", font="times14", background="#FFAAA8"
        )
        lbl_price = Label(
            add_nomen_main, text="Введите цену", font="times14", background="#FFAAA8"
        )
        entry_nome_add = Entry(add_nomen_main,)
        entry_price_add = Entry(add_nomen_main,)
        btn_add_db = Button(
            add_nomen_main,
            text="Добавить услугу",
            command=lambda: Registrator.add_to_db(),
            font="times12",
        )
        btn_add_db.place(x=200, y=150)
        lbl_nomen.place(x=1, y=1)
        entry_nome_add.place(x=150, y=1)
        lbl_price.place(x=1, y=50)
        entry_price_add.place(x=150, y=50)
        add_nomen_main.config(background="#FFAAA8")
        price_main.resizable(width=False, height=False)
        add_nomen_main.mainloop()

    # Добавление услуги в бд
    @staticmethod
    def add_to_db():
        if str(entry_nome_add.get()) == "" or str(entry_price_add.get()) == "":
            messagebox.showerror("Ошибка", "Заполните все поля")
        else:
            params = (
                str(array_doc_id[id__]),
                "doctor_name",
                str(entry_nome_add.get()),
                str(entry_price_add.get()),
            )
            cursor.execute("INSERT INTO price VALUES (?,?,?,?)", params)
            connection_SQL.commit()
            answer = messagebox.askyesno(title="Вопрос", message="Хотите добавить еще?")
            if answer == True:
                add_nomen_main.destroy()
                Registrator.add_nomen()
            else:
                add_nomen_main.destroy()
                price_main.destroy()
                Registrator.main_edit_price()

    # Окно журнала пациентов
    @staticmethod
    def patient_journal():
        global polis_entr, text_journal
        root_info = Tk()
        root_info.geometry("925x650")
        root_info.title("Журал пациентов")
        root_info.config(background="#FFAAA8")
        root_info.resizable(width=False, height=False)
        lbl_polis = Label(
            root_info,
            text="Введите номер полиса (16 цифр)",
            background="#FFAAA8",
            font="times12",
        )
        polis_entr = Entry(root_info, width=40)  # Поле ввода полиса
        btn_polis = Button(
            root_info,
            text="Найти",
            command=lambda: Registrator.patient_journal_funk(),
            background="#FFAAA8",
            font="times12",
        )
        text_journal = Text(root_info, width=100, height=30, wrap=WORD, font="times10")
        btn_delete = Button(
            root_info,
            text="Очистить",
            command=lambda: Registrator.patient_journal_clear(),
            background="#FFAAA8",
            font="times12",
        )
        lbl_polis.place(x=1, y=5)
        polis_entr.place(x=1, y=35)
        btn_polis.place(x=1, y=55)
        btn_delete.place(x=70, y=55)
        text_journal.place(x=1, y=90)
        root_info.mainloop()

    # Функция заполнения журнала пациентов
    @staticmethod
    def patient_journal_funk():
        connections.connect_coll("patient")
        if polis_entr.get() == "":
            messagebox.showerror("Ошибка", "Зполните поле полиса!")
        else:
            pol = polis_entr.get()
            array_array = []
            # Поиск по полису и вывод всех данных
            for pat_inf in connections.coll_connector.find({"polis": pol}):
                for inf in range(len(pat_inf["service"])):
                    array_array.append(
                        str(pat_inf["service"][inf][0])
                        + " "
                        + str(pat_inf["service"][inf][1])
                    )
                info = (
                    "Имя врача: "
                    + pat_inf["doc_name"]
                    + " , "
                    + "Cпециализация: "
                    + pat_inf["doc_spec"]
                    + " , "
                    + "ФИО пациента: "
                    + pat_inf["patient_name"]
                    + " ,"
                    + "Информация о пациенте: "
                    + pat_inf["patient_info"]
                    + " , "
                    + "Дата посещения: "
                    + str(pat_inf["date"])
                    + " , "
                    + "Время посещения: "
                    + pat_inf["time"]
                    + " , "
                    + "Полис:"
                    + pat_inf["polis"]
                    + " , "
                    + "Услуги: "
                    + " ".join(array_array)
                    + " , "
                    + "Комментарий врача: "
                    + pat_inf["comment"]
                    + "\n"
                    + "--------------------------------------------------------------------------------------------"
                    "----------------------------------------------------------------------------------------"
                    + "\n"
                )
                text_journal.insert(1.0, info)

    @staticmethod
    def patient_journal_clear():
        polis_entr.delete(0, END)
        text_journal.delete(1.0, END)


# Клас доктора
class Doctors(Registrator, Auth):
    def __init__(self):
        pass

    # Главное окно доктора
    @staticmethod
    def doctors_main():
        global doctor_main_window
        time_now_doc = time.strftime("%d-%m-%Y")
        doctor_main_window = Tk()
        doctor_main_window.geometry("1000x800")
        doctor_main_window.title("Расписание " + (specialization))
        doctor_main_window.config(background="#FFAAA8")
        doctor_main_window.resizable(width=False, height=False)
        date = Label(
            doctor_main_window, text=time_now_doc, background="#FFAAA8", font="times 12"
        )
        name_label = Label(
            doctor_main_window,
            text="Врач: " + name,
            background="#FFAAA8",
            font="times 14",
        )
        lbl_fio_pat = Label(
            doctor_main_window,
            text="ФИО пациента",
            background="#FFAAA8",
            font="times 12",
        )
        lbl_worry_pat = Label(
            doctor_main_window,
            text="Беспокойства",
            background="#FFAAA8",
            font="times 12",
        )
        lbl_fio_pat.place(x=100, y=20)
        lbl_worry_pat.place(x=400, y=20)
        Doctors.search_time_doc()
        Doctors.doctors_main_functions()
        date.place(x=10, y=1)
        name_label.place(x=1, y=780)
        doctor_main_window.mainloop()

    # Функция вывода всех пациентов авторизированного доктора
    @staticmethod
    def doctors_main_functions():
        i = 0
        entr_place = 0
        lp = ""
        if len(array_zapis_fio_doc) == 0:
            label_dont = Label(
                doctor_main_window,
                text="Записей нет!",
                background="#FFAAA8",
                font="times 14",
            )
            label_dont.place(x=400, y=250)
        else:

            while i < len(array_zapis_fio_doc):
                time1 = Label(
                    doctor_main_window,
                    text=sortedArray[i],
                    background="#FFAAA8",
                    font="times 14",
                )
                time1.place(x=1, y=70 + entr_place)
                lbl_name = Entry(doctor_main_window, font="times 12")
                lbl_name.insert(END, array_zapis_fio_doc[i]["patient_name"])
                lbl_name.configure(
                    disabledbackground="white",
                    state=DISABLED,
                    disabledforeground="black",
                    width=30,
                )
                lbl_name.place(x=80, y=60 + entr_place)
                lbl_worry = Entry(doctor_main_window, font="times 12")
                lbl_worry.insert(END, array_zapis_worry_doc[i])
                lbl_worry.configure(
                    disabledbackground="white",
                    state=DISABLED,
                    disabledforeground="black",
                    width=35,
                )
                lbl_worry.place(x=350, y=60 + entr_place)
                lp = array_zapis_fio_doc[i]["id"]
                btn_info_pat = Button(
                    doctor_main_window,
                    text="Карточка пациента",
                    command=lambda lp=lp: Doctors.funktion_patient_card(lp),
                )
                btn_spend = Button(
                    doctor_main_window,
                    text="Выбор услуги",
                    command=lambda lp=lp: Doctors.spend(lp),
                )
                btn_info_pat.place(x=650, y=60 + entr_place)
                btn_spend.place(x=800, y=60 + entr_place)
                entr_place += 50
                i += 1

    # Фунция поиска пациентов по дате
    @staticmethod
    def search_time_doc():
        global array_zapis_fio_doc, array_zapis_worry_doc, array_time_doc, array_polis, array_id_patient, sortedArray
        array_time_doc = []
        array_zapis_fio_doc = []
        array_zapis_worry_doc = []
        array_polis = []
        array_id_patient = []
        end = datetime.datetime.today()
        start = datetime.datetime.today() + datetime.timedelta(days=-1)
        connections.connect_coll("app_reception")
        for poisk_time in connections.coll_connector.find(
            {"date": {"$gt": start, "$lt": end}, "doctor_id": id_docs}
        ):
            array_time_doc.append(poisk_time["time"])
            array_polis.append(poisk_time["polis"])
        sortedArray = sorted(
            array_time_doc, key=lambda x: datetime.datetime.strptime(x, "%H:%M")
        )
        ccc = 0
        while ccc < len(sortedArray):
            for zapis in connections.coll_connector.find(
                {
                    "date": {"$gt": start, "$lt": end},
                    "doctor_id": id_docs,
                    "time": sortedArray[ccc],
                }
            ):
                array_id_patient.append(zapis["id"])
                array_zapis_fio_doc.append(zapis)
                array_zapis_worry_doc.append(zapis["patient_info"])  # Беспокойства
            ccc += 1

    # Функция карточки пациента
    @staticmethod
    def funktion_patient_card(id_pat):
        connections.connect_coll("app_reception")
        # Цикл поиска id пациента в бд
        for patinet_informations in connections.coll_connector.find({"id": id_pat}):
            connections.connect_coll("patient")
            # Цикл поиска полиса этого пацента
            for patinet_informations_polis1 in connections.coll_connector.find(
                {"polis": patinet_informations["polis"]}
            ):
                global patient_card_main, text_journal
                patient_card_main = Tk()
                patient_card_main.geometry("900x600")
                patient_card_main.title("Журал пациентов")
                patient_card_main.config(background="#FFAAA8")
                patient_card_main.resizable(width=False, height=False)
                lbl_patinet_card = Label(
                    patient_card_main,
                    text="Карточка пациента:",
                    background="#FFAAA8",
                    font="times 14",
                )
                text_journal = Text(
                    patient_card_main, width=100, height=25, wrap=WORD, font="times 12"
                )
                connections.connect_coll("patient")
                infor = []
                # Цикл поиска информации о пациенте и запись данных
                for patinet_informations_polis in connections.coll_connector.find(
                    {"polis": patinet_informations["polis"]}
                ):
                    for inf in range(len(patinet_informations_polis["service"])):
                        infor.append(
                            str(patinet_informations_polis["service"][inf][0])
                            + " "
                            + str(patinet_informations_polis["service"][inf][1])
                        )
                    kek = patinet_informations_polis["service"]
                    info = (
                        "Имя врача: "
                        + patinet_informations_polis["doc_name"]
                        + " , "
                        + "Cпециализация: "
                        + patinet_informations_polis["doc_spec"]
                        + " , "
                        + "ФИО пациента: "
                        + patinet_informations_polis["patient_name"]
                        + " , "
                        + "Информация о пациенте: "
                        + patinet_informations_polis["patient_info"]
                        + " , "
                        + "Дата посещения: "
                        + patinet_informations_polis["date"].strftime("%d-%m-%Y")
                        + " , "
                        + "Время посещения: "
                        + patinet_informations_polis["time"]
                        + " , "
                        + "Полис: "
                        + patinet_informations_polis["polis"]
                        + " , "
                        + "Услуги: "
                        + " ".join(infor)
                        + " , "
                        + "Комментарий врача: "
                        + patinet_informations_polis["comment"]
                        + "\n"
                        + "--------------------------------------------------------------------------------------------------------------------------------"
                        + "\n"
                    )
                    text_journal.insert(1.0, info)
                    text_journal.place(x=1, y=50)
                    lbl_patinet_card.place(x=1, y=1)
                break
            else:
                messagebox.showerror("Ошибка", "У пациента нет карточки!")

    # Функция записи услуг
    @staticmethod
    def spend(id_button):
        global list_cb, abc, abc1, array_provesti, array_provesti1, search_patient, entry_com, spend_main_window
        array_provesti = []
        doctor_main_window.destroy()
        spend_main_window = Tk()
        spend_main_window.geometry("825x600")
        spend_main_window.title("Записи услуг")
        spend_main_window.config(background="#FFAAA8")
        spend_main_window.resizable(width=False, height=False)
        pr = 0
        connections.connect_coll("app_reception")
        # Цикл записи выбранных услуг пациенту в бд
        for search_patient in connections.coll_connector.find({"id": id_button}):
            search_patient
            sql_officium = "SELECT officium,price FROM price WHERE doctor_id=?"
            cursor.execute(sql_officium, [(str(search_patient["doctor_id"]))])
            abc = cursor.fetchall()
        plus = 0
        list_cb = []
        # Цикл отображения всех услун из БД
        for pr in range(len(abc)):
            list_cb.append(IntVar())
            list_cb[-1].set(0)
            c1 = Checkbutton(
                text=abc[pr],
                variable=list_cb[-1],
                background="#FFAAA8",
                font="times 12",
                command=lambda pr=pr: Doctors.provesti_pat(pr),
                onvalue=1,
                offvalue=0,
            )
            c1.place(x=1, y=30 + plus)
            plus += 30
        btn_ok = Button(
            spend_main_window,
            text="Провести",
            command=lambda: Doctors.spend_trans(),
            font="times 14",
        )
        btn_ok.place(x=1, y=250 + plus)
        lbl_com = Label(
            spend_main_window, text="Комметарий:", background="#FFAAA8", font="times 14"
        )
        btn_end = Button(
            spend_main_window,
            text="Назад",
            command=lambda: Doctors.back(),
            font="times 14",
        )
        btn_end.place(x=500, y=500)
        lbl_com.place(x=1, y=60 + plus)
        entry_com = Text(spend_main_window, width=50, height=5, wrap=WORD)
        entry_com.place(x=1, y=100 + plus)
        lbl_price_nomen = Label(
            spend_main_window,
            text="Выбор услуги:",
            background="#FFAAA8",
            font="times 14",
        )
        lbl_price_nomen.place(x=1, y=1)
        lbl_patient_name = Label(
            spend_main_window,
            text="Пациент:" + search_patient["patient_name"],
            background="#FFAAA8",
            font="times 14",
        )
        lbl_patient_name.place(x=1, y=570)
        spend_main_window.mainloop()

    # Функция назад
    @staticmethod
    def back():
        spend_main_window.destroy()
        Doctors.doctors_main()

    # Функция которя позволяет определить,какие услуги были выбраны
    # путем записи и удаления из массива
    @staticmethod
    def provesti_pat(pr):
        if list_cb[pr].get() == 1:
            array_provesti.append(abc[pr])
        else:
            array_provesti.remove(abc[pr])

    # Функция записи всех данных о пациенте после приема и передача данных в регистратуру
    @staticmethod
    def spend_trans():
        conn = pymongo.MongoClient(
            "mongodb://dron2026:55555@dron2026-shard-00-00-x59g6.mongodb.net:27017,dron2026-shard-00-01-x59g6.mongodb.net:27017,dron2026-shard-00-02-x59g6.mongodb.net:27017/test?ssl=true&replicaSet=dron2026-shard-0&authSource=admin&retryWrites=true&w=majority"
        )
        db = conn.polyclinic
        coll = db.patient
        patient_info = {
            "patient_id": search_patient["id"],
            "doctor_id": search_patient["doctor_id"],
            "patient_name": search_patient["patient_name"],
            "patient_info": search_patient["patient_info"],
            "date": search_patient["date"],
            "time": search_patient["time"],
            "polis": search_patient["polis"],
            "service": array_provesti,
            "comment": entry_com.get(1.0, END),
            "doc_name": name,
            "doc_spec": specialization,
            "id_check": "1",
        }
        coll.insert_one(patient_info)
        messagebox.showinfo("Успешно", "Данные переданы в регистратуру!")
        spend_main_window.destroy()
        Doctors.doctors_main()


if __name__ == "__main__":
    Auth.main()
