import requests, pytz
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os, re
from airflow.models.param import Param
from airflow.decorators import dag, task
from airflow.operators.empty import EmptyOperator
import sqlalchemy as sa
# from sqlalchemy import create_engine
from airflow.providers.postgres.hooks.postgres import PostgresHook
import csv


@dag(
    params = {
        "url": Param("https://www.carmudi.co.id/mobil-dijual/indonesia?type=used&page_number=", description="masukkan url"), # definisikan parameternya
        # "last_page":Param(1, type="integer", description="Mau scraping sampai halaman berapa?"),
        "filename": Param("carmudi_data", description="masukkan nama file")
    }
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
    def extract_web(param1, param2, param3):
                
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
    def extract_from_csv(param1):
        filename = '/opt/airflow/data/'+param1+'.csv'
        # Membaca data CSV
        with open(filename, "r") as f:
            reader = csv.DictReader(f)
            data   = pd.DataFrame([row for row in reader])
        return data
    

    @task
    def load_database(df, table_name):
        
        # ======== mysql =======
        # DATABASE_URL = "mysql://root:ajinusa@ajinusa-mysql-container:3306/de8_final_project"
        # engine = sa.create_engine(DATABASE_URL)
        engine = PostgresHook("ajinusa-mysql").get_sqlalchemy_engine()
        # Cek koneksi
        try:
            with engine.connect() as connection:
                print("Koneksi ke MySQL berhasil!")
        
            print(df)
            df.to_sql(table_name, con=engine, if_exists='replace', index=False)
            
        except Exception as e:
            print("Error koneksi:", e)

    
    def get_last_page(**context):
        last_page = int(context["params"]["last_page"])  
        return last_page

    
    @task
    def read_mysql(table_name):
        DATABASE_URL = "mysql+pymysql://root:ajinusa@ajinusa-mysql-container:3306/de8_final_project"

        # Membuat engine untuk koneksi
        # engine = create_engine(DATABASE_URL)
        engine = PostgresHook("ajinusa-mysql").get_sqlalchemy_engine()
        # Menjalankan query untuk mengambil data dari tabel
        try:
            # Koneksi dan query
            with engine.connect() as connection:
                print("Koneksi ke MySQL berhasil!")
                
                # Misalnya kita ingin mengambil data dari tabel 'your_table_name'
                query = "SELECT nama_mobil, AVG(CAST(harga AS DECIMAL(10, 2))) AS avg_harga FROM "+table_name+" group by 1 order by 2 desc limit 10"  # Ganti dengan nama tabel kamu
                
                # Menjalankan query dan mengubahnya ke dalam DataFrame
                df_read_mysql = pd.read_sql(query, connection)
                print(df_read_mysql)
                # Tampilkan DataFrame
                # df.head()  # Mengambil beberapa baris pertama dari DataFrame untuk ditampilkan

        except Exception as e:
            print("Error koneksi:", e)


    extract_web = extract_web(param1 = "{{ params['url'] }}", param2 = "{{ params['filename'] }}", param3 = 200)
    load_database = load_database(df = extract_web,table_name = "{{ params['filename'] }}")
    read_mysql = read_mysql(table_name = "{{ params['filename'] }}")
    start_task >> extract_web >> load_database >> read_mysql >> end_task

web_scraping()