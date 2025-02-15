-- Active: 1739433054694@@localhost@3306@de8_final_project
-- Cek apakah schema (database) 'de8_final_project' ada, jika tidak maka buat
CREATE DATABASE IF NOT EXISTS de8_final_project;

-- Pilih database yang akan digunakan
USE de8_final_project;

-- Membuat tabel jika belum ada
CREATE TABLE IF NOT EXISTS carmudi_data (
    id INT AUTO_INCREMENT PRIMARY KEY,  -- Auto-increment ID di MySQL
    judul VARCHAR(200),
    harga DECIMAL(15,2),  -- Gunakan DECIMAL untuk tipe data angka dengan presisi
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
