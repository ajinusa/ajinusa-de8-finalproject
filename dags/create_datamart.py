import pandas as pd
from airflow.models.param import Param
from airflow.decorators import dag, task
from airflow.operators.empty import EmptyOperator
import sqlalchemy as sa
from airflow.providers.postgres.hooks.postgres import PostgresHook
from pyspark.sql import SparkSession

@dag(
    params = {
        "filename": Param("carmudi_data", description="masukkan nama file")
    },
    # schedule_interval = "0 1 * * *",
    # start_date        = datetime(2025, 1, 1, tzinfo=pytz.timezone("Asia/Jakarta")),
    # catchup           = False,
)


def create_datamart():

     
    start_task   = EmptyOperator(task_id="start_task")
    end_task   = EmptyOperator(task_id="end_task")

    @task
    def read_datalake(table_name):
        # read postgres
        engine = PostgresHook("de8_final_project").get_sqlalchemy_engine()
        try:
            # Koneksi dan query
            with engine.connect() as connection:
                print("Koneksi ke Postgres berhasil!")
                
                query = "SELECT * FROM "+table_name

                # Menjalankan query dan mengubahnya ke dalam DataFrame
                df_read_datalake = pd.read_sql(query, connection)
                return df_read_datalake

        except Exception as e:
            print("Error koneksi:", e)


    @task
    def load_datamart(df_datalake, table_name):
        # print(df_datalake)
        # inisialisasi koneksi mysql airflow
        engine = PostgresHook("ajinusa-mysql").get_sqlalchemy_engine()
        
        # Inisialisasi Spark Session
        spark = SparkSession.builder.appName("FinalProject").getOrCreate()
        df_spark = spark.createDataFrame(df_datalake)
        # Contoh query dengan PySpark
        df_spark.createOrReplaceTempView(table_name) 
        
        
        def dm_transmisi():
            df_result = spark.sql("select transmisi, count(*) total_product from "+table_name+" group by 1 order by 2 desc")  # SQL Query
            df_result.show()
            df_result = df_result.toPandas()

            # insert to mysql datamart
            try:
                with engine.connect() as connection:
                    print("Koneksi ke MySQL berhasil!")
            
                print(df_result)
                df_result.to_sql("dm_carmudi_transmisi", con=engine, if_exists='replace', index=False)
                
            except Exception as e:
                print("Error koneksi:", e) 
        
        def dm_carmudi_mobil_dijual():
            df_result = spark.sql("select nama_mobil, count(*) jumlah from "+table_name+" group by 1 order by 2 desc")  # SQL Query
            df_result.show()
            df_result = df_result.toPandas()

            # insert to mysql datamart
            try:
                with engine.connect() as connection:
                    print("Koneksi ke MySQL berhasil!")
            
                print(df_result)
                df_result.to_sql("dm_carmudi_mobil_dijual", con=engine, if_exists='replace', index=False)
                
            except Exception as e:
                print("Error koneksi:", e) 

        def dm_carmudi_mobil_avg():
            df_result = spark.sql("select concat(nama_mobil,\" (\",tahun,\")\") nama_mobil, avg(harga) avg_harga from "+table_name+" group by 1 order by 2 desc")  # SQL Query
            df_result.show()
            df_result = df_result.toPandas()

            # insert to mysql datamart
            try:
                with engine.connect() as connection:
                    print("Koneksi ke MySQL berhasil!")
            
                print(df_result)
                df_result.to_sql("dm_carmudi_mobil_avg", con=engine, if_exists='replace', index=False)
                
            except Exception as e:
                print("Error koneksi:", e)

        def dm_carmudi_tahun():
            df_result = spark.sql("select tahun, count(*) jumlah from "+table_name+" group by 1 order by 2 desc")  # SQL Query
            df_result.show()
            df_result = df_result.toPandas()

            # insert to mysql datamart
            try:
                with engine.connect() as connection:
                    print("Koneksi ke MySQL berhasil!")
            
                print(df_result)
                df_result.to_sql("dm_carmudi_tahun", con=engine, if_exists='replace', index=False)
                
            except Exception as e:
                print("Error koneksi:", e)

        def dm_carmudi_km():
            df_result = spark.sql("select kilometer, count(*) total from carmudi_data group by 1 order by 2 desc ")  # SQL Query
            df_result.show()
            df_result = df_result.toPandas()

            # insert to mysql datamart
            try:
                with engine.connect() as connection:
                    print("Koneksi ke MySQL berhasil!")
            
                print(df_result)
                df_result.to_sql("dm_carmudi_km", con=engine, if_exists='replace', index=False)
                
            except Exception as e:
                print("Error koneksi:", e)

        def dm_carmudi_seller_type():
            df_result = spark.sql("select dealer, count(*) total_product from carmudi_data group by 1 order by 2 desc")  # SQL Query
            df_result.show()
            df_result = df_result.toPandas()

            # insert to mysql datamart
            try:
                with engine.connect() as connection:
                    print("Koneksi ke MySQL berhasil!")
            
                print(df_result)
                df_result.to_sql("dm_carmudi_seller_type", con=engine, if_exists='replace', index=False)
                
            except Exception as e:
                print("Error koneksi:", e)

        
        def dm_carmudi_location():
            df_result = spark.sql("select lokasi, count(*) total_product from carmudi_data group by 1 order by 2 desc")  # SQL Query
            df_result.show()
            df_result = df_result.toPandas()

            # insert to mysql datamart
            try:
                with engine.connect() as connection:
                    print("Koneksi ke MySQL berhasil!")
            
                print(df_result)
                df_result.to_sql("dm_carmudi_location", con=engine, if_exists='replace', index=False)
                
            except Exception as e:
                print("Error koneksi:", e)
        

        def dm_carmudi_company():
            df_result = spark.sql("select merek, count(*) total_product from carmudi_data group by 1 order by 2 desc")  # SQL Query
            df_result.show()
            df_result = df_result.toPandas()

            # insert to mysql datamart
            try:
                with engine.connect() as connection:
                    print("Koneksi ke MySQL berhasil!")
            
                print(df_result)
                df_result.to_sql("dm_carmudi_company", con=engine, if_exists='replace', index=False)
                
            except Exception as e:
                print("Error koneksi:", e)
                
        def dm_carmudi_seller():
            df_result = spark.sql("select phone_number as seller, count(*) total_product from carmudi_data group by 1 order by 2 desc")  # SQL Query
            df_result.show()
            df_result = df_result.toPandas()

            # insert to mysql datamart
            try:
                with engine.connect() as connection:
                    print("Koneksi ke MySQL berhasil!")
            
                print(df_result)
                df_result.to_sql("dm_carmudi_seller", con=engine, if_exists='replace', index=False)
                
            except Exception as e:
                print("Error koneksi:", e)

        def dm_carmudi_last_update():
            df_result = spark.sql("select max(snapshot_dt) from carmudi_data")  # SQL Query
            df_result.show()
            df_result = df_result.toPandas()

            # insert to mysql datamart
            try:
                with engine.connect() as connection:
                    print("Koneksi ke MySQL berhasil!")
            
                print(df_result)
                df_result.to_sql("dm_carmudi_last_update", con=engine, if_exists='replace', index=False)
                
            except Exception as e:
                print("Error koneksi:", e)



        dm_transmisi()
        dm_carmudi_mobil_dijual()
        dm_carmudi_mobil_avg()
        dm_carmudi_tahun()
        dm_carmudi_km()
        dm_carmudi_seller_type()
        dm_carmudi_location()
        dm_carmudi_company()
        dm_carmudi_seller()
        dm_carmudi_last_update()

    


    read_datalake = read_datalake(table_name = "{{ params['filename'] }}")
    load_datamart = load_datamart(df_datalake = read_datalake, table_name = "{{ params['filename'] }}")
    start_task >> read_datalake >> load_datamart >> end_task

create_datamart()