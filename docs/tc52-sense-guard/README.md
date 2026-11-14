# TC52（有線）：check_spec に「SENSE と行ストローブの間の GND ガード」検査を移植（2026-11-14）

対象：`main` の 3367699。変更したのは検査スクリプト `pcb/tc52-build/check_spec.py` と、この記録（`docs/tc52-sense-guard/`）だけ。
**基板ファイル・回路図・DRC ルール・製造データは変更していない。**

## 1. 無線側（tc52-wireless 3fa54e7）で追加された検査

`pcb/tc52w-build/check_spec.py` の項目 6b（監査 2-1「AFE 入口で SENSE が ROW1 のストローブ（モジュールのパッド 48 → R31）と GND を挟まず 0.95 mm で並走」を受けたもの）。

| 観点 | 無線側の中身 |
| --- | --- |
| 対象（守る側） | `SENSE`・`AMP_IN` の **L4（B.Cu）の配線** |
| 対象（攻撃側） | 名前が `ROW` で始まり `DRV` で終わるネット（`ROWn_DRV`＝直列抵抗の GPIO 側）の **L4 の配線だけ**。ビアは合否に含めない |
| 判定（合否） | 両者の中心線距離が 1.5 mm 未満の組について、ストローブ側の線を 11 点で標本化し、各点から SENSE 線上の最近点までの線分が **L4 の GND 配線の中心線と交差**しなければ FAIL。GND ベタは数えない |
| 表示のみ | ① `SENSE`/`AMP_IN` と `ROWn_DRV` の 1.5 mm 未満の中心線距離、② `SENSE`/`AMP_IN` の L4 配線から縁どうし 1.0 mm 以内にある他ネットのビア（GND・SENSE・AMP_IN・COL* 以外） |
| 動機（コミットの記述） | 従来の項目 5 は `ROW*` 全部を、項目 6 は `*_DRV` を除外しており、ビアは見ていなかった。旧基板 6897a62 にかけると FAIL することを確認済み |

## 2. 有線側に同じ穴があるか → **ある（検査の穴。基板の違反ではない）**

有線基板にも `ROW1_DRV`〜`ROW4_DRV`（L4 だけを走る、GPIO → 直列抵抗）と `ROW1`〜`ROW4`（抵抗の行側。L1 の行バス、L4 の引き込み、ビア、ROW1 は L3 にも）がある。SENSE・AMP_IN・AMP_FB は L4。各検査がこれらをどう扱っていたか：

| 検査 | `ROWn_DRV` | `ROWn`（L4 配線） | ストローブのビア | SENSE 以外の AFE 入力 |
| --- | --- | --- | --- | --- |
| check_spec 4（L3 の配線が列・SENSE から 1 mm 以上） | L3 に無いので対象外（L4 は見ない） | L3 の ROW1 は **見ている**（ハード） | 見ない | AMP_IN/AMP_FB は見ない |
| check_spec 5（HIZ と他ネット、2.0 mm 未満を表示） | **`m.startswith('ROW')` で除外** | **除外** | 見ない（配線だけ） | 主体は COL*・SENSE のみ |
| check_spec 6（列・SENSE と行引き込み 2.38 mm、表示） | **`not m.endswith('DRV')` で除外** | 見ている（ただし note で合否なし） | 見ない | 主体は COL*・SENSE のみ |
| check_spec 8（電極・リング内の他ネットのビア） | 電極・リングの中だけ | — | 電極・リングの中だけ | — |
| DRC ルール「HIZ to other nets 2.0 mm」（`ts52k.kicad_dru`） | **`B.NetName != 'ROW*'` で除外（基板全域）** | **除外** | 除外 | A は COL*・SENSE のみ |

つまり **SENSE（と AMP_IN・AMP_FB）の脇に `ROWn_DRV` の配線やビアが来ても、DRC・check_spec のどれも合否で拾わない**。`ROWn` の L4 配線も項目 6 の note に出るだけで合否にはならず、ストローブのビアはどこにも現れない。無線側の 3fa54e7 以前と同じ構造で、レビューの指摘（「5 番は行ライン系を除外して配線だけ」「6 番は *_DRV を除外」）は有線側でも事実だった。

