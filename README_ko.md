TTSClient
---
  [[日本語]](./README.md) [[English]](./README_en.md) [[한국어]](./README_ko.md) [[中文简体](./README_cn.md)

Text To Speech(TTS) 클라이언트 소프트웨어입니다.
각종 AI에 대응할 계획입니다. (현재는 GPT-SoVITS만 지원합니다)

- 지원 AI
  - [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)
  - coming soon...

# 다운로드
[Hugging Face 리포지토리](https://huggingface.co/wok000/ttsclient000/tree/main)에서 다운로드해주세요.

- win_std 에디션: Windows용 CPU에서 동작하는 에디션입니다. cuda 버전과 비교하여 속도가 느리지만, 최근 사양의 CPU라면 동작합니다.
- win_cuda 에디션: Windows용 NVIDIA GPU에서 동작하는 에디션입니다. GPU 하드웨어 가속을 통해 빠르게 작동합니다.
- mac 에디션: Mac용 에디션입니다.

# 사용 방법
- zip 파일을 해제한 후, `start_http.bat`을 실행하십시오. 표시된 URL에 브라우저로 접근하십시오.
- `start_https.bat`을 사용하면 원격에서도 접근할 수 있습니다.
- (상급자용)`start_http_with_ngrok.bat`을 사용하면 ngrok을 이용한 터널링으로 접근할 수 있습니다.

note: mac 에디션은 .bat 파일을 .command 파일로 읽어주세요.

## GPT-SoVITS

모델의 자세한 사항은 [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS) 공식 리포지토리를 참조하십시오.

GPT-SoVITS에서는 모델과 참조 음성 및 참조 텍스트를 선택한 후, 음성을 생성합니다. TTSClient에서는 참조 화자라는 개념이 있으며, 참조 화자는 여러 참조 음성과 참조 텍스트를 가질 수 있습니다.

![image](https://github.com/user-attachments/assets/032a65ed-b9d5-4f8a-8efe-73bd10b66593)

### 음성 생성

1. 모델과 참조 화자를 선택합니다((1), (2)).
2. 참조 화자에 등록된 참조 음성 및 참조 텍스트를 선택합니다(3).
3. 생성하고 싶은 텍스트를 입력하여 음성을 생성합니다(4).

### 모델 등록

모델 선택 영역의 편집 버튼을 통해 등록하십시오.

### 참조 화자 등록

참조 화자 등록 영역의 편집 버튼을 통해 등록하십시오.

### 참조 음성, 텍스트 등록

참조 음성 선택 영역에서 미등록 슬롯을 선택하여 등록하십시오.

# Acknowledgements
- [JVNV corpus](https://sites.google.com/site/shinnosuketakamichi/research-topics/jvnv_corpus)