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
        query.exec("SELECT id_accounts, F_sotr, I_sotr, O_sotr FROM dbo.accounts")
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
        model.setHeaderData(6, Qt.Orientation.Horizontal, "Фамилия")
        model.setHeaderData(7, Qt.Orientation.Horizontal, "Имя")
        model.setHeaderData(8, Qt.Orientation.Horizontal, "Отчество")
        model.setHeaderData(9, Qt.Orientation.Horizontal, "Должность")

        model.select()

        self.polzTable.setModel(model)

        self.polzTable.setColumnHidden(3, True)  # Скрыть столбец "Администратор"
        self.polzTable.setColumnHidden(4, True)  # Скрыть столбец "Руководитель"
        self.polzTable.setColumnHidden(2, True)  # Скрываем столбец с паролем
        self.polzTable.setColumnHidden(5, True)  # Скрыть столбец "Руководитель"

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
            SELECT user_login, F_sotr, I_sotr, O_sotr, dolj, administrator, supervisor
            FROM dbo.accounts
            WHERE id_accounts = :user_id
        """)
        query.bindValue(":user_id", user_id)

        if query.exec() and query.next():
            self.fEdit.setText(query.value("F_sotr"))
            self.iEdit.setText(query.value("I_sotr"))
            self.oEdit.setText(query.value("O_sotr"))
            self.doljEdit.setText(query.value("dolj"))
            self.adminCheck.setChecked(query.value("administrator"))
            self.supervisorCheck.setChecked(query.value("supervisor"))

    def userDataUpdate(self):  # Обновляет данные пользователя в базе данных.
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

        # Обновляем данные в базе
        query = QSqlQuery()
        query.prepare("""
            UPDATE dbo.accounts
            SET F_sotr = :fam, I_sotr = :name, O_sotr = :otch, dolj = :dolj,
                administrator = :is_admin, supervisor = :is_supervisor
            WHERE id_accounts = :user_id
        """)
        query.bindValue(":fam", fam)
        query.bindValue(":name", name)
        query.bindValue(":otch", otch)
        query.bindValue(":dolj", dolj)
        query.bindValue(":is_admin", is_admin)
        query.bindValue(":is_supervisor", is_supervisor)
        query.bindValue(":user_id", user_id)

        if query.exec():
            QMessageBox.information(self, "Успех", "Данные пользователя обновлены.")
            self.polzTableShowData()  # Обновляем таблицу
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось обновить данные пользователя.")

    def changePasswordFormShow(self):
        """Открывает диалоговое окно для изменения пароля."""
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
        newPasswordEdit.setFont(font)  # Устанавливаем шрифт
        layout.addWidget(newPasswordEdit)

        confirmPasswordEdit = QLineEdit(dialog)
        confirmPasswordEdit.setPlaceholderText("Повторите пароль")
        confirmPasswordEdit.setEchoMode(QLineEdit.EchoMode.Password)
        confirmPasswordEdit.setFont(font)  # Устанавливаем шрифт
        layout.addWidget(confirmPasswordEdit)

        save_btn = QPushButton("Сохранить", dialog)
        save_btn.setFont(font)  # Устанавливаем шрифт
        cancel_btn = QPushButton("Отмена", dialog)
        cancel_btn.setFont(font)  # Устанавливаем шрифт

        layout.addWidget(save_btn)
        layout.addWidget(cancel_btn)

        save_btn.clicked.connect(
            lambda: self.updatePassword(user_id, newPasswordEdit.text(), confirmPasswordEdit.text(), dialog))
        cancel_btn.clicked.connect(dialog.close)

        dialog.setLayout(layout)
        dialog.exec()

    def updatePassword(self, user_id, new_password, confirm_password, dialog):  # Изменяет пароль пользователя.
        if new_password != confirm_password:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают.")
            return

        query = QSqlQuery()
        query.prepare("""
            UPDATE dbo.accounts
            SET user_password = :password
            WHERE id_accounts = :user_id
        """)
        query.bindValue(":password", new_password)
        query.bindValue(":user_id", user_id)

        if query.exec():
            QMessageBox.information(self, "Успех", "Пароль успешно изменен.")
            self.polzTableShowData()
            dialog.close()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось изменить пароль.")

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
            self.adminCheck.setEnabled(False)

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

    def saveNewUser(self, fam, name, otch, login, password, dolj, is_admin, is_supervisor, dialog): # Сохраняет нового сотрудника в базу данных.
        # Проверка на пустые поля
        if not fam or not name or not otch or not login or not password or not dolj:
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены.")
            return

        # Добавляем данные в базу
        query = QSqlQuery()
        query.prepare("""
            INSERT INTO dbo.accounts (
            user_login, 
            user_password, 
            F_sotr, 
            I_sotr, 
            O_sotr, 
            dolj, 
            administrator, 
            supervisor, 
            superadmin
            )
            VALUES (:login, :password, :fam, :name, :otch, :dolj, :is_admin, :is_supervisor, :is_superadmin)
        """)
        query.bindValue(":login", login)
        query.bindValue(":password", password)
        query.bindValue(":fam", fam)
        query.bindValue(":name", name)
        query.bindValue(":otch", otch)
        query.bindValue(":dolj", dolj)
        query.bindValue(":is_admin", is_admin)
        query.bindValue(":is_supervisor", is_supervisor)
        query.bindValue(":is_superadmin", False)

        if query.exec():
            QMessageBox.information(self, "Успех", "Новый сотрудник успешно добавлен.")
            self.polzTableShowData()  # Обновляем таблицу
            self.usersList()  # Обновляем ComboBox
            dialog.close()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось добавить сотрудника.")
