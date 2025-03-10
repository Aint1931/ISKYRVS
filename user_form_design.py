from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_uchet(object):
    def setupUi(self, uchet):
        uchet.setObjectName("uchet")
        uchet.resize(320, 120)
        self.centralwidget = QtWidgets.QWidget(parent=uchet)
        self.centralwidget.setObjectName("centralwidget")
        self.startBtn = QtWidgets.QPushButton(parent=self.centralwidget)
        self.startBtn.setGeometry(QtCore.QRect(10, 60, 120, 40))
        font = QtGui.QFont()
        font.setFamily("Noto Sans")
        font.setPointSize(16)
        font.setBold(False)
        font.setWeight(50)
        self.startBtn.setFont(font)
        self.startBtn.setObjectName("startBtn")
        self.finishBtn = QtWidgets.QPushButton(parent=self.centralwidget)
        self.finishBtn.setEnabled(False)
        self.finishBtn.setGeometry(QtCore.QRect(150, 60, 140, 40))
        font = QtGui.QFont()
        font.setFamily("Noto Sans")
        font.setPointSize(16)
        font.setBold(False)
        font.setWeight(50)
        self.finishBtn.setFont(font)
        self.finishBtn.setObjectName("finishBtn")
        self.labelTime = QtWidgets.QLabel(parent=self.centralwidget)
        self.labelTime.setGeometry(QtCore.QRect(10, 20, 300, 23))
        font = QtGui.QFont()
        font.setFamily("Noto Sans")
        font.setPointSize(16)
        self.labelTime.setFont(font)
        self.labelTime.setObjectName("labelTime")
        uchet.setCentralWidget(self.centralwidget)

        self.retranslateUi(uchet)
        QtCore.QMetaObject.connectSlotsByName(uchet)

    def retranslateUi(self, uchet):
        _translate = QtCore.QCoreApplication.translate
        uchet.setWindowTitle(_translate("uchet", "MainWindow"))
        self.startBtn.setText(_translate("uchet", "Начать"))
        self.finishBtn.setText(_translate("uchet", "Завершить"))
        self.labelTime.setText(_translate("uchet", "Время активности: 00:00:00"))
