CREATE TABLE holdjyo_tb
(
    datejyo_id INT PRIMARY KEY,
    holddate DATE,
    jyo_cd INT,
    jyo_name VARCHAR(30),
    shinko VARCHAR(100),
    ed_race_no INT,
    FOREIGN KEY (jyo_cd)
    REFERENCES jyo_master (jyo_code)
)
