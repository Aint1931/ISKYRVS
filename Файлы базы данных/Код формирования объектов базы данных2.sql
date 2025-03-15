USE [mdu]
GO

-- Создаем таблицы
CREATE TABLE [DBO].[dolj]
(
    [id_dolj] INT NOT NULL IDENTITY(1,1),
    [dolj] VARCHAR(MAX) NOT NULL,
    CONSTRAINT [PK_dolj] PRIMARY KEY CLUSTERED ([id_dolj] ASC) ON [PRIMARY]
);
GO

CREATE TABLE [DBO].[sotr]
(
    [id_sotr] INT NOT NULL IDENTITY(1,1),
    [F_sotr] VARCHAR(MAX) NOT NULL,
    [I_sotr] VARCHAR(MAX) NOT NULL,
    [O_sotr] VARCHAR(MAX) NOT NULL,
    [dolj_id] INT NOT NULL,
    CONSTRAINT [PK_sotr] PRIMARY KEY CLUSTERED ([id_sotr] ASC) ON [PRIMARY],
    FOREIGN KEY ([dolj_id]) REFERENCES [DBO].[dolj]([id_dolj])
);
GO

CREATE TABLE [DBO].[accounts]
(
    [id_accounts] INT NOT NULL IDENTITY(1,1),
    [user_login] VARCHAR(MAX) NOT NULL,
    [user_password] VARCHAR(MAX) NOT NULL,
    [administrator] BIT NOT NULL,
    [supervisor] BIT NOT NULL,
    [superadmin] BIT NOT NULL,
    [sotr_id] INT NOT NULL,
    CONSTRAINT [PK_accounts] PRIMARY KEY CLUSTERED ([id_accounts] ASC) ON [PRIMARY],
    FOREIGN KEY ([sotr_id]) REFERENCES [DBO].[sotr]([id_sotr])
);
GO

CREATE TABLE [DBO].[PO]
(
    [id_po] INT NOT NULL IDENTITY(1,1),
    [nazv_po] VARCHAR(MAX) NOT NULL,
    [data_ychet_po] VARCHAR(MAX) NOT NULL,
    [accounts1_id] INT NOT NULL,
    CONSTRAINT [PK_po] PRIMARY KEY CLUSTERED ([id_po] ASC) ON [PRIMARY],
    FOREIGN KEY ([accounts1_id]) REFERENCES [DBO].[accounts]([id_accounts])
);
GO

CREATE TABLE [DBO].[TYRV]
(
    [id_TYRV] INT NOT NULL IDENTITY(1,1),
    [nachal_rab_den] VARCHAR(MAX) NOT NULL,
    [okonch_rab_den] VARCHAR(MAX) NOT NULL,
    [dlit] VARCHAR(MAX) NOT NULL,
    [data] VARCHAR(MAX) NOT NULL,
    [accounts2_id] INT NOT NULL,
    CONSTRAINT [PK_TYRV] PRIMARY KEY CLUSTERED ([id_TYRV] ASC) ON [PRIMARY],
    FOREIGN KEY ([accounts2_id]) REFERENCES [DBO].[accounts]([id_accounts])
);
GO

CREATE TABLE [DBO].[web]
(
    [id_web] INT NOT NULL IDENTITY(1,1),
    [url_web] VARCHAR(MAX) NOT NULL,
    [data_ychet_web] VARCHAR(MAX) NOT NULL,
    [accounts3_id] INT NOT NULL,
    CONSTRAINT [PK_web] PRIMARY KEY CLUSTERED ([id_web] ASC) ON [PRIMARY],
    FOREIGN KEY ([accounts3_id]) REFERENCES [DBO].[accounts]([id_accounts])
);
GO

-- Создаем процедуры
CREATE PROCEDURE [DBO].[AddSotrInfo]
    @F_sotr VARCHAR(MAX),
    @I_sotr VARCHAR(MAX),
    @O_sotr VARCHAR(MAX),
    @nazvanie_dolj VARCHAR(MAX),
    @user_login VARCHAR(MAX),
    @user_password VARCHAR(MAX),
    @administrator BIT,
    @supervisor BIT,
    @superadmin BIT
AS
BEGIN
    DECLARE @dolj_id INT;
    DECLARE @sotr_id INT;

    -- Проверяем, существует ли должность
    SELECT @dolj_id = id_dolj
    FROM [DBO].[dolj]
    WHERE dolj = @nazvanie_dolj;

    -- Если должность не существует, добавляем её
    IF @dolj_id IS NULL
    BEGIN
        INSERT INTO [DBO].[dolj] (dolj)
        VALUES (@nazvanie_dolj);
        SET @dolj_id = SCOPE_IDENTITY();
    END;

    -- Добавляем сотрудника
    INSERT INTO [DBO].[sotr] (F_sotr, I_sotr, O_sotr, dolj_id)
    VALUES (@F_sotr, @I_sotr, @O_sotr, @dolj_id);

    -- Получаем ID добавленного сотрудника
    SET @sotr_id = SCOPE_IDENTITY();

    -- Добавляем учетную запись
    INSERT INTO [DBO].[accounts] (user_login, user_password, administrator, supervisor, superadmin, sotr_id)
    VALUES (@user_login, @user_password, @administrator, @supervisor, @superadmin, @sotr_id);
