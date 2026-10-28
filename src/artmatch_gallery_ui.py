"""ArtMatch Campus visitor UI. No third-party web framework required.
Launch from the notebook after loading model functions and CU gallery metadata.
"""
import base64
import io
import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from PIL import Image, ImageOps

PAGE = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ArtMatch Campus — Discover Campus Art</title>
<style>
:root {color-scheme:light; --ink:#252821;--soft:#676e66;--bg:#f7f5f0;--card:#fff;--line:#e5e1d8;--accent:#304e40;--accent-hover:#213a2e;--focus:#d9a757}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:system-ui,-apple-system,'Segoe UI',Arial,sans-serif;line-height:1.5}button,input{font:inherit}button{cursor:pointer}button:focus-visible,input:focus-visible,summary:focus-visible{outline:3px solid var(--focus);outline-offset:3px}button:disabled{opacity:.6;cursor:wait}
header{background:#fff;border-bottom:1px solid var(--line)}.wrap{width:min(1080px,calc(100% - 32px));margin:auto}.nav{min-height:76px;display:flex;align-items:center;justify-content:space-between;gap:12px}.brand{font-weight:750;letter-spacing:-.025em;font-size:clamp(22px,3vw,28px)}.brandmark{color:#9b6b3f;margin-right:8px}.eyebrow{font-size:12px;letter-spacing:.12em;font-weight:750;color:#666c63;text-transform:uppercase}
main{padding-bottom:75px}.hero{padding:42px 0 25px}.hero h1{font-family:Georgia,serif;font-weight:500;font-size:clamp(32px,4vw,52px);line-height:1.12;letter-spacing:-.02em;margin:10px 0 12px;max-width:780px}.hero p{font-size:17px;color:#555d56;margin:0;max-width:700px}
.panel{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:22px}.upload-grid{display:grid;grid-template-columns:minmax(220px,310px) 1fr;gap:24px;align-items:center}.upload-photo{width:100%;height:218px;object-fit:contain;background:#f0ede6;border-radius:10px;display:none}.upload-placeholder{height:218px;border:2px dashed #b6bbb1;background:#fafaf8;border-radius:10px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;gap:10px;color:#646960}.upload-placeholder .symbol{font-size:35px}.upload-copy h2{font-size:23px;margin:0 0 8px}.upload-copy p{color:#646a62;margin:0 0 17px}.buttons{display:flex;gap:10px;flex-wrap:wrap}.btn{min-height:48px;padding:11px 20px;border-radius:9px;border:1px solid #c5ccc4;background:white;color:var(--ink);font-weight:700}.btn.primary{background:var(--accent);border-color:var(--accent);color:white}.btn.primary:hover{background:var(--accent-hover)}.hint{font-size:13px;color:#666d66;margin-top:14px}.status{font-weight:650;margin:15px 0 0;min-height:24px;color:#36584a}.status.error{color:#a52d24}
.section{margin-top:36px}.section-head{display:flex;justify-content:space-between;align-items:end;gap:12px;margin-bottom:16px}.section h2{font-size:25px;letter-spacing:-.02em;margin:0}.sub{font-size:14px;color:#626a61;margin:4px 0 0}.hidden{display:none!important}.query-data{display:grid;grid-template-columns:150px 1fr;gap:20px;align-items:start}.query-thumb{width:100%;height:150px;object-fit:contain;background:#f3f0e9;border-radius:10px}.attributes{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:11px 22px;margin:0}.attribute{min-width:0}.attribute dt{font-size:12px;font-weight:750;text-transform:uppercase;letter-spacing:.04em;color:#646961}.attribute dd{margin:3px 0 0;font-size:15px;overflow-wrap:anywhere}
.results{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}.art-card{background:#fff;border:1px solid var(--line);border-radius:13px;overflow:hidden;min-width:0}.art-card img{width:100%;height:220px;object-fit:contain;background:#eeeae2;display:block}.art-body{padding:17px}.rank{font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:#6f746c;font-weight:750}.art-title{font-size:21px;font-weight:750;margin:4px 0 6px}.art-meta{font-size:14px;color:#485247;margin:0 0 14px}.floor{font-weight:750;color:#2b4a37}.art-card details{border-top:1px solid var(--line);padding-top:12px}.art-card summary{cursor:pointer;font-weight:750;color:#254e38;min-height:36px}.card-attrs{display:grid;grid-template-columns:1fr;gap:9px;margin-top:9px}.shared{background:#eef3ed;padding:11px;border-radius:8px;margin-top:12px;font-size:14px;overflow-wrap:anywhere}.empty{padding:27px;border:1px dashed #ccd0c8;border-radius:12px;color:#60675d;background:#fbfaf7}.foot{border-top:1px solid var(--line);margin-top:45px;padding-top:18px;color:#676d65;font-size:13px}
@media(max-width:760px){.upload-grid{grid-template-columns:1fr}.upload-placeholder,.upload-photo{height:190px}.results{grid-template-columns:repeat(2,minmax(0,1fr))}.query-data{grid-template-columns:110px 1fr}.query-thumb{height:110px}.attributes{grid-template-columns:1fr}.hero{padding-top:29px}}
@media(max-width:520px){.wrap{width:min(100% - 24px,1080px)}.nav{min-height:68px}.eyebrow{font-size:10px}.panel{padding:16px}.results{grid-template-columns:1fr}.art-card img{height:265px}.query-data{grid-template-columns:1fr}.query-thumb{height:180px}.hero p{font-size:15px}}
</style></head>
<body><header><div class="wrap nav"><div class="brand"><span class="brandmark">✦</span>ArtMatch Campus</div><span class="eyebrow">CU Artwork Discovery</span></div></header>
<main class="wrap"><section class="hero"><span class="eyebrow">Explore the collection</span><h1>Discover art that connects with your image.</h1><p>Upload a photograph or reference artwork and find five related works displayed across the campus.</p></section>
<section class="panel" aria-label="Search for artwork"><div class="upload-grid"><div><div id="placeholder" class="upload-placeholder"><span class="symbol" aria-hidden="true">▧</span><strong>Your photo appears here</strong><span>JPG · PNG · WEBP</span></div><img id="preview" class="upload-photo" alt="Your chosen image"></div><div class="upload-copy"><h2>Start with an image</h2><p>Choose a photo from your device. We'll match it with works in the CU collection.</p><input id="file" type="file" accept="image/jpeg,image/png,image/webp" hidden><div class="buttons"><button type="button" class="btn" id="choose">Choose photo</button><button type="button" class="btn primary" id="search" disabled>Find artworks →</button><button type="button" class="btn" id="reset">Start over</button></div><div class="hint">Your image is analyzed for this search; it is not saved by this application.</div><div id="status" class="status" role="status" aria-live="polite">Choose an image to begin.</div></div></div></section>
<section id="querySection" class="section hidden"><div class="section-head"><div><h2>Your image</h2><p class="sub">Predicted visual attributes</p></div></div><div class="panel query-data"><img id="queryPreview" class="query-thumb" alt="Your query photograph"><dl id="queryAttributes" class="attributes"></dl></div></section>
<section id="resultSection" class="section hidden"><div class="section-head"><div><h2>Your artwork matches</h2><p class="sub">Five related CU artworks, ranked by visual similarity</p></div><span class="eyebrow">5 results</span></div><div id="cards" class="results"></div></section>
<section id="emptySection" class="section"><div class="section-head"><div><h2>Explore related artworks</h2></div></div><div class="empty">Your five artwork matches will appear here after you select an image and start the search.</div></section>
<div class="foot">Artwork locations are recorded floor metadata. Similarity scores indicate visual closeness, not accuracy. Image descriptions are automated predictions and may be incorrect.</div></main>
<script>
(() => {
 const $=id=>document.getElementById(id);
 const file=$('file'), preview=$('preview'), queryPreview=$('queryPreview'), status=$('status');
 let selected=null, previewUrl=null, busy=false;
 const setStatus=(message,error=false)=>{status.textContent=message;status.classList.toggle('error',error)};
 const attrList=(obj,compact=false)=>{const dl=document.createElement('dl');dl.className=compact?'card-attrs':'attributes';for(const [key,value] of Object.entries(obj||{})){const box=document.createElement('div');box.className='attribute';const dt=document.createElement('dt');dt.textContent=key;const dd=document.createElement('dd');dd.textContent=Array.isArray(value)?(value.join(', ')||'Not detected'):String(value??'Not determined');box.append(dt,dd);dl.append(box)}return dl};
 const clearResults=()=>{$('querySection').classList.add('hidden');$('resultSection').classList.add('hidden');$('emptySection').classList.remove('hidden');$('cards').replaceChildren();$('queryAttributes').replaceChildren()};
 $('choose').addEventListener('click',()=>file.click());
 file.addEventListener('change',()=>{if(previewUrl){URL.revokeObjectURL(previewUrl);previewUrl=null}selected=file.files?.[0]||null;clearResults();if(!selected){preview.style.display='none';$('placeholder').style.display='flex';$('search').disabled=true;return}if(!/^image\/(jpeg|png|webp)$/.test(selected.type)){setStatus('Choose a JPG, PNG, or WEBP image.',true);selected=null;file.value='';return}if(selected.size>12*1024*1024){setStatus('Please choose an image smaller than 12 MB.',true);selected=null;file.value='';return}previewUrl=URL.createObjectURL(selected);preview.src=previewUrl;preview.style.display='block';$('placeholder').style.display='none';$('search').disabled=false;setStatus('Photo ready. Select “Find artworks”.')});
 $('reset').addEventListener('click',()=>{if(busy)return;file.value='';selected=null;if(previewUrl){URL.revokeObjectURL(previewUrl);previewUrl=null}preview.removeAttribute('src');preview.style.display='none';$('placeholder').style.display='flex';$('search').disabled=true;clearResults();setStatus('Choose an image to begin.')});
 function showResults(data){$('queryAttributes').replaceChildren(...attrList(data.query_attributes).childNodes);queryPreview.src=preview.src;$('querySection').classList.remove('hidden');const cards=$('cards');cards.replaceChildren();for(const item of data.results){const card=document.createElement('article');card.className='art-card';const img=document.createElement('img');img.src=item.image;img.alt=`Artwork ${item.artwork_id}`;img.loading='lazy';const body=document.createElement('div');body.className='art-body';const rank=document.createElement('div');rank.className='rank';rank.textContent=`Match ${item.rank}`;const name=document.createElement('h3');name.className='art-title';name.textContent=item.artwork_id;const meta=document.createElement('p');meta.className='art-meta';const fl=document.createElement('span');fl.className='floor';fl.textContent=`Floor ${item.floor}`;meta.append(fl,document.createTextNode(` · Similarity ${Number(item.similarity).toFixed(3)}`));const details=document.createElement('details');const summary=document.createElement('summary');summary.textContent='View artwork details';details.append(summary,attrList(item.attributes,true));const shared=document.createElement('div');shared.className='shared';const strong=document.createElement('strong');strong.textContent='Shared with your image: ';shared.append(strong,document.createTextNode(item.shared_features||'No shared attributes detected'));details.append(shared);body.append(rank,name,meta,details);card.append(img,body);cards.append(card)}$('resultSection').classList.remove('hidden');$('emptySection').classList.add('hidden');$('querySection').scrollIntoView({behavior:'smooth',block:'start'})}
 const toBase64=f=>new Promise((resolve,reject)=>{const r=new FileReader();r.onload=()=>resolve(String(r.result).split(',')[1]);r.onerror=()=>reject(new Error('Unable to read image'));r.readAsDataURL(f)});
 $('search').addEventListener('click',async()=>{if(!selected||busy)return;busy=true;$('search').disabled=true;$('choose').disabled=true;setStatus('Finding related artworks and analyzing images…');try{const b64=await toBase64(selected);const res=await fetch('api/search',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({image:b64})});const data=await res.json();if(!res.ok)throw new Error(data.error||`Request failed (${res.status})`);showResults(data);setStatus('Five matches found. Select “View artwork details” to learn more.')}catch(err){setStatus(`Unable to complete search: ${err.message}`,true)}finally{busy=false;$('choose').disabled=false;$('search').disabled=!selected}});
})();
</script></body></html>'''


def start_artmatch_ui(retrieve_adapted, analyze_artwork, shared_features,
                      gallery_image_root, port=8765):
    """Start local server and show the JupyterHub proxy URL for a new browser tab."""
    gallery_image_root = Path(gallery_image_root)
    inference_lock = threading.Lock()

    def encode_image(img):
        img = img.convert("RGB")
        img.thumbnail((900, 900))
        b = io.BytesIO()
        img.save(b, "JPEG", quality=82, optimize=True)
        return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode("ascii")

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            return  # Avoid logging visitor query metadata

        def do_GET(self):
            if self.path.split("?")[0].endswith("favicon.ico"):
                self.send_response(204)
                self.end_headers()
                return
            payload = PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(payload)

        def do_POST(self):
            if not self.path.split("?")[0].endswith("/api/search"):
                self.send_error(404)
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length < 18_000_000:
                    raise ValueError("Image request too large or missing")
                payload = json.loads(self.rfile.read(length))
                raw = base64.b64decode(payload["image"], validate=True)
                if len(raw) > 12 * 1024 * 1024:
                    raise ValueError("Image must be under 12 MB")
                with Image.open(io.BytesIO(raw)) as incoming:
                    if incoming.width * incoming.height > 35_000_000:
                        raise ValueError("Image dimensions are too large")
                    query = ImageOps.exif_transpose(incoming).convert("RGB")
                with inference_lock:
                    results = retrieve_adapted(query, top_k=5)
                    query_attrs = analyze_artwork(query)
                    items = []
                    for row in results.itertuples():
                        artwork_path = gallery_image_root / f"floor_{row.floor}" / str(row.filename)
                        if not artwork_path.is_file():
                            raise FileNotFoundError(f"Gallery artwork missing: {row.filename}")
                        with Image.open(artwork_path) as gallery_img:
                            artwork = gallery_img.convert("RGB")
                        attrs = analyze_artwork(artwork)
                        items.append({"rank": int(row.rank), "artwork_id": str(row.artwork_id),
                                      "floor": str(row.floor), "similarity": float(row.similarity),
                                      "image": encode_image(artwork), "attributes": attrs,
                                      "shared_features": shared_features(query_attrs, attrs)})
                content = {"query_attributes": query_attrs, "results": items}
                response = json.dumps(content, default=str).encode("utf-8")
                status = 200
            except Exception as e:
                response = json.dumps({"error": str(e)}).encode("utf-8")
                status = 400
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(response)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(response)

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    prefix = os.environ.get("JUPYTERHUB_SERVICE_PREFIX", "/user/jovyan/")
    url_path = f"{prefix.rstrip('/')}/proxy/{port}/"
    from IPython.display import display, HTML
    display(HTML(f'<p><b>ArtMatch visitor interface is running.</b> '
                 f'Open a new browser tab at: <a href="{url_path}" target="_blank" rel="noopener">'
                 f'{url_path}</a></p>'))
    print(f"Local server: http://127.0.0.1:{port}/")
    print("If the proxy link is unavailable, ask the server administrator whether Jupyter Server Proxy is enabled.")
    return server
