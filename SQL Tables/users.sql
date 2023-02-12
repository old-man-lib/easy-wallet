/*Sqlite Table*/
CREATE TABLE users (
    id integer PRIMARY KEY AUTOINCREMENT,
    tg_id int(11) DEFAULT NULL,
    tg_username text DEFAULT NULL,
    wallet_mnemonic text DEFAULT NULL,
    milling integer DEFAULT 1,
    language text DEFAULT NULL,
    reg_datetime datetime DEFAULT NULL,
    last_use datetime DEFAULT NULL,
    status_mes text DEFAULT NULL
)

/*MySql Table*/
CREATE TABLE users (
    id int NOT NULL AUTO_INCREMENT,
    tg_id int(11) DEFAULT NULL,
    tg_username text DEFAULT NULL,
    wallet_mnemonic text DEFAULT NULL,
    milling integer DEFAULT 1,
    language text DEFAULT NULL,
    reg_datetime datetime DEFAULT NULL,
    last_use datetime DEFAULT NULL,
    status_mes text DEFAULT NULL,
    PRIMARY KEY (id)
)