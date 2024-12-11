import psycopg2
from datetime import date
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Konfigurasi koneksi ke database sumber
source_config = {
    'dbname': os.getenv('SOURCE_DBNAME'),
    'user': os.getenv('SOURCE_USER'),
    'password': os.getenv('SOURCE_PASSWORD'),
    'host': os.getenv('SOURCE_HOST'),
    'port': os.getenv('SOURCE_PORT'),
    'sslmode': 'require',
    'sslrootcert': 'ca.pem'
}

# Konfigurasi koneksi ke database target
target_config = {
    'dbname': os.getenv('TARGET_DBNAME'),
    'user': os.getenv('TARGET_USER'),
    'password': os.getenv('TARGET_PASSWORD'),
    'host': os.getenv('TARGET_HOST'),
    'port': os.getenv('TARGET_PORT'),
    'sslmode': 'require',
    'sslrootcert': 'ca.pem'
}
# Tanggal saat program dijalankan
current_date = date.today()

# Fungsi untuk rekap total siswa per kabupaten/kota
def rekap_total():
    aggregation_query = """
    SELECT 
        kabupaten_kota,
        COUNT(*) AS jumlah_siswa,
        COUNT(*) FILTER (WHERE jenis_kelamin = 'L') AS jumlah_laki_laki,
        COUNT(*) FILTER (WHERE jenis_kelamin = 'P') AS jumlah_perempuan
    FROM siswa
    GROUP BY kabupaten_kota
    ORDER BY jumlah_siswa DESC;
    """
    
    create_table_query = """
    CREATE TABLE IF NOT EXISTS siswa_rekap (
        id SERIAL PRIMARY KEY,
        kabupaten_kota VARCHAR(50) NOT NULL,
        jumlah_siswa INT NOT NULL,
        jumlah_laki_laki INT NOT NULL,
        jumlah_perempuan INT NOT NULL,
        date DATE NOT NULL,
        CONSTRAINT unique_kabupaten_date UNIQUE (kabupaten_kota, date)
    );
    """
    
    insert_query = """
    INSERT INTO siswa_rekap (kabupaten_kota, jumlah_siswa, jumlah_laki_laki, jumlah_perempuan, date)
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (kabupaten_kota, date) 
    DO UPDATE SET 
        jumlah_siswa = EXCLUDED.jumlah_siswa,
        jumlah_laki_laki = EXCLUDED.jumlah_laki_laki,
        jumlah_perempuan = EXCLUDED.jumlah_perempuan;
    """
    
    execute_transfer(aggregation_query, create_table_query, insert_query, "rekap total siswa")

# Fungsi untuk rekap jumlah siswa laki-laki dan perempuan per kabupaten/kota
def rekap_jenis_kelamin():
    aggregation_query = """
    SELECT 
        COUNT(*) FILTER (WHERE jenis_kelamin = 'L') AS jumlah_laki_laki,
        COUNT(*) FILTER (WHERE jenis_kelamin = 'P') AS jumlah_perempuan
    FROM siswa;
    """
    
    create_table_query = """
    CREATE TABLE IF NOT EXISTS siswa_rekap_gender (
        id SERIAL PRIMARY KEY,
        jumlah_laki_laki INT NOT NULL,
        jumlah_perempuan INT NOT NULL,
        date DATE NOT NULL,
        CONSTRAINT unique_date UNIQUE (date)
    );
    """
    
    insert_query = """
    INSERT INTO siswa_rekap_gender (jumlah_laki_laki, jumlah_perempuan, date)
    VALUES (%s, %s, %s)
    ON CONFLICT (date)
    DO UPDATE SET 
        jumlah_laki_laki = EXCLUDED.jumlah_laki_laki,
        jumlah_perempuan = EXCLUDED.jumlah_perempuan;
    """
    
    execute_transfer(aggregation_query, create_table_query, insert_query, "rekap jumlah siswa berdasarkan jenis kelamin")

# Fungsi untuk rekap jumlah siswa per agama
def rekap_per_agama():
    aggregation_query = """
    SELECT 
        agama,
        COUNT(*) AS jumlah_siswa
    FROM siswa
    GROUP BY agama
    ORDER BY jumlah_siswa DESC;
    """
    
    create_table_query = """
    CREATE TABLE IF NOT EXISTS siswa_rekap_agama (
        id SERIAL PRIMARY KEY,
        agama VARCHAR(50) NOT NULL,
        jumlah_siswa INT NOT NULL,
        date DATE NOT NULL,
        CONSTRAINT unique_agama_date UNIQUE (agama, date)
    );
    """
    
    insert_query = """
    INSERT INTO siswa_rekap_agama (agama, jumlah_siswa, date)
    VALUES (%s, %s, %s)
    ON CONFLICT (agama, date)
    DO UPDATE SET 
        jumlah_siswa = EXCLUDED.jumlah_siswa;
    """
    
    execute_transfer(aggregation_query, create_table_query, insert_query, "rekap jumlah siswa berdasarkan agama")

