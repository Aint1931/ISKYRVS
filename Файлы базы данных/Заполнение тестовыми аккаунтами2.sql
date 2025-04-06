USE mdu;
GO

INSERT INTO dbo.dolj (dolj)
VALUES 
('Главный администратор'),
('Администратор'),
('Руководитель'),
('Сотрудник');
GO

INSERT INTO dbo.sotr (F_sotr, I_sotr, O_sotr, dolj_id)
VALUES 
('Голоухов', 'Руслан', 'Игоревич', (SELECT id_dolj FROM dbo.dolj WHERE dolj = 'Главный администратор')),
('Иванов', 'Олег', 'Сергеевич', (SELECT id_dolj FROM dbo.dolj WHERE dolj = 'Администратор')),
('Петров', 'Максим', 'Евгеньевич', (SELECT id_dolj FROM dbo.dolj WHERE dolj = 'Администратор')),
('Сидоров', 'Олег', 'Владимирович', (SELECT id_dolj FROM dbo.dolj WHERE dolj = 'Руководитель')),
('Егоров', 'Александр', 'Алексеевич', (SELECT id_dolj FROM dbo.dolj WHERE dolj = 'Сотрудник')),
('Егоров', 'Генадий', 'Алексеевич', (SELECT id_dolj FROM dbo.dolj WHERE dolj = 'Сотрудник')),
('Синицин', 'Иван', 'Игоревич', (SELECT id_dolj FROM dbo.dolj WHERE dolj = 'Сотрудник'));
GO

INSERT INTO dbo.accounts (user_login, user_password, administrator, supervisor, superadmin, sotr_id)
VALUES 
('rgoloukhov1931@gmail.com', 'c775e7b757ede630cd0aa1113bd102661ab38829ca52a6422ab782862f268646', 1, 1, 1, (SELECT id_sotr FROM dbo.sotr WHERE F_sotr = 'Голоухов' AND I_sotr = 'Руслан' AND O_sotr = 'Игоревич')),
('ivanovos@gmail.com', 'c775e7b757ede630cd0aa1113bd102661ab38829ca52a6422ab782862f268646', 1, 1, 0, (SELECT id_sotr FROM dbo.sotr WHERE F_sotr = 'Иванов' AND I_sotr = 'Олег' AND O_sotr = 'Сергеевич')),
('petrovme@gmail.com', 'c775e7b757ede630cd0aa1113bd102661ab38829ca52a6422ab782862f268646', 0, 1, 0, (SELECT id_sotr FROM dbo.sotr WHERE F_sotr = 'Петров' AND I_sotr = 'Максим' AND O_sotr = 'Евгеньевич')),
('sidorovov@gmail.com', 'c775e7b757ede630cd0aa1113bd102661ab38829ca52a6422ab782862f268646', 1, 0, 0, (SELECT id_sotr FROM dbo.sotr WHERE F_sotr = 'Сидоров' AND I_sotr = 'Олег' AND O_sotr = 'Владимирович')),
('egorovaa@gmail.com', 'c775e7b757ede630cd0aa1113bd102661ab38829ca52a6422ab782862f268646', 0, 0, 0, (SELECT id_sotr FROM dbo.sotr WHERE F_sotr = 'Егоров' AND I_sotr = 'Александр' AND O_sotr = 'Алексеевич')),
('egorovga@gmail.com', 'c775e7b757ede630cd0aa1113bd102661ab38829ca52a6422ab782862f268646', 0, 0, 0, (SELECT id_sotr FROM dbo.sotr WHERE F_sotr = 'Егоров' AND I_sotr = 'Генадий' AND O_sotr = 'Алексеевич')),
('sinicinii@gmail.com', 'c775e7b757ede630cd0aa1113bd102661ab38829ca52a6422ab782862f268646', 0, 0, 0, (SELECT id_sotr FROM dbo.sotr WHERE F_sotr = 'Синицин' AND I_sotr = 'Иван' AND O_sotr = 'Игоревич'));
GO