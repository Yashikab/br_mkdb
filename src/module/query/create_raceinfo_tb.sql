CREATE TABLE raceinfo_tb(
    race_id BIGINT PRIMARY KEY,
    datejyo_id INT,
    taikai_name VARCHAR(400),
    grade VARCHAR(100),
    race_type VARCHAR(100),
    race_kyori INT,
    is_antei BOOLEAN,
    is_shinnyukotei BOOLEAN,
    FOREIGN KEY (datejyo_id)
    REFERENCES holdjyo_tb (datejyo_id)
)
CHARACTER SET utf8;