# Fungsi untuk rekap jumlah siswa per kecamatan
def rekap_per_kecamatan():
    aggregation_query = """
    SELECT 
        kecamatan,
        COUNT(*) AS jumlah_siswa
    FROM siswa
    GROUP BY kecamatan
    ORDER BY jumlah_siswa DESC;
    """
    
    create_table_query = """
    CREATE TABLE IF NOT EXISTS siswa_rekap_kecamatan (
        id SERIAL PRIMARY KEY,
        kecamatan VARCHAR(50) NOT NULL,
        jumlah_siswa INT NOT NULL,
        date DATE NOT NULL,
        CONSTRAINT unique_kecamatan_date UNIQUE (kecamatan, date)
    );
    """
    
    insert_query = """
    INSERT INTO siswa_rekap_kecamatan (kecamatan, jumlah_siswa, date)
    VALUES (%s, %s, %s)
    ON CONFLICT (kecamatan, date)
    DO UPDATE SET 
        jumlah_siswa = EXCLUDED.jumlah_siswa;
    """
    
    execute_transfer(aggregation_query, create_table_query, insert_query, "rekap jumlah siswa berdasarkan kecamatan")

# Fungsi untuk rekap jumlah siswa per sekolah
def rekap_per_sekolah():
    aggregation_query = """
    SELECT 
        sekolah,
        COUNT(*) AS jumlah_siswa
    FROM siswa
    GROUP BY sekolah
    ORDER BY jumlah_siswa DESC;
    """
    
    create_table_query = """
    CREATE TABLE IF NOT EXISTS siswa_rekap_sekolah (
        id SERIAL PRIMARY KEY,
        nama_sekolah VARCHAR(100) NOT NULL,
        jumlah_siswa INT NOT NULL,
        date DATE NOT NULL,
        CONSTRAINT unique_sekolah_date UNIQUE (nama_sekolah, date)
    );
    """
    
    insert_query = """
    INSERT INTO siswa_rekap_sekolah (nama_sekolah, jumlah_siswa, date)
    VALUES (%s, %s, %s)
    ON CONFLICT (nama_sekolah, date)
    DO UPDATE SET 
        jumlah_siswa = EXCLUDED.jumlah_siswa;
    """
    
    execute_transfer(aggregation_query, create_table_query, insert_query, "rekap jumlah siswa berdasarkan sekolah")


# Fungsi umum untuk eksekusi transfer data
def execute_transfer(aggregation_query, create_table_query, insert_query, operation_name):
    try:
        # Koneksi ke database sumber
        source_conn = psycopg2.connect(**source_config)
        source_cursor = source_conn.cursor()
        
        # Eksekusi query untuk mengambil data
        source_cursor.execute(aggregation_query)
        processed_data = source_cursor.fetchall()
        
        # Tambahkan kolom date ke setiap row hasil query
        processed_data_with_date = [row + (current_date,) for row in processed_data]
        
        # Koneksi ke database target
        target_conn = psycopg2.connect(**target_config)
        target_cursor = target_conn.cursor()
        
        # Buat tabel baru di target database
        target_cursor.execute(create_table_query)
        
        # Masukkan data ke tabel baru menggunakan UPSERT
        target_cursor.executemany(insert_query, processed_data_with_date)
        
        # Commit perubahan
        target_conn.commit()
        print(f"Data berhasil ditransfer untuk {operation_name}!")
    
    except Exception as e:
        print(f"Terjadi kesalahan selama {operation_name}: {e}")
    finally:
        # Tutup koneksi
        if source_cursor:
            source_cursor.close()
        if source_conn:
            source_conn.close()
        if target_cursor:
            target_cursor.close()
        if target_conn:
            target_conn.close()

# Fungsi utama
if __name__ == "__main__":
    print("Pilih opsi rekapitulasi:")
    print("1. Rekap total siswa per kabupaten/kota")
    print("2. Rekap jumlah siswa berdasarkan jenis kelamin")
    print("3. Rekap jumlah siswa berdasarkan agama")
    print("4. Rekap jumlah siswa berdasarkan kecamatan")
    print("5. Rekap jumlah siswa berdasarkan sekolah")
    pilihan = input("Masukkan pilihan (1/2/3/4/5): ").strip()
    
    if pilihan == "1":
        rekap_total()
    elif pilihan == "2":
        rekap_jenis_kelamin()
    elif pilihan == "3":
        rekap_per_agama()
    elif pilihan == "4":
        rekap_per_kecamatan()
    elif pilihan == "5":
        rekap_per_sekolah()
    else:
        print("Pilihan tidak valid. Program dihentikan.")
