-- Active: 1739429599282@@127.0.0.1@5433@de8_final_project
create schema if not exists de8_final_project;

CREATE TABLE IF NOT EXISTS de8_final_project.carmudi_data (
    id SERIAL PRIMARY KEY,  -- Auto-increment ID
    judul VARCHAR(200),
    harga NUMERIC(15,2),
    tahun int,
    merek VARCHAR(100),
    nama_mobil VARCHAR(100),
    phone_number VARCHAR(25),
    snapshot_date varchar(100),
    link TEXT
);


select * from de8_final_project.carmudi_data