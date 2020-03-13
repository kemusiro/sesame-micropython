# sesame-micropython
セサミをMicroPythonで操作するサンプルプログラム(ESP32-DevKitC用)

# 概要
1つ以上のセサミを同時に施錠または解錠できます。セサミの操作をするために、あらかじめSesame API用のアクセスキーを入手しておく必要があります。

# 動作環境
- Sesame Mini
- ESP32-DevKitC
- MicroPython 1.12 (1.12以前のバージョンでもおそらく動きます)

# 設定方法
- `WIFI_SSID`、`WIFI_PASSWORD`に、ESP32が接続するWiFiアクセスポイントのSSIDとパスワードを設定。
- `APIKEY`にSesame APIアクセス用のAPIキーを設定。

# 使い方
ESP32-DevKitCのENボタンでセサミの解錠と施錠を行います。
- 解錠: ENボタン長押し
- 施錠: ENボタン短押し

