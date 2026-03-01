import logging
import os
import datetime
from pathlib import Path
import pyopenjtalk
from ttsclient.const import GPT_SOVITS_USER_DICT_PATH, LOGGER_NAME, OPENJTALK_USER_DICT_CSV_FILE, OPENJTALK_USER_DICT_FILE, OPENJTALK_USER_DICT_TEMP_CSV_FILE, ModelDir, VoiceCharacterDir
from ttsclient.services.configuration_manager import ConfigurationManager
from ttsclient.models.tts import GenerateVoiceParam, GetPhonesParam, GetJpTextToUserDictRecordsParam, OpenJTalkUserDictRecord
from ttsclient.services.slot_manager import SlotManager
from ttsclient.tts.tts_manager.pipeline.pipline_manager import PipelineManager
from ttsclient.services.voice_character_slot_manager import VoiceCharacterSlotManager
import hashlib


class TTSManager:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:

            cls._instance = cls()
            return cls._instance

        return cls._instance

    def __init__(self):
        self.loaded_model_slot_id = -1
        self.pipeline = None
        self.backend_mode = None

        self.current_voice_character_slot_index = -1
        self.current_voice_character_user_dict_hash = ""
        self.current_voice_character_user_dict_tmp_hash = ""

    def load_model(self, slot_id: int):
        self.loaded_model_slot_id = slot_id
        slot_manager = SlotManager.get_instance()
        slot_info = slot_manager.get_slot_info(slot_id)
        if slot_info is None:
            raise ValueError(f"Slot {slot_id} not found. Please check the slot configuration.")
        self.pipeline = PipelineManager.get_pipeline(slot_info)
        self.use_faster = slot_info.enable_faster
        self.backend_mode = slot_info.backend_mode

    def stop_tts(self):
        if self.pipeline is not None:
            self.pipeline.force_stop()

    def jp_text_to_user_dict_records(self, param: GetJpTextToUserDictRecordsParam):
        self.check_and_load_voice_character_setting(param.voice_character_slot_index)

        words = pyopenjtalk.run_frontend(param.text)
        words = [word for word in words if word["pos"] != "記号"]
        # wordsの情報をuser dict形式で出力
        user_dict_records: list[OpenJTalkUserDictRecord] = []
        for word in words:
            record = OpenJTalkUserDictRecord(
                string=word["string"],
                pos=word["pos"],
                pos_group1=word["pos_group1"],
                pos_group2=word["pos_group2"],
                pos_group3=word["pos_group3"],
                ctype=word["ctype"],
                cform=word["cform"],
                orig=word["orig"],
                read=word["read"],
                pron=word["pron"],
                acc=word["acc"],
                mora_size=word["mora_size"],
                chain_rule=word["chain_rule"],
                chain_flag=word["chain_flag"],
            )
            user_dict_records.append(record)

        return user_dict_records

    # 下記で、run_frontendの処理が見れる。
    # import pyopenjtalk
    #
    # text = "こんにちは、世界。"
    # words = pyopenjtalk.run_frontend(text)
    # for word in words:
    #     print(word)
    # {'string': 'こんにちは', 'pos': '感動詞', 'pos_group1': '*', 'pos_group2': '*', 'pos_group3': '*', 'ctype': '*', 'cform': '*', 'orig': 'こんにちは', 'read': 'コンニチハ', 'pron': 'コンニチワ', 'acc': 0, 'mora_size': 5, 'chain_rule': '-1', 'chain_flag': -1}
    # {'string': '、', 'pos': '記号', 'pos_group1': '読点', 'pos_group2': '*', 'pos_group3': '*', 'ctype': '*', 'cform': '*', 'orig': '、', 'read': '、', 'pron': '、', 'acc': 0, 'mora_size': 0, 'chain_rule': '*', 'chain_flag': 0}
    # {'string': '世界', 'pos': '名詞', 'pos_group1': '一般', 'pos_group2': '*', 'pos_group3': '*', 'ctype': '*', 'cform': '*', 'orig': '世界', 'read': 'セカイ', 'pron': 'セカイ', 'acc': 1, 'mora_size': 3, 'chain_rule': 'C1', 'chain_flag': 0}
    # {'string': '。', 'pos': '記号', 'pos_group1': '句点', 'pos_group2': '*', 'pos_group3': '*', 'ctype': '*', 'cform': '*', 'orig': '。', 'read': '、', 'pron': '、', 'acc': 0, 'mora_size': 0, 'chain_rule': '*', 'chain_flag': 0}

    def check_and_load_model(self):
        conf = ConfigurationManager.get_instance().get_tts_configuration()
        slot_info = SlotManager.get_instance().get_slot_info(conf.current_slot_index)

        # Check
        exec_load = False
        if self.pipeline is None:
            exec_load = True
        elif self.loaded_model_slot_id != conf.current_slot_index:
            exec_load = True
        elif self.pipeline.gpu_device_id != conf.gpu_device_id_int:
            exec_load = True
        elif slot_info is None:
            exec_load = True
        elif slot_info.enable_faster != self.use_faster:
            exec_load = True
        elif self.backend_mode != slot_info.backend_mode:
            exec_load = True
        # print("self.backend_mode != slot_info.backend_mode:", self.backend_mode, slot_info.backend_mode)
        # Load
        if exec_load is True:
            self.load_model(conf.current_slot_index)

    def get_phones(self, get_phones_param: GetPhonesParam):

        # 一時ユーザ辞書のCSV作成
        user_dict_tmp_cvs_path = VoiceCharacterDir / f"{get_phones_param.voice_character_slot_index}" / OPENJTALK_USER_DICT_TEMP_CSV_FILE
        if get_phones_param.user_dict_records is not None and len(get_phones_param.user_dict_records) > 0:
            # user_dict_recordsを一時ファイルに保存
            with open(user_dict_tmp_cvs_path, "w", encoding="utf8") as f:
                for record in get_phones_param.user_dict_records:
                    entry = f"{record.string},*,*,-32768,{record.pos},{record.pos_group1},{record.pos_group2},{record.pos_group3},{record.ctype},{record.cform},{record.orig},{record.read},{record.pron},{record.acc}/{record.mora_size},{record.chain_rule}\n"
                    f.write(entry)
                    logging.getLogger(LOGGER_NAME).debug(f"temporary pronounce: {entry}")

        # ユーザ辞書アップデート
        self.check_and_load_voice_character_setting(get_phones_param.voice_character_slot_index)

        # 一時ユーザ辞書のCSV削除
        if os.path.exists(user_dict_tmp_cvs_path):
            user_dict_tmp_cvs_path.unlink()

        self.check_and_load_model()
        assert self.pipeline is not None, "Model is not loaded"

        # phonesを取得
        phones, bert, norm_text, phone_symbols = self.pipeline.get_phones(text=get_phones_param.text, language=get_phones_param.language)
        return phones, phone_symbols

    def check_and_load_voice_character_setting(self, voice_character_slot_index: int):
        # openjtalkの辞書 update
        need_user_dict_update = False
        voice_character_slot_dir = VoiceCharacterDir / f"{voice_character_slot_index}"
        user_dict_cvs_path = voice_character_slot_dir / OPENJTALK_USER_DICT_CSV_FILE
        user_dict_tmp_csv_path = voice_character_slot_dir / OPENJTALK_USER_DICT_TEMP_CSV_FILE

        user_dict_hash = ""
        user_dict_tmp_hash = ""

        # ハッシュ値取得. ファイルが存在しない場合はデフォルトの殻文字列のまま。
        if user_dict_cvs_path.exists():
            hash_md5 = hashlib.md5()
            with open(user_dict_cvs_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            user_dict_hash = hash_md5.hexdigest()

        if user_dict_tmp_csv_path.exists():
            hash_md5 = hashlib.md5()
            with open(user_dict_tmp_csv_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            user_dict_tmp_hash = hash_md5.hexdigest()

        # update要否チェック
        if self.current_voice_character_slot_index != voice_character_slot_index:
            self.current_voice_character_slot_index = voice_character_slot_index
            need_user_dict_update = True
        if self.current_voice_character_user_dict_hash != user_dict_hash:
            self.current_voice_character_user_dict_hash = user_dict_hash
            need_user_dict_update = True
        if self.current_voice_character_user_dict_tmp_hash != user_dict_tmp_hash:
            self.current_voice_character_user_dict_tmp_hash = user_dict_tmp_hash
            need_user_dict_update = True

        if need_user_dict_update:
            logging.getLogger(LOGGER_NAME).debug("user dict update")

            # 日付でタイムスタンプ文字列作成
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            # GPT-SoVITSのユーザ辞書と、VoiceCharacterのユーザ辞書と、テンポラリのユーザ辞書をマージ
            user_dict_merged_csv_path = voice_character_slot_dir / f"{OPENJTALK_USER_DICT_CSV_FILE}_{timestamp}"
            gpt_sovits_user_dict_path = Path(GPT_SOVITS_USER_DICT_PATH)

            with open(user_dict_merged_csv_path, "w", encoding="utf8") as f:
                if gpt_sovits_user_dict_path.exists():
                    with open(gpt_sovits_user_dict_path, "r", encoding="utf8") as f2:
                        f.write(f2.read())
                else:
                    print("gpt_sovits_user_dict_path not found", GPT_SOVITS_USER_DICT_PATH)
                # 改行を挿入
                f.write("\n")
                if user_dict_cvs_path.exists():
                    with open(user_dict_cvs_path, "r", encoding="utf8") as f2:
                        f.write(f2.read())
                if user_dict_tmp_csv_path.exists():
                    with open(user_dict_tmp_csv_path, "r", encoding="utf8") as f2:
                        f.write(f2.read())

            # user_dict_merged_csv_pathに空業があったら削除
            with open(user_dict_merged_csv_path, "r", encoding="utf8") as f:
                lines = f.readlines()
            with open(user_dict_merged_csv_path, "w", encoding="utf8") as f:
                for line in lines:
                    if line.strip() != "":
                        f.write(line)

            # ユーザ辞書の登録
            user_dict_path = voice_character_slot_dir / f"{OPENJTALK_USER_DICT_FILE}_{timestamp}"

            import builtins

            original_print = builtins.print

            def custom_print(*args, **kwargs):
                logging.getLogger(LOGGER_NAME).debug(" ".join(map(str, args)))
                # text = "[module] " + " ".join(map(str, args))
                # original_print(color_text(text, format="FAINT"), **kwargs)

            builtins.print = custom_print

            with open(os.devnull, "w") as devnull:
                # モジュールの標準出力を一時的に無効化。内部でprintしても表示されない(エラーになる)ので注意。
                # エラーが出たときはモジュール内でprintが使われていないか確認。使われていたら、出力抑制の方法を再検討。
                stdout_fd = os.dup(1)
                os.dup2(devnull.fileno(), 1)
                try:
                    pyopenjtalk.mecab_dict_index(str(user_dict_merged_csv_path), str(user_dict_path))
                    pyopenjtalk.update_global_jtalk_with_user_dict(str(user_dict_path))
                finally:
                    os.dup2(stdout_fd, 1)
                    os.close(stdout_fd)
                    pass

            builtins.print = original_print
            # 旧ファイル削除
            for p in voice_character_slot_dir.glob(f"{OPENJTALK_USER_DICT_FILE}_*"):
                if p != user_dict_path:
                    p.unlink()

            if user_dict_merged_csv_path.exists():
                user_dict_merged_csv_path.unlink()

    def run(self, generarte_voice_param: GenerateVoiceParam):
        conf = ConfigurationManager.get_instance().get_tts_configuration()

        slot_manager = SlotManager.get_instance()
        slot_info = slot_manager.get_slot_info(conf.current_slot_index)
        if slot_info is None:
            raise ValueError(f"Slot {conf.current_slot_index} not found. Please check the slot configuration.")
        self.check_and_load_model()

        self.check_and_load_voice_character_setting(generarte_voice_param.voice_character_slot_index)

        assert self.pipeline is not None, "Model is not loaded"

        voice_character_slot_manager = VoiceCharacterSlotManager.get_instance()
        voice_character = voice_character_slot_manager.get_slot_info(generarte_voice_param.voice_character_slot_index)
        reference_voices = [v for v in voice_character.reference_voices if v.slot_index == generarte_voice_param.reference_voice_slot_index]
        assert len(reference_voices) == 1, f"reference voice not found. voice_character_slot_index:{generarte_voice_param.voice_character_slot_index}, reference_voice_slot_index:{generarte_voice_param.reference_voice_slot_index}"
        reference_voice = reference_voices[0]

        slot_dir = VoiceCharacterDir / f"{generarte_voice_param.voice_character_slot_index}"

        ref_wav_path = slot_dir / f"{reference_voice.wav_file}"

        synthesis_result = self.pipeline.run(
            ref_wav_path=str(ref_wav_path),
            prompt_text=reference_voice.text,
            prompt_language=reference_voice.language,
            text=generarte_voice_param.text,
            text_language=generarte_voice_param.language,
            how_to_cut=generarte_voice_param.cutMethod,
            speed=generarte_voice_param.speed,
            # slot_infoからの入力
            top_k=slot_info.top_k,
            top_p=slot_info.top_p,
            temperature=slot_info.temperature,
            # faster用の入力
            batch_size=slot_info.batch_size,
            batch_threshold=slot_info.batch_threshold,
            split_bucket=slot_info.split_bucket,
            return_fragment=slot_info.return_fragment,
            fragment_interval=slot_info.fragment_interval,
            seed=slot_info.seed,
            parallel_infer=slot_info.parallel_infer,
            repetition_penalty=slot_info.repetition_penalty,
            # v3追加オプション
            sample_steps=generarte_voice_param.sample_steps if generarte_voice_param.sample_steps is not None else 8,
            phone_symbols=generarte_voice_param.phone_symbols,
        )
        last_sampling_rate, last_audio_data = synthesis_result

        return last_sampling_rate, last_audio_data
