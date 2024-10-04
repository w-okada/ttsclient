import logging
import traceback
from fastapi import APIRouter, HTTPException, Response

# from fastapi.responses import StreamingResponse

from ttsclient.const import LOGGER_NAME, UPLOAD_DIR
from ttsclient.server.validation_error_logging_route import ValidationErrorLoggingRoute
from ttsclient.tts.data_types.slot_manager_data_types import MoveModelParam, ReferenceVoice, ReferenceVoiceImportParam, SetIconParam, VoiceCharacter, VoiceCharacterImportParam
from ttsclient.tts.voice_character_slot_manager.voice_character_slot_manager import VoiceCharacterSlotManager


class RestAPIVoiceCharacterSlotManager:
    def __init__(self):
        self.router = APIRouter()
        self.router.route_class = ValidationErrorLoggingRoute
        self.router.add_api_route("/api/voice-character-slot-manager/slots", self.get_slots, methods=["GET"])
        self.router.add_api_route("/api/voice-character-slot-manager/slots/{index}", self.get_slot, methods=["GET"])
        self.router.add_api_route("/api/voice-character-slot-manager/slots", self.post_slot, methods=["POST"])
        self.router.add_api_route("/api/voice-character-slot-manager/slots/{index}", self.put_slot_info, methods=["PUT"])
        self.router.add_api_route("/api/voice-character-slot-manager/slots/{index}", self.delete_slot_info, methods=["DELETE"])
        self.router.add_api_route("/api/voice-character-slot-manager/slots/operation/move_model", self.post_move_model, methods=["POST"])
        self.router.add_api_route("/api/voice-character-slot-manager/slots/{index}/operation/set_icon_file", self.post_set_icon_file, methods=["POST"])

        self.router.add_api_route("/api/voice-character-slot-manager/slots/{index}/voices", self.post_voice, methods=["POST"])
        self.router.add_api_route("/api/voice-character-slot-manager/slots/{index}/voices/{voice_index}", self.put_voice, methods=["PUT"])
        self.router.add_api_route("/api/voice-character-slot-manager/slots/{index}/voices/{voice_index}", self.delete_voice, methods=["DELETE"])
        self.router.add_api_route("/api/voice-character-slot-manager/slots/{index}/voices/operation/move_voice", self.post_move_voice, methods=["POST"])
        self.router.add_api_route("/api/voice-character-slot-manager/slots/{index}/voices/operation/zip_and_download", self.post_zip_and_download, methods=["POST"])
        self.router.add_api_route("/api/voice-character-slot-manager/slots/{index}/voices/{voice_index}/operation/set_icon_file", self.post_set_voice_icon_file, methods=["POST"])

        # {index}_voices_operation_set_icon_fileと{index}_operation_set_icon_fileが混同されないように、長い方を先に登録する。
        self.router.add_api_route("/api_voice-character-slot-manager_slots_{index}_voices", self.post_voice, methods=["POST"])
        self.router.add_api_route("/api_voice-character-slot-manager_slots_{index}_voices_{voice_index}", self.put_voice, methods=["PUT"])
        self.router.add_api_route("/api_voice-character-slot-manager_slots_{index}_voices_{voice_index}", self.delete_voice, methods=["DELETE"])
        self.router.add_api_route("/api_voice-character-slot-manager_slots_{index}_voices_operation_move_voice", self.post_move_voice, methods=["POST"])
        self.router.add_api_route("/api_voice-character-slot-manager_slots_{index}_voices_operation_zip_and_download", self.post_zip_and_download, methods=["POST"])
        self.router.add_api_route("/api_voice-character-slot-manager_slots_{index}_voices_{voice_index}_operation_set_icon_file", self.post_set_voice_icon_file, methods=["POST"])

        self.router.add_api_route("/api_voice-character-slot-manager_slots", self.get_slots, methods=["GET"])
        self.router.add_api_route("/api_voice-character-slot-manager_slots_{index}", self.get_slot, methods=["GET"])
        self.router.add_api_route("/api_voice-character-slot-manager_slots", self.post_slot, methods=["POST"])
        self.router.add_api_route("/api_voice-character-slot-manager_slots_{index}", self.put_slot_info, methods=["PUT"])
        self.router.add_api_route("/api_voice-character-slot-manager_slots_{index}", self.delete_slot_info, methods=["DELETE"])
        self.router.add_api_route("/api_voice-character-slot-manager_slots_operation_move_model", self.post_move_model, methods=["POST"])
        self.router.add_api_route("/api_voice-character-slot-manager_slots_{index}_operation_set_icon_file", self.post_set_icon_file, methods=["POST"])

    def get_slots(self, reload: bool = False):
        slot_manager = VoiceCharacterSlotManager.get_instance()
        if reload:
            slot_manager.reload()
        slots = slot_manager.get_slot_infos()
        return slots

    def get_slot(self, index: int, reload: bool = False):
        slot_manager = VoiceCharacterSlotManager.get_instance()
        if reload:
            slot_manager.reload()
        slot = slot_manager.get_slot_info(index)
        return slot

    def post_slot(self, import_param: VoiceCharacterImportParam):
        try:
            slot_manager = VoiceCharacterSlotManager.get_instance()
            if import_param.zip_file is not None:
                import_param.zip_file = UPLOAD_DIR / import_param.zip_file
            slot_manager.set_new_slot(import_param, remove_src=True)
        except Exception as e:
            logging.getLogger(LOGGER_NAME).error(f"Failed to set_new_slot: {e}")
            logging.getLogger(LOGGER_NAME).error(f"Failed to set_new_slot: {traceback.format_exc()}")
            raise HTTPException(status_code=400, detail=str(e))

    def post_set_icon_file(self, index: int, param: SetIconParam):
        param.icon_file = UPLOAD_DIR / param.icon_file.name
        slot_manager = VoiceCharacterSlotManager.get_instance()
        slot_manager.set_icon_file(index, param)

    def put_slot_info(self, index: int, slot_info: VoiceCharacter):
        slot_manager = VoiceCharacterSlotManager.get_instance()
        slot_manager.update_slot_info(slot_info)

    def delete_slot_info(self, index: int):
        slot_manager = VoiceCharacterSlotManager.get_instance()
        slot_manager.delete_slot(index)

    def post_move_model(self, param: MoveModelParam):
        slot_manager = VoiceCharacterSlotManager.get_instance()
        slot_manager.move_model_slot(param)

    def post_zip_and_download(self, index: int):
        slot_manager = VoiceCharacterSlotManager.get_instance()
        name, buffer = slot_manager.zip_and_download(index)
        # print("zip returing..")

        # ストリームで返す方が遅い。なぜだ？？？
        # return StreamingResponse(buffer, media_type="application/zip", headers={"Content-Disposition": f"attachment; filename={name}.zip"})

        # バッファの内容を全て読み込んでファイルとして返す。
        file_content = buffer.read()
        headers = {"Content-Disposition": f"attachment; filename={name}.zip"}
        return Response(content=file_content, media_type="application/zip", headers=headers)

    def post_voice(self, index: int, reference_voice_import_params: ReferenceVoiceImportParam):
        slot_manager = VoiceCharacterSlotManager.get_instance()
        reference_voice_import_params.wav_file = UPLOAD_DIR / reference_voice_import_params.wav_file.name
        if reference_voice_import_params.icon_file is not None:
            reference_voice_import_params.icon_file = UPLOAD_DIR / reference_voice_import_params.icon_file.name

        slot_manager.add_voice_audio(index, reference_voice_import_params, remove_src=True)

    # colabで二つパスパラメータをとれないので。voice_indexはパラメータとする。  ★1 ⇒ルータへの登録順序で解決。。。
    def delete_voice(self, index: int, voice_index: int):
        slot_manager = VoiceCharacterSlotManager.get_instance()
        slot_manager.delete_voice_audio(index, voice_index)

    # おなじ ★1 ⇒ルータへの登録順序で解決。。。
    def put_voice(self, index: int, voice_index: int, reference_voice: ReferenceVoice):
        slot_manager = VoiceCharacterSlotManager.get_instance()
        slot_manager.update_voice_audio(index, voice_index, reference_voice)

    def post_move_voice(self, index: int, param: MoveModelParam):
        slot_manager = VoiceCharacterSlotManager.get_instance()
        slot_manager.move_voice_audio(index, param)

    # おなじ ★1
    def post_set_voice_icon_file(self, index: int, voice_index: int, param: SetIconParam):
        param.icon_file = UPLOAD_DIR / param.icon_file.name
        slot_manager = VoiceCharacterSlotManager.get_instance()
        slot_manager.set_voice_icon_file(index, voice_index, param)
