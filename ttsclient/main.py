import logging
import platform
import signal
import fire

from ttsclient.tts.tts_manager.tts_manager import TTSManager
from ttsclient.utils.download_callback import get_download_callback

import time
from ttsclient.misc.download_eunjeon import download_modules
from ttsclient.app_status import AppStatus
from ttsclient.const import LOG_FILE, LOGGER_NAME, VERSION
from ttsclient.logger import setup_logger
from ttsclient.proxy.ngrok_proxy_manager import NgrokProxyManager
from ttsclient.server.tts_server import TTSServer
from ttsclient.tts.data_types.slot_manager_data_types import GPTSoVITSModelImportParam, VoiceCharacterImportParam
from ttsclient.tts.gpu_device_manager.gpu_device_manager import GPUDeviceManager
from ttsclient.tts.module_manager.module_manager import ModuleManager
from ttsclient.tts.slot_manager.slot_manager import SlotManager
from ttsclient.tts.voice_character_slot_manager.voice_character_slot_manager import VoiceCharacterSlotManager
from ttsclient.utils.parseBoolArg import parse_bool_arg
from ttsclient.utils.resolve_url import resolve_base_url
from simple_performance_timer.Timer import Timer


setup_logger(LOGGER_NAME, LOG_FILE)

import atexit


def goodbye():
    print("Program ended")


atexit.register(goodbye)

import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def download_initial_data() -> None:
    # ## 重みのダウンロード
    download_callback = get_download_callback()

    module_manager = ModuleManager.get_instance()
    module_manager.download_initial_modules(download_callback)


def download_initial_models() -> None:
    # ModelDirの中身が空だった場合
    slot_manager = SlotManager.get_instance()
    slot_infos = slot_manager.get_slot_infos()
    slot_infos = [slot_info for slot_info in slot_infos if slot_info.tts_type is not None]
    if len(slot_infos) > 0:
        return

    # ## 重みのダウンロード
    download_callback = get_download_callback()

    module_manager = ModuleManager.get_instance()
    module_manager.download_initial_models(download_callback)

    # プレトレインの設定
    gpt_sovits_icon = module_manager.get_module_filepath("GPT-SoVITS_icon")
    model_import_param = GPTSoVITSModelImportParam(
        tts_type="GPT-SoVITS",
        name="pretrained",
        terms_of_use_url="https://huggingface.co/wok000/gpt-sovits-models/raw/main/pretrained/term_of_use.txt",
        icon_file=gpt_sovits_icon,
    )
    slot_manager.set_new_slot(model_import_param, remove_src=True)

    # finetuneの設定
    ft_semantic = module_manager.get_module_filepath("GPT-SoVITS_FT_JVNV_semantice")
    ft_synthesizer = module_manager.get_module_filepath("GPT-SoVITS_FT_JVNV_synthesizer")
    ft_icon = module_manager.get_module_filepath("GPT-SoVITS_FT_JVNV_icon")

    model_import_param = GPTSoVITSModelImportParam(
        tts_type="GPT-SoVITS",
        name="JVNV_FT_F1",
        terms_of_use_url="https://huggingface.co/wok000/gpt-sovits-models/raw/main/fine-tune-by-JVNV-F1/term_of_use.txt",
        icon_file=ft_icon,
        semantic_predictor_model=ft_semantic,
        synthesizer_path=ft_synthesizer,
    )
    slot_manager.set_new_slot(model_import_param, remove_src=True)

    # JVNV Voicesの設定
    for v in ["JVNV_F1_VOICE", "JVNV_F2_VOICE", "JVNV_M1_VOICE", "JVNV_M2_VOICE"]:
        voice_character_slot_manager = VoiceCharacterSlotManager.get_instance()
        zipfile = module_manager.get_module_filepath(v)
        voice_character_import_param = VoiceCharacterImportParam(
            tts_type="GPT-SoVITS",
            name=v,
            terms_of_use_url="",
            zip_file=zipfile,
        )
        voice_character_slot_manager.set_new_slot(voice_character_import_param, remove_src=True)


