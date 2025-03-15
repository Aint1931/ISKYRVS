USE mdu;
GO

INSERT INTO dbo.dolj (dolj)
VALUES 
('������� �������������'),
('�������������'),
('������������'),
('���������');
GO

INSERT INTO dbo.sotr (F_sotr, I_sotr, O_sotr, dolj_id)
VALUES 
('��������', '������', '��������', (SELECT id_dolj FROM dbo.dolj WHERE dolj = '������� �������������')),
('������', '����', '���������', (SELECT id_dolj FROM dbo.dolj WHERE dolj = '�������������')),
('������', '������', '����������', (SELECT id_dolj FROM dbo.dolj WHERE dolj = '�������������')),
('�������', '����', '������������', (SELECT id_dolj FROM dbo.dolj WHERE dolj = '������������')),
('������', '���������', '����������', (SELECT id_dolj FROM dbo.dolj WHERE dolj = '���������'));
GO

INSERT INTO dbo.accounts (user_login, user_password, administrator, supervisor, superadmin, sotr_id)
VALUES 
('rgoloukhov1931@gmail.com', 'e7k5eadsr', 1, 1, 1, (SELECT id_sotr FROM dbo.sotr WHERE F_sotr = '��������' AND I_sotr = '������' AND O_sotr = '��������')),
('ivanovos@gmail.com', 'e7k5eadsr', 1, 1, 0, (SELECT id_sotr FROM dbo.sotr WHERE F_sotr = '������' AND I_sotr = '����' AND O_sotr = '���������')),
('petrovme@gmail.com', 'e7k5eadsr', 0, 1, 0, (SELECT id_sotr FROM dbo.sotr WHERE F_sotr = '������' AND I_sotr = '������' AND O_sotr = '����������')),
('sidorovov@gmail.com', 'e7k5eadsr', 1, 0, 0, (SELECT id_sotr FROM dbo.sotr WHERE F_sotr = '�������' AND I_sotr = '����' AND O_sotr = '������������')),
('egorovaa@gmail.com', 'e7k5eadsr', 0, 0, 0, (SELECT id_sotr FROM dbo.sotr WHERE F_sotr = '������' AND I_sotr = '���������' AND O_sotr = '����������'));
GO