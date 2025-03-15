from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QLineEdit
from PyQt6.QtSql import QSqlDatabase, QSqlQuery
from auth import Ui_Authorization
from user_form import UchetForm
from otcheti import OtchetForm
import sys
import hashlib


class AuthApp(QMainWindow, Ui_Authorization):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.is_admin = False
        self.is_supervisor = False
        self.is_superadmin = False
        self.user_id = None
        self.user_dolj = None

        # Подключение к базе данных
        self.db = QSqlDatabase.addDatabase("QODBC")
        self.db.setDatabaseName("DRIVER={SQL Server};SERVER=.\\SQLEXPRESS;DATABASE=mdu;")
        if not self.db.open():
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к базе данных")
            sys.exit(1)

        self.logBtn.clicked.connect(self.on_login)
        self.exitBtn.clicked.connect(self.close)
        self.showPassword.stateChanged.connect(self.toggle_password_visibility)

    def toggle_password_visibility(self, state):
        if state == 2:
            self.pasEdit.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.pasEdit.setEchoMode(QLineEdit.EchoMode.Password)

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def on_login(self):
        login = self.logEdit.text()
        password = self.pasEdit.text()
        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Логин и пароль не могут быть пустыми!")
            return

        hashed_password = self.hash_password(password)

        query = QSqlQuery()
        query.prepare("EXEC dbo.CheckLogPass @user_login = :user_login, @user_password = :user_password")
        query.bindValue(":user_login", login)
        query.bindValue(":user_password", hashed_password)

        if query.exec() and query.next():
            self.is_admin = query.value("administrator")
            self.is_supervisor = query.value("supervisor")
            self.is_superadmin = query.value("superadmin")
            self.user_id = query.value("id_accounts")
            self.user_dolj = query.value("dolj")

            QMessageBox.information(self, "Успех", f"Авторизация прошла успешно!")
            self.hide()

            if not self.is_admin and not self.is_supervisor:
                self.open_uchet_form()
            else:
                self.open_otchet_form()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")

    def open_uchet_form(self):
        self.uchet_form = UchetForm(self.user_id)
        self.uchet_form.show()

    def open_otchet_form(self):
        self.otchet_form = OtchetForm(self.user_id, self.is_admin, self.is_superadmin)
        self.otchet_form.show()

    def closeEvent(self, event):
        self.db.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AuthApp()
    window.show()
    sys.exit(app.exec())
