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
('������', '���������', '����������', (SELECT id_dolj FROM dbo.dolj WHERE dolj = '���������')),
('������', '�������', '����������', (SELECT id_dolj FROM dbo.dolj WHERE dolj = '���������')),
('�������', '����', '��������', (SELECT id_dolj FROM dbo.dolj WHERE dolj = '���������'));
GO

INSERT INTO dbo.accounts (user_login, user_password, administrator, supervisor, superadmin, sotr_id)
VALUES 
('rgoloukhov1931@gmail.com', 'c775e7b757ede630cd0aa1113bd102661ab38829ca52a6422ab782862f268646', 1, 1, 1, (SELECT id_sotr FROM dbo.sotr WHERE F_sotr = '��������' AND I_sotr = '������' AND O_sotr = '��������')),
('ivanovos@gmail.com', 'c775e7b757ede630cd0aa1113bd102661ab38829ca52a6422ab782862f268646', 1, 1, 0, (SELECT id_sotr FROM dbo.sotr WHERE F_sotr = '������' AND I_sotr = '����' AND O_sotr = '���������')),
('petrovme@gmail.com', 'c775e7b757ede630cd0aa1113bd102661ab38829ca52a6422ab782862f268646', 0, 1, 0, (SELECT id_sotr FROM dbo.sotr WHERE F_sotr = '������' AND I_sotr = '������' AND O_sotr = '����������')),
('sidorovov@gmail.com', 'c775e7b757ede630cd0aa1113bd102661ab38829ca52a6422ab782862f268646', 1, 0, 0, (SELECT id_sotr FROM dbo.sotr WHERE F_sotr = '�������' AND I_sotr = '����' AND O_sotr = '������������')),
('egorovaa@gmail.com', 'c775e7b757ede630cd0aa1113bd102661ab38829ca52a6422ab782862f268646', 0, 0, 0, (SELECT id_sotr FROM dbo.sotr WHERE F_sotr = '������' AND I_sotr = '���������' AND O_sotr = '����������')),
('egorovga@gmail.com', 'c775e7b757ede630cd0aa1113bd102661ab38829ca52a6422ab782862f268646', 0, 0, 0, (SELECT id_sotr FROM dbo.sotr WHERE F_sotr = '������' AND I_sotr = '�������' AND O_sotr = '����������')),
('sinicinii@gmail.com', 'c775e7b757ede630cd0aa1113bd102661ab38829ca52a6422ab782862f268646', 0, 0, 0, (SELECT id_sotr FROM dbo.sotr WHERE F_sotr = '�������' AND I_sotr = '����' AND O_sotr = '��������'));
GO