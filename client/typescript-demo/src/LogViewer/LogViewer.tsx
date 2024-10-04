import React, { useEffect, useMemo, useRef, useState } from "react";
import hljs from "highlight.js";
// import "highlight.js/styles/default.css";
import { decoratedWordBlue, decoratedWordGreen, decoratedWordRed, logLine, loggerArea, loggerControlArea, loggerControlButton, loggerDiv } from "../styles";
import { useAppRoot } from "../001_AppRootProvider";
import { Logger } from "../util/logger";

export const LogViewer = () => {
    const { setUnhandledRejectionToastEnabled } = useAppRoot();
    const [autoLoad, _setAutoLoad] = useState<boolean>(true);
    const autoLoadRef = useRef(autoLoad);
    const setAutoLoad = (val: boolean) => {
        autoLoadRef.current = val;
        _setAutoLoad(val);
    };

    const [log, setLog] = useState<string>();
    const bottomRef = useRef<HTMLDivElement>(null);
    useEffect(() => {
        setUnhandledRejectionToastEnabled(false);
    }, []);

    useEffect(() => {
        const handleKeyDown = (event: KeyboardEvent) => {
            if (event.ctrlKey && event.key === "r") {
                event.preventDefault(); // ブラウザのリロードを防ぐ
                setAutoLoad(!autoLoadRef.current);
            }
        };

        window.addEventListener("keydown", handleKeyDown);
        return () => {
            window.removeEventListener("keydown", handleKeyDown);
        };
    }, []);

    useEffect(() => {
        let timeoutId: number; // setTimeoutが返すタイマーIDを記録するための変数
        const fetchLog = () => {
            if (autoLoadRef.current) {
                fetch("/ttsclient.log")
                    .then((res) => res.text())
                    .then((text) => setLog(text));
            } else {
                Logger.getLogger().info("skip fetch");
            }

            timeoutId = window.setTimeout(fetchLog, 1000); // タイマーをセットし、タイマーIDを記録
        };

        fetchLog(); // 最初のログ取得を開始
        return () => window.clearTimeout(timeoutId); // 終了時（リレンダーやアンマウント）にタイマーをクリア
    }, []);

    const logDiv = useMemo(() => {
        if (!log) {
            return <div>loading...</div>;
        }

        const redKeywords = ["ERROR"];
        const blueKeywords = ["WARNING"];
        const greenKeywords = ["GPU[cuda]"];

        const keywords = redKeywords.concat(blueKeywords).concat(greenKeywords);
        const escapeRegExp = (string) => {
            return string.replace(/([.*+?^=!:${}()|\[\]\/\\])/g, "\\$1");
        };
        const escapedKeywords = keywords.map(escapeRegExp);

        const lines = log.split("\n").map((line, index) => {
            const parts = line.split(new RegExp(`(${escapedKeywords.join("|")})`));
            return (
                <div key={index} className={logLine}>
                    {parts.map((part, partIndex) => {
                        if (redKeywords.includes(part)) {
                            return (
                                <span key={partIndex} className={decoratedWordRed}>
                                    {part}
                                </span>
                            );
                        } else if (blueKeywords.includes(part)) {
                            return (
                                <span key={partIndex} className={decoratedWordBlue}>
                                    {part}
                                </span>
                            );
                        } else if (greenKeywords.includes(part)) {
                            return (
                                <span key={partIndex} className={decoratedWordGreen}>
                                    {part}
                                </span>
                            );
                        } else {
                            return <span key={partIndex}>{part}</span>;
                        }
                    })}
                </div>
            );
        });

        return lines;
    }, [log]);

    useEffect(() => {
        if (log) {
            // ログの最後に移動
            if (bottomRef.current) {
                bottomRef.current.scrollIntoView({ behavior: "smooth" });
            }
        }
    }, [log]);

    return (
        <div className={loggerDiv}>
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
            <div className={loggerArea}>
                {logDiv}
                <div ref={bottomRef} />
            </div>
        </div>
    );
};
