from flask import Flask, render_template, flash, redirect, url_for, request
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
import os
from newagregasi import rekap_total, rekap_jenis_kelamin, rekap_per_agama, rekap_per_kecamatan, rekap_per_sekolah  # Import fungsi agregasi

app = Flask(__name__)

app.secret_key = 'your_secret_key'  


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


def get_db_connection(config):
    """Create and return a database connection"""
    return psycopg2.connect(**config)

@app.route('/')
def index():
    """Main index page displaying data from siswasma"""
    conn = get_db_connection(source_config)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            NISN, 
            Nama_Siswa, 
            Jenis_Kelamin, 
            Agama, 
            Sekolah, 
            NPSN, 
            Kecamatan, 
            Kabupaten_Kota 
        FROM siswa
        ORDER BY Nama_Siswa ASC
    """)
    
    students = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('base.html', students=students)


@app.route('/lihat-data-terakhir', methods=['GET'])
def lihat_data_terakhir():
    """Route untuk melihat data terakhir berdasarkan tanggal input terbaru"""
    try:
        # Koneksi ke database target
        conn = get_db_connection(target_config)
        cursor = conn.cursor()

        # Ambil data dengan tanggal input terakhir
        cursor.execute("""
            SELECT 
                kabupaten_kota, 
                jumlah_siswa, 
                jumlah_laki_laki, 
                jumlah_perempuan, 
                date 
            FROM siswa_rekap 
            WHERE date = (
                SELECT MAX(date) 
                FROM siswa_rekap
            )
            ORDER BY kabupaten_kota ASC
        """)
        students = cursor.fetchall()

        # Ambil data gender berdasarkan tanggal terakhir
        cursor.execute("""
            SELECT 
                jumlah_laki_laki, 
                jumlah_perempuan, 
                date 
            FROM siswa_rekap_gender 
            WHERE date = (
                SELECT MAX(date) 
                FROM siswa_rekap_gender
            )
        """)
        gender_stats = cursor.fetchall()

        # Ambil data agama berdasarkan tanggal terakhir
        cursor.execute("""
            SELECT 
                agama, 
                jumlah_siswa, 
                date 
            FROM siswa_rekap_agama 
            WHERE date = (
                SELECT MAX(date) 
                FROM siswa_rekap_agama
            )
        """)
        agama_stats = cursor.fetchall()

        # Ambil data kecamatan berdasarkan tanggal terakhir
        cursor.execute("""
            SELECT 
                kecamatan, 
                jumlah_siswa, 
                date 
            FROM siswa_rekap_kecamatan 
            WHERE date = (
                SELECT MAX(date) 
                FROM siswa_rekap_kecamatan
            )
        """)
        kecamatan_stats = cursor.fetchall()

        # Ambil data sekolah berdasarkan tanggal terakhir
        cursor.execute("""
            SELECT 
                nama_sekolah, 
                jumlah_siswa, 
                date 
            FROM siswa_rekap_sekolah 
            WHERE date = (
                SELECT MAX(date) 
                FROM siswa_rekap_sekolah
            )
        """)
        sekolah_stats = cursor.fetchall()

        cursor.close()
        conn.close()

        # Render template dengan data terbaru
        return render_template(
            'lihat_data_terakhir.html', 
            students=students, 
            gender_stats=gender_stats, 
            agama_stats=agama_stats, 
            kecamatan_stats=kecamatan_stats, 
            sekolah_stats=sekolah_stats
        )

    except Exception as e:
        flash(f"Terjadi kesalahan saat melihat data terakhir: {e}", "danger")
        return redirect(url_for('index'))




@app.route('/lihat-agregasi', methods=['POST'])
def lihat_agregasi():
    """Route untuk melihat data agregasi berdasarkan periode tanggal"""
    tanggal_awal = request.form['tanggal_awal']
    tanggal_akhir = request.form['tanggal_akhir']

    try:
        # Format tanggal agar cocok dengan format di database
        start_date = datetime.strptime(tanggal_awal, '%Y-%m-%d').date()
        end_date = datetime.strptime(tanggal_akhir, '%Y-%m-%d').date()

        # Query data berdasarkan periode
        conn = get_db_connection(target_config)
        cursor = conn.cursor()

        # Tampilkan rekap total siswa berdasarkan periode
        cursor.execute("""
            SELECT 
                kabupaten_kota, 
                jumlah_siswa, 
                jumlah_laki_laki, 
                jumlah_perempuan, 
                date 
            FROM siswa_rekap 
            WHERE date BETWEEN %s AND %s
            ORDER BY date DESC, jumlah_siswa DESC
        """, (start_date, end_date))

        students = cursor.fetchall()

        # Tampilkan rekap jumlah siswa berdasarkan jenis kelamin
        cursor.execute("""
            SELECT 
                jumlah_laki_laki, 
                jumlah_perempuan, 
                date 
            FROM siswa_rekap_gender 
            WHERE date BETWEEN %s AND %s
            ORDER BY date DESC
        """, (start_date, end_date))

        gender_stats = cursor.fetchall()

        # Tampilkan rekap berdasarkan agama
        cursor.execute("""
            SELECT 
                agama, 
                jumlah_siswa,
                date
            FROM siswa_rekap_agama 
            WHERE date BETWEEN %s AND %s
            ORDER BY date DESC, jumlah_siswa DESC
        """, (start_date, end_date))
        
        agama_stats = cursor.fetchall()

        # Tampilkan rekap berdasarkan kecamatan
        cursor.execute("""
            SELECT 
                kecamatan, 
                jumlah_siswa,
                date 
            FROM siswa_rekap_kecamatan 
            WHERE date BETWEEN %s AND %s
            ORDER BY date DESC, jumlah_siswa DESC
        """, (start_date, end_date))
        
        kecamatan_stats = cursor.fetchall()

        # Tampilkan rekap berdasarkan sekolah
        cursor.execute("""
            SELECT 
                nama_sekolah,
                jumlah_siswa,
                date
            FROM siswa_rekap_sekolah 
            WHERE date BETWEEN %s AND %s
            ORDER BY date DESC, jumlah_siswa  DESC
        """, (start_date, end_date))
        
        sekolah_stats = cursor.fetchall()

        cursor.close()
        conn.close()

        # Return data berdasarkan periode
        return render_template(
            'lihat_agregasi.html', 
            students=students, 
            gender_stats=gender_stats, 
            agama_stats=agama_stats, 
            kecamatan_stats=kecamatan_stats, 
            sekolah_stats=sekolah_stats,
            tanggal_awal=start_date, 
            tanggal_akhir=end_date
        )

    except Exception as e:
        flash(f"Terjadi kesalahan saat melihat data agregasi: {e}", "danger")
        return redirect(url_for('index'))
    



@app.route('/total-students')
def total_students():
    """Display total students by region"""
    conn = get_db_connection(target_config)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            kabupaten_kota, 
            jumlah_siswa, 
            jumlah_laki_laki, 
            jumlah_perempuan, 
            date 
        FROM siswa_rekap 
        ORDER BY date DESC, kabupaten_kota ASC
    """)
    
    students = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('total_students.html', students=students)

