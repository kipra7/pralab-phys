# pralab-phys 0.4.0

Pralab-phys provides some extensions of QCoDes (python-based data acquisition framework) and Plotly and more.

Especially, it includes following QCoDes Instrument Drivers

- Keithley2182A
- Keithley6221
- Yokogawa7651
- Quantum Design Instruments (PPMS, Dynacool)

### Attention: 
For versions below 0.3.11, we **strongly discourage usage** due to instability in versioning and other concerns.


# pralab-phys 0.4.0 日本語解説

## 概要
本ライブラリは、物性研究室で用いることを想定した、QCoDesをベースとした測定用ライブラリであり、これを用いることで、様々な計測器制御や測定プログラムの作成が容易に行えます。

このライブラリは、QCoDesを中心としたライブラリの拡張ドライバとして、以下の機能を提供します。

QCoDesの基本的な使い方については、[公式ドキュメント](https://microsoft.github.io/Qcodes/)またはqiita記事をご覧ください。

### 各計測器の制御用ライブラリ
- Keithley2182A Nanovoltmeter
- keithley6221 DC and AC Current Source
- Yokogawa7651 電流源
- エヌエフ LI5650 ロックインアンプ
- Quantum Design Multivu経由の装置制御（QDInstrument.dll必須）
- M81 (予定)

### より平易なリアルタイムプロット機能
- RealtimePlotモジュールによる、Jupyter上での測定結果確認


## インストール&最初の利用
本ライブラリは、uvを用いたPython仮想環境上へのインストールを推奨しています。

Windows Powershellを用いたインストール手順は以下の通りです。

1. 仮想環境を作成したいディレクトリ上で以下のコードを入力（任意の仮想環境名を入力しない場合、該当ディレクトリにそのまま仮想環境が構築されます）

```
uv init <任意の仮想環境名>
```

2. pralab-physライブラリのインストール

```
uv add pralab-phys
```

3. jupyter labを起動する。自動的にブラウザが開き、Jupyter Labが使える状態になる。

```
uv run jupyter lab
```

もしブラウザが開かない場合、Powershell上に出力されたリンク(localhost:9999など)をブラウザに入力する。

Jupyter Labを終了する場合、Powershell上でctrl+cを入力。

