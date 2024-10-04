export class RingBuffer {
    private size: number;
    private buffer: Float32Array;
    private head: number;
    private tail: number;
    private isFull: boolean;

    constructor(size: number) {
        this.size = size;
        this.buffer = new Float32Array(size);
        this.head = 0; // 書き込み位置
        this.tail = 0; // 読み取り位置
        this.isFull = false; // バッファが満杯かどうか
    }

    // 新しいサンプルを追加する
    addSamples(inputData: Float32Array) {
        const inputLength = inputData.length;
        const availableSpace = this.getAvailableSpace();

        if (inputLength > availableSpace) {
            throw new Error("Ring Buffer is over: not enough space to add new samples.");
        }

        if (this.head >= this.tail) {
            const spaceUntilEnd = this.size - this.head;
            if (inputLength <= spaceUntilEnd) {
                // バッファの最後を突き抜けない場合。
                this.buffer.set(inputData, this.head);
                this.head += inputLength;
                if (this.head === this.size) this.head = 0;
            } else {
                // バッファの最後を突き抜ける場合。
                this.buffer.set(inputData.subarray(0, spaceUntilEnd), this.head);
                this.buffer.set(inputData.subarray(spaceUntilEnd), 0);
                this.head = inputLength - spaceUntilEnd;
            }
        } else {
            // 満杯じゃないことが分かっているので、そのまま書き込めばよい。(tailを追い越すことはない。)
            this.buffer.set(inputData, this.head);
            this.head += inputLength;
        }

        this.isFull = this.head === this.tail;
    }

    // 現在の未読みのバッファ内容を読み取る
    readSamples(count: number): Float32Array {
        if (this.head === this.tail && !this.isFull) {
            // バッファが空の場合
            return new Float32Array(0);
        }
        const availableSamples = this.getCurrentSize();
        if (availableSamples < count) {
            throw new Error("Ring Buffer is short: not enough data to read new samples.");
        }

        const readTo = (this.tail + count) % this.size;

        let samples;
        if (readTo > this.tail) {
            // データが連続している場合
            samples = new Float32Array(this.buffer.slice(this.tail, readTo));
        } else {
            // データが循環している場合
            samples = new Float32Array([...this.buffer.slice(this.tail), ...this.buffer.slice(0, readTo)]);
        }

        // データを読み取った後、tail の位置を head の位置に更新
        this.tail = readTo;
        this.isFull = false;

        return samples;
    }

    // 現在のバッファサイズを取得する
    getCurrentSize(): number {
        if (this.isFull) {
            return this.size;
        } else if (this.head >= this.tail) {
            return this.head - this.tail;
        } else {
            return this.size - this.tail + this.head;
        }
    }

    // 利用可能なスペースを取得する
    getAvailableSpace(): number {
        if (this.isFull) {
            return 0;
        } else if (this.head >= this.tail) {
            return this.size - (this.head - this.tail);
        } else {
            return this.tail - this.head;
        }
    }
}
