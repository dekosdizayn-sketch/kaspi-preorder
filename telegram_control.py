import json, os, subprocess, tempfile, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from pathlib import Path

TOKEN=os.environ['TELEGRAM_BOT_TOKEN']; CHAT=str(os.environ['TELEGRAM_CHAT_ID'])
STATE=Path('.github/telegram_bot_state.json'); XML=Path('ACTIVE_preorder1.xml')
KEYBOARD={"keyboard":[["🔍 Статус","📊 Есеп"],["▶️ Іске қосу","ℹ️ Көмек"]],"resize_keyboard":True,"is_persistent":True}
def local(t): return t.rsplit('}',1)[-1]
def api(method, data=None):
    url=f'https://api.telegram.org/bot{TOKEN}/{method}'
    if data is None: return json.load(urllib.request.urlopen(url))
    body=urllib.parse.urlencode(data).encode(); return json.load(urllib.request.urlopen(url, body))
def send(text, keyboard=False):
    data={'chat_id':CHAT,'text':text,'parse_mode':'HTML'}
    if keyboard: data['reply_markup']=json.dumps(KEYBOARD,ensure_ascii=False)
    api('sendMessage', data)
def info():
    root=ET.parse(XML).getroot(); company=next((e.text.strip() for e in root.iter() if local(e.tag)=='company' and e.text),''); merchant=next((e.text.strip() for e in root.iter() if local(e.tag)=='merchantid' and e.text),'')
    offers=[]; seen=set(); preorder=0; available=0
    for e in root.iter():
        if local(e.tag)!='offer': continue
        sku=(e.get('sku') or '').strip()
        if not sku or sku in seen: continue
        seen.add(sku); offers.append(e)
        a=next((x for x in e.iter() if local(x.tag)=='availability'),None)
        if a is not None and a.get('available')=='yes':
            available+=1
            if a.get('preOrder')=='1': preorder+=1
    return company,merchant,len(offers),available,preorder
state=json.loads(STATE.read_text() if STATE.exists() else '{"last_update_id":0}')
resp=api('getUpdates'); updates=resp.get('result',[]); changed=False
for u in updates:
    uid=u.get('update_id',0)
    if uid<=state.get('last_update_id',0): continue
    state['last_update_id']=uid; changed=True
    msg=u.get('message',{}); raw=(msg.get('text') or '').strip(); text=raw.split()[0].lower() if raw else ''; chat=str(msg.get('chat',{}).get('id',''))
    if chat!=CHAT: continue
    if text in ('/start','/help') or raw=='ℹ️ Көмек':
        send('<b>🤖 DEKOS Kaspi Bot</b>\n\nТөмендегі батырмалар арқылы басқарыңыз.\n\n🔍 Статус — каталогтың қазіргі жағдайы\n📊 Есеп — толық есеп\n▶️ Іске қосу — 50 тауарды тексеріп, 1 күндік предзаказды іске қосу\nℹ️ Көмек — батырмалар туралы ақпарат\n\n🛡 Бот тек осы Telegram чат пен 50 тауарлық тексерілген каталогқа рұқсат береді.', True)
    elif text in ('/status',) or raw=='🔍 Статус':
        c,m,total,av,p=info(); send(f'<b>📊 DEKOS Kaspi Status</b>\n\n🏪 <b>Компания:</b> {c}\n🏬 <b>Магазин:</b> {m}\n📦 <b>Бірегей тауар:</b> {total}\n🟢 <b>Қолжетімді:</b> {av}\n🛒 <b>1 күндік предзаказ:</b> {p}\n\n🛡 Күтілетін каталог: 50 тауар')
    elif text in ('/report',) or raw=='📊 Есеп':
        c,m,total,av,p=info(); send(f'<b>📋 DEKOS Kaspi толық есеп</b>\n\n🏪 <b>Компания:</b> {c}\n🏬 <b>Магазин:</b> {m}\n📦 <b>Барлық бірегей тауар:</b> {total}\n🟢 <b>Қолжетімді:</b> {av}\n🛒 <b>1 күндік предзаказ:</b> {p}\n⏳ <b>Қалғаны:</b> {max(av-p,0)}\n\n🎯 Қауіпсіздік лимиті: 50 тауар')
    elif text=='/run' or raw=='▶️ Іске қосу':
        send('<b>🟡 Қолмен тексеру басталды</b>\n\n🔍 Каталог тексеріліп жатыр...\n🎯 Күтілетіні: 50 тауар\n🛒 Предзаказ: 1 күн')
        with tempfile.NamedTemporaryFile(delete=False) as f: out=f.name
        env=os.environ.copy(); env['GITHUB_OUTPUT']=out
        r=subprocess.run(['python','set-preorder.py'],env=env,text=True,capture_output=True)
        vals={}
        if Path(out).exists():
            for line in Path(out).read_text().splitlines():
                if '=' in line: k,v=line.split('=',1); vals[k]=v
        Path(out).unlink(missing_ok=True)
        if r.returncode==0:
            send(f'<b>🟢 Қолмен тексеру аяқталды</b>\n\n📦 <b>Нақты тауар:</b> {vals.get("total",0)}\n🔄 <b>1 күнге өзгертілді:</b> {vals.get("updated",0)}\n📋 <b>Бұрыннан 1 күнде:</b> {vals.get("already_preorder",0)}\n⚠️ <b>Availability жоқ:</b> {vals.get("skipped",0)}')
        else:
            send(f'<b>🔴 Қауіпсіздік үшін тоқтатылды</b>\n\n📦 <b>Табылған тауар:</b> {vals.get("total",0)}\n🛡 Ешқандай өзгеріс жасалған жоқ.')
    elif text.startswith('/'):
        send('⚠️ Белгісіз команда. ℹ️ Көмек батырмасын басыңыз.', True)
if changed: STATE.write_text(json.dumps(state,ensure_ascii=False))
