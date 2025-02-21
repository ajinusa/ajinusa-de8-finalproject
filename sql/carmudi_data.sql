-- Active: 1739429599282@@127.0.0.1@5433@de8_final_project
create schema if not exists de8_final_project;

CREATE TABLE IF NOT EXISTS carmudi_data (
    id SERIAL PRIMARY KEY,  -- Menggunakan SERIAL untuk auto-increment di PostgreSQL
    judul VARCHAR(200),
    harga DECIMAL(15,2),  -- DECIMAL untuk tipe data angka dengan presisi
    tahun INT,
    merek VARCHAR(100),
    nama_mobil VARCHAR(100),
    kilometer VARCHAR(50),  -- Kolom untuk menyimpan informasi kilometer
    transmisi VARCHAR(50),  -- Kolom untuk menyimpan informasi transmisi
    lokasi VARCHAR(100),  -- Kolom untuk menyimpan lokasi
    dealer VARCHAR(100),  -- Kolom untuk menyimpan informasi dealer
    phone_number VARCHAR(25),
    link TEXT,
    snapshot_dt VARCHAR(100)  -- Kolom untuk menyimpan tanggal snapshot
);



select * from de8_final_project.carmudi_data