END;
GO

CREATE PROCEDURE [DBO].[UpdateSotrInfo]
    @id_sotr INT,
    @F_sotr VARCHAR(MAX),
    @I_sotr VARCHAR(MAX),
    @O_sotr VARCHAR(MAX),
    @nazvanie_dolj VARCHAR(MAX),
    @user_login VARCHAR(MAX),
    @user_password VARCHAR(MAX),
    @administrator BIT,
    @supervisor BIT,
    @superadmin BIT
AS
BEGIN
    DECLARE @dolj_id INT;

    -- Проверяем, существует ли должность
    SELECT @dolj_id = id_dolj
    FROM [DBO].[dolj]
    WHERE dolj = @nazvanie_dolj;

    -- Если должность не существует, добавляем её
    IF @dolj_id IS NULL
    BEGIN
        INSERT INTO [DBO].[dolj] (dolj)
        VALUES (@nazvanie_dolj);
        SET @dolj_id = SCOPE_IDENTITY();
    END;

    -- Обновляем данные сотрудника
    UPDATE [DBO].[sotr]
    SET F_sotr = @F_sotr,
        I_sotr = @I_sotr,
        O_sotr = @O_sotr,
        dolj_id = @dolj_id
    WHERE id_sotr = @id_sotr;

    -- Обновляем учетную запись
    UPDATE [DBO].[accounts]
    SET user_login = @user_login,
        user_password = @user_password,
        administrator = @administrator,
        supervisor = @supervisor,
        superadmin = @superadmin
    WHERE sotr_id = @id_sotr;
END;
GO

CREATE PROCEDURE [DBO].[update_role]
(
    @id_accounts INT,
    @administrator BIT,
    @supervisor BIT,
    @superadmin BIT
)
AS
BEGIN
    UPDATE [dbo].accounts
    SET administrator = @administrator,
        supervisor = @supervisor,
        superadmin = @superadmin
    WHERE id_accounts = @id_accounts;
END;
GO

CREATE PROCEDURE [dbo].[add_TYRV]
(
    @nachal_rab_den VARCHAR(MAX),
    @okonch_rab_den VARCHAR(MAX),
    @dlit VARCHAR(MAX),
    @data VARCHAR(MAX),
    @accounts2_id INT
)
AS
BEGIN
    INSERT INTO [dbo].[TYRV] ([nachal_rab_den], [okonch_rab_den], [dlit], [data], [accounts2_id])
    VALUES (@nachal_rab_den, @okonch_rab_den, @dlit, @data, @accounts2_id);
END;
GO

CREATE PROCEDURE [DBO].[update_PO]
(
    @id_po INT,
    @nazv_po VARCHAR(MAX),
    @data_ychet_po VARCHAR(MAX),
    @accounts1_id INT
)
AS
BEGIN
    UPDATE [dbo].PO
    SET nazv_po = @nazv_po,
        data_ychet_po = @data_ychet_po,
        accounts1_id = @accounts1_id
    WHERE id_po = @id_po;
END;
GO

CREATE PROCEDURE [DBO].[add_PO]
(
    @nazv_po VARCHAR(MAX),
    @data_ychet_po VARCHAR(MAX),
    @accounts1_id INT
)
AS
BEGIN
    INSERT INTO [dbo].[PO] ([nazv_po], [data_ychet_po], [accounts1_id])
    VALUES (@nazv_po, @data_ychet_po, @accounts1_id);
END;
GO

CREATE PROCEDURE [DBO].[add_web]
(
    @url_web VARCHAR(MAX),
    @data_ychet_web VARCHAR(MAX),
    @accounts3_id INT
)
AS
BEGIN
    INSERT INTO [dbo].[web] ([url_web], [data_ychet_web], [accounts3_id])
    VALUES (@url_web, @data_ychet_web, @accounts3_id);
END;
GO

CREATE PROCEDURE [DBO].[CheckLogPass]
    @user_login VARCHAR(MAX),
    @user_password VARCHAR(MAX)
AS
BEGIN
    SELECT 
        a.id_accounts, 
        a.administrator, 
        a.supervisor, 
        a.superadmin, 
        d.dolj AS dolj
    FROM dbo.accounts a
    JOIN dbo.sotr s ON a.sotr_id = s.id_sotr
    JOIN dbo.dolj d ON s.dolj_id = d.id_dolj
    WHERE a.user_login = @user_login AND a.user_password = @user_password;
END;
GO