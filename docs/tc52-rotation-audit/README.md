# TC52（有線）：CPL 回転の全数照合（2026-11-14）

対象：`main`（監査開始 733bf7d）の `pcb/jlcpcb/` の製造出力。BOM 22 行・LCSC 22 種・CPL 76 点（全点 Bottom）。
方法と水準は TC52 wireless の監査（sadaoikebe/tc52-wireless c372044、`docs/tc52w-rotation-audit/`）に倣った。
基板・回路図は変更していない。変更は `pcb/jlcpcb/export.py` の `ROTATION_CORRECTIONS`（新設）と、再生成した製造データだけ。

**ランドの出典：JLCEDA/EasyEDA Official Library（嘉立创EDA/EasyEDA官方库）** — [JLCEDA](https://lceda.cn/) / [EasyEDA](https://easyeda.com/)。

前提の訂正：監査前の有線 `export.py` には `ROTATION_CORRECTIONS` が**存在しなかった**（回転は KiCad の値そのまま）。
C15127（AO3401A）+180° は無線版の Q1 の補正で、有線の BOM に C15127 はない。そのため「既存補正の再検証」の対象はなく、補正は今回すべて新規に入れた。

## 結論

| 区分 | LCSC 種類 | 実装点 |
| --- | ---: | ---: |
| **補正を追加：C2866134 TPS7A2433（U3）+180°**（無線版にない部品） | 1 | 1 |
| **補正を追加：C97521 W25Q128JVS（U4）+90°**（無線版にない部品） | 1 | 1 |
| **補正を追加：C41249 AD8601（U6）+180°**（無線版と同じ差） | 1 | 1 |
| **補正を追加：C21379 CD4051（U7, U8）+90°**（無線版と同じ差） | 1 | 2 |
| 照合済み・補正なし（向きが意味を持ち、一致を確認） | 4 | 6 |
| **未確認：C27636964 OC2EL89CJO-113YLC-12M（X2）**：EasyEDA/JLCEDA にランドが存在しない。補正は入れていない | 1 | 1 |
| 向き無関係（無極性 2 端子の MLCC・抵抗。0°/180° が等価。90° ずれていないことも確認） | 13 | 64 |
| 合計 | 22 | 76 |

CPL の Rotation の変更：U3 −90 → 90、U4 0 → 90、U6 −90 → 90、U7 0 → 90、U8 0 → 90。その他の 71 点は変わらない。BOM は 1 バイトも変わっていない。
ガーバー・ドリルは、日付行以外は再生成前と同一。

### 向きのある部品（12 点）

| 部品 | LCSC | KiCad フットプリント | EasyEDA パッケージ | ランド照合（EasyEDA→KiCad） | ピン名照合 | 判定 |
| --- | --- | --- | --- | --- | --- | --- |
| D89, D90, D91 H5VU10U | C22395519 | Diode_SMD:D_SOD-882D | DFN1006-2L-RD | 0°、rms 0.000 mm（90° は 0.566） | EasyEDA 1=K（西）、2=A。基板 1=D−/D+/+5V、2=GND（保護対象が 1。`pcb/jlcpcb/README.md` の記載と一致） | 照合済み・補正なし |
| J1 USB-C | C165948 | Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12 | USB-C_SMD-TYPE-C-31-M-12_1 | 0°、16 ランド rms 0.068 mm（次点 90° は 4.49） | A5 CC1, A6 DP1, A7 DN1, B5 CC2 …（A1B12/A4B9 等の結合ランドとシールド 4 か所は別名として対応付け） | 照合済み・補正なし |
| SW1 TS-1187A-B-A-B | C318884 | rp2040:SW_Tactile_XKB_TS-1187A_5.1x5.1mm | SW-SMD_4P-L5.1-W5.1-P3.70 | 0°、rms 0.025 mm（90° は 4.99） | EasyEDA 1..4 = A..D。KiCad は内部で導通する対（上の 2 つ＝1、下の 2 つ＝2）。180° 回転でも電気的に等価、90° は不可 | 照合済み・補正なし |
| U3 TPS7A2433DBVR | C2866134 | Package_TO_SOT_SMD:SOT-23-5 | SOT-23-5_L2.9-W1.6-P0.95-LS2.8-BR | **180°**、rms 0.037 mm（次点 90° は 1.96） | EasyEDA 1 IN 2 GND 3 EN 4 NC 5 OUT。基板 1=+5V 2=GND 3=+5V（EN=IN 直結）4=GND 5=+3V3。TI データシートと一致。KiCad は 1 番が北西（1–3 西）、EasyEDA は 1 番が南東（1–3 東） | **補正 +180°** |
| U4 W25Q128JVS | C97521 | Package_SO:SOIC-8_5.3x5.3mm_P1.27mm | SOIC-8_L5.3-W5.3-P1.27-LS8.0-BL | **90°**、rms 0.057 mm（次点 0° は 5.42） | EasyEDA 1 CS# 2 DO 3 IO2 4 GND 5 DI 6 CLK 7 IO3 8 VCC。基板の QSPI ネットと一致（Winbond の割り当て）。KiCad は縦 2 列で 1 番が北西、EasyEDA は横 2 行で 1 番が南西 | **補正 +90°** |
| U5 RP2040 | C2040 | rp2040:IC57_RP2040 | LQFN-56_L7.0-W7.0-P0.4-EP | 0°、57 ランド rms 0.024 mm（次点 90° は 5.29） | 57 ピンすべて同名。表記の違いは SWD/SWDIO、VREG_IN/VREG_VIN、QSPI_SS/QSPI_SS_N、EP=GND の 4 件だけ | 照合済み・補正なし |
| U6 AD8601ARTZ | C41249 | Package_TO_SOT_SMD:SOT-23-5 | SOT-23-5_L3.0-W1.7-P0.95-LS2.8-BR | **180°**、rms 0.159 mm（次点 90° は 2.08） | EasyEDA 1 OUT 2 −V 3 +IN 4 −IN 5 +V。基板 1=AMP_OUT 2=GND 3=AMP_IN 4=AMP_FB 5=+3V3A | **補正 +180°** |
| U7, U8 CD4051BM96 | C21379 | Package_SO:SOIC-16_3.9x9.9mm_P1.27mm | SOIC-16_L9.9-W3.9-P1.27-LS6.0-BL | **90°**、rms 0.261 mm（次点 0° は 5.53） | EasyEDA 3 COM、6 INH、7 VEE、8 VSS、9/10/11 C/B/A、16 VDD。基板 3=SENSE 6=INHA 7/8=GND 9/10/11=S3A/S2A/S1A 16=+3V3M | **補正 +90°** |
| X2 OC2EL89CJO-113YLC-12M | C27636964 | Oscillator:Oscillator_SMD_Abracon_ASE-4Pin_3.2x2.5mm | **なし** | **照合不能** | YXC データシート（YSO140TC、3.2×2.5）：上面視で #1 左下 Tri-state、#2 右下 GND、#3 右上 OUT、#4 左上 VDD。KiCad のパッド位置・基板ネット（1=X2-EN、2=GND、3=U5-XIN、4=+3V3）と一致 | **未確認・補正なし** |

rms は、番号付きランドの中心を 0/90/180/270° 回転と平行移動で最小二乗に当てはめた残差（`audit-summary.txt`, `audit.json`）。
ここに書いた角度は「EasyEDA のランドを KiCad のフットプリントに重ねる回転」で、CPL の補正量は `required_angles.py` が Bottom の約束事（下記モデル A）で計算した値。

### 未確認：X2（C27636964）

- `easyeda.com/api/products/C27636964/components` → 404「Component not found」、`/svgs` → 422「原理图未绘制」（回路図未作成）。
- `lceda.cn/api/products/C27636964/components` → 404「元件库未找到」（部品ライブラリに未登録）。
- `pro.easyeda.com/api/eda/product/search` では部品自体（SMD3225-4P、在庫 2414）は見つかるが、`hasDevice` が空で `device_info` は null。EasyEDA のデバイスもフットプリントも無い。
- したがって JLCPCB が実装に使うランドの向き（1 番の位置）を実データで確かめる方法がない。ピン機能とパッド位置は、KiCad・基板・データシートの三者で一致することを確認した。現 CPL は KiCad の値 180° のまま。
- **発注時に必ず確認すること：** JLCPCB の配置プレビューでこの部品にランドが付くか、付く場合は 1 番（Tri-state/EN、データシートの面取りコーナー）が KiCad の 1 番パッド（X2-EN ネット）に重なるか。JLCPCB 側でフットプリントを新規作成する場合は、その向きを確認してから角度を決める。

## 方法

1. `extract_board.py`：pcbnew で基板の 76 点を読み、Bottom 反転と配置角をメモリ上で戻して、表面 0° でのパッド（番号・座標・寸法・ネット・ピン機能）を取り出す（基板は保存しない）。
   使っているライブラリのフットプリントとも全パッドを比較し、76 点すべて一致した（J1 はシールド 4 パッドの並び順だけが違う）。結果は `board-extract.json`。
2. `fetch.py`：22 種すべてについて `GET https://easyeda.com/api/products/<C>/components` と `/svgs`（JLCPCB の部品ページのビューアが使う元データ）、
   `GET https://wmsc.lcsc.com/ftps/wm/product/detail?productCode=<C>`（型番・メーカー・パッケージ・データシート URL）を取得し、`raw/` に保存。
   21 種は 3 種類とも HTTP 200 で取得できた。C27636964 は上記のとおりランドが存在しない。取得記録（URL・日付・SHA-256）は `fetch-log.json`。
   `/components` と `/svgs` のランドは 21 種すべてで、番号と座標が 0.005 mm 以内で一致した（`audit.json` の `components_vs_svgs_same_pads`）。
3. `audit.py`：番号付きランドを 0/90/180/270° と平行移動で最小二乗比較する（`audit.json`, `audit-summary.txt`）。
   EasyEDA の回路記号のピン名と、基板のネット名・KiCad のピン機能を突き合わせ、番号の意味が同じことを確認した。
4. `required_angles.py`：CPL の各点について、JLCPCB のランドが基板の銅に重なる CPL 角度を 3 つのモデルで計算する（`required-angles.json/.txt`）。
   無線版のスクリプトから、−45° に置いた C16 のような非直交の配置も扱えるように拡張した（候補角 = KiCad 角 mod 90 + k·90）。
   補正後はモデル A で 75 点が一致。残る 1 点は未確認の X2。

監査前後の検査（従来値と同じ）：DRC エラー 0・未接続 0・回路図との不一致 0（警告 15）、ERC エラー 0（警告 6 件はすべて lib_symbol_mismatch で、既知のライブラリ版差）、
check_spec 12/12 ok（note 2 件は従来どおり。`check_spec-2026-11-14.txt`）。`manifest.json` のハッシュはすべて実ファイルと一致する。

## 未解決：JLCPCB が Bottom の角度をどう読むか（発注前に要確認）

この基板は**実装部品 76 点がすべて Bottom**なので、この論点は全点に関係する。内容は無線版の記録と同じ。

JLCPCB の公開資料（[Pick & Place File](https://jlcpcb.com/help/article/pick-place-file-for-pcb-assembly)）は「正の値は反時計回り」としか書いておらず、**Bottom 面の角度の約束事は定義されていない**。EasyEDA のランドデータからも決められない。公開されている報告は次のとおりで、互いに食い違う。

| モデル | 式（KiCad 角 φ、補正 c） | 根拠 |
| --- | --- | --- |
| A | φ + c（KiCad の値そのまま。現在の export.py） | これを支持する公開報告は見つからなかった |
| B | 180 − φ + c | [kicad-jlcpcb-tools #159](https://github.com/Bouni/kicad-jlcpcb-tools/issues/159)（2022）、[KiBot の位置ファイル説明](https://kibot.readthedocs.io/en/latest/notes_position.html)（2023-11）。アップロード時のプレビューはこれで正しく見えるという報告がある |
| C | φ + 180 + c | [kicad-jlcpcb-tools #636](https://github.com/Bouni/kicad-jlcpcb-tools/issues/636)（2025）。JLCPCB の技術者がこの値で機械を設定し、正しく実装されたという報告 |

[KiBot #510](https://github.com/INTI-CMNB/KiBot/issues/510) では「JLCPCB は少なくとも 3 回 Bottom 角の扱いを変えた」とされている。リポジトリにある旧 `pcb/jlcpcb/project.db` は kicad-jlcpcb-tools（モデル B）の時代のもの。

**向きが意味を持つ部品の要求 CPL 角（補正込み）**

| 部品 | KiCad φ | 現 CPL（A） | B | C |
| --- | ---: | ---: | ---: | ---: |
| D89 H5VU10U | 180 | 180 | 0 | 0 |
| D90, D91 H5VU10U | 0 | 0 | 180 | 180 |
| J1 USB-C | 0 | 0 | 180 | 180 |
| SW1（180° 等価） | 90 | 90 | 90 | 270 |
| U3 TPS7A2433 | 270 | 90 | 90 | 270 |
| U4 W25Q128JVS | 0 | 90 | 90 | 270 |
| U5 RP2040 | 180 | 180 | 0 | 0 |
| U6 AD8601 | 270 | 90 | 90 | 270 |
| U7, U8 CD4051 | 0 | 90 | 90 | 270 |
| X2 発振器 | 180 | 180 | 未確認 | 未確認 |

0°/180° に置いた部品は、B と C がそろって現 CPL と 180° 違う。±90° に置いた部品は B が現 CPL と一致し、C だけが 180° 違う。
推測で全体の約束事を書き換えることはしていない。発注画面のプレビューで上の表のどの列で正しく見えるかを確かめ、必要なら JLCPCB に Bottom の角度の解釈を問い合わせてから、`export.py` の Bottom の基本の式を決めること。
ライブラリ差の補正量（`ROTATION_CORRECTIONS`）自体は、どのモデルでも同じ値を加える。

## 再実行

リポジトリ直下から（pcbnew が必要なものはシステムの python3）：

```sh
/usr/bin/python3 -I docs/tc52-rotation-audit/extract_board.py . docs/tc52-rotation-audit/board-extract.json
python3 -I docs/tc52-rotation-audit/fetch.py            # 実データの再取得（raw/ と fetch-log.json を上書き）
python3 -I docs/tc52-rotation-audit/audit.py docs/tc52-rotation-audit/board-extract.json > docs/tc52-rotation-audit/audit-summary.txt
/usr/bin/python3 -I docs/tc52-rotation-audit/required_angles.py > docs/tc52-rotation-audit/required-angles.txt
```

`fetch.py` を再実行すると、X2 についての手作業の記録（`fetch-log.json` の `C27636964` の追記分）は消える。必要なら追記し直すこと。
