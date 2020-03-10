# -*- coding: utf-8 -*-
import network
import urequests
import ujson
import utime
from machine import Pin

# Wi-Fiアクセス用のSSIDとパスワード
WIFI_SSID = 'XXXXXXXX'
WIFI_PASSWORD = 'XXXXXXXX'
# Sesame APIアクセス用のAPIキー
APIKEY = 'XXXXXXXX'

# 文字列定数の定義
API_COMMON = 'https://api.candyhouse.co/public'
HEADER_GET = {'Authorization': APIKEY}
HEADER_POST = {'Authorization': APIKEY,
               'Content-Type': 'application/json'}

# ボタン状態を表す定数
RELEASED = 0
SHORT_PUSHED = 1
LONG_PUSHED = 2

# WiFiアクセスポイントに接続する。
def do_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())

# REST APIに要求を送信し、応答をJSON形式で返す。
def request_and_get_json(kind, url, headers=None, data=None):
    j = {}
    r = None
    try:
        # 指定されたURLに要求を送信し、応答をrに格納する。
        r = urequests.request(kind, url, headers=headers, data=data)
        # 応答をJSONデータに変換する。
        j = r.json()
    except Exception as e:
        print('{}: requests_and_get_json()'.format(e))
    finally:
        # 応答格納変数rは不要になったらすぐにcloseする。
        if r is not None:
            r.close()
    return j

# セサミの一覧を取得しリストで返す。
def get_sesames():
    return request_and_get_json(
        "GET", API_COMMON + '/sesames', headers=HEADER_GET)

# セサミの状態を取得する。
# 返値は'locked', 'unlocked', 'failed'のいずれか。
def get_sesame_status(sesame):
    j = request_and_get_json(
        "GET",
        (API_COMMON + '/sesame/{}').format(sesame['device_id']),
        headers=HEADER_GET)
    try:
        return 'locked' if j['locked'] else 'unlocked'
    except KeyError:
        # 'locked'というキーが無い場合
        return 'unknown'

# 指定されたセサミを解錠または施錠する。
# command引数で'lock'または'unlock'を指定する。
def do_sesame(sesame, command):
    post_data = ujson.dumps(dict(command=command))
    print('{} {}ing.'.format(sesame['nickname'], command), end='')
    # コマンドを送信する。
    # 応答結果としてタスクID(task_id)が得られる。
    j = request_and_get_json(
        "POST",
        (API_COMMON + '/sesame/{}').format(sesame['device_id']),
        headers=HEADER_POST,
        data=post_data)
    # タスクが完了状態(terminated)になるまで待つ。
    while True:
        j = request_and_get_json(
            "GET",
            (API_COMMON + '/action-result?task_id={}').format(j['task_id']),
            headers=HEADER_GET)
        print('.', end='')
        if 'status' in j and j['status'] == 'terminated':
            if j['successful']:
                print('{}ed'.format(command))
            else:
                print('failed')
            break
        # タスクが処理中なら1秒待つ。
        else:
            utime.sleep(1)

# セサミの状態一覧を表示する。
def dump_all_sesame_status(sesames):
    for s in sesames:
        status = get_sesame_status(s)
        print('{} {}'.format(s['nickname'], status))

# すべてのセサミを施錠する。
def lock_sesames(sesames):
    for s in sesames:
        status = get_sesame_status(s)
        print('{} {}'.format(s['nickname'], status))
        if status == 'unlocked':
            do_sesame(s, 'lock')

# すべてのセサミを解錠する。
def unlock_sesames(sesames):
    for s in sesames:
        status = get_sesame_status(s)
        print('{} {}'.format(s['nickname'], status))
        if status == 'locked':
            do_sesame(s, 'unlock')

# GPIOピンの割り込みハンドラ
def gpio_callback(p):
    global pushed_time
    global button_pushed

    # ピンの状態が0(ボタン押下)となった時刻を記録する。
    if p.value() == 0:
        pushed_time = utime.ticks_ms()
        return
    # ピンの状態が1(ボタンが離された)になった時刻との差が
    # 1秒未満かどうかで短押しか長押しかを判定する。
    else:
        released_time = utime.ticks_ms()
        if released_time - pushed_time < 1000:
            button_pushed = SHORT_PUSHED
        else:
            button_pushed = LONG_PUSHED

# メイン処理
if __name__ == "__main__":
    button_pushed = RELEASED
    pushed_time = 0
    p0 = Pin(0, Pin.IN)
    # GPIO0に割り込みハンドラを設定する。
    # ピン状態の立ち上がりと立ち下がりを検出する。
    p0.irq(
        trigger=Pin.IRQ_RISING|Pin.IRQ_FALLING,
        handler=gpio_callback)
    # Wi-Fiに接続
    do_connect()
    sesames = get_sesames()
    while True:
        try:
            # ボタン短押しなら施錠
            if button_pushed == SHORT_PUSHED:
                print('LOCKING All Sesames')
                lock_sesames(sesames)
                print('LOCKED')
                button_pushed = RELEASED
            # ボタン長押しなら解錠
            elif button_pushed == LONG_PUSHED:
                print('UNLOCKING All Sesames')
                unlock_sesames(sesames)
                print('UNLOCKED')
                button_pushed = RELEASED
            # ボタン押下判定を100msごとに実行する。
            utime.sleep_ms(100)
        except:
            # エラー発生時には何もしない。
            button_pushed = RELEASED
