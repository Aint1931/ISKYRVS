from PyQt6.QtCore import QDate, QTime
from PyQt6.QtSql import QSqlQuery, QSqlQueryModel
from PyQt6.QtWidgets import QMainWindow, QHeaderView, QMessageBox
from adminFormTimeDesign import Ui_adminFormTime


class AdminFormTime(QMainWindow, Ui_adminFormTime):
    def __init__(self, is_superadmin):
        super().__init__()
        self.setupUi(self)
        self.is_superadmin = is_superadmin
        self.usersList()
        self.menuTime.setEnabled(False)
        self.menuSotr.triggered.connect(self.open_sotr_form)
        self.menuPo.triggered.connect(self.open_po_form)
        self.menuWeb.triggered.connect(self.open_web_form)
        self.selectDate.setDate(QDate.currentDate())
        self.setup_table()
        self.startTimeEdit.setEnabled(False)
        self.finishTimeEdit.setEnabled(False)
        self.selectPolz.currentIndexChanged.connect(self.load_work_time)
        self.selectDate.dateChanged.connect(self.load_work_time)
        self.clearBtn.clicked.connect(self.clearData)
        self.deleteBtn.clicked.connect(self.deleteWorkTime)
        self.updateBtn.clicked.connect(self.updateWorkTime)
        self.addTimeBtn.clicked.connect(self.addWorkTime)

    def usersList(self):
        query = QSqlQuery()
        query.exec("""
            SELECT a.id_accounts, s.F_sotr, s.I_sotr, s.O_sotr
            FROM dbo.accounts a
            JOIN dbo.sotr s ON a.sotr_id = s.id_sotr
        """)
        self.selectPolz.clear()
        self.selectPolz.addItem("- Выберите пользователя -", None)
        while query.next():
            user_id = query.value(0)
            user_name = f"{query.value(1)} {query.value(2)} {query.value(3)}"
            self.selectPolz.addItem(user_name, user_id)

    def load_work_time(self):
        """Загружает данные о рабочем времени для выбранного пользователя и даты"""
        user_id = self.selectPolz.currentData()
        selected_date = self.selectDate.date().toString("dd-MM-yyyy")

        if user_id:
            self.startTimeEdit.setEnabled(True)
            self.finishTimeEdit.setEnabled(True)
        else:
            self.startTimeEdit.setEnabled(False)
            self.finishTimeEdit.setEnabled(False)
            self.startTimeEdit.setTime(QTime(0, 0))
            self.finishTimeEdit.setTime(QTime(0, 0))
            return

        query = QSqlQuery()
        query.prepare("""
            SELECT nachal_rab_den, okonch_rab_den 
            FROM dbo.TYRV 
            WHERE accounts2_id = ? AND data = ?
        """)
        query.addBindValue(user_id)
        query.addBindValue(selected_date)

        if not query.exec():
            print("Ошибка SQL:", query.lastError().text())
            return

        if query.next():
            start_str = query.value(0)
            end_str = query.value(1)
            start_time = QTime.fromString(start_str, "HH:mm:ss") if start_str else QTime(0, 0)
            end_time = QTime.fromString(end_str, "HH:mm:ss") if end_str else QTime(0, 0)
            self.startTimeEdit.setTime(start_time)
            self.finishTimeEdit.setTime(end_time)
        else:
            self.startTimeEdit.setTime(QTime(0, 0))
            self.finishTimeEdit.setTime(QTime(0, 0))

    def calculate_duration(self, start_time: QTime, end_time: QTime) -> str:
        if not start_time.isValid() or not end_time.isValid():
            return "00:00:00"

        if end_time < start_time:
            end_time = end_time.addSecs(24 * 60 * 60)

        seconds = start_time.secsTo(end_time)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def updateWorkTime(self):
        user_id = self.selectPolz.currentData()
        if not user_id:
            QMessageBox.warning(self, "Ошибка", "Пользователь не выбран!")
            return
        selected_date = self.selectDate.date().toString("dd-MM-yyyy")
        start_time = self.startTimeEdit.time()
        end_time = self.finishTimeEdit.time()
        duration = self.calculate_duration(start_time, end_time)
        check_query = QSqlQuery()
        check_query.prepare("SELECT id_TYRV FROM dbo.TYRV WHERE accounts2_id = ? AND data = ?")
        check_query.addBindValue(user_id)
        check_query.addBindValue(selected_date)

        if not check_query.exec() or not check_query.next():
            QMessageBox.information(self, "Ошибка", "Данные за выбранный день отсутствуют!")
            return
        update_query = QSqlQuery()
        update_query.prepare("""
                UPDATE dbo.TYRV 
                SET nachal_rab_den = ?, okonch_rab_den = ?, dlit = ?
                WHERE id_TYRV = ?
            """)
        update_query.addBindValue(start_time.toString("HH:mm:ss"))
        update_query.addBindValue(end_time.toString("HH:mm:ss"))
        update_query.addBindValue(duration)
        update_query.addBindValue(check_query.value(0))

        if update_query.exec():
            QMessageBox.information(self, "Успех", "Данные успешно обновлены!")
            self.setup_table()
        else:
            QMessageBox.critical(self, "Ошибка", f"Ошибка обновления: {update_query.lastError().text()}")

    def addWorkTime(self):
        user_id = self.selectPolz.currentData()
        if not user_id:
            QMessageBox.warning(self, "Ошибка", "Пользователь не выбран!")
            return
        selected_date = self.selectDate.date().toString("dd-MM-yyyy")
        start_time = self.startTimeEdit.time()
        end_time = self.finishTimeEdit.time()
        duration = self.calculate_duration(start_time, end_time)
        query_check = QSqlQuery()
        query_check.prepare("""
            SELECT 1 FROM dbo.TYRV WHERE accounts2_id = :user_id AND data = :selected_date
        """)
        query_check.bindValue(":user_id", user_id)
        query_check.bindValue(":selected_date", selected_date)

        if query_check.exec() and query_check.next():
            QMessageBox.warning(self, "Ошибка", "Запись за этот день уже существует!")
            return

        insert_query = QSqlQuery()
        insert_query.prepare("""
            INSERT INTO dbo.TYRV (accounts2_id, data, nachal_rab_den, okonch_rab_den, dlit) 
            VALUES (:user_id, :selected_date, :start_time, :end_time, :duration)
        """)
        insert_query.bindValue(":user_id", user_id)
        insert_query.bindValue(":selected_date", selected_date)
        insert_query.bindValue(":start_time", start_time.toString("HH:mm:ss"))
        insert_query.bindValue(":end_time", end_time.toString("HH:mm:ss"))
        insert_query.bindValue(":duration", duration)

        if insert_query.exec():
            QMessageBox.information(self, "Успех", "Данные успешно добавлены!")
            self.setup_table()
        else:
            QMessageBox.critical(self, "Ошибка", f"Ошибка добавления: {insert_query.lastError().text()}")

    def clearData(self):
        self.selectPolz.setCurrentIndex(0)
        self.startTimeEdit.setTime(QTime(0, 0))
        self.finishTimeEdit.setTime(QTime(0, 0))
        self.startTimeEdit.setEnabled(False)
        self.finishTimeEdit.setEnabled(False)
        self.usersList()
        self.setup_table()

    def deleteWorkTime(self):
        user_id = self.selectPolz.currentData()

        if not user_id:
            QMessageBox.warning(self, "Ошибка", "Пользователь не выбран!")
            return

        selected_date = self.selectDate.date().toString("dd-MM-yyyy")
        check_query = QSqlQuery()
        check_query.prepare("""
            SELECT id_TYRV FROM dbo.TYRV 
            WHERE accounts2_id = ? AND data = ?
        """)
        check_query.addBindValue(user_id)
        check_query.addBindValue(selected_date)

        if not check_query.exec():
            QMessageBox.critical(self, "Ошибка", "Ошибка при проверке данных!")
            return

        if not check_query.next():
            QMessageBox.information(self, "Информация", "Данные за выбранный день отсутствуют!")
            return
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы действительно хотите удалить данные за выбранный день?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.No:
            return
        delete_query = QSqlQuery()
        delete_query.prepare("""
            DELETE FROM dbo.TYRV 
            WHERE accounts2_id = ? AND data = ?
        """)
        delete_query.addBindValue(user_id)
        delete_query.addBindValue(selected_date)

        if delete_query.exec():
            QMessageBox.information(self, "Успех", "Данные успешно удалены!")
            self.clearData()
            self.setup_table()
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось удалить данные!")
    def setup_table(self):
        self.model = QSqlQueryModel()
        query = """
            SELECT 
                t.nachal_rab_den AS 'Начало работы',
                t.okonch_rab_den AS 'Конец работы',
                t.dlit AS 'Длительность',
                t.data AS 'Дата',
                s.F_sotr + ' ' + s.I_sotr + ' ' + s.O_sotr AS 'Сотрудник',
                t.id_TYRV AS 'ID'
            FROM dbo.TYRV t
            JOIN dbo.accounts a ON t.accounts2_id = a.id_accounts
            JOIN dbo.sotr s ON a.sotr_id = s.id_sotr
            ORDER BY t.data DESC
        """
        self.model.setQuery(query)
        self.timeTable.setModel(self.model)
        self.timeTable.resizeColumnsToContents()
        self.timeTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def open_sotr_form(self):
        from adminFormSotr import AdminForm
        self.close()
        self.form = AdminForm(self.is_superadmin)
        self.form.show()

    def open_po_form(self):
        from adminFormPO import AdminFormPO
        self.close()
        self.form = AdminFormPO(self.is_superadmin)
        self.form.show()

    def open_web_form(self):
        from adminFormWeb import AdminFormWeb
        self.close()
        self.form = AdminFormWeb(self.is_superadmin)
        self.form.show()

    def closeEvent(self, event):
        self.menuTime.setEnabled(True)