def start_cui(
    host: str = "0.0.0.0",
    port: int = 19000,
    https: bool = False,
    launch_client: bool = True,
    allow_origins=None,
    no_cui: bool = False,
    ngrok_token: str | None = None,
    ngrok_proxy_url_file: str | None = None,
):
    timer_enabled = False
    # print_active_threads("at start")
    with Timer("start_cui", enalbe=timer_enabled) as t:

        https = parse_bool_arg(https)
        launch_client = parse_bool_arg(launch_client)
        no_cui = parse_bool_arg(no_cui)

        logging.getLogger(LOGGER_NAME).info(f"Starting TTSClient CUI version:{VERSION}")

        if ngrok_token is not None and https is True:
            print("ngrok with https is not supported.")
            print("use http.")
            return

        print("checking the modules...")
        download_initial_data()
        download_initial_models()

        GPUDeviceManager.get_instance()

        # 各種プロセス起動
        app_status = AppStatus.get_instance()
        # # (1) VCServer 起動
        allow_origins = "*"
        tts_server = TTSServer.get_instance(host=host, port=port, https=https, allow_origins=allow_origins)
        tts_server_port = tts_server.start()

        # # (2) NgrokProxy
        if ngrok_token is not None:
            try:
                proxy_manager = NgrokProxyManager.get_instance()
                proxy_url = proxy_manager.start(tts_server_port, token=ngrok_token)
                # print(f"NgrokProxy:{proxy_url}")
                logging.getLogger(LOGGER_NAME).info(f"NgrokProxy: {proxy_url}")
                if ngrok_proxy_url_file is not None:
                    with open(ngrok_proxy_url_file, "w") as f:
                        f.write(proxy_url)

            except Exception as e:
                logging.getLogger(LOGGER_NAME).error(f"NgrokProxy Error:{e}")
                print("NgrokProxy Error:", e)
                print("")
                print("Ngrok proxy is not launched. Shutdown server... ")
                print("")
                tts_server.stop()
                return
        else:
            proxy_manager = None
            proxy_url = None

        base_url = resolve_base_url(https, port)

        bold_green_start = "\033[1;32m"
        reset = "\033[0m"
        title = "    tts client    "
        urls = [
            ["Application", base_url],
            ["Log(rich)", f"{base_url}/?app_mode=LogViewer"],
            ["Log(text)", f"{base_url}/vcclient.log"],
            ["API", f"{base_url}/docs"],
            ["License(js)", f"{base_url}/licenses-js.json"],
            ["License(py)", f"{base_url}/licenses-py.json"],
        ]

        if proxy_url is not None:
            urls.append(["Ngrok", proxy_url])

        key_max_length = max(len(url[0]) for url in urls)
        url_max_length = max(len(url[1]) for url in urls)

        padding = (key_max_length + url_max_length + 3 - len(title)) // 2

        if platform.system() != "Darwin":

            def gradient_text(text, start_color, end_color):
                text_color = (0, 255, 0)  # Green color for the text
                n = len(text)
                grad_text = ""
                for i, char in enumerate(text):
                    r = int(start_color[0] + (end_color[0] - start_color[0]) * i / n)
                    g = int(start_color[1] + (end_color[1] - start_color[1]) * i / n)
                    b = int(start_color[2] + (end_color[2] - start_color[2]) * i / n)
                    grad_text += f"\033[1m\033[38;2;{text_color[0]};{text_color[1]};{text_color[2]}m\033[48;2;{r};{g};{b}m{char}"
                return grad_text + reset

            start_color = (18, 121, 255)
            end_color = (0, 58, 158)
            print("")
            print(" " * padding + gradient_text(" " * len(title), start_color, end_color))
            print(" " * padding + gradient_text(title, start_color, end_color))
            print(" " * padding + gradient_text(" " * len(title), start_color, end_color))
        else:
            print("")
            print(f"{bold_green_start}{title}{reset}")
            print("")

        print("-" * (key_max_length + url_max_length + 5))
        for url in urls:
            print(f" {bold_green_start}{url[0].ljust(key_max_length)}{reset} | {url[1]} ")
        print("-" * (key_max_length + url_max_length + 5))

        logging.getLogger(LOGGER_NAME).info("--- TTSClient READY ---")
        print(f"{bold_green_start}Please press Ctrl+C once to exit ttsclient.{reset}")

        # # # (4)Native Client 起動
        # # if launch_client and platform.system() != "Darwin":
        # clinet_launcher = ClientLauncher(app_status.stop_app)
        # clinet_launcher.launch(port, https)

    try:
        while True:
            current_time = time.strftime("%Y/%m/%d %H:%M:%S")
            logging.getLogger(LOGGER_NAME).info(f"{current_time}: running...")
            if app_status.end_flag is True:
                break
            time.sleep(60)
    except KeyboardInterrupt:
        err_msg = "KeyboardInterrupt"

    print(f"{bold_green_start}terminate ttsclient...{reset}")
    # 終了処理
    with Timer("end_cui", enalbe=timer_enabled) as t:  # noqa

        def ignore_ctrl_c(signum, frame):
            print(f"{bold_green_start}Ctrl+C is disabled during this process{reset}")

        original_handler = signal.getsignal(signal.SIGINT)

        try:
            signal.signal(signal.SIGINT, ignore_ctrl_c)
            # # (3)Native Client 終了(サーバとの通信途中でのサーバ停止を極力避けるため、クライアントから落とす。)
            # if launch_client:
            #     clinet_launcher.stop()

            # # (1) VCServer 終了処理
            print(f"{bold_green_start}tts client is terminating...{reset}")
            tts_server.stop()
            print(f"{bold_green_start}tts client is terminated.[{tts_server_port}]{reset}")

            TTSManager.get_instance().stop_tts()

            if len(err_msg) > 0:
                print("msg: ", err_msg)

            # ngrok
            if proxy_manager is not None:
                proxy_manager.stop()
        finally:
            print("")
            # signal.signal(signal.SIGINT, original_handler)

        signal.signal(signal.SIGINT, original_handler)


def main():
    fire.Fire(
        {
            "cui": start_cui,
            "download": download_modules,
        }
    )


if __name__ == "__main__":
    main()
