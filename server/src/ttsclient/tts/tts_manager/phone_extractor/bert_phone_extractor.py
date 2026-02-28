from pathlib import Path
import re
import os
import pyopenjtalk
import torch

# from inference_webui import get_phones_and_bert as get_phones_and_bert_webui
from text import chinese
from text.cleaner import clean_text, cleaned_text_to_sequence
from text.LangSegmenter.langsegmenter import LangSegmenter
from transformers import AutoModelForMaskedLM, AutoTokenizer

from ttsclient.services.module_manager import ModuleManager
from ttsclient.tts.tts_manager.device_manager.device_manager import DeviceManager
from ttsclient.tts.tts_manager.phone_extractor.phone_extractor import PhoneExtractor
from ttsclient.tts.tts_manager.phone_extractor.phone_extractor_info import PhoneExtractorInfo


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
        os.environ["bert_path"] = str(model_path)

    def get_info(self) -> PhoneExtractorInfo:
        return self.info

    def phone_symbols_to_sequence_and_bert(self, cleaned_text, version):
        phones = cleaned_text_to_sequence(cleaned_text, version)
        bert = torch.zeros(
            (1024, len(phones)),
            dtype=torch.float16 if self.is_half == True else torch.float32,
        ).to(self.device)

        return phones, bert

    # GPT-SoVITSからコピー
    def __clean_text_inf(self, text, language, version, is_reference_voice: bool = True):
        language = language.replace("all_", "")
        phones, word2ph, norm_text = clean_text(text, language, version)
        # print("phones1:", phones, "word2ph:", word2ph, "norm_text:", norm_text)
        # phones = ["a", "[", "a", "?", "d", "o", "[", "o", "]", "sh", "i", "t", "e", "#", "k", "o", "[", "N", "]", "n", "a", "[", "n", "i", "#", "a", "[", "r", "a", "a", "r", "a", "sh", "i", "]", "i", "#", "t", "a", "[", "i", "d", "o", "]", "o", "#", "t", "o", "]", "r", "u", "#", "N", "[", "d", "a", "?", "o", "[", "ch", "i", "ts", "u", "i", "t", "e", "#", "h", "a", "[", "n", "a", "sh", "i", "]", "o", "#", "k", "i", "[", "k", "e", "]", "b", "a", "#", "i", "]", "i", "#", "n", "o", "[", "n", "i", "."]
        # phones = ["a", "]", "a", "?", "d", "o", "]", "o", "sh", "i", "t", "o", "[", "r", "u", "#", "k", "o", "[", "N", "n", "a", "n", "[", "y", "a", "#", "a", "[", "r", "a", "a", "r", "a", "sh", "i", "]", "i", "#", "t", "a", "]", "i", "d", "[", "o", "o", "#", "t", "o", "]", "r", "u", "#", "N", "]", "y", "a", "?", "o", "[", "ch", "i", "ts", "u", "i", "t", "e", "#", "h", "a", "[", "n", "a", "sh", "i", "]", "o", "#", "k", "i", "[", "k", "e", "]", "b", "a", "#", "e", "e", "]", "i", "#", "n", "o", "[", "n", "i", "."]
        # phones = ["a", "]", "a", "?", "d", "o", "[", "o", "sh", "i", "t", "e", "#", "k", "o", "]", "N", "n", "a", "[", "n", "i", "#", "a", "]", "r", "a", "a", "r", "a", "sh", "[", "i", "#", "t", "a", "[", "i", "d", "o", "o", "#", "t", "o", "]", "r", "u", "#", "N", "[", "d", "a", "?", "o", "]", "ch", "i", "ts", "u", "i", "t", "e", "#", "h", "a", "]", "n", "a", "[", "sh", "i", "o", "#", "k", "i", "]", "k", "e", "[", "b", "a", "#", "i", "[", "i", "#", "n", "o", "]", "n", "i", "."]
        # phones = ["s", "a", "[", "N", "sh", "o", "o", "o", "]", "N", "s", "e", "e", "w", "a", "n", "a", "i", "t", "o", "#", "i", "[", "k", "e", "n", "a", "i", "#", "n", "o", "[", "d", "a", "."]
        # from text import symbols2 as symbols_v2

        # symbols = symbols_v2.symbols
        # phones = ["UNK" if ph not in symbols else ph for ph in phones]

        # if is_reference_voice is False:
        #     # phones = self.convert_to_kansai_accent(phones)
        #     phones = ["s", "a", "N", "sh", "o", "o", "o", "N", "s", "e", "e", "w", "a", "n", "a", "i", "t", "o", "UNK", "i", "_", "]", "k", "e", "]", "n", "a", "i", "UNK", "n", "o", "]", "d", "a", "."]
        # # print("phones2:", phones, "word2ph:", word2ph, "norm_text:", norm_text)

        phones_sequence = cleaned_text_to_sequence(phones, version)
        # print("phones3:", phones)
        return phones_sequence, phones, word2ph, norm_text

    def __get_bert_feature(self, text, word2ph):
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

    def __get_bert_inf(self, phones, word2ph, norm_text, language):
        language = language.replace("all_", "")
        if language == "zh":
            bert = self.__get_bert_feature(norm_text, word2ph).to(self.device)  # .to(dtype)
        else:
            bert = torch.zeros(
                (1024, len(phones)),
                dtype=torch.float16 if self.is_half == True else torch.float32,
            ).to(self.device)

        return bert

    def get_phones_and_bert(self, text, language, version, final=False, is_reference_voice: bool = True):

        # G2PWModelのダウンロード
        if language in {"zh", "all_zh"}:
            import os
            import zipfile

            module_manager = ModuleManager.get_instance()
            modules = module_manager.get_modules()
            G2PWModel_zip = [x for x in modules if x.info.id == "chinese-roberta-wwm-ext-large_G2PWModel_1.1.zip"][0]
            model_dir = "GPT_SoVITS/text/G2PWModel"
            if os.path.exists(model_dir) is False:
                if G2PWModel_zip.valid is False:
                    module_manager.download("chinese-roberta-wwm-ext-large_G2PWModel_1.1.zip", lambda _: None)

                parent_directory = os.path.dirname(model_dir)
                zip_dir = os.path.join(parent_directory, "G2PWModel_1.1.zip")
                extract_dir = os.path.join(parent_directory, "G2PWModel_1.1")
                extract_dir_new = os.path.join(parent_directory, "G2PWModel")
                print("Extracting g2pw model...")
                with zipfile.ZipFile(zip_dir, "r") as zip_ref:
                    zip_ref.extractall(parent_directory)

                os.rename(extract_dir, extract_dir_new)

        # 実処理
        if language in {"en", "all_zh", "all_ja", "all_ko", "all_yue"}:
            formattext = text
            while "  " in formattext:
                formattext = formattext.replace("  ", " ")
            if language == "all_zh":
                if re.search(r"[A-Za-z]", formattext):
                    formattext = re.sub(r"[a-z]", lambda x: x.group(0).upper(), formattext)
                    formattext = chinese.mix_text_normalize(formattext)
                    return self.get_phones_and_bert(formattext, "zh", version)
                else:
                    phones_sequence, phones, word2ph, norm_text = self.__clean_text_inf(formattext, language, version, is_reference_voice=is_reference_voice)
                    bert = self.__get_bert_feature(norm_text, word2ph).to(self.device)
            elif language == "all_yue" and re.search(r"[A-Za-z]", formattext):
                formattext = re.sub(r"[a-z]", lambda x: x.group(0).upper(), formattext)
                formattext = chinese.mix_text_normalize(formattext)
                return self.get_phones_and_bert(formattext, "yue", version)
            else:
                phones_sequence, phones, word2ph, norm_text = self.__clean_text_inf(formattext, language, version, is_reference_voice=is_reference_voice)
                bert = torch.zeros(
                    (1024, len(phones_sequence)),
                    dtype=torch.float16 if self.is_half == True else torch.float32,
                ).to(self.device)
        elif language in {"zh", "ja", "ko", "yue", "auto", "auto_yue"}:
            textlist = []
            langlist = []
            if language == "auto":
                for tmp in LangSegmenter.getTexts(text):
                    langlist.append(tmp["lang"])
                    textlist.append(tmp["text"])
            elif language == "auto_yue":
                for tmp in LangSegmenter.getTexts(text):
                    if tmp["lang"] == "zh":
                        tmp["lang"] = "yue"
                    langlist.append(tmp["lang"])
                    textlist.append(tmp["text"])
            else:
                for tmp in LangSegmenter.getTexts(text):
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
                phones_sequence, phones, word2ph, norm_text = self.__clean_text_inf(textlist[i], lang, version, is_reference_voice=is_reference_voice)
                bert = self.__get_bert_inf(phones_sequence, word2ph, norm_text, lang)
                phones_list.append(phones_sequence)
                norm_text_list.append(norm_text)
                bert_list.append(bert)
            bert = torch.cat(bert_list, dim=1)
            phones_sequence = sum(phones_list, [])
            norm_text = "".join(norm_text_list)

        if not final and len(phones_sequence) < 6:
            return self.get_phones_and_bert("." + text, language, version, final=True)

        return phones_sequence, bert.to(self.dtype), norm_text, phones