一方、**現行の有線基板には該当パターンは無い**（実地確認の判定と一致）：SENSE に最も近いストローブの銅は ROW1_DRV の 3.2 mm（中心間）、以下 ROW1 3.28、ROW2_DRV 3.6、ROW2 3.95 mm。AMP_IN・AMP_FB の 4 mm 以内にストローブは無い。SENSE・AMP_IN・AMP_FB の脇 1.0 mm 以内の他ネットのビアは 0 個。

## 3. 移植した検査（check_spec 項目 6b、ハード）

**「SENSE / AMP_IN / AMP_FB の L4 配線から中心距離 1.5 mm 未満にある行ストローブの銅（L4 の `ROWn_DRV`・`ROWn` 配線、および `ROWn_DRV`・`ROWn` のビア）については、両者を結ぶ最短線上に GND（L4 の GND 配線、または L4 の GND ベタ）があること」**。違反があれば FAIL（終了コード 1）。

無線側からの変更点（有線の実態に合わせたもの）：

| 変更 | 理由 |
| --- | --- |
| 守る側に **AMP_FB** を追加 | 有線の仕様書では HIZ ネットクラスが COL*・SENSE・AMP_IN・AMP_FB（design-spec §5）。check_spec 3 の `hiz` も AMP_FB を含む |
| 攻撃側に **`ROWn`（抵抗の行側）** を追加。ネット名は `ROW<数字>` / `ROW<数字>_DRV` に厳密一致 | 抵抗の後ろも同じストローブのエッジを運ぶ。有線では `ROWn` の L4 引き込みとビアが基板全体にあり、DRC は `ROW*` を全域で免除しているので、SENSE の近くに来ても合否で拾うものが無い。名前の一致は無線の `startswith('ROW') and endswith('DRV')` より厳密にした |
| 攻撃側に **ストローブのビア** を追加（点として扱う） | ビアは L4 を貫くので L4 上の攻撃源。無線側はビアを表示だけにしていた |
| ガードとして **L4 の GND ベタ** も数える。ベタは **2 枚目の基板オブジェクトにメモリ上で再充填** してから使う（ファイルには書かない） | 有線の L4 には GND ベタ（F.Cu＋B.Cu のゾーン）がある。HIZ の 2.0 mm ルールは Track/Via 同士だけなので、ベタは SENSE に近づき得て、それ自体が正当な GND の壁になる。再充填するのは、ファイルに残った古い充填が「ガード」に見えるのを防ぐため（下の §4 の確認）。項目 11b などほかの項目は従来どおりファイルの充填を見る |
| GND 配線は「中心線が交差」ではなく「銅（幅の半分）が最短線にかかる」で判定 | 線幅を持った実際の銅で判定するため |
| 表示 2 行：AFE 入力に最も近いストローブの銅（4 mm 未満、中心距離）、他ネットのビア 1.0 mm 以内（縁どうし） | 無線側の表示を、AMP_FB とビアの攻撃側を含めて同じ形で出す。合否ではない |
| `check_spec.py [基板ファイル]` の引数（省略時は従来どおり `pcb/ts52k.kicad_pcb`） | 負例をコピーした基板で走らせるため。既定の動作は変わらない |

層構成の前提：有線 TC52 は 4 層、L1＝電極・行バス、L2＝GND（配線なし、項目 1）、L3＝島の配線＋GND、L4＝HIZ 配線と信号。SENSE・AMP_IN・AMP_FB は L4 にしか無いので、L4 で判定する。L3 の配線が SENSE の真上・脇に来る場合は従来の項目 4（1 mm、ハード）が見ている。

## 4. 実証

### 現行基板：PASS（`check_spec-2026-11-14.txt`）

