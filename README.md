# sesame-micropython
セサミをMicroPythonで操作するサンプルプログラム(ESP32-DevKitC用)

# 動作環境
- ESP32-DevKitC
- MicroPython 1.12 (1.12以前のバージョンでもおそらく動きます)

# 設定方法
- `WIFI_SSID`、`WIFI_PASSWORD`に、ESP32が接続するWiFiアクセスポイントのSSIDとパスワードを設定。
- `APIKEY`にSesame APIアクセス用のAPIキーを設定。

# 使い方
ESP32-DevKitCのENボタンでセサミの解錠と施錠を行います。
- 解錠: ENボタン長押し
- 施錠: ENボタン短押し
