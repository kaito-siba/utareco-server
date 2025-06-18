"""sqlite-vecを使用したベクトル検索管理クラス."""

import sqlite3
from pathlib import Path

import numpy as np
import sqlite_vec
from sqlite_vec import serialize_float32


class SQLiteVecManager:
    """sqlite-vecを使用したHPCP特徴量ベクトル検索管理クラス.

    フレーム単位のHPCP特徴量と楽曲レベルの統計的特徴量を管理し、
    類似楽曲検索機能を提供する。
    """

    def __init__(self, db_path: str = "utareco.db"):
        """初期化.

        Args:
            db_path: データベースファイルのパス
        """
        self.db_path = Path(db_path)
        self._connection: sqlite3.Connection | None = None

    def _get_connection(self) -> sqlite3.Connection:
        """データベース接続を取得する（sqlite-vec拡張付き）.

        Returns:
            sqlite3データベース接続
        """
        if self._connection is None:
            self._connection = sqlite3.connect(str(self.db_path))
            self._connection.enable_load_extension(True)
            sqlite_vec.load(self._connection)
            self._connection.enable_load_extension(False)
        return self._connection

    def close(self):
        """データベース接続を閉じる."""
        if self._connection:
            self._connection.close()
            self._connection = None

    def initialize_vector_tables(self):
        """ベクトル検索用テーブルを初期化する."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # HPCP特徴量ベクトルテーブル（フレーム単位）
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS hpcp_frames USING vec0(
                recording_id INTEGER,
                frame_index INTEGER,
                hpcp_vector FLOAT[12]
            )
        """)

        # 楽曲レベル統計的特徴量ベクトルテーブル
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS hpcp_summary USING vec0(
                recording_id INTEGER,
                mean_vector FLOAT[12],
                std_vector FLOAT[12],
                dominant_chord FLOAT[12]
            )
        """)

        conn.commit()

    def store_hpcp_vectors(self, recording_id: int, hpcp_array: np.ndarray):
        """HPCP特徴量をベクトルDBに格納する.

        Args:
            recording_id: 録音データID
            hpcp_array: HPCP特徴量配列（フレーム数 x 12）

        Raises:
            ValueError: HPCP配列の形状が不正な場合
        """
        if hpcp_array.ndim != 2 or hpcp_array.shape[1] != 12:
            raise ValueError(
                f"HPCP配列は(フレーム数, 12)の形状である必要があります。"
                f"実際の形状: {hpcp_array.shape}"
            )

        conn = self._get_connection()
        cursor = conn.cursor()

        # 既存のフレームデータを削除
        cursor.execute(
            "DELETE FROM hpcp_frames WHERE recording_id = ?", (recording_id,)
        )

        # フレーム単位でベクトルを格納
        for frame_index, hpcp_vector in enumerate(hpcp_array):
            # float32形式でシリアライズ
            vector_data = serialize_float32(hpcp_vector.astype(np.float32))
            cursor.execute(
                "INSERT INTO hpcp_frames(recording_id, frame_index, hpcp_vector) VALUES (?, ?, ?)",
                (recording_id, frame_index, vector_data),
            )

        # 楽曲レベル統計的特徴量を計算・格納
        self._store_summary_vectors(cursor, recording_id, hpcp_array)

        conn.commit()

    def _store_summary_vectors(
        self, cursor: sqlite3.Cursor, recording_id: int, hpcp_array: np.ndarray
    ):
        """楽曲レベル統計的特徴量を計算・格納する.

        Args:
            cursor: データベースカーソル
            recording_id: 録音データID
            hpcp_array: HPCP特徴量配列（フレーム数 x 12）
        """
        # 既存のサマリーデータを削除
        cursor.execute(
            "DELETE FROM hpcp_summary WHERE recording_id = ?", (recording_id,)
        )

        # 統計的特徴量を計算
        mean_vector = np.mean(hpcp_array, axis=0).astype(np.float32)
        std_vector = np.std(hpcp_array, axis=0).astype(np.float32)

        # 最も強いHPCPフレームを取得（各フレームのL2ノルムが最大）
        frame_norms = np.linalg.norm(hpcp_array, axis=1)
        dominant_frame_idx = np.argmax(frame_norms)
        dominant_chord = hpcp_array[dominant_frame_idx].astype(np.float32)

        # サマリーベクトルを格納
        cursor.execute(
            "INSERT INTO hpcp_summary(recording_id, mean_vector, std_vector, dominant_chord) VALUES (?, ?, ?, ?)",
            (
                recording_id,
                serialize_float32(mean_vector),
                serialize_float32(std_vector),
                serialize_float32(dominant_chord),
            ),
        )

    def search_similar_recordings_by_frames(
        self, query_hpcp: np.ndarray, k: int = 5
    ) -> list[tuple[int, float]]:
        """フレーム単位でのHPCP特徴量による類似楽曲検索.

        Args:
            query_hpcp: クエリHPCP特徴量配列（フレーム数 x 12）
            k: 取得する類似楽曲数

        Returns:
            (recording_id, 平均距離)のタプルリスト
        """
        if query_hpcp.ndim != 2 or query_hpcp.shape[1] != 12:
            raise ValueError(
                f"クエリHPCP配列は(フレーム数, 12)の形状である必要があります。"
                f"実際の形状: {query_hpcp.shape}"
            )

        conn = self._get_connection()
        cursor = conn.cursor()

        # 各フレームに対して最も類似するベクトルを検索
        recording_distances = {}

        for frame_hpcp in query_hpcp:
            vector_data = serialize_float32(frame_hpcp.astype(np.float32))

            # フレーム単位で類似検索
            cursor.execute(
                """
                SELECT recording_id, distance 
                FROM hpcp_frames 
                WHERE hpcp_vector MATCH ?
                ORDER BY distance 
                LIMIT 20
            """,
                (vector_data,),
            )

            results = cursor.fetchall()

            # 録音データIDごとに距離を蓄積
            for recording_id, distance in results:
                if recording_id not in recording_distances:
                    recording_distances[recording_id] = []
                recording_distances[recording_id].append(distance)

        # 各録音データの平均距離を計算
        avg_distances = []
        for recording_id, distances in recording_distances.items():
            avg_distance = np.mean(distances)
            avg_distances.append((recording_id, avg_distance))

        # 距離でソートしてトップKを返す
        avg_distances.sort(key=lambda x: x[1])
        return avg_distances[:k]

    def search_similar_recordings_by_summary(
        self, query_hpcp: np.ndarray, k: int = 5, method: str = "mean"
    ) -> list[tuple[int, float]]:
        """楽曲レベル統計的特徴量による類似楽曲検索.

        Args:
            query_hpcp: クエリHPCP特徴量配列（フレーム数 x 12）
            k: 取得する類似楽曲数
            method: 検索方法 ("mean", "dominant", "std")

        Returns:
            (recording_id, 距離)のタプルリスト
        """
        if query_hpcp.ndim != 2 or query_hpcp.shape[1] != 12:
            raise ValueError(
                f"クエリHPCP配列は(フレーム数, 12)の形状である必要があります。"
                f"実際の形状: {query_hpcp.shape}"
            )

        # クエリの統計的特徴量を計算
        if method == "mean":
            query_vector = np.mean(query_hpcp, axis=0).astype(np.float32)
            column_name = "mean_vector"
        elif method == "dominant":
            frame_norms = np.linalg.norm(query_hpcp, axis=1)
            dominant_idx = np.argmax(frame_norms)
            query_vector = query_hpcp[dominant_idx].astype(np.float32)
            column_name = "dominant_chord"
        elif method == "std":
            query_vector = np.std(query_hpcp, axis=0).astype(np.float32)
            column_name = "std_vector"
        else:
            raise ValueError(f"無効な検索方法: {method}")

        conn = self._get_connection()
        cursor = conn.cursor()

        # ベクトル検索を実行
        vector_data = serialize_float32(query_vector)
        cursor.execute(
            f"""
            SELECT recording_id, distance 
            FROM hpcp_summary 
            WHERE {column_name} MATCH ?
            ORDER BY distance 
            LIMIT ?
        """,
            (vector_data, k),
        )

        return cursor.fetchall()

    def delete_recording_vectors(self, recording_id: int):
        """指定した録音データのベクトルデータを削除する.

        Args:
            recording_id: 録音データID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM hpcp_frames WHERE recording_id = ?", (recording_id,)
        )
        cursor.execute(
            "DELETE FROM hpcp_summary WHERE recording_id = ?", (recording_id,)
        )

        conn.commit()

    def get_vector_stats(self) -> dict:
        """ベクトルデータベースの統計情報を取得する.

        Returns:
            統計情報の辞書
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # フレーム数をカウント
        cursor.execute("SELECT COUNT(*) FROM hpcp_frames")
        frame_count = cursor.fetchone()[0]

        # 録音データ数をカウント
        cursor.execute("SELECT COUNT(DISTINCT recording_id) FROM hpcp_frames")
        recording_count = cursor.fetchone()[0]

        # サマリーデータ数をカウント
        cursor.execute("SELECT COUNT(*) FROM hpcp_summary")
        summary_count = cursor.fetchone()[0]

        return {
            "total_frames": frame_count,
            "total_recordings": recording_count,
            "summary_records": summary_count,
        }
