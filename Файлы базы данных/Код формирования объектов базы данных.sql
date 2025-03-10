SET ANSI_PADDING ON
	GO
	SET ANSI_NULLS ON
	GO
	SET QUOTED_IDENTIFIER ON
	GO

	USE [mdu]
	GO

	CREATE TABLE [DBO].[accounts]
	(
		[id_accounts] int not null identity (1,1),
		[user_login] varchar(max) not null,
		[user_password] varchar(max) not null,
		[administrator] bit not null,
		[supervisor] bit not null,
		[superadmin] bit not null,
		[F_sotr] varchar(max) not null,
		[I_sotr] varchar(max) not null,
		[O_sotr] varchar(max) not null,
		[dolj] varchar(max) not null,
		CONSTRAINT [PK_accounts] PRIMARY KEY CLUSTERED
			([id_accounts] ASC) ON [PRIMARY],
		)

	CREATE TABLE [DBO].[PO]
	(
		[id_po] int not null identity (1,1),
		[nazv_po] varchar(max) not null,
		[data_ychet_po] varchar(max) not null,
		[accounts1_id] int not null,
		CONSTRAINT [PK_po] PRIMARY KEY CLUSTERED
			([id_po] ASC) ON [PRIMARY],
		FOREIGN KEY ([accounts1_id])
			REFERENCES [DBO].[accounts]([id_accounts])
	)



	CREATE TABLE [DBO].[TYRV]
	(
		[id_TYRV] int not null identity (1,1),
		[nachal_rab_den] varchar(max) not null,
		[okonch_rab_den] varchar(max) not null,
		[dlit] varchar(max) not null,
		[data] varchar(max) not null,
		[accounts2_id] int not null,
		CONSTRAINT [PK_TYRV] PRIMARY KEY CLUSTERED
			([id_TYRV] ASC) ON [PRIMARY],
		FOREIGN KEY ([accounts2_id])
			REFERENCES [DBO].[accounts]([id_accounts])
	)

	CREATE TABLE [DBO].[web]
		(
		[id_web] int not null identity (1,1),
		[url_web] varchar(max) not null,
		[data_ychet_web] varchar(max) not null,
		[accounts3_id] int not null,
		CONSTRAINT [PK_web] PRIMARY KEY CLUSTERED
			([id_web] ASC) ON [PRIMARY],
		FOREIGN KEY ([accounts3_id])
			REFERENCES [DBO].[accounts]([id_accounts])
		)


use [mdu]
go

CREATE PROCEDURE [DBO].[accounts_delete]
(
	@id_accounts int
)
	AS
		DELETE from [dbo].[accounts]
		where id_accounts=@id_accounts;
	go

CREATE PROCEDURE [DBO].[account_add]
(
@login varchar(max),
@password varchar(max),
@administrator bit,
@supervisor bit,
@superadmin bit,
@f_sotr varchar(max),
@i_sotr varchar(max),
@o_sotr varchar(max),
@dolj varchar(max)
)
AS
	insert into [dbo].[accounts]([user_login],[user_password],[administrator],[supervisor],[superadmin],[F_sotr],[I_sotr],[O_sotr],[dolj]) values ((@login),(@password),(@administrator),(@supervisor),(@superadmin),(@f_sotr),(@i_sotr),(@o_sotr),(@dolj))
go


USE [mdu]
GO

CREATE PROCEDURE [DBO].[account_update]
(
@id_accounts int,
@login varchar(max),
@password varchar(max),
@administrator bit,
@supervisor bit,
@superadmin bit,
@f_sotr varchar(max),
@i_sotr varchar(max),
@o_sotr varchar(max),
@dolj varchar(max)
)
AS
	update [dbo].accounts
	set
	user_login=@login,
	user_password=@password,
	administrator=@administrator,
	supervisor=@supervisor,
	superadmin=@superadmin,
	F_sotr=@f_sotr,
	I_sotr=@i_sotr,
	O_sotr=@o_sotr,
	dolj=@dolj
	where id_accounts=@id_accounts
go





CREATE PROCEDURE [DBO].[update_role]
(
@id_accounts int,
@administrator bit,
@supervisor bit,
@superadmin bit
)
AS
	update [dbo].accounts
	set
	administrator=@administrator,
	supervisor=@supervisor,
	superadmin=@superadmin
	where id_accounts=@id_accounts
go

use [mdu]
go

create procedure [dbo].[add_TYRV]
(
	@nachal_rab_den varchar(max),
	@okonch_rab_den varchar(max),
	@dlit varchar(max),
	@data varchar(max),
	@accounts2_id int
)
as 
insert into [dbo].[TYRV]([nachal_rab_den],[okonch_rab_den],[dlit],[data],[accounts2_id]) values ((@nachal_rab_den),(@okonch_rab_den),(@dlit),(@data),(@accounts2_id))
go

use [mdu]
go

CREATE PROCEDURE [DBO].[update_PO]
(
	@id_po int,
	@nazv_po varchar(max),
	@data_ychet_po varchar(max),
	@accounts1_id int
)
AS
	update [dbo].PO
	set
	nazv_po=@nazv_po,
	data_ychet_po=@data_ychet_po,
	accounts1_id=@accounts1_id
	where id_po=@id_po
go

CREATE PROCEDURE [DBO].[add_PO]
(
	@nazv_po varchar(max),
	@data_ychet_po varchar(max),
	@start_time varchar(max),
	@end_time varchar(max),
	@accounts1_id int
)
AS
	insert into [dbo].[PO]([nazv_po],[data_ychet_po],[accounts1_id]) values ((@nazv_po),(@data_ychet_po),(@accounts1_id))
go


CREATE PROCEDURE [DBO].[add_web]
(
@url_web varchar(max),
@data_ychet_web varchar(max),
@accounts3_id int
)
AS
	insert into [dbo].[web]([url_web],[data_ychet_web],[accounts3_id]) values ((@url_web),(@data_ychet_web),(@accounts3_id))
go

