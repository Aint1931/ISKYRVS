import psutil
from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.QtCore import QTimer, QDateTime
from PyQt6.QtSql import QSqlQuery
from user_form_design import Ui_uchet  # Импортируйте сгенерированный класс формы


class UchetForm(QMainWindow, Ui_uchet):
    def __init__(self, user_id):
        super().__init__()
        self.setupUi(self)
        self.user_id = user_id
        self.start_time = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.startBtn.clicked.connect(self.start_work)
        self.finishBtn.clicked.connect(self.finish_work)
        self.active_processes = set()  # Используем множество для уникальных приложений

    def start_work(self):
        query = QSqlQuery()
        query.prepare("""
                   SELECT id_TYRV FROM dbo.TYRV 
                   WHERE accounts2_id = :user_id AND data = :today
               """)
        query.bindValue(":user_id", self.user_id)
        query.bindValue(":today", QDateTime.currentDateTime().toString("dd-MM-yyyy"))

        if query.exec() and query.next():
            QMessageBox.warning(self, "Ошибка", "Рабочий день уже завершен. Для изменения данных учета рабочего дня "
                                                "обратитесь к своему руководителю или администратору.")
            return

        self.start_time = QDateTime.currentDateTime()
        self.timer.start(1000)
        self.startBtn.setEnabled(False)
        self.finishBtn.setEnabled(True)


        self.active_processes = self.getActiveProcesses()

    def finish_work(self):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Подтверждение")
        msg_box.setText("Вы действительно хотите завершить рабочий день?")
        yes_button = msg_box.addButton("Да", QMessageBox.ButtonRole.YesRole)
        no_button = msg_box.addButton("Нет", QMessageBox.ButtonRole.NoRole)
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.exec()
        if msg_box.clickedButton() == yes_button:
            self.timer.stop()
            end_time = QDateTime.currentDateTime()
            duration = self.start_time.secsTo(end_time)

            # Сохранение данных рабочего дня
            self.saveWorkDay(self.start_time.toString("HH:mm:ss"),
                               end_time.toString("HH:mm:ss"),
                               duration)

            # Сохранение уникальных активных приложений
            self.saveAtiveApps(self.active_processes)

            self.startBtn.setEnabled(True)
            self.finishBtn.setEnabled(False)
        else:
            return

    def update_time(self): # Выводит длительность рабочего дня на форму в объект Label
        current_time = QDateTime.currentDateTime()
        duration = self.start_time.secsTo(current_time)
        self.labelTime.setText(
            f"Время активности: {duration // 3600:02}:{(duration % 3600) // 60:02}:{duration % 60:02}")

    def getActiveProcesses(self): # Получает список всех запущенных приложений
        processes = set()
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                processes.add(proc.info['name'])
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return processes

    def saveWorkDay(self, start_time, end_time, duration_seconds):
        # Сохранить данные о рабочем дне
        hours, remainder = divmod(duration_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        dlit = f"{hours:02}:{minutes:02}:{seconds:02}"
        query = QSqlQuery()
        query.prepare("""
            INSERT INTO dbo.TYRV (nachal_rab_den, okonch_rab_den, dlit, data, accounts2_id)
            VALUES (:start_time, :end_time, :duration, :date, :user_id)
        """)
        query.bindValue(":start_time", start_time)
        query.bindValue(":end_time", end_time)
        query.bindValue(":duration", dlit)
        query.bindValue(":date", QDateTime.currentDateTime().toString("dd-MM-yyyy"))
        query.bindValue(":user_id", self.user_id)
        if not query.exec():
            print("Ошибка при сохранении данных:", query.lastError().text())

    def saveActiveApps(self, active_processes):
        # Сохраняет данные о приложениях в БД с использованием хранимой процедуры add_PO
        for app in active_processes:
            query = QSqlQuery()
            query.prepare("EXEC dbo.add_PO @nazv_po = :nazv_po, @data_ychet_po = :data_ychet_po, @accounts1_id = :user_id")
            query.bindValue(":nazv_po", app)  # Название приложения
            query.bindValue(":data_ychet_po", QDateTime.currentDateTime().toString("dd-MM-yyyy"))
            query.bindValue(":user_id", self.user_id)
            if not query.exec():
                print("Ошибка при сохранении приложения:", query.lastError().text())