import json
import logging
from pathlib import Path
import sys
import shutil
from typing import Any, Dict, Optional
from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import swagger_ui_default_parameters

from ttsclient.const import LOGGER_NAME, UPLOAD_DIR, ConfigFile, ModelDir, ModuleDir, VoiceCharacterDir
from ttsclient.server.fileuploader.fileuploader import EasyFileUploader
from ttsclient.server.tts_server_rest_api_configuration_manager import RestAPIConfigurationManager
from ttsclient.server.tts_server_rest_api_gpu_device_manager import RestAPIGPUDeviceManager
from ttsclient.server.tts_server_rest_api_hello import RestHello
from ttsclient.server.tts_server_rest_api_module_manager import RestAPIModuleManager
from ttsclient.server.tts_server_rest_api_slot_manager import RestAPISlotManager
from ttsclient.server.tts_server_rest_api_tts_manager import RestAPITTSManager
from ttsclient.server.tts_server_rest_api_voice_character_slot_manager import RestAPIVoiceCharacterSlotManager
from ttsclient.server.validation_error_logging_route import ValidationErrorLoggingRoute
from ttsclient.tts.configuration_manager.configuration_manager import ConfigurationManager
from ttsclient.tts.gpu_device_manager.gpu_device_manager import GPUDeviceManager
from ttsclient.tts.module_manager.module_manager import ModuleManager
from ttsclient.tts.slot_manager.slot_manager import SlotManager
from ttsclient.tts.voice_character_slot_manager.voice_character_slot_manager import VoiceCharacterSlotManager


