# CONwithPhS

PIAORをコンテンツ指向ネットワークに応用した経路制御法

## 命名規則
命名規則は，PEP8に準ずる

参考サイト:

[pep8-jp](https://pep8-ja.readthedocs.io/ja/latest/)

[Python命名規則（PEP8より)](https://qiita.com/shiracamus/items/bc3bdfc206b39e0a75b2)

[[Pythonコーディング規約]PEP8を読み解く](https://qiita.com/simonritchie/items/bb06a7521ae6560738a7#%E5%91%BD%E5%90%8D%E8%A6%8F%E5%89%87)

## 設計書
- Main : シミュレーション実行プログラム
- Packet : パケットの情報群
    - インスタンス変数
        - living_time: パケット生存時間
        - TTL: パケット最大生存時間
        - content_id: コンテンツのID(URLのようなもの)
        - content_positions[]: コンテンツのIDを持った端末の位置情報
        - position_node: パケットがあるnode番号
        - trace[]: 辿った経路
    - メソッド
        - init: 初期化
- Node : ノードが行う処理，情報
    - インスタンス変数
        - position(x,y): ノードの座標(x,y)
        - neighbor[]: ノードが通信可能なNode
        - energy: ノードの電池
        - buffer_occupancy: ノードのバッファ占有率
        - content_store[content_id, data]: コンテンツのIDとデータの辞典
        - pit[contente_id, face]: Interestパケットが受信された時の履歴．face:次に送るノード
        - fib[content_id, face]: Dataパケットが受信された時の履歴．
    - メソッド
        - init: ノードの初期化
        - move: ノードの移動
        - sendHello: neighberの更新
        - selectNext: 次のノードの選択．Q(流量)の大きさ
        - sendPacket: パケットの送信．
        - getPacket: パケットの取得．
        - updateQ: 流量の更新
- Slime : ノード内で行う最短経路探索プログラム
    - インスタンス変数
        - conductivity[]: 接続されたノード間の伝導率
        - length[]:　接続されたノード間の距離
        - pressure[]: 接続されたノード間の圧力差
        - quantity[]: 接続されたノード間の流量
    - メソッド
        - init: 初期化
        - dD: Dの時間変化
        - dP: Pの時間変化
        - update_q: 流量の更新
- Export : グラフの描画，ファイル出力を行う
    - 