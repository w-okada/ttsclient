TTSClient
---
  [[日本語]](./README.md) [[English]](./README_en.md) [[한국어]](./README_ko.md) [[中文简体]](./README_cn.md)

这是一个文本转语音（TTS）的客户端软件。
计划支持各种AI。（目前仅支持GPT-SoVITS）

- 支持的AI
  - [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)
  - 敬请期待...

## 相关软件
- [实时语音变换器 VCClient](https://github.com/w-okada/voice-changer)

## 下载
请从[Hugging Face的仓库](https://huggingface.co/wok000/ttsclient000/tree/main)下载。

- win_std版：适用于Windows的版本，运行在CPU上。虽然比cuda版慢，但在现代规格较高的CPU上也可以运行。
- win_cuda版：适用于Windows的版本，运行在NVIDIA的GPU上。利用GPU硬件加速，可以快速运行。
- mac版：适用于Mac的版本。

## 使用方法
- 解压缩文件后，运行`start_http.bat`。在浏览器中访问显示的URL。
- 使用`start_https.bat`可以从远程访问。
- （高级用户）使用`start_http_with_ngrok.bat`可以通过ngrok隧道进行访问。

注意：mac版请将.bat替换为.command。

### GPT-SoVITS

有关模型的详细信息，请参考[GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)的官方仓库。

在GPT-SoVITS中，选择模型、参考音频和参考文本后，进行语音生成。在TTSClient中，有参考说话人的概念，可以给参考说话人设置多个参考音频和参考文本。

![image](https://github.com/user-attachments/assets/032a65ed-b9d5-4f8a-8efe-73bd10b66593)

#### 生成语音

1. 选择模型和参考说话人((1), (2))。
2. 从参考说话人已注册的参考音频和参考文本中选择(3)。
3. 输入想要生成的文本并生成语音(4)。

#### 注册模型

请通过编辑按钮从模型选择区域进行注册。

#### 注册参考说话人

请通过编辑按钮从参考说话人注册区域进行注册。

#### 注册参考音频和文本

在参考音频选择区域选择未注册的插槽进行注册。


## Acknowledgements
- [JVNV corpus](https://sites.google.com/site/shinnosuketakamichi/research-topics/jvnv_corpus)