# original is get_swagger_ui_html of fastapi.openapi.docs
def get_custom_swagger_ui_html(
    *,
    openapi_url: str,
    title: str,
    swagger_js_url: str = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
    swagger_css_url: str = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
    swagger_favicon_url: str = "https://fastapi.tiangolo.com/img/favicon.png",
    oauth2_redirect_url: Optional[str] = None,
    init_oauth: Optional[Dict[str, Any]] = None,
    swagger_ui_parameters: Optional[Dict[str, Any]] = None,
) -> HTMLResponse:

    current_swagger_ui_parameters = swagger_ui_default_parameters.copy()
    if swagger_ui_parameters:
        current_swagger_ui_parameters.update(swagger_ui_parameters)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <link type="text/css" rel="stylesheet" href="{swagger_css_url}">
    <link rel="shortcut icon" href="{swagger_favicon_url}">
    <title>{title}</title>
    </head>
    <body>
    <div style="color:red;font-weight: 600;">Note: API may be subject to change in the future.</div>
    <div id="swagger-ui">
    </div>
    <script src="{swagger_js_url}"></script>
    <!-- `SwaggerUIBundle` is now available on the page -->
    <script>
    const ui = SwaggerUIBundle({{
        url: '{openapi_url}',
    """

    for key, value in current_swagger_ui_parameters.items():
        html += f"{json.dumps(key)}: {json.dumps(jsonable_encoder(value))},\n"

    if oauth2_redirect_url:
        html += f"oauth2RedirectUrl: window.location.origin + '{oauth2_redirect_url}',"

    html += """
    presets: [
        SwaggerUIBundle.presets.apis,
        SwaggerUIBundle.SwaggerUIStandalonePreset
        ],
    })"""

    if init_oauth:
        html += f"""
        ui.initOAuth({json.dumps(jsonable_encoder(init_oauth))})
        """

    html += """
    </script>
    </body>
    </html>
    """
    return HTMLResponse(html)


class RestAPI:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            app_fastapi = FastAPI(title="VCClient REST API", docs_url=None, redoc_url=None)
            app_fastapi.router.route_class = ValidationErrorLoggingRoute

            # app_fastapi.router.add_api_route("/docs", get_custom_swagger_ui_html, methods=["GET"])
            @app_fastapi.get("/docs", include_in_schema=False)
            def custom_swagger_ui_html():
                logging.getLogger(LOGGER_NAME).info("CUSTOM UI")

                return get_custom_swagger_ui_html(
                    openapi_url=app_fastapi.openapi_url,
                    title="VCClient API Docs",
                )

            # app_fastapi.mount("/tmp", StaticFiles(directory=f"{TMP_DIR}"), name="static")
            # app_fastapi.mount("/upload_dir", StaticFiles(directory=f"{UPLOAD_DIR}"), name="static")

            if sys.platform.startswith("darwin"):
                app_fastapi.mount(
                    f"/{ModelDir}",
                    StaticFiles(directory=ModelDir),
                    name="static",
                )
            else:
                app_fastapi.mount(
                    f"/{ModelDir}",
                    StaticFiles(directory=ModelDir),
                    name="static",
                )
            app_fastapi.mount(
                f"/{VoiceCharacterDir}",
                StaticFiles(directory=VoiceCharacterDir),
                name="static",
            )
            # 全てのルートを上書きしてしまうのでダメ。
            # app_fastapi.mount(
            #     "/",
            #     StaticFiles(directory=get_frontend_path()),
            #     name="static",
            # )

            rest_hello = RestHello()
            app_fastapi.include_router(rest_hello.router)
            rest_configuration_manager = RestAPIConfigurationManager()
            app_fastapi.include_router(rest_configuration_manager.router)
            rest_gpu_device_manager = RestAPIGPUDeviceManager()
            app_fastapi.include_router(rest_gpu_device_manager.router)
            rest_module_manager = RestAPIModuleManager()
            app_fastapi.include_router(rest_module_manager.router)
            rest_slot_manager = RestAPISlotManager()
            app_fastapi.include_router(rest_slot_manager.router)
            fileuploader = EasyFileUploader(UPLOAD_DIR)
            app_fastapi.include_router(fileuploader.router)
            rest_voice_character_slot_manager = RestAPIVoiceCharacterSlotManager()
            app_fastapi.include_router(rest_voice_character_slot_manager.router)
            rest_tts_manager = RestAPITTSManager()
            app_fastapi.include_router(rest_tts_manager.router)

            # voice_changer = RestAPIVoiceChanger()
            # app_fastapi.include_router(voice_changer.router)

            app_fastapi.router.add_api_route("/api/operation/initialize", initialize, methods=["POST"])

            app_fastapi.router.add_api_route("/api_operation_initialize", initialize, methods=["POST"])
            app_fastapi.router.add_api_route("/get_proxy", get_proxy, methods=["GET"])

            app_fastapi

            cls._instance = app_fastapi
            return cls._instance

        return cls._instance


def get_proxy(path: str):

    if path.startswith("/"):
        path = path[1:]

    if path.startswith("assets"):
        file_path = Path(f"web_front/{path}")
    elif path.startswith("models"):
        file_path = Path(f"{path}")
    elif path.startswith("voice_characters"):
        file_path = Path(f"{path}")
    else:
        file_path = Path(f"web_front/{path}")

    logging.getLogger(LOGGER_NAME).info(f"GET_PROXY_PATH:{path} -> {file_path}")

    # ファイルが存在するかチェック
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    # ファイルがディレクトリでないかチェック
    if file_path.is_dir():
        raise HTTPException(status_code=400, detail="Path is a directory, not a file")

    return FileResponse(file_path)
    logging.getLogger(LOGGER_NAME).info(f"GET_PROXY_PATH:{path}")
    return {"message": f"proxy. path:{path}"}


def initialize():
    ConfigFile.unlink(missing_ok=True)
    shutil.rmtree(ModelDir)
    ModelDir.mkdir(parents=True, exist_ok=True)
    shutil.rmtree(VoiceCharacterDir)
    VoiceCharacterDir.mkdir(parents=True, exist_ok=True)
    shutil.rmtree(ModuleDir)
    ModuleDir.mkdir(parents=True, exist_ok=True)
    shutil.rmtree(UPLOAD_DIR)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    configuration_manager = ConfigurationManager.get_instance()
    configuration_manager.reload()
    gpu_device_manager = GPUDeviceManager.get_instance()
    gpu_device_manager.reload()
    moduele_manager = ModuleManager.get_instance()
    moduele_manager.reload()
    slot_manager = SlotManager.get_instance()
    slot_manager.reload()
    voice_character_slot_manager = VoiceCharacterSlotManager.get_instance()
    voice_character_slot_manager.reload()

    # audio_device_manager = AudioDeviceManager.get_instance()
    # audio_device_manager.reload_device()

    # voice_changer = VoiceChanger.get_instance()
    # voice_changer.initialize()

    return {"message": "initialized."}
