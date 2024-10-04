import React, { useEffect, useRef, useState } from "react";
import hljs from "highlight.js";
import "highlight.js/styles/default.css";
import { loggerArea, loggerControlArea, loggerControlButton, loggerDiv } from "../styles";
import { useAppRoot } from "../001_AppRootProvider";
import { use } from "i18next";
import { Logger } from "../util/logger";

type JsonViewerProps = {
    url: string;
};

export const JsonViewer = (props: JsonViewerProps) => {
    const { setUnhandledRejectionToastEnabled } = useAppRoot();
    const [autoLoad, _setAutoLoad] = useState<boolean>(true);
    const autoLoadRef = useRef(autoLoad);
    const setAutoLoad = (val: boolean) => {
        autoLoadRef.current = val;
        _setAutoLoad(val);
    };
    const [data, setData] = useState<string>();
    const bottomRef = useRef<HTMLDivElement>(null);
    useEffect(() => {
        setUnhandledRejectionToastEnabled(false);
    }, []);
    // useEffect(() => {
    //     const fetchLog = async () => {
    //         Logger.getLogger().info(`fetch ${props.url}`);
    //         fetch(props.url)
    //             .then((res) => res.json()) // JSONとしてフェッチ
    //             .then((json) => setData(JSON.stringify(json, null, 8))); // インデントを追加して整形

    //         setTimeout(() => {
    //             fetchLog();
    //         }, 1000);
    //     };
    //     setTimeout(() => {
    //         fetchLog();
    //     }, 1000);
    // }, []);
    useEffect(() => {
        let timeoutId: number; // setTimeoutが返すタイマーIDを記録するための変数
        const fetchLog = () => {
            Logger.getLogger().info(`fetch ${props.url}`);
            if (autoLoadRef.current) {
                fetch(props.url)
                    .then((res) => res.json())
                    .then((json) => setData(JSON.stringify(json, null, 8)));
            } else {
                Logger.getLogger().info("skip fetch");
            }

            timeoutId = window.setTimeout(fetchLog, 1000); // タイマーをセットし、タイマーIDを記録
        };

        fetchLog(); // 最初のログ取得を開始
        return () => window.clearTimeout(timeoutId); // 終了時（リレンダーやアンマウント）にタイマーをクリア
    }, []);

    useEffect(() => {
        if (data) {
            const elements = document.querySelectorAll("pre code");
            elements.forEach((el) => {
                hljs.highlightElement(el as HTMLElement);
            });
            // ログの最後に移動
            if (bottomRef.current) {
                bottomRef.current.scrollIntoView({ behavior: "smooth" });
            }
        }
    }, [data]);
    return (
        <div className={loggerDiv}>
            <div className={loggerArea}>
                <pre>
                    {/* <code className="accesslog">{log}</code> */}
                    {/* <code className="unicorn-rails-log">{log}</code> */}
                    <code className="json">{data}</code>
                </pre>
                <div ref={bottomRef} /> {/* このdivタグは画面の一番下を示すために使用します */}
            </div>

            <div className={loggerControlArea}>
                <span
                    className={loggerControlButton}
                    onClick={() => {
                        Logger.getLogger().info(`${autoLoad} -> ${!autoLoad}`);
                        setAutoLoad(!autoLoad);
                    }}
                >
                    Autoload(Ctrl + r):{autoLoad ? "ON" : "OFF"}
                </span>
            </div>
        </div>
    );
};