```
ok   ground guard between SENSE / AMP_IN / AMP_FB and every row strobe (ROWn_DRV, ROWn) closer than 1.5 mm (L4 tracks, vias)
     nearest strobe copper to SENSE / AMP_IN / AMP_FB (centre, L4 tracks and vias): [(('SENSE', 'ROW1_DRV'), 3.2), (('SENSE', 'ROW1'), 3.28), (('SENSE', 'ROW2_DRV'), 3.6), (('SENSE', 'ROW2'), 3.95)]
     foreign vias within 1.0 mm (edge to edge) of SENSE / AMP_IN / AMP_FB: none
```

check_spec 全体：**13/13 ok**（従来の 12 項目＋6b）、FAIL 0、終了コード 0。note 2 件（項目 5・6）は従来どおり。
新しい 3 行を除いた出力は、前回の記録 `../tc52-silk-pin1/check_spec-2026-11-14.txt` と **1 字違わず同一**（`diff` で確認）。

### 負例：FAIL（`negative.py`、出力 `negative-2026-11-14.txt`）

`python3 docs/tc52-sense-guard/negative.py`：基板を `/tmp` にコピーして pcbnew で銅を少し足し、新しい check_spec（引数でコピーを指定）と、旧 check_spec（3367699、使い捨ての git worktree の基板ファイルをコピーで差し替えて実行、終了後に worktree を削除）を走らせる。本物の基板ファイルは読むだけ。

SENSE の幹線（L4、y = 118.4、x 0〜221.5）の脇で：

| 負例 | 内容 | 新 check_spec | 旧 check_spec |
| --- | --- | --- | --- |
| N1 | ROW1_DRV の L4 配線（0.15 mm、10 mm）を SENSE から中心 1.0 mm に並走、ガードなし（無線の監査 2-1 と同じ形） | **FAIL**（項目 6b だけ、11 点、終了 1） | 全 ok（終了 0）＝見逃す |
| N2 | N1 ＋ 間に GND 配線（0.2 mm） | ok（項目 6b、終了 0、FAIL 0）＝ガードを正しく認める | 全 ok |
| N3 | ROW2_DRV のビアを SENSE から中心 0.9 mm（L4 には配線なし。L1 側に短いスタブ） | **FAIL**（項目 6b だけ、1 点、終了 1）。ビアの一覧にも `('SENSE','ROW2_DRV',0.58)` | 全 ok（終了 0）＝見逃す |
| N4 | ROW4（抵抗の行側）の L4 配線を SENSE から中心 1.2 mm | **FAIL**（項目 6b だけ、11 点、終了 1） | FAIL なし（項目 6 の note に出るだけ、終了 0） |

4 件とも期待どおり（`ALL CASES AS EXPECTED`）。どの負例でも FAIL は項目 6b の 1 行だけで、他の項目は ok のまま。

補足の確認：
- **再充填が要る理由**：N1 のコピーをそのまま（ファイルの充填で）見ると、ストローブ→SENSE の最短線（x = 105）上の 19 点のうち 5 点が GND ベタの中にあり、ガードがあるように見えてしまう（新しい配線の下に古い充填が残っているため）。メモリ上で再充填すると 0 点になり、正しく FAIL する。
- N3 の作り方：配線の付かないビアは、コピーを保存するときに周囲の GND ベタのネットにされてしまう（KiCad の挙動）。そのため L1 に ROW2_DRV の短いスタブ（L1 は行バスの層で項目 2 に触れない）を付け、電極・リングから 24 mm 以上離れた位置（x = 120）に置いた（項目 8 を巻き込まないため）。

## 5. 再現手順

```
python3 pcb/tc52-build/check_spec.py                  # 現行基板、13 項目
python3 docs/tc52-sense-guard/negative.py             # 負例 N1〜N4（/tmp と一時 worktree を使う）
```
pcbnew の Python（KiCad 9）が要る。基板・回路図を変えていないので DRC（`drc.sh`）と製造出力は前回の記録のまま。
