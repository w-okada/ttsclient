# Lessons

## L-001: コードだけでなく実データ（モデルファイル・設定ファイル）も検証する

**発生**: v2Pro vs v2ProPlus の違いを調査した際、コードの条件分岐だけ見て「アーキテクチャ同一」と誤報告した。実際はチェックポイント内の config (`upsample_initial_channel`: 512 vs 768) で Generator のサイズが異なっていた。

**ルール**: モデルやデータの性質について結論を出すときは、コードの分岐だけでなく、**実際のファイルを開いて中身を確認する**。特に config がファイルに埋め込まれている場合（`torch.load` して `dict["config"]` を読む等）、コードからは差異が見えない。

**適用場面**:
- モデルのバージョン間比較
- 設定値がハードコードではなくファイルから読み込まれるケース
- 「同一コードパスだから同一動作」と結論づけそうになったとき

## L-002: ファイル削除時は全参照元を確認する

**発生**: `symbols.py`（v1用）を削除した際、`symbols2.py` に同等の定義があることを確認したが、`chinese.py`, `chinese2.py`, `cantonese.py`, `japanese.py`, `english.py` の5ファイルが `from .symbols import punctuation` で参照していることを見落とした。

**ルール**: ファイルを削除する前に、**そのファイル内のすべてのエクスポートされたシンボルについて `grep` で参照元を検索する**。特に `from .module import symbol` パターンは IDE でなくても見落としやすい。

**適用場面**:
- ファイルやモジュールを削除するとき
- "v1 only" "旧バージョン用" と判断してコードを除去するとき
- `sys.path` ハックを削除してインポートチェインが変わるとき

## L-003: sys.path ハック削除は連鎖的な影響を確認する

**発生**: `app.py` の `sys.path.append(third_party/GPT-SoVITS)` を削除した際、直接参照している6箇所は修正したが、`cnhubert_embedder.py` の `from feature_extractor import cnhubert` が間接的に同じ sys.path に依存していた。

**ルール**: `sys.path` を変更する際は、そのパスが提供していた**すべてのパッケージ名**を特定し、それぞれについて `grep -r "from <package_name>" --include="*.py"` で参照元を漏れなく探す。

**適用場面**:
- `sys.path.append` / `sys.path.insert` の追加・削除
- パッケージ構成の変更（ディレクトリ移動、リネーム）
- import 方式の変更（相対→絶対、sys.path→パッケージ内参照）
