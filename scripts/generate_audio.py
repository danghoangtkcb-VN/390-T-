"""Generate reusable northern male MP3s, using a user-provided FPT key.
Run: FPT_API_KEY=<configured privately> python3 scripts/generate_audio.py
Never commits the key. Existing matching files are reused on retries.
"""
import hashlib,json,os,time,urllib.request,urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
KEY=os.environ.get('FPT_API_KEY')
if not KEY:raise SystemExit('Thiếu FPT_API_KEY. Cấu hình khóa qua môi trường, không đưa vào mã nguồn.')
questions=json.loads((ROOT/'questions.json').read_text());out=ROOT/'audio';out.mkdir(exist_ok=True)
manifest={'voice':'leminh','locale':'vi-VN','region':'north','complete':False,'files':{}}
mp=out/'manifest.json'
if mp.exists():manifest['files']=json.loads(mp.read_text()).get('files',{})
for q in questions:
    answer=f"{q['ans']}. {q['opts'][q['ans']]}" if q['ans'] else f"Chưa chốt đáp án. {q['answer_text']}. {q['note']}"
    hook=q['hook'] or (f"Gợi ý ôn tập tự động: {q['opts'][q['ans']]}. Đối chiếu: {q['basis']}" if q['ans'] else 'Câu chưa chốt: ghi nhớ điểm cần xác minh, không học thuộc một phương án.')
    for part,text in [('q','Câu hỏi. '+q['q']),('a','Đáp án. '+answer+'. Móc nhớ. '+hook)]:
        name=f"{q['id']}_{part}.mp3";digest=hashlib.sha256(text.encode()).hexdigest();target=out/name
        if manifest['files'].get(name)==digest and target.exists():continue
        req=urllib.request.Request('https://api.fpt.ai/hmi/tts/v5',data=text.encode(),headers={'api_key':KEY,'voice':'leminh','speed':'0','format':'mp3'},method='POST')
        with urllib.request.urlopen(req,timeout=30) as r:result=json.load(r)
        if result.get('error')!=0:raise RuntimeError(f"FPT thất bại cho {name}: {result.get('message','không có âm thanh')}")
        url=result['async']
        from urllib.parse import urlparse
        host=urlparse(url).hostname or ''
        if urlparse(url).scheme!='https' or not(host.endswith('.amazonaws.com') or host.endswith('.fpt.ai')):raise RuntimeError('Địa chỉ audio ngoài nhà cung cấp')
        for attempt in range(30):
            try:
                with urllib.request.urlopen(url,timeout=30) as r:audio=r.read()
                if len(audio)<256:raise ValueError('Empty audio')
                target.write_bytes(audio);break
            except (urllib.error.HTTPError,ValueError):time.sleep(2)
        else:raise RuntimeError('Âm thanh chưa sẵn sàng. Chạy lại để tiếp tục.')
        manifest['files'][name]=digest;mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2));print(name,flush=True)
manifest['complete']=True;mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2));print('Đã tạo 780 bản ghi giọng nam miền Bắc.')
