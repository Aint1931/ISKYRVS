from PyQt6.QtCore import QDate
from PyQt6.QtSql import QSqlQuery, QSqlQueryModel
from PyQt6.QtWidgets import QMainWindow, QHeaderView
from adminFormPODesign import Ui_adminFormPO


class AdminFormPO(QMainWindow, Ui_adminFormPO):
    def __init__(self, is_superadmin):
        super().__init__()
        self.setupUi(self)
        self.is_superadmin = is_superadmin
        self.usersList()
        self.menuPo.setEnabled(False)
        self.menuSotr.triggered.connect(self.open_sotr_form)
        self.menuTime.triggered.connect(self.open_time_form)
        self.menuWeb.triggered.connect(self.open_web_form)
        self.selectDate.setDate(QDate.currentDate())
        self.deleteBtn.clicked.connect(self.delete_data)
        self.setup_table()
        self.setup_date_filter()

    def setup_table(self):
        self.model = QSqlQueryModel()
        selected_user_id = self.selectPolz.currentData()
        selected_date = self.selectDate.date().toString("dd-MM-yyyy")  # Формат даты

        if selected_user_id is None:
            query = f"""
                SELECT 
                    s.F_sotr + ' ' + s.I_sotr + ' ' + s.O_sotr AS Сотрудник,
                    p.nazv_po AS 'Название ПО',
                    p.data_ychet_po AS 'Дата учёта',
                    p.id_po AS 'ID ПО'
                FROM dbo.PO p
                JOIN dbo.accounts a ON p.accounts1_id = a.id_accounts
                JOIN dbo.sotr s ON a.sotr_id = s.id_sotr
                WHERE p.data_ychet_po = '{selected_date}'
                ORDER BY p.data_ychet_po DESC
            """
        else:
            query = f"""
                SELECT 
                    s.F_sotr + ' ' + s.I_sotr + ' ' + s.O_sotr AS Сотрудник,
                    p.nazv_po AS 'Название ПО',
                    p.data_ychet_po AS 'Дата учёта',
                    p.id_po AS 'ID ПО'
                FROM dbo.PO p
                JOIN dbo.accounts a ON p.accounts1_id = a.id_accounts
                JOIN dbo.sotr s ON a.sotr_id = s.id_sotr
                WHERE p.data_ychet_po = '{selected_date}' 
                AND a.id_accounts = {selected_user_id}
                ORDER BY p.data_ychet_po DESC
            """

        self.model.setQuery(query)
        self.poTable.setModel(self.model)
        self.poTable.setColumnHidden(3, True)
        self.poTable.resizeColumnsToContents()
        self.poTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def delete_data(self):
        selected_user_id = self.selectPolz.currentData()
        selected_date = self.selectDate.date().toString("dd-MM-yyyy")

        if selected_user_id is None:
            query = QSqlQuery()
            query.prepare("""
                DELETE FROM dbo.PO 
                WHERE data_ychet_po = :date
            """)
            query.bindValue(":date", selected_date)
        else:
            query = QSqlQuery()
            query.prepare("""
                DELETE FROM dbo.PO 
                WHERE accounts1_id = :user_id 
                AND data_ychet_po = :date
            """)
            query.bindValue(":user_id", selected_user_id)
            query.bindValue(":date", selected_date)

        if query.exec():
            self.statusBar().showMessage("Данные удалены успешно")
            self.setup_table()
        else:
            self.statusBar().showMessage("Ошибка при удалении данных")

    def usersList(self):
        query = QSqlQuery()
        query.exec("""
            SELECT a.id_accounts, s.F_sotr, s.I_sotr, s.O_sotr
            FROM dbo.accounts a
            JOIN dbo.sotr s ON a.sotr_id = s.id_sotr
        """)
        self.selectPolz.clear()
        self.selectPolz.addItem("- Все пользователи -", None)
        while query.next():
            user_id = query.value(0)
            user_name = f"{query.value(1)} {query.value(2)} {query.value(3)}"
            self.selectPolz.addItem(user_name, user_id)
        self.selectPolz.currentIndexChanged.connect(self.setup_table)

    def setup_date_filter(self):
        self.selectDate.dateChanged.connect(self.setup_table)

    def open_sotr_form(self):
        from adminFormSotr import AdminForm
        self.close()
        self.form = AdminForm(self.is_superadmin)
        self.form.show()

    def open_time_form(self):
        from adminFormTime import AdminFormTime
        self.close()
        self.form = AdminFormTime(self.is_superadmin)
        self.form.show()

    def open_web_form(self):
        from adminFormWeb import AdminFormWeb
        self.close()
        self.form = AdminFormWeb(self.is_superadmin)
        self.form.show()

    def closeEvent(self, event):
        self.menuPo.setEnabled(True)
        event.accept()