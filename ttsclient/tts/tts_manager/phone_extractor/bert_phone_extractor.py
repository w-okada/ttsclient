from pathlib import Path
import re

import torch
from ttsclient.tts.tts_manager.device_manager.device_manager import DeviceManager
from ttsclient.tts.tts_manager.phone_extractor.phone_extractor import PhoneExtractor
from transformers import AutoModelForMaskedLM, AutoTokenizer

from ttsclient.tts.tts_manager.phone_extractor.phone_extractor_info import PhoneExtractorInfo
import LangSegment
from ttsclient.tts.tts_manager.text import chinese, cleaned_text_to_sequence
from ttsclient.tts.tts_manager.text.cleaner import clean_text


class BertPhoneExtractor(PhoneExtractor):
    def __init__(self, model_path: Path, device_id: int):
        self.device = DeviceManager.get_instance().get_pytorch_device(device_id)
        self.is_half = DeviceManager.get_instance().half_precision_available(device_id)
        self.dtype = torch.float16 if self.is_half is True else torch.float32

        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.bert_model = AutoModelForMaskedLM.from_pretrained(model_path)
        if self.is_half is True:
            # self.tokenizer = self.tokenizer.half()
            self.bert_model = self.bert_model.half()
        # self.tokenizer = self.tokenizer.to(self.device)
        self.bert_model = self.bert_model.to(self.device)
        # self.tokenizer.eval()
        self.bert_model.eval()

        self.info = PhoneExtractorInfo(
            path=model_path,
            phone_extractor_type="BertPhoneExtractor",
        )

    def get_info(self) -> PhoneExtractorInfo:
        return self.info

    def _get_bert_feature(self, text, word2ph):
        with torch.no_grad():
            inputs = self.tokenizer(text, return_tensors="pt")
            for i in inputs:
                inputs[i] = inputs[i].to(self.device)
            res = self.bert_model(**inputs, output_hidden_states=True)
            res = torch.cat(res["hidden_states"][-3:-2], -1)[0].cpu()[1:-1]
        assert len(word2ph) == len(text)
        phone_level_feature = []
        for i in range(len(word2ph)):
            repeat_feature = res[i].repeat(word2ph[i], 1)
            phone_level_feature.append(repeat_feature)
        phone_level_feature = torch.cat(phone_level_feature, dim=0)
        return phone_level_feature.T

    def _clean_text_inf(self, text, language, version):
        phones, word2ph, norm_text = clean_text(text, language, version)
        # print("phones1:", phones)
        phones = cleaned_text_to_sequence(phones, version)
        # print("phones2:", phones) # 音素のシンボル列を数値(インデックス)の列に置き換えてる。

        return phones, word2ph, norm_text

    def _get_bert_inf(self, phones, word2ph, norm_text, language):
        language = language.replace("all_", "")
        if language == "zh":
            bert = self._get_bert_feature(norm_text, word2ph).to(self.device)  # .to(dtype)
        else:
            bert = torch.zeros(
                (1024, len(phones)),
                dtype=torch.float16 if self.is_half is True else torch.float32,
            ).to(self.device)

        return bert

    def get_phones_and_bert(self, text, language, version, final=False):
        if language in {"en", "all_zh", "all_ja", "all_ko", "all_yue"}:
            language = language.replace("all_", "")
            if language == "en":
                LangSegment.setfilters(["en"])
                formattext = " ".join(tmp["text"] for tmp in LangSegment.getTexts(text))
            else:
                # 因无法区别中日韩文汉字,以用户输入为准
                formattext = text
            while "  " in formattext:
                formattext = formattext.replace("  ", " ")
            if language == "zh":
                if re.search(r"[A-Za-z]", formattext):
                    formattext = re.sub(r"[a-z]", lambda x: x.group(0).upper(), formattext)
                    formattext = chinese.mix_text_normalize(formattext)
                    return self.get_phones_and_bert(formattext, "zh", version)
                else:
                    phones, word2ph, norm_text = self._clean_text_inf(formattext, language, version)
                    bert = self._get_bert_feature(norm_text, word2ph).to(self.device)
            elif language == "yue" and re.search(r"[A-Za-z]", formattext):
                formattext = re.sub(r"[a-z]", lambda x: x.group(0).upper(), formattext)
                formattext = chinese.mix_text_normalize(formattext)
                return self.get_phones_and_bert(formattext, "yue", version)
            else:
                phones, word2ph, norm_text = self._clean_text_inf(formattext, language, version)

                bert = torch.zeros(
                    (1024, len(phones)),
                    dtype=torch.float16 if self.is_half is True else torch.float32,
                ).to(
                    self.device
                )  # 日本語はbertを使っていない。
        elif language in {"zh", "ja", "ko", "yue", "auto", "auto_yue"}:
            # mixのjaはbertを使っているかもしれない。
            textlist = []
            langlist = []
            LangSegment.setfilters(["zh", "ja", "en", "ko"])
            if language == "auto":
                for tmp in LangSegment.getTexts(text):
                    langlist.append(tmp["lang"])
                    textlist.append(tmp["text"])
            elif language == "auto_yue":
                for tmp in LangSegment.getTexts(text):
                    if tmp["lang"] == "zh":
                        tmp["lang"] = "yue"
                    langlist.append(tmp["lang"])
                    textlist.append(tmp["text"])
            else:
                for tmp in LangSegment.getTexts(text):
                    if tmp["lang"] == "en":
                        langlist.append(tmp["lang"])
                    else:
                        # 因无法区别中日韩文汉字,以用户输入为准
                        langlist.append(language)
                    textlist.append(tmp["text"])
            print(textlist)
            print(langlist)
            phones_list = []
            bert_list = []
            norm_text_list = []
            for i in range(len(textlist)):
                lang = langlist[i]
                phones, word2ph, norm_text = self._clean_text_inf(textlist[i], lang, version)
                bert = self._get_bert_inf(phones, word2ph, norm_text, lang)
                phones_list.append(phones)
                norm_text_list.append(norm_text)
                bert_list.append(bert)
            bert = torch.cat(bert_list, dim=1)
            phones = sum(phones_list, [])
            norm_text = "".join(norm_text_list)

        if not final and len(phones) < 6:
            return self.get_phones_and_bert("." + text, language, version, final=True)

        return phones, bert.to(self.dtype), norm_text
