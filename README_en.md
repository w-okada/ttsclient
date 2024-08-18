TTSClient
---
  [[日本語]](./README.md) [[English]](./README_en.md) [[한국어]](./README_ko.md) [[中文简体]](./README_cn.md)


This is client software for Text To Speech (TTS).
We plan to support various AIs (currently, only GPT-SoVITS is supported).

- Supported AIs
  - [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)
  - coming soon...

## Related Software
- [Real-Time Voice Changer VCClient](https://github.com/w-okada/voice-changer)

## Download
Please download from the [Hugging Face repository](https://huggingface.co/wok000/ttsclient000/tree/main).

- win_std Edition: This is the edition for Windows that runs on a CPU. It is slower compared to the CUDA version, but should work on recent CPUs with decent specs.
- win_cuda Edition: This is the edition for Windows that runs on an NVIDIA GPU. It operates faster due to GPU hardware acceleration.
- mac Edition: This is the edition for Mac.

## Usage
- After extracting the zip file, execute `start_http.bat`. Then, access the displayed URL in a browser.
- Use `start_https.bat` to access the software remotely.
- (For advanced users) Use `start_http_with_ngrok.bat` to access the software via ngrok tunneling.

Note: For the mac edition, replace .bat with .command.

### GPT-SoVITS

For details about the model, please refer to the [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS) official repository.

In GPT-SoVITS, you select a model, a reference audio, and a reference text before generating speech. In TTSClient, there is a concept of a reference speaker, which can hold multiple reference audios and reference texts.

![image](https://github.com/user-attachments/assets/032a65ed-b9d5-4f8a-8efe-73bd10b66593)

#### Generating Speech

1. Select the model and reference speaker ((1), (2)).
2. Choose the reference audio and reference text registered to the reference speaker (3).
3. Input the text you want to generate speech for and create the voice output (4).

#### Registering a Model

Please register using the edit button in the model selection area.

#### Registering a Reference Speaker

You can register using the edit button in the reference speaker registration area.

#### Registering Reference Audio and Text

Select an unregistered slot in the reference audio selection area to register them.

## Acknowledgements
- [JVNV corpus](https://sites.google.com/site/shinnosuketakamichi/research-topics/jvnv_corpus)