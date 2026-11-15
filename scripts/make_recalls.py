# マツダ各車種のリコール情報ファイル（data/recalls/<slug>.json）を作るプログラム
#
# 使い方（プロジェクトのフォルダで実行）:
#   python3 scripts/make_recalls.py
#   node scripts/build-data.js      ← 作ったファイルを site/data/recalls/ にコピーする
#
# 読み込むもの:
#   data/recalls-source/mazda_raw.json
#     国土交通省「自動車不具合情報ホットライン」のリコール検索で、車名「マツダ」の
#     届出一覧（543件、2026年9月30日まで）と、対象車種を含む84件の詳細ページの内容を
#     ブラウザで読み取って保存したもの（2026-11-15取得）。
#     list:    "id|届出番号|届出日|通称名" の一覧
#     details: id ごとの詳細（f=届出の項目、tg=対象車種の型式・車台番号の行）
#   data/recalls/マツダ-CX-5.json
#     CX-5 は別の手順で先に作ったファイルを読み込み、同じ形式に整えて書き戻す。
#
# 書き出すもの:
#   data/recalls/ 以下の 9 ファイル（CX-30, MAZDA3, CX-3, CX-60, MX-30,
#   デミオ-MAZDA2, ロドスタ, CX-80, CX-5）。同じ名前のファイルは上書きする。
#
# 世代の名前と年代は、マツダ公式ニュースルームの情報で確認したもの（下の MODELS に出典URL）。
# 型式と世代の対応は、国交省データの製作期間と公式の発売時期を照らし合わせて決めた。
import json, re, sys, unicodedata, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
RAW = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'data', 'recalls-source', 'mazda_raw.json')
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, 'data', 'recalls')
d = json.load(open(RAW, encoding='utf-8'))
N = lambda x: unicodedata.normalize('NFKC', x).replace(' ', '').replace('　', '')
LIST = {r.split('|')[0]: r.split('|') for r in d['list']}

SOURCE = {
    "name": "国土交通省 自動車不具合情報ホットライン リコール情報検索",
    "url": "https://renrakuda.mlit.go.jp/renrakuda/recall-search.html",
    "credit": "出典：国土交通省 自動車不具合情報ホットライン（https://renrakuda.mlit.go.jp/renrakuda/recall-search.html）を加工して作成",
    "license": "公共データ利用規約（第1.0版）（PDL1.0）",
}
NR = 'https://newsroom.mazda.com/ja/'
def gen(id, name, launched, url, title, current=False, note=None):
    g = {"id": id, "name": name, "launched": launched, "current": current,
         "officialSource": {"title": title, "url": url}}
    if note: g["note"] = note
    return g

