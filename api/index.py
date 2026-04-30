import os
from flask import Flask, render_template, request
from serpapi import GoogleSearch

# Ambil path absolut folder ini
base_dir = os.path.dirname(os.path.abspath(__file__))
# Gabungkan dengan folder templates yang ada di luar folder api
template_dir = os.path.join(base_dir, '..', 'templates')

app = Flask(__name__, template_folder=template_dir)

# Mengambil API Key dari Environment Variable (Lebih Aman untuk Vercel)
SERPAPI_KEY = os.environ.get("SERPAPI_KEY", "976f7a337da733050f49dd4eadb29096effbe45f55a107f0a1f02db122bae560")

@app.route('/', methods=['GET', 'POST'])
def home():
    results = None
    error = None
    
    if request.method == 'POST':
        file = request.files.get('file')
        
        if not file or file.filename == '':
            error = "Silakan upload foto terlebih dahulu!"
        else:
            try:
                # Simpan sementara di /tmp
                if not os.path.exists("/tmp"):
                    os.makedirs("/tmp")
                
                temp_path = os.path.join("/tmp", file.filename)
                file.save(temp_path)
                
                # 1. Upload ke Hosting Sementara (Catbox) agar dapat URL Publik
                import requests
                url_catbox = "https://catbox.moe/user/api.php"
                with open(temp_path, 'rb') as f:
                    upload_response = requests.post(
                        url_catbox, 
                        data={"reqtype": "fileupload"}, 
                        files={"fileToUpload": f}
                    )
                
                if upload_response.status_code != 200:
                    error = "Gagal mengunggah gambar ke server sementara. Coba lagi."
                else:
                    public_image_url = upload_response.text.strip()
                    
                    # 2. Kirim URL Publik tersebut ke Google Lens (SerpApi)
                    search = GoogleSearch({
                        "engine": "google_lens",
                        "url": public_image_url,
                        "api_key": SERPAPI_KEY
                    })
                    
                    # Ambil hasil pencarian
                    results_data = search.get_dict()
                    
                    if 'error' in results_data:
                        print("DEBUG Error Message:", results_data['error'])
                        error = f"Error dari AI: {results_data['error']}"
                    
                    results = results_data.get("visual_matches", [])
                    if not results:
                        results = results_data.get("reverse_image_search", [])
                        
                    if not results and not error:
                        error = "Tidak ditemukan kembaran yang mirip. Coba foto lain!"

                # Hapus file setelah selesai agar hemat storage
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                
                if not results:
                    error = "Tidak ditemukan kembaran yang mirip. Coba foto lain!"
                    
            except Exception as e:
                error = f"Terjadi kesalahan: {str(e)}"
                
    return render_template('index.html', results=results, error=error)

# Handler untuk Vercel
def handler(event, context):
    return app(event, context)

if __name__ == "__main__":
    app.run(debug=True)
