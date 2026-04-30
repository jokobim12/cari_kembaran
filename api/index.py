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
        image_url = request.form.get('image_url')
        
        if not image_url:
            error = "Gagal memproses foto. Pastikan Anda mengunggah gambar yang valid."
        else:
            try:
                # Langsung Kirim URL Publik tersebut ke Google Lens (SerpApi)
                search = GoogleSearch({
                    "engine": "google_lens",
                    "url": image_url,
                    "api_key": SERPAPI_KEY
                })
                
                # Ambil hasil pencarian
                results_data = search.get_dict()
                
                if 'error' in results_data:
                    error = f"Error dari SerpApi: {results_data['error']}"
                else:
                    results = results_data.get("visual_matches", [])
                    if not results:
                        results = results_data.get("reverse_image_search", [])
                        
                if not results and not error:
                    error = "Tidak ditemukan kembaran yang mirip. Coba foto lain!"
                    
            except Exception as e:
                error = f"Terjadi kesalahan: {str(e)}"
                
    return render_template('index.html', results=results, error=error)

# Handler untuk Vercel
def handler(event, context):
    return app(event, context)

if __name__ == "__main__":
    app.run(debug=True)