MODELS = {
  'CX-30': dict(match=lambda n: n == 'CX-30', gens=[
      gen('DM', '初代（DM系・2019年10月〜）', '2019年10月', NR+'publicity/release/2019/201909/190920a.html', 'マツダ ニュースリリース「MAZDA CX-30」の予約受注を開始', True)]),
  'MAZDA3': dict(match=lambda n: n == 'MAZDA3', note='2019年5月より前の先代モデルは「アクセラ」という別の車名で販売されていたため、ここには含めていません。', gens=[
      gen('BP', '初代（BP系・2019年5月〜）', '2019年5月', NR+'other/1904/index.html', 'マツダ ニュースルーム 系図 MAZDA3', True)]),
  'CX-3': dict(match=lambda n: n == 'CX-3', gens=[
      gen('DK', '初代（DK系・2015年2月〜）', '2015年2月', NR+'other/1906/index.html', 'マツダ ニュースルーム 系図 CX-3', True)]),
  'CX-60': dict(match=lambda n: n == 'CX-60', gens=[
      gen('KH', '初代（KH系・2022年9月〜）', '2022年9月', NR+'publicity/release/2022/202209/220915a.html', 'マツダ ニュースリリース「MAZDA CX-60」の販売を開始', True)]),
  'MX-30': dict(match=lambda n: n == 'MX-30', gens=[
      gen('DR', '初代（DR系・2020年10月〜）', '2020年10月', NR+'publicity/release/2020/202010/201008a.html', 'マツダ ニュースリリース 新型コンパクトSUV「MAZDA MX-30」を発売', True)]),
  'デミオ/MAZDA2': dict(match=lambda n: 'デミオ' in n or 'MAZDA2' in n, gens=[
      gen('DJ', '4代目（DJ系・2014年9月〜、2019年9月にMAZDA2へ改名）', '2014年9月', NR+'publicity/release/2019/201907/190718a.html', 'マツダ ニュースルーム 系図 DEMIO／ニュースリリース「MAZDA2」の予約受注を開始', True),
      gen('DE', '3代目（DE系・2007〜2014年）', '2007年7月', NR+'other/1909/index.html', 'マツダ ニュースルーム 系図 DEMIO'),
      gen('DY', '2代目（DY系・2002〜2007年）', '2002年8月', NR+'other/1909/index.html', 'マツダ ニュースルーム 系図 DEMIO'),
      gen('DW', '初代（DW系・1996〜2002年）', '1996年8月', NR+'other/1909/index.html', 'マツダ ニュースルーム 系図 DEMIO')]),
  'ロードスター': dict(match=lambda n: 'ロードスター' in n or 'ROADSTER' in n,
      note='ロードスターRF（リトラクタブルハードトップ）も国交省のデータでは同じ「ロードスター」として届け出られており、RFだけを区別できません。RFが対象かどうかは、型式・車台番号でご確認ください。', gens=[
      gen('ND', '4代目（ND系・2015年5月〜）', '2015年5月', NR+'other/1901/index.html', 'マツダ ニュースルーム 系図 ROADSTER', True),
      gen('NC', '3代目（NC系・2005〜2015年）', '2005年8月', NR+'other/1901/index.html', 'マツダ ニュースルーム 系図 ROADSTER'),
      gen('NB', '2代目（NB系・1998〜2005年）', '1998年1月', NR+'other/1901/index.html', 'マツダ ニュースルーム 系図 ROADSTER'),
      gen('NA', '初代（NA系・1989〜1998年、ユーノスロードスター）', '1989年9月', NR+'other/1901/index.html', 'マツダ ニュースルーム 系図 ROADSTER')]),
}
SPECIAL = {'リ国-3092-0': '社外の警光灯を後から取り付けた車両（25台）だけが対象の届出です。'}

def slugify(s):
    s = s.replace('/', '-'); s = re.sub(r'\s+', '-', s)
    return re.sub(r'[^A-Za-z0-9_\-一-龠ぁ-んァ-ヶ]', '', s)  # build-data.js と同じ規則

def fam(tc):
    return tc.split('-', 1)[1][:2]

# ---- 不具合装置名の補完（国交省データ自身に出てくる完全な表記だけを使う）----
cx5_path = os.path.join(OUTDIR, 'マツダ-CX-5.json')
cx5 = json.load(open(cx5_path, encoding='utf-8'))
all_devs = [v['f']['defective_device'] for v in d['details'].values()]
all_devs += [r.get('deviceOriginal', r['device']) for r in cx5['recalls']]
truncated = lambda s: s.count('(') > s.count(')')
FULL = sorted({s for s in all_devs if not truncated(s)})
def fix_device(s):
    if not truncated(s): return s, None
    cands = [f for f in FULL if f.startswith(s)]
    if len(cands) == 1: return cands[0], s
    return s + '…)', s

def clean(s): return re.sub(r'[ 　]+', '', s) if s else s

