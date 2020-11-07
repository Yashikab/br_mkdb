CREATE TABLE chokuzen_cond_tb(
    race_id BIGINT PRIMARY KEY,
    datejyo_id INT,
    temp FLOAT,
    weather VARCHAR(10),
    wind_v INT,
    w_temp FLOAT,
    wave INT,
    wind_dr INT,
    FOREIGN KEY (race_id)
    REFERENCES raceinfo_tb (race_id)
)
CHARACTER SET utf8;
