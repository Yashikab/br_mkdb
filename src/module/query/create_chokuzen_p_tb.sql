CREATE TABLE chokuzen_player_tb(
    waku_id BIGINT PRIMARY KEY,
    race_id BIGINT,
    p_name VARCHAR(100),
    p_weight FLOAT,
    p_chosei_weight FLOAT,
    p_tenji_time FLOAT,
    p_tilt FLOAT,
    p_tenji_course INT,
    p_tenji_st FLOAT,
    FOREIGN KEY (waku_id)
    REFERENCES program_tb (waku_id),
    FOREIGN KEY (race_id)
    REFERENCES chokuzen_cond_tb (race_id)
)
CHARACTER SET utf8;
