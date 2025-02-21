import requests, pytz
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os, re
from airflow.models.param import Param
from airflow.decorators import dag, task
from airflow.operators.empty import EmptyOperator
import sqlalchemy as sa
from airflow.providers.postgres.hooks.postgres import PostgresHook
from pathlib import Path


@dag(
    params = {
        "url": Param("https://www.carmudi.co.id/mobil-dijual/indonesia?type=used&page_number=", description="masukkan url"), # definisikan parameternya
        # "last_page":Param(1, type="integer", description="Mau scraping sampai halaman berapa?"),
        "filename": Param("carmudi_data", description="masukkan nama file"),
        
    },
    # schedule_interval = "0 0 * * *",
    # start_date        = datetime(2025, 1, 1, tzinfo=pytz.timezone("Asia/Jakarta")),
    # catchup           = False,
)



def web_scraping():

     
    start_task   = EmptyOperator(task_id="start_task")
    end_task   = EmptyOperator(task_id="end_task")

    # Header agar tidak terdeteksi sebagai bot
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }


    # List untuk menyimpan data
    mobil_list = []

    @task
    def extract_web(param1, param3):
                
        # for url in urls:
        for i in range(1, param3 + 1):
            url = f"{param1}{i}"  
            # print(url)  # Cek apakah URL sudah benar

            # Request ke website
            response = requests.get(url, headers=headers)

            # Parsing HTML dengan BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")

            # Scrape data mobil
            items = soup.find_all("article", class_="listing")  # Sesuaikan dengan class dari Carmudi
            # print(items)
            def convert_to_number(rp_string):
                return int(rp_string.replace("Rp", "").replace(".", "").strip())

            for item in items:
                try:
                    judul = item.find("h2", class_="listing__title").text.strip()
                    tahun = judul.split(" ")[0]
                    merek = judul.split(" ")[1]
                    # merek2 = judul.split(" ")[2]
                    harga = item.find("div", class_="listing__price").text.strip()
                    snapshot_date = datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%Y-%m-%d %H:%M:%S")
                    link = item.find("a")["href"]
                    whatsapp_link = item.find('a', {'data-whatsapp-number': True})
                    # Extract the phone number
                    phone_number = whatsapp_link['data-whatsapp-number'] if whatsapp_link else None
                    km = item.find('div', class_='item push-quarter--ends soft--right push-quarter--right').text.strip()
                    transmission = item.find('div', class_='item push-quarter--ends').text.strip()
                    location = item.find_all('div', class_='item push-quarter--ends')[1].text.strip()
                    dealer = item.find('div', class_='item push-quarter--ends listing__spec--dealer').text.strip()


                    match = re.search(r'^\d+\s+(.+?)\s+\d', judul)

                    if match:
                        brand_model = match.group(1)

                    # Tambahkan ke list
                    mobil_list.append({
                        "judul": judul,
                        "harga": convert_to_number(harga),
                        "tahun": tahun,
                        "merek": merek,
                        "nama_mobil": brand_model,
                        "kilometer": km,
                        "transmisi": transmission,
                        "lokasi": location,
                        "dealer": dealer,
                        "phone_number":phone_number,
                        "link": link,
                        "snapshot_dt": snapshot_date

                    })
                except:
                    continue

        # Simpan ke DataFrame
        df_data = pd.DataFrame(mobil_list)
        # print(df_data)

        return df_data


    @task
    def load_datalake_stg(df, table_name):
        # ========= postgres ==========
    
        # DATABASE_URL = "postgresql://ajinusa:ajinusa@ajinusa-de8-postgres:5432/de8_final_project"

        # Membuat engine untuk koneksi ke PostgreSQL
        # engine = sa.create_engine(DATABASE_URL)
        engine = PostgresHook("de8_final_project").get_sqlalchemy_engine()

        # Menyimpan DataFrame ke PostgreSQL (untuk tarikan pertama kali)
        # df.to_sql("carmudi_data_staging", engine, if_exists='replace', index=False)
        
        # Menyimpan DataFrame ke PostgreSQL (untuk tarikan terupdate halaman 1 dan 2)
        df.to_sql("carmudi_data_staging", engine, if_exists='append', index=False)
        
    
    @task
    def load_datalake(table_name):
        # DATABASE_URL = "mysql+pymysql://root:ajinusa@ajinusa-mysql-container:3306/de8_final_project"
        # Membuat engine untuk koneksi
        # engine = create_engine(DATABASE_URL)

        engine = PostgresHook("de8_final_project").get_sqlalchemy_engine()
      
        # Menjalankan query untuk mengambil data dari tabel
        try:
            # Koneksi dan query
            with engine.connect() as connection:
                print("Koneksi ke Postgres berhasil!")
                
          
                # query = "SELECT count(*) jumlah_data FROM "+table_name
                query = """
                with cte_data as (
                    select distinct judul, harga, tahun, merek, nama_mobil, kilometer, transmisi, lokasi, dealer, phone_number, link
                    from carmudi_data_staging
                )
                
                select * from cte_data a
                """

                
                df_read_datalake = pd.read_sql(query, connection)

                jakarta_tz = pytz.timezone('Asia/Jakarta')
                df_read_datalake['snapshot_dt'] = pd.to_datetime(datetime.now(jakarta_tz))
                df_read_datalake['snapshot_dt'] = df_read_datalake['snapshot_dt'].dt.tz_convert('Asia/Jakarta').astype(str)

                df_read_datalake.to_sql(table_name, engine, if_exists='replace', index=False)
                
                print(df_read_datalake)

        except Exception as e:
            print("Error koneksi:", e)


    extract_web = extract_web(param1 = "{{ params['url'] }}", param3 = 2)
    load_datalake_stg = load_datalake_stg(df = extract_web,table_name = "carmudi_data_staging")
    load_datalake = load_datalake(table_name = "{{ params['filename'] }}")
    start_task >> extract_web >> load_datalake_stg >> load_datalake >> end_task

web_scraping()