import hashlib
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtSql import QSqlQuery, QSqlTableModel, QSqlQueryModel
from PyQt6.QtWidgets import QMainWindow, QHeaderView, QMessageBox, QDialog, QLineEdit, QVBoxLayout, QPushButton, \
    QCheckBox, QTableView


from adminFormSotrDesign import Ui_adminFormSotr


class AdminForm(QMainWindow, Ui_adminFormSotr):
    def __init__(self, is_superadmin):
        super().__init__()
        self.setupUi(self)
        self.usersList()
        self.is_superadmin = is_superadmin
        self.polzTableShowData()
        self.selectPolz.currentIndexChanged.connect(self.userSelected)
        self.updatePolzBtn.clicked.connect(self.userDataUpdate)
        self.updatePasswordBtn.clicked.connect(self.changePasswordFormShow)
        self.clearBtn.clicked.connect(self.clearData)
        self.addPolzBtn.clicked.connect(self.addUserForm)
        self.menuSotr.setEnabled(False)
        self.menuTime.triggered.connect(self.open_time_form)
        self.menuPo.triggered.connect(self.open_po_form)
        self.menuWeb.triggered.connect(self.open_web_form)
        self.upFrameEnabled(False)
        if not self.is_superadmin:
            self.adminCheck.setEnabled(False)

    def upFrameEnabled(self, enabled):
        self.fEdit.setEnabled(enabled)
        self.iEdit.setEnabled(enabled)
        self.oEdit.setEnabled(enabled)
        self.doljEdit.setEnabled(enabled)
        if self.is_superadmin:
            self.adminCheck.setEnabled(enabled)
        self.supervisorCheck.setEnabled(enabled)
        self.updatePolzBtn.setEnabled(enabled)
        self.updatePasswordBtn.setEnabled(enabled)

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

    def polzTableShowData(self):
        model = QSqlQueryModel()
        query = """
            SELECT 
                a.id_accounts AS 'ID',
                a.user_login AS 'Логин',
                a.user_password AS 'Пароль',
                a.administrator AS 'Администратор',
                a.supervisor AS 'Руководитель',
                a.superadmin AS 'Супер-админ',
                s.F_sotr AS 'Фамилия',
                s.I_sotr AS 'Имя',
                s.O_sotr AS 'Отчество',
                d.dolj AS 'Должность'
            FROM 
                accounts a
            JOIN 
                sotr s ON a.sotr_id = s.id_sotr
            JOIN 
                dolj d ON s.dolj_id = d.id_dolj
        """
        model.setQuery(query)
        self.polzTable.setModel(model)
        self.polzTable.setColumnHidden(2, True)
        self.polzTable.setColumnHidden(3, True)
        self.polzTable.setColumnHidden(4, True)
        self.polzTable.setColumnHidden(5, True)
        self.polzTable.resizeColumnsToContents()
        self.polzTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def userSelected(self, index):
        user_id = self.selectPolz.currentData()

        if user_id is None:
            self.upFrameEnabled(False)
            return


        self.upFrameEnabled(True)


        query = QSqlQuery()
        query.prepare("""
            SELECT a.user_login, s.F_sotr, s.I_sotr, s.O_sotr, d.dolj, a.administrator, a.supervisor
            FROM dbo.accounts a
            JOIN dbo.sotr s ON a.sotr_id = s.id_sotr
            JOIN dbo.dolj d ON s.dolj_id = d.id_dolj
            WHERE a.id_accounts = :user_id
        """)
        query.bindValue(":user_id", user_id)

        if query.exec() and query.next():
            self.fEdit.setText(query.value("F_sotr"))
            self.iEdit.setText(query.value("I_sotr"))
            self.oEdit.setText(query.value("O_sotr"))
            self.doljEdit.setText(query.value("dolj"))
            self.adminCheck.setChecked(query.value("administrator"))
            self.supervisorCheck.setChecked(query.value("supervisor"))

    def userDataUpdate(self):
        user_id = self.selectPolz.currentData()

        if user_id is None:
            QMessageBox.warning(self, "Ошибка", "Пользователь не выбран.")
            return

        fam = self.fEdit.text()
        name = self.iEdit.text()
        otch = self.oEdit.text()
        dolj = self.doljEdit.text()
        is_admin = self.adminCheck.isChecked()
        is_supervisor = self.supervisorCheck.isChecked()

        if not fam or not name or not otch or not dolj:
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены.")
            return
        query = QSqlQuery()
        query.prepare("SELECT user_login, user_password FROM dbo.accounts WHERE sotr_id = :user_id")
        query.bindValue(":user_id", user_id)
        if query.exec() and query.next():
            current_login = query.value(0)
            current_password = query.value(1)
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось получить текущие данные пользователя.")
            return
        query.prepare(
            "EXEC [DBO].[UpdateSotrInfo] @id_sotr = :user_id, @F_sotr = :fam, @I_sotr = :name, @O_sotr = :otch, "
            "@nazvanie_dolj = :dolj, @user_login = :login, @user_password = :password, "
            "@administrator = :is_admin, @supervisor = :is_supervisor, @superadmin = :is_superadmin")
        query.bindValue(":user_id", user_id)
        query.bindValue(":fam", fam)
        query.bindValue(":name", name)
        query.bindValue(":otch", otch)
        query.bindValue(":dolj", dolj)
        query.bindValue(":login", current_login)
        query.bindValue(":password", current_password)
        query.bindValue(":is_admin", is_admin)
        query.bindValue(":is_supervisor", is_supervisor)
        query.bindValue(":is_superadmin", False)

        if query.exec():
            QMessageBox.information(self, "Успех", "Данные пользователя обновлены.")
            self.polzTableShowData()
            self.usersList()
        else:
            QMessageBox.warning(self, "Ошибка", f"Ошибка обновления данных: {query.lastError().text()}")

    def changePasswordFormShow(self):
        user_id = self.selectPolz.currentData()

        if user_id is None:
            QMessageBox.warning(self, "Ошибка", "Пользователь не выбран.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Изменить пароль")
        dialog.setModal(True)

        font = QFont("Noto Sans", 12)
        dialog.setFont(font)

        layout = QVBoxLayout()

        newPasswordEdit = QLineEdit(dialog)
        newPasswordEdit.setPlaceholderText("Новый пароль")
        newPasswordEdit.setEchoMode(QLineEdit.EchoMode.Password)
        newPasswordEdit.setFont(font)
        layout.addWidget(newPasswordEdit)

        confirmPasswordEdit = QLineEdit(dialog)
        confirmPasswordEdit.setPlaceholderText("Повторите пароль")
        confirmPasswordEdit.setEchoMode(QLineEdit.EchoMode.Password)
        confirmPasswordEdit.setFont(font)
        layout.addWidget(confirmPasswordEdit)

        save_btn = QPushButton("Сохранить", dialog)
        save_btn.setFont(font)
        cancel_btn = QPushButton("Отмена", dialog)
        cancel_btn.setFont(font)

        layout.addWidget(save_btn)
        layout.addWidget(cancel_btn)

        save_btn.clicked.connect(
            lambda: self.updatePassword(user_id, newPasswordEdit.text(), confirmPasswordEdit.text(), dialog))
        cancel_btn.clicked.connect(dialog.close)

        dialog.setLayout(layout)
        dialog.exec()

    def hash_password(self, password):

        return hashlib.sha256(password.encode()).hexdigest()

    def updatePassword(self, user_id, new_password, confirm_password, dialog):
        if new_password != confirm_password:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают.")
            return

        hashed_password = self.hash_password(new_password)

        query = QSqlQuery()
        query.prepare("""
            UPDATE dbo.accounts
            SET user_password = :password
            WHERE id_accounts = :user_id
        """)
        query.bindValue(":password", hashed_password)
        query.bindValue(":user_id", user_id)

        if query.exec():
            QMessageBox.information(self, "Успех", "Пароль успешно изменен.")
            self.polzTableShowData()
            dialog.close()
        else:
            QMessageBox.warning(self, "Ошибка", f"Не удалось изменить пароль: {query.lastError().text()}")

    def clearData(self):
        self.selectPolz.setCurrentIndex(0)
        self.upFrameEnabled(False)
        self.fEdit.clear()
        self.iEdit.clear()
        self.oEdit.clear()
        self.doljEdit.clear()
        self.adminCheck.setChecked(False)
        self.supervisorCheck.setChecked(False)

    def addUserForm(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить нового сотрудника")
        dialog.setModal(True)

        font = QFont("Noto Sans", 12)
        dialog.setFont(font)

        layout = QVBoxLayout()

        famEdit = QLineEdit(dialog)
        famEdit.setPlaceholderText("Фамилия")
        famEdit.setFont(font)
        layout.addWidget(famEdit)

        nameEdit = QLineEdit(dialog)
        nameEdit.setPlaceholderText("Имя")
        nameEdit.setFont(font)
        layout.addWidget(nameEdit)

        otchEdit = QLineEdit(dialog)
        otchEdit.setPlaceholderText("Отчество")
        otchEdit.setFont(font)
        layout.addWidget(otchEdit)

        loginEdit = QLineEdit(dialog)
        loginEdit.setPlaceholderText("Логин")
        loginEdit.setFont(font)
        layout.addWidget(loginEdit)

        passwordEdit = QLineEdit(dialog)
        passwordEdit.setPlaceholderText("Пароль")
        passwordEdit.setEchoMode(QLineEdit.EchoMode.Password)
        passwordEdit.setFont(font)
        layout.addWidget(passwordEdit)

        doljEdit = QLineEdit(dialog)
        doljEdit.setPlaceholderText("Должность")
        doljEdit.setFont(font)
        layout.addWidget(doljEdit)

        adminCheck = QCheckBox("Администратор", dialog)
        adminCheck.setFont(font)
        layout.addWidget(adminCheck)
        if not self.is_superadmin:
            adminCheck.setEnabled(False)

        supervisorCheck = QCheckBox("Руководитель", dialog)
        supervisorCheck.setFont(font)
        layout.addWidget(supervisorCheck)

        save_btn = QPushButton("Сохранить", dialog)
        save_btn.setFont(font)
        cancel_btn = QPushButton("Отмена", dialog)
        cancel_btn.setFont(font)

        layout.addWidget(save_btn)
        layout.addWidget(cancel_btn)

        save_btn.clicked.connect(
            lambda: self.saveNewUser(
                famEdit.text(),
                nameEdit.text(),
                otchEdit.text(),
                loginEdit.text(),
                passwordEdit.text(),
                doljEdit.text(),
                adminCheck.isChecked(),
                supervisorCheck.isChecked(),
                dialog
            )
        )
        cancel_btn.clicked.connect(dialog.close)

        dialog.setLayout(layout)
        dialog.exec()

    def saveNewUser(self, fam, name, otch, login, password, dolj, is_admin, is_supervisor, dialog):
        if not fam or not name or not otch or not login or not password or not dolj:
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены.")
            return

        hashed_password = self.hash_password(password)

        query = QSqlQuery()
        query.prepare("EXEC [DBO].[AddSotrInfo] @F_sotr = :fam, @I_sotr = :name, @O_sotr = :otch, "
                      "@nazvanie_dolj = :dolj, @user_login = :login, @user_password = :password, "
                      "@administrator = :is_admin, @supervisor = :is_supervisor, @superadmin = :is_superadmin")
        query.bindValue(":fam", fam)
        query.bindValue(":name", name)
        query.bindValue(":otch", otch)
        query.bindValue(":dolj", dolj)
        query.bindValue(":login", login)
        query.bindValue(":password", hashed_password)
        query.bindValue(":is_admin", is_admin)
        query.bindValue(":is_supervisor", is_supervisor)
        query.bindValue(":is_superadmin", False)

        if query.exec():
            QMessageBox.information(self, "Успех", "Новый сотрудник успешно добавлен.")
            self.polzTableShowData()
            self.usersList()
            dialog.close()
        else:
            QMessageBox.warning(self, "Ошибка", f"Ошибка добавления сотрудника: {query.lastError().text()}")

    def open_time_form(self):
        from adminFormTime import AdminFormTime
        self.close()
        self.form = AdminFormTime(self.is_superadmin)
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
        self.menuSotr.setEnabled(True)
        event.accept()