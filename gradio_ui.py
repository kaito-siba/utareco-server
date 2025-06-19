"""Gradio UI for UtaReco API testing."""

import json
import os

import gradio as gr
import requests


class UtaRecoAPIClient:
    """UtaReco API client for Gradio UI."""

    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        """Initialize API client.

        Args:
            base_url: Base URL of the UtaReco API server
        """
        self.base_url = base_url

    def health_check(self) -> tuple[str, str]:
        """Check API server health status.

        Returns:
            Tuple of (status, details)
        """
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            response.raise_for_status()
            data = response.json()
            return data.get("status", "unknown"), json.dumps(
                data, indent=2, ensure_ascii=False
            )
        except requests.RequestException as e:
            return "error", f"API server connection failed: {str(e)}"

    def test_essentia(self) -> tuple[str, str]:
        """Test Essentia functionality.

        Returns:
            Tuple of (status, details)
        """
        try:
            response = requests.get(f"{self.base_url}/test-essentia", timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("status", "unknown"), json.dumps(
                data, indent=2, ensure_ascii=False
            )
        except requests.RequestException as e:
            return "error", f"Essentia test failed: {str(e)}"

    def extract_hpcp(self, audio_file: str) -> tuple[str, str]:
        """Extract HPCP features from audio file.

        Args:
            audio_file: Path to audio file

        Returns:
            Tuple of (status, response_json)
        """
        if not audio_file:
            return "error", "No audio file provided"

        try:
            with open(audio_file, "rb") as f:
                files = {"file": (os.path.basename(audio_file), f, "audio/wav")}
                response = requests.post(
                    f"{self.base_url}/api/v1/hpcp/extract-only", files=files, timeout=30
                )
                response.raise_for_status()
                data = response.json()
                return "success", json.dumps(data, indent=2, ensure_ascii=False)
        except requests.RequestException as e:
            return "error", f"HPCP extraction failed: {str(e)}"
        except Exception as e:
            return "error", f"Unexpected error: {str(e)}"

    def search_similar(
        self,
        audio_file: str,
        search_method: str = "frames",
        threshold: float = 0.89,
        limit: int = 10,
    ) -> tuple[str, str]:
        """Search for similar recordings.

        Args:
            audio_file: Path to audio file
            search_method: Search method (frames, average, median)
            threshold: Similarity threshold
            limit: Maximum number of results

        Returns:
            Tuple of (status, response_json)
        """
        if not audio_file:
            return "error", "No audio file provided"

        try:
            # First extract HPCP features
            with open(audio_file, "rb") as f:
                files = {"file": (os.path.basename(audio_file), f, "audio/wav")}
                hpcp_response = requests.post(
                    f"{self.base_url}/api/v1/hpcp/extract-only", files=files, timeout=30
                )
                hpcp_response.raise_for_status()
                hpcp_data = hpcp_response.json()

            # Then search for similar recordings
            search_request = {
                "hpcp_data": hpcp_data["hpcp_data"],
                "search_method": search_method,
                "limit": limit,
            }

            search_response = requests.post(
                f"{self.base_url}/api/v1/hpcp/search",
                json=search_request,
                params={"threshold": threshold},
                timeout=30,
            )
            search_response.raise_for_status()
            data = search_response.json()
            return "success", json.dumps(data, indent=2, ensure_ascii=False)

        except requests.RequestException as e:
            return "error", f"Search failed: {str(e)}"
        except Exception as e:
            return "error", f"Unexpected error: {str(e)}"

    def get_vector_stats(self) -> tuple[str, str]:
        """Get vector database statistics.

        Returns:
            Tuple of (status, stats_json)
        """
        try:
            response = requests.get(f"{self.base_url}/api/v1/hpcp/stats", timeout=10)
            response.raise_for_status()
            data = response.json()
            return "success", json.dumps(data, indent=2, ensure_ascii=False)
        except requests.RequestException as e:
            return "error", f"Stats retrieval failed: {str(e)}"

    def save_recording_with_hpcp(
        self,
        audio_file: str,
        title: str,
        artist: str,
        recording_name: str,
        song_id: int | None = None,
    ) -> tuple[str, str]:
        """Save recording with HPCP features to database.

        Args:
            audio_file: Path to audio file
            title: Song title (for new songs)
            artist: Artist name (for new songs)
            recording_name: Recording name
            song_id: Existing song ID (if adding to existing song)

        Returns:
            Tuple of (status, response_json)
        """
        if not audio_file:
            return "error", "No audio file provided"

        if not song_id and not title:
            return "error", "Either song_id or title must be provided"

        if song_id and title:
            return "error", "Cannot specify both song_id and title"

        if not recording_name:
            return "error", "Recording name is required"

        try:
            # First extract HPCP features
            with open(audio_file, "rb") as f:
                files = {"file": (os.path.basename(audio_file), f, "audio/wav")}
                hpcp_response = requests.post(
                    f"{self.base_url}/api/v1/hpcp/extract-only", files=files, timeout=30
                )
                hpcp_response.raise_for_status()
                hpcp_data = hpcp_response.json()

            # Prepare recording creation request
            create_request = {
                "hpcp_data": hpcp_data["hpcp_data"],
                "audio_file_name": os.path.basename(audio_file),
                "recording_name": recording_name.strip(),
            }

            if song_id:
                create_request["song_id"] = song_id
            else:
                create_request["title"] = title.strip()
                if artist:
                    create_request["artist"] = artist.strip()

            # Create recording with HPCP
            create_response = requests.post(
                f"{self.base_url}/api/v1/recordings/create",
                json=create_request,
                timeout=30,
            )
            create_response.raise_for_status()
            data = create_response.json()
            return "success", json.dumps(data, indent=2, ensure_ascii=False)

        except requests.RequestException as e:
            return "error", f"Recording creation failed: {str(e)}"
        except Exception as e:
            return "error", f"Unexpected error: {str(e)}"

    def get_recordings_list(self, skip: int = 0, limit: int = 100) -> tuple[str, str]:
        """Get list of recordings.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (status, recordings_json)
        """
        try:
            params = {"skip": skip, "limit": limit}
            response = requests.get(
                f"{self.base_url}/api/v1/recordings/", params=params, timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return "success", json.dumps(data, indent=2, ensure_ascii=False)
        except requests.RequestException as e:
            return "error", f"Recordings list retrieval failed: {str(e)}"


def create_gradio_interface():
    """Create Gradio interface for UtaReco API testing."""

    # Initialize API client
    api_client = UtaRecoAPIClient()

    with gr.Blocks(
        title="UtaReco API Test Interface",
        theme=gr.themes.Soft(),
    ) as demo:
        gr.Markdown("# 🎵 UtaReco API Test Interface")
        gr.Markdown("音楽認識API (UtaReco) のテスト用インターフェース")

        with gr.Tabs():
            # API Health Check Tab
            with gr.TabItem("🏥 API Health Check"):
                gr.Markdown("### API Server Status")

                with gr.Row():
                    health_button = gr.Button("Check Health Status", variant="primary")
                    essentia_button = gr.Button("Test Essentia", variant="secondary")

                health_status = gr.Textbox(
                    label="Health Status", interactive=False, max_lines=1
                )
                health_details = gr.Code(label="Health Details", language="json")

                essentia_status = gr.Textbox(
                    label="Essentia Status", interactive=False, max_lines=1
                )
                essentia_details = gr.Code(label="Essentia Details", language="json")

                health_button.click(
                    fn=api_client.health_check, outputs=[health_status, health_details]
                )

                essentia_button.click(
                    fn=api_client.test_essentia,
                    outputs=[essentia_status, essentia_details],
                )

            # HPCP Extraction Tab
            with gr.TabItem("🎼 HPCP Extraction"):
                gr.Markdown("### HPCP特徴量抽出テスト")
                gr.Markdown(
                    "音声ファイルからHPCP特徴量を抽出します（データベース保存なし）"
                )

                with gr.Row():
                    hpcp_audio = gr.Audio(
                        label="音声ファイル", type="filepath", sources=["upload"]
                    )

                hpcp_extract_button = gr.Button(
                    "Extract HPCP Features", variant="primary"
                )

                hpcp_status = gr.Textbox(
                    label="Extraction Status", interactive=False, max_lines=1
                )
                hpcp_result = gr.Code(label="HPCP Extraction Result", language="json")

                hpcp_extract_button.click(
                    fn=api_client.extract_hpcp,
                    inputs=[hpcp_audio],
                    outputs=[hpcp_status, hpcp_result],
                )

            # Similarity Search Tab
            with gr.TabItem("🔍 Similarity Search"):
                gr.Markdown("### 類似楽曲検索テスト")
                gr.Markdown(
                    "アップロードした音声ファイルに類似する楽曲をデータベースから検索します"
                )

                with gr.Row():
                    search_audio = gr.Audio(
                        label="検索用音声ファイル", type="filepath", sources=["upload"]
                    )

                with gr.Row():
                    search_method = gr.Radio(
                        choices=[
                            "frames",
                            "mean",
                            "dominant",
                            "std",
                        ],
                        value="frames",
                        label="検索方法",
                        info="frames: フレーム単位（推奨）, mean: 平均, dominant: 主要和音, std: 標準偏差",
                    )

                    threshold = gr.Number(
                        value=0.89,
                        minimum=0.0,
                        maximum=1.0,
                        step=0.01,
                        label="類似度閾値",
                        info="この値以上の類似度を持つ楽曲のみ返します",
                    )

                    limit = gr.Number(
                        value=10,
                        minimum=1,
                        maximum=100,
                        step=1,
                        label="最大結果数",
                        info="返す結果の最大数",
                    )

                search_button = gr.Button("Search Similar Songs", variant="primary")

                search_status = gr.Textbox(
                    label="Search Status", interactive=False, max_lines=1
                )
                search_result = gr.Code(label="Search Results", language="json")

                search_button.click(
                    fn=api_client.search_similar,
                    inputs=[search_audio, search_method, threshold, limit],
                    outputs=[search_status, search_result],
                )

            # Save Recording Tab
            with gr.TabItem("💾 Save Recording"):
                gr.Markdown("### 録音データ保存")
                gr.Markdown("音声ファイルとHPCP特徴量をデータベースに保存します")

                with gr.Row():
                    save_audio = gr.Audio(
                        label="音声ファイル", type="filepath", sources=["upload"]
                    )

                gr.Markdown("#### 楽曲情報")

                with gr.Row():
                    save_mode = gr.Radio(
                        choices=["new_song", "existing_song"],
                        value="new_song",
                        label="保存モード",
                        info="新規楽曲として保存 or 既存楽曲への音源追加",
                    )

                # 新規楽曲用フィールド
                with gr.Row() as new_song_row:
                    title = gr.Textbox(
                        label="楽曲タイトル", placeholder="必須", max_lines=1
                    )
                    artist = gr.Textbox(
                        label="アーティスト名", placeholder="任意", max_lines=1
                    )

                # 既存楽曲用フィールド
                with gr.Row(visible=False) as existing_song_row:
                    song_id = gr.Number(
                        label="楽曲ID", value=None, precision=0, info="既存楽曲のID"
                    )

                # 共通フィールド
                with gr.Row():
                    recording_name = gr.Textbox(
                        label="録音名",
                        placeholder="例: オリジナル版、ライブ版、カバー版",
                        max_lines=1,
                    )

                save_button = gr.Button("Save Recording to Database", variant="primary")

                save_status = gr.Textbox(
                    label="Save Status", interactive=False, max_lines=1
                )
                save_result = gr.Code(label="Save Result", language="json")

                # モード切り替えのイベント
                def toggle_save_mode(mode):
                    if mode == "new_song":
                        return gr.update(visible=True), gr.update(visible=False)
                    else:
                        return gr.update(visible=False), gr.update(visible=True)

                save_mode.change(
                    fn=toggle_save_mode,
                    inputs=[save_mode],
                    outputs=[new_song_row, existing_song_row],
                )

                # 保存処理
                def save_recording_wrapper(
                    audio, mode, title, artist, song_id, recording_name
                ):
                    if mode == "existing_song":
                        return api_client.save_recording_with_hpcp(
                            audio,
                            None,
                            None,
                            recording_name,
                            int(song_id) if song_id is not None else None,
                        )
                    else:
                        return api_client.save_recording_with_hpcp(
                            audio, title, artist, recording_name, None
                        )

                save_button.click(
                    fn=save_recording_wrapper,
                    inputs=[
                        save_audio,
                        save_mode,
                        title,
                        artist,
                        song_id,
                        recording_name,
                    ],
                    outputs=[save_status, save_result],
                )

            # Recordings List Tab
            with gr.TabItem("📋 Recordings List"):
                gr.Markdown("### 録音データ一覧")
                gr.Markdown("データベースに保存されている録音データの一覧を表示します")

                with gr.Row():
                    list_skip = gr.Number(
                        value=0,
                        minimum=0,
                        step=1,
                        label="スキップ数",
                        info="スキップするレコード数",
                    )
                    list_limit = gr.Number(
                        value=100,
                        minimum=1,
                        maximum=1000,
                        step=10,
                        label="取得件数",
                        info="取得するレコード数の上限",
                    )

                list_button = gr.Button("Get Recordings List", variant="primary")

                list_status = gr.Textbox(
                    label="List Status", interactive=False, max_lines=1
                )
                list_result = gr.Code(label="Recordings List", language="json")

                list_button.click(
                    fn=api_client.get_recordings_list,
                    inputs=[list_skip, list_limit],
                    outputs=[list_status, list_result],
                )

            # Database Stats Tab
            with gr.TabItem("📊 Database Stats"):
                gr.Markdown("### データベース統計情報")
                gr.Markdown("ベクトルデータベースの統計情報を表示します")

                stats_button = gr.Button("Get Vector Database Stats", variant="primary")

                stats_status = gr.Textbox(
                    label="Stats Status", interactive=False, max_lines=1
                )
                stats_result = gr.Code(label="Database Statistics", language="json")

                stats_button.click(
                    fn=api_client.get_vector_stats, outputs=[stats_status, stats_result]
                )

        # Footer
        gr.Markdown("---")
        gr.Markdown(
            "💡 **使用方法**: 各タブでAPIの機能をテストできます。\n"
            "- **API Health Check**: サーバーの状態を確認\n"
            "- **HPCP Extraction**: 音声ファイルから特徴量を抽出\n"
            "- **Similarity Search**: 類似楽曲を検索\n"
            "- **Save Recording**: 音声ファイルをデータベースに保存\n"
            "- **Recordings List**: 保存済み録音データ一覧を表示\n"
            "- **Database Stats**: データベース統計を表示"
        )

    return demo


def main():
    """Main function to launch Gradio interface."""
    demo = create_gradio_interface()

    # Launch the interface
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_api=False,
        debug=True,
    )


if __name__ == "__main__":
    main()