out_files = []
for model, cfg in MODELS.items():
    gens = cfg['gens']; gids = {g['id'] for g in gens}
    recalls = []
    for id, v in d['details'].items():
        rows = [t for t in v['tg'] if cfg['match'](N(t['通称名']))]
        if not rows: continue
        _, no, date, _ = LIST[id]
        f = v['f']
        targets = []
        for t in rows:
            tc = N(t['型式/型番']); g = fam(tc)
            assert g in gids, (model, no, tc)
            targets.append({"typeCode": tc, "chassisRange": t['車台番号又はシリアル番号'], "generation": g})
        dev, orig = fix_device(f['defective_device'])
        r = {"no": no, "baseNo": no.rsplit('-', 1)[0],
             "kind": 'リコール' if no.startswith('リ') else '改善対策',
             "date": date, "startDate": clean(f.get('model_import_production_start_date', '')),
             "device": dev}
        if orig: r["deviceOriginal"] = orig
        r.update({"situation": f['situation_explanatory_text'], "measures": f['measures_explanatory_text'],
                  "productionPeriod": f.get('import_production_date', ''), "units": clean(f.get('recall_car_count', '')),
                  "generations": [g['id'] for g in gens if any(t['generation'] == g['id'] for t in targets)],
                  "targets": targets, "specialVehicle": no in SPECIAL})
        if no in SPECIAL: r["note"] = SPECIAL[no]
        r["url"] = f"https://renrakuda.mlit.go.jp/renrakuda/ris-detail-car.html?selCarTp=1&id={id}"
        recalls.append(r)
    recalls.sort(key=lambda r: (r['date'], r['no']), reverse=True)
    doc = {"slug": slugify('マツダ-' + model), "maker": 'マツダ', "model": model, "source": SOURCE,
           "retrievedAt": '2026-11-15', "coveredUntil": '2026-09-30'}
    if cfg.get('note'): doc["note"] = cfg['note']
    doc["generations"] = gens
    doc["recalls"] = recalls
    out_files.append((doc['slug'], doc))

# CX-80：届出なし
out_files.append(('マツダ-CX-80', {"slug": 'マツダ-CX-80', "maker": 'マツダ', "model": 'CX-80', "source": SOURCE,
    "retrievedAt": '2026-11-15', "coveredUntil": '2026-09-30',
    "generations": [gen('current', '初代（2024年10月〜）', '2024年10月', NR+'publicity/release/2024/202410/241010a.html', 'マツダ ニュースリリース「MAZDA CX-80」の販売を開始', True,
        '2026年9月30日までの届出に、「CX-80」を対象とするものはありません。')],
    "recalls": []}))

# CX-5：新しい形式に書き換え（内容は同じ。装置名の補完だけ追加）
cx5_gens = [
    gen('current', '3代目（2026年5月〜）', '2026年5月', NR+'publicity/release/2026/202605/260521a.html', 'マツダ ニュースリリース 新型「MAZDA CX-5」の販売を開始', True,
        '2026年9月30日までの届出には、現行型のリコールはありません。'),
    gen('KF', '2代目（KF系・2017〜2026年）', '2017年2月', None, None),
    gen('KE', '初代（KE系・2012〜2017年）', '2012年2月', None, None)]
for g in cx5_gens[1:]:
    g.pop('officialSource'); g.pop('launched')
new_cx5 = {k: cx5[k] for k in ['slug', 'maker', 'model', 'source', 'retrievedAt', 'coveredUntil']}
new_cx5['generations'] = cx5_gens
new_cx5['recalls'] = []
for r in cx5['recalls']:
    r = dict(r)
    dev, orig = fix_device(r.get('deviceOriginal', r['device']))
    r['device'] = dev
    if orig: r['deviceOriginal'] = orig
    r['targets'] = [dict(t, generation=('KE' if '-KE' in t['typeCode'] else 'KF')) for t in r['targets']]
    # キーの順番を揃える
    keys = ['no','baseNo','kind','date','startDate','device','deviceOriginal','situation','measures','productionPeriod','units','generations','targets','specialVehicle','note','url']
    new_cx5['recalls'].append({k: r[k] for k in keys if k in r})
out_files.append(('マツダ-CX-5', new_cx5))

for slug, doc in out_files:
    with open(os.path.join(OUTDIR, slug + '.json'), 'w', encoding='utf-8') as fp:
        json.dump(doc, fp, ensure_ascii=False, indent=2); fp.write('\n')
    print(slug, len(doc['recalls']), '件（枝番込み）', len({r['baseNo'] for r in doc['recalls']}), '届出')
print('補完した装置名:', sorted({(r.get('deviceOriginal'), r['device']) for _, doc in out_files for r in doc['recalls'] if r.get('deviceOriginal')}))
