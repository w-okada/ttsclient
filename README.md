TTSClient
---
[日本語](./README.md) [English](./README_en.md) [한국어](./README_ko.md) [中文简体](./README_cn.md)

Text To Speech(TTS)のクライアントソフトウェアです。
各種AIに対応していく計画です。(現時点ではGPT-SoVITSのみ)

- 対応 AI
  - [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)
  - coming soon...

# ダウンロード
[Hugging Faceのリポジトリ](https://huggingface.co/wok000/ttsclient000/tree/main)よりダウンロードしてください。

- win_stdエディション：Windows向けのCPUで動作するエディションです。cuda版と比較して低速ですが、最近のそれなりのスペックのCPUであれば動きます。
- win_cudaエディション：Windows向けのNVIDIAのGPUで動作するエディションです。GPUのハードウェアアクセラレーションにより高速に動きます。
- macエディション：Mac向けのエディションです。

# 使用方法
- zipファイルを展開後、`start_http.bat`を実行してください。表示された、URLにブラウザでアクセスしてください。
- `start_https.bat`を使用すると、リモートからでもアクセスすることができます。
- (上級者向け)`start_http_with_ngrok.bat`を使用するとngrokを用いたトンネリングを使用してアクセスすることができます。

note: macエディションは.batを.commandで読み替えてください。

## GPT-SoVITS

モデルの詳細は[GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)の公式リポジトリを参照してください。

GPT-SoVITSでは、モデルと参照音声と参照テキストを選択してから、音声生成を行います。TTSClientでは参照話者という概念があり、参照話者に複数の参照音声と参照テキストを持たせることができます。

![image](https://github.com/user-attachments/assets/032a65ed-b9d5-4f8a-8efe-73bd10b66593)

### 音声生成

1. モデルと、参照話者を選択します((1), (2))。
2. 参照話者に登録された参照音声と参照テキストを選択します(3)。
3. 生成したいテキストを入力して音声を生成します(4)。

### モデルの登録

モデル選択エリアの編集ボタンから登録してください。

### 参照話者の登録

参照話者登録エリアの編集ボタンから登録してください。

### 参照音声、テキストの登録

参照音声選択エリアで未登録のスロットを選択して登録してください。

# Acknowledgements
- [JVNVコーパス](https://sites.google.com/site/shinnosuketakamichi/research-topics/jvnv_corpus)

