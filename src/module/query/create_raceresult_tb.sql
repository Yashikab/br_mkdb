CREATE TABLE race_result_tb(
    race_id BIGINT PRIMARY KEY,
    datejyo_id INT,
    temp FLOAT,
    weather VARCHAR(10),
    wind_v INT,
    w_temp FLOAT,
    wave INT,
    wind_dr INT,
    henkantei_list VARCHAR(100),
    is_henkan BOOL,
    kimarite VARCHAR(100),
    biko VARCHAR(500),
    payout_3tan INT,
    popular_3tan INT,
    payout_3fuku INT,
    popular_3fuku INT,
    payout_2tan INT,
    popular_2tan INT,
    payout_2fuku INT,
    popular_2fuku INT,
    payout_1tan INT,
    FOREIGN KEY (race_id)
    REFERENCES raceinfo_tb (race_id)
)
CHARACTER SET utf8;
