import hashlib
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtSql import QSqlQuery, QSqlTableModel
from PyQt6.QtWidgets import QMainWindow, QHeaderView, QMessageBox, QDialog, QLineEdit, QVBoxLayout, QPushButton, \
    QCheckBox, QTableView


from adminFormDesign import Ui_adminForm


class AdminForm(QMainWindow, Ui_adminForm):
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
        self.addPolzBtn.clicked.connect(self.addUserForm)  # Подключаем кнопку добавления сотрудника

        # Делаем кнопки и поля неактивными до выбора пользователя
        self.upFrameEnabled(False)
        if not self.is_superadmin:
            self.adminCheck.setEnabled(False)

    def upFrameEnabled(self, enabled):
        """Активирует или деактивирует поля и кнопки."""
        self.fEdit.setEnabled(enabled)
        self.iEdit.setEnabled(enabled)
        self.oEdit.setEnabled(enabled)
        self.doljEdit.setEnabled(enabled)
        if self.is_superadmin:
            self.adminCheck.setEnabled(enabled)
        self.supervisorCheck.setEnabled(enabled)
        self.updatePolzBtn.setEnabled(enabled)
        self.updatePasswordBtn.setEnabled(enabled)

    def usersList(self):  # Заполняет ComboBox данными о сотрудниках из базы данных.
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

    def polzTableShowData(self):  # Выводит данные о пользователях в таблицу.
        model = QSqlTableModel()
        model.setTable("accounts")
        model.setHeaderData(0, Qt.Orientation.Horizontal, "ID")
        model.setHeaderData(1, Qt.Orientation.Horizontal, "Логин")
        model.setHeaderData(2, Qt.Orientation.Horizontal, "Пароль")
        model.setHeaderData(3, Qt.Orientation.Horizontal, "Администратор")
        model.setHeaderData(4, Qt.Orientation.Horizontal, "Руководитель")
        model.setHeaderData(5, Qt.Orientation.Horizontal, "Супер-админ")
        model.setHeaderData(6, Qt.Orientation.Horizontal, "ID сотрудника")
        model.select()

        self.polzTable.setModel(model)

        # Скрываем ненужные столбцы
        self.polzTable.setColumnHidden(2, True)  # Скрываем столбец с паролем
        self.polzTable.setColumnHidden(6, True)  # Скрываем столбец с ID сотрудника

        self.polzTable.resizeColumnsToContents()
        self.polzTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def userSelected(self, index):  # Загружает данные о выбранном пользователе в форму.
        user_id = self.selectPolz.currentData()

        if user_id is None:
            self.upFrameEnabled(False)
            return

        # Активируем форму
        self.upFrameEnabled(True)

        # Загружаем данные о пользователе
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

        # Получаем данные из формы
        fam = self.fEdit.text()
        name = self.iEdit.text()
        otch = self.oEdit.text()
        dolj = self.doljEdit.text()
        is_admin = self.adminCheck.isChecked()
        is_supervisor = self.supervisorCheck.isChecked()

        if not fam or not name or not otch or not dolj:
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены.")
            return

        # Вызываем хранимую процедуру UpdateSotrInfo
        query = QSqlQuery()
        query.prepare(
            "EXEC [DBO].[UpdateSotrInfo] @id_sotr = :user_id, @F_sotr = :fam, @I_sotr = :name, @O_sotr = :otch, "
            "@nazvanie_dolj = :dolj, @user_login = :login, @user_password = :password, "
            "@administrator = :is_admin, @supervisor = :is_supervisor, @superadmin = :is_superadmin")
        query.bindValue(":user_id", user_id)
        query.bindValue(":fam", fam)
        query.bindValue(":name", name)
        query.bindValue(":otch", otch)
        query.bindValue(":dolj", dolj)
        query.bindValue(":login", "")  # Логин не изменяем, передаем пустую строку
        query.bindValue(":password", "")  # Пароль не изменяем, передаем пустую строку
        query.bindValue(":is_admin", is_admin)
        query.bindValue(":is_supervisor", is_supervisor)
        query.bindValue(":is_superadmin", False)  # Если супер-админ не используется, передаем False

        if query.exec():
            QMessageBox.information(self, "Успех", "Данные пользователя обновлены.")
            self.polzTableShowData()  # Обновляем таблицу
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
        # Хэшируем пароль с использованием SHA-256
        return hashlib.sha256(password.encode()).hexdigest()

    def updatePassword(self, user_id, new_password, confirm_password, dialog):
        if new_password != confirm_password:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают.")
            return

        # Хешируем пароль
        hashed_password = self.hash_password(new_password)

        query = QSqlQuery()
        query.prepare("""
            UPDATE dbo.accounts
            SET user_password = :password
            WHERE id_accounts = :user_id
        """)
        query.bindValue(":password", hashed_password)  # Используем хешированный пароль
        query.bindValue(":user_id", user_id)

        if query.exec():
            QMessageBox.information(self, "Успех", "Пароль успешно изменен.")
            self.polzTableShowData()
            dialog.close()
        else:
            QMessageBox.warning(self, "Ошибка", f"Не удалось изменить пароль: {query.lastError().text()}")

    def clearData(self):  # Сбрасывает форму к исходному состоянию.
        self.selectPolz.setCurrentIndex(0)  # Сбрасываем выбор пользователя
        self.upFrameEnabled(False)
        self.fEdit.clear()
        self.iEdit.clear()
        self.oEdit.clear()
        self.doljEdit.clear()
        self.adminCheck.setChecked(False)
        self.supervisorCheck.setChecked(False)

    def addUserForm(self):  # Открывает диалоговое окно для добавления нового сотрудника.
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
        # Проверка на пустые поля
        if not fam or not name or not otch or not login or not password or not dolj:
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены.")
            return

        # Хешируем пароль
        hashed_password = self.hash_password(password)

        # Вызываем хранимую процедуру AddSotrInfo
        query = QSqlQuery()
        query.prepare("EXEC [DBO].[AddSotrInfo] @F_sotr = :fam, @I_sotr = :name, @O_sotr = :otch, "
                      "@nazvanie_dolj = :dolj, @user_login = :login, @user_password = :password, "
                      "@administrator = :is_admin, @supervisor = :is_supervisor, @superadmin = :is_superadmin")
        query.bindValue(":fam", fam)
        query.bindValue(":name", name)
        query.bindValue(":otch", otch)
        query.bindValue(":dolj", dolj)
        query.bindValue(":login", login)
        query.bindValue(":password", hashed_password)  # Используем хешированный пароль
        query.bindValue(":is_admin", is_admin)
        query.bindValue(":is_supervisor", is_supervisor)
        query.bindValue(":is_superadmin", False)  # Если супер-админ не используется, передаем False

        if query.exec():
            QMessageBox.information(self, "Успех", "Новый сотрудник успешно добавлен.")
            self.polzTableShowData()  # Обновляем таблицу
            self.usersList()  # Обновляем ComboBox
            dialog.close()
        else:
            QMessageBox.warning(self, "Ошибка", f"Ошибка добавления сотрудника: {query.lastError().text()}")