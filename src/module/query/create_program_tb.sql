CREATE TABLE program_tb(
    waku_id BIGINT PRIMARY KEY,
    race_id BIGINT,
    p_name VARCHAR(100),
    p_id INT,
    p_level VARCHAR(30),
    p_home VARCHAR(30),
    p_birthplace VARCHAR(30),
    p_age INT,
    p_weight FLOAT,
    p_num_f INT,
    p_num_l INT,
    p_avg_st FLOAT,
    p_all_1rate FLOAT,
    p_all_2rate FLOAT,
    p_all_3rate FLOAT,
    p_local_1rate FLOAT,
    p_local_2rate FLOAT,
    p_local_3rate FLOAT,
    motor_no INT,
    motor_2rate FLOAT,
    motor_3rate FLOAT,
    boat_no INT,
    boat_2rate FLOAT,
    boat_3rate FLOAT,
    FOREIGN KEY (race_id)
    REFERENCES raceinfo_tb (race_id)
)
CHARACTER SET utf8;