@app.route('/gender-students')
def gender_students():
    """Display students by gender"""
    conn = get_db_connection(target_config)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            jumlah_laki_laki, 
            jumlah_perempuan, 
            date 
        FROM siswa_rekap_gender 
        ORDER BY date DESC
    """)
    
    gender_stats = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('gender_students.html', gender_stats=gender_stats)

@app.route('/rekap-agama')
def rekap_agama_view():
    """Display students by religion"""
    conn = get_db_connection(target_config)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            agama, 
            jumlah_siswa, 
            date 
        FROM siswa_rekap_agama 
        ORDER BY date DESC
    """)
    
    agama_stats = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('rekap_agama.html', agama_stats=agama_stats)

@app.route('/rekap-kecamatan')
def rekap_kecamatan_view():
    """Display students by district"""
    conn = get_db_connection(target_config)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            kecamatan, 
            jumlah_siswa, 
            date 
        FROM siswa_rekap_kecamatan 
        ORDER BY date DESC
    """)
    
    kecamatan_stats = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('rekap_kecamatan.html', kecamatan_stats=kecamatan_stats)

@app.route('/rekap-sekolah')
def rekap_sekolah_view():
    """Display students by school"""
    conn = get_db_connection(target_config)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            nama_sekolah, 
            jumlah_siswa, 
            date 
        FROM siswa_rekap_sekolah 
        ORDER BY date DESC
    """)
    
    sekolah_stats = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('rekap_sekolah.html', sekolah_stats=sekolah_stats)

@app.route('/jalankan-agregasi', methods=['POST'])
def jalankan_agregasi():
    """Route untuk menjalankan agregasi saat tombol diklik"""
    pilihan = request.form['pilihan']  # Ambil nilai pilihan dari form
    
    try:
        if pilihan == "1":
            rekap_total()
            flash("Agregasi Rekap Total Siswa per Kabupaten/Kota berhasil dijalankan!", "success")
        elif pilihan == "2":
            rekap_jenis_kelamin()
            flash("Agregasi Rekap Jumlah Siswa Berdasarkan Jenis Kelamin berhasil dijalankan!", "success")
        elif pilihan == "3":
            rekap_per_agama()
            flash("Agregasi Rekap Berdasarkan Agama berhasil dijalankan!", "success")
        elif pilihan == "4":
            rekap_per_kecamatan()
            flash("Agregasi Rekap Berdasarkan Kecamatan berhasil dijalankan!", "success")
        elif pilihan == "5":
            rekap_per_sekolah()
            flash("Agregasi Rekap Berdasarkan Sekolah berhasil dijalankan!", "success")
        else:
            flash("Pilihan tidak valid!", "danger")
    except Exception as e:
        flash(f"Terjadi kesalahan saat menjalankan agregasi: {e}", "danger")
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
