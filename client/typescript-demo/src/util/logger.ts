export type LogEntry = {
    timestamp: string;
    level: string;
    message: any[];
    callerInfo: string;
};

export class Logger {
    LEVEL = {
        DEBUG: 1,
        INFO: 2,
        WARN: 3,
        ERROR: 4,
    };
    level = this.LEVEL.DEBUG;

    private static instance: Logger;
    private logs: LogEntry[] = []; // メッセージを蓄積する配列
    private maxLogSize = 5000; // 最大蓄積メッセージ数
    private constructor() {} // コンストラクタをプライベート化

    static getLogger() {
        if (!Logger.instance) {
            Logger.instance = new Logger();
        }
        return Logger.instance;
    }

    debug(...args: any[]) {
        if (this.level > this.LEVEL.DEBUG) return;
        this.logWithLevel("debug", args);
    }

    info(...args: any[]) {
        if (this.level > this.LEVEL.INFO) return;
        this.logWithLevel("info", args);
    }

    warn(...args: any[]) {
        if (this.level > this.LEVEL.WARN) return;
        this.logWithLevel("warn", args);
    }

    error(...args: any[]) {
        if (this.level > this.LEVEL.ERROR) return;
        this.logWithLevel("error", args);
    }
    getLogs() {
        return this.logs;
    }

    private logWithLevel(level: string, args: any[]) {
        // 引数リストにタイムスタンプを追加
        const timestamp = new Date().toISOString();
        const callerInfo = this.getCallerInfo();
        args.unshift(`[${timestamp}]`);
        console[level].apply(console, args);

        // メッセージを蓄積
        this.addLogEntry({
            timestamp,
            level,
            message: args,
            callerInfo,
        });
    }
    private addLogEntry(entry: LogEntry) {
        if (this.logs.length >= this.maxLogSize) {
            this.logs.shift(); // 古いメッセージを削除
        }
        this.logs.push(entry);
    }
    private getCallerInfo = (): string => {
        const error = new Error();
        const stack = error.stack || "";
        const stackLines = stack.split("\n");

        // スタックトレースの3行目には呼び出し元の情報が通常含まれている
        const callerLine = stackLines[4] || "";

        // 正規表現を使ってファイル名と行番号を抽出
        const regex = /\((.*):(\d+):(\d+)\)/;
        const match = regex.exec(callerLine);

        if (match && match.length === 4) {
            return `${match[1]}:${match[2]}`;
        }

        return "unknown";
    };
}
