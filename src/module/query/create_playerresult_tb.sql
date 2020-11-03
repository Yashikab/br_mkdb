CREATE TABLE p_result_tb(
    waku_id BIGINT PRIMARY KEY,
    race_id BIGINT,
    p_rank INT,
    p_name VARCHAR(100),
    p_id INT,
    p_racetime FLOAT,
    p_course INT,
    p_st_time FLOAT,
    FOREIGN KEY (race_id)
    REFERENCES race_result_tb (race_id),
    FOREIGN KEY (waku_id)
    REFERENCES program_tb (waku_id)
)
CHARACTER SET utf8;
