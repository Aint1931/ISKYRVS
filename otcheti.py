from PyQt6.QtWidgets import QMainWindow, QMessageBox, QHeaderView, QFileDialog
from PyQt6.QtSql import QSqlQuery, QSqlTableModel
from PyQt6.QtCore import QDate, Qt, QDateTime
from openpyxl.workbook import Workbook

from otcheti_design import Ui_otchetForm
from adminForm import AdminForm


class OtchetForm(QMainWindow, Ui_otchetForm):
    def __init__(self, user_id, is_admin, is_superadmin):
        super().__init__()
        self.setupUi(self)
        self.user_id = user_id
        self.is_superadmin = is_superadmin
        self.usersListUReport()
        self.usersListPoReport()
        self.userReport.toggled.connect(self.toggle_user_report_frame)
        self.dayReport.toggled.connect(self.toggle_day_report_frame)
        self.poReport.toggled.connect(self.toggle_po_report_frame)
        self.pushButton.clicked.connect(self.user_generate_report)
        self.dayReportBtn.clicked.connect(self.day_generate_report)
        self.poReportBtn.clicked.connect(self.po_generate_report)
        self.fistDate.setDate(QDate.currentDate())
        self.reportDate.setDate(QDate.currentDate())
        self.lastDate.setDate(QDate.currentDate())
        self.poDate.setDate(QDate.currentDate())
        self.userReportFrame.setVisible(False)
        self.dayReportFrame.setVisible(False)
        self.poReportFrame.setVisible(False)
        self.exportBtn.clicked.connect(self.exportToExcel)
        self.is_admin = is_admin
        if not self.is_admin:
            self.adminBtn.setVisible(False)
        self.adminBtn.clicked.connect(self.showAdminForm)

    def toggle_user_report_frame(self, checked):
        if checked:
            self.userReportFrame.setVisible(True)
        else:
            self.userReportFrame.setVisible(False)

    def toggle_day_report_frame(self, checked):
        if checked:
            self.dayReportFrame.setVisible(True)
        else:
            self.dayReportFrame.setVisible(False)

    def toggle_po_report_frame(self, checked):
        if checked:
            self.poReportFrame.setVisible(True)
        else:
            self.poReportFrame.setVisible(False)

    def usersListUReport(self):  # Заполняет ComboBox данными о сотрудниках из базы данных.
        query = QSqlQuery()
        query.exec("SELECT id_accounts, F_sotr, I_sotr, O_sotr FROM dbo.accounts")
        self.selectUser.clear()
        self.selectUser.addItem("- Выберите пользователя -", None)
        while query.next():
            user_id = query.value(0)
            user_name = f"{query.value(1)} {query.value(2)} {query.value(3)}"
            self.selectUser.addItem(user_name, user_id)

    def usersListPoReport(self): # Заполняет ComboBox данными о сотрудниках из базы данных.
        query = QSqlQuery()
        query.exec("SELECT id_accounts, F_sotr, I_sotr, O_sotr FROM dbo.accounts")
        self.selectPoUser.clear()
        self.selectPoUser.addItem("- Выберите пользователя -", None)
        while query.next():
            user_id = query.value(0)
            user_name = f"{query.value(1)} {query.value(2)} {query.value(3)}"
            self.selectPoUser.addItem(user_name, user_id)

    def user_generate_report(self): # Формирует отчет о рабочем времени сотрудника за выбранный период.
        user_id = self.selectUser.currentData()
        start_date = self.fistDate.date().toString("dd-MM-yyyy")
        end_date = self.lastDate.date().toString("dd-MM-yyyy")

        if not user_id:
            QMessageBox.warning(self, "Ошибка", "Сотрудник не выбран")
            return

        query = QSqlQuery()
        query.prepare("""
            SELECT data, nachal_rab_den, okonch_rab_den, dlit
            FROM dbo.TYRV
            WHERE accounts2_id = :user_id AND data BETWEEN :start_date AND :end_date
        """)
        query.bindValue(":user_id", user_id)
        query.bindValue(":start_date", start_date)
        query.bindValue(":end_date", end_date)

        if query.exec():
            model = QSqlTableModel()
            model.setQuery(query)

            model.setHeaderData(0, Qt.Orientation.Horizontal, "Дата")
            model.setHeaderData(1, Qt.Orientation.Horizontal, "Начало рабочего дня")
            model.setHeaderData(2, Qt.Orientation.Horizontal, "Окончание рабочего дня")
            model.setHeaderData(3, Qt.Orientation.Horizontal, "Длительность")

            self.otchetTable.setModel(model)

            self.otchetTable.resizeColumnsToContents()
            self.otchetTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось сформировать отчет")

    def day_generate_report(self):  # Формирует отчет о рабочем времени всех сотрудников за выбранный день.
        selected_date = self.reportDate.date().toString("dd-MM-yyyy")

        query = QSqlQuery()
        query.prepare("""
               SELECT 
                   CONCAT(a.F_sotr, ' ', a.I_sotr, ' ', a.O_sotr) AS ФИО, 
                   t.nachal_rab_den, 
                   t.okonch_rab_den, 
                   t.dlit
               FROM dbo.TYRV t
               JOIN dbo.accounts a ON t.accounts2_id = a.id_accounts
               WHERE t.data = :selected_date
           """)
        query.bindValue(":selected_date", selected_date)

        if query.exec():
            model = QSqlTableModel()
            model.setQuery(query)

            model.setHeaderData(0, Qt.Orientation.Horizontal, "ФИО")
            model.setHeaderData(1, Qt.Orientation.Horizontal, "Начало рабочего дня")
            model.setHeaderData(2, Qt.Orientation.Horizontal, "Окончание рабочего дня")
            model.setHeaderData(3, Qt.Orientation.Horizontal, "Длительность")

            self.otchetTable.setModel(model)
            self.otchetTable.resizeColumnsToContents()
            self.otchetTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось сформировать отчет")

    def po_generate_report(self):  # Генерирует отчет о запущенных процессах для выбранного пользователя
        selected_user_id = self.selectPoUser.currentData()  # Получаем ID выбранного пользователя
        selected_date = self.reportDate.date().toString("dd-MM-yyyy")  # Получаем выбранную дату

        if not selected_user_id:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите сотрудника.")
            return

        query = QSqlQuery()
        query.prepare("""
            SELECT id_po, nazv_po
            FROM dbo.PO
            WHERE accounts1_id = :user_id AND data_ychet_po = :date
        """)
        query.bindValue(":user_id", selected_user_id)
        query.bindValue(":date", selected_date)

        if query.exec():
            model = QSqlTableModel()
            model.setQuery(query)

            model.setHeaderData(0, Qt.Orientation.Horizontal, "ID")
            model.setHeaderData(1, Qt.Orientation.Horizontal, "Запущенные процессы")

            self.otchetTable.setModel(model)

            self.otchetTable.resizeColumnsToContents()
            self.otchetTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось сформировать отчет.")

    def showAdminForm(self):
        self.admin_form = AdminForm(self.is_superadmin)
        self.admin_form.show()

    def closeEvent(self, event):
        """Обрабатывает закрытие формы."""
        event.accept()

    def exportToExcel(self): # Экспортирует данные из таблицы в файл Excel.
        # Получаем модель таблицы
        model = self.otchetTable.model()

        # Проверяем, что таблица не пустая
        if model is None or model.rowCount() == 0:
            QMessageBox.warning(self, "Ошибка", "Нет данных для экспорта. Сформируйте отчет.")
            return
        if self.userReport.isChecked():
            report_type = "Отчет по пользователю"
        else:
            report_type = "Отчет за день"

        current_datetime = QDateTime.currentDateTime()
        formatted_datetime = current_datetime.toString("dd-MM-yyyy_hh-mm")
        file_name = f"{report_type}_{formatted_datetime}.xlsx"

        # Открываем окно для сохранения файла
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить файл Excel",
            file_name,
            "Excel Files (*.xlsx)"
        )

        if not file_path:
            return

        # Создаем новый Excel-файл
        workbook = Workbook()
        sheet = workbook.active

        # Записываем заголовки столбцов
        headers = []
        for col in range(model.columnCount()):
            headers.append(model.headerData(col, Qt.Orientation.Horizontal))
        sheet.append(headers)

        # Записываем данные из таблицы
        for row in range(model.rowCount()):
            row_data = []
            for col in range(model.columnCount()):
                index = model.index(row, col)
                row_data.append(model.data(index))
            sheet.append(row_data)

        # Сохраняем файл
        try:
            workbook.save(file_path)
            QMessageBox.information(self, "Успех", f"Данные успешно экспортированы в файл:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл:\n{str(e)}")
