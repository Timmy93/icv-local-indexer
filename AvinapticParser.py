import re

class AvinapticParser:
    def __init__(self, report):
        self.content = report
        self.data = {}
        self._parse_report()

    def _parse_report(self):
        # Estrarre le informazioni principali
        self.data["file_name"] = self._extract_field(self.content, r"Nome:\s(.+)")
        self.data["file_size"] = self._extract_field(self.content, r"Dimensione:\s(.+bytes)")
        self.data["duration"] = self._extract_field(self.content, r"Durata:\s([\d:]+)")
        self.data["resolution"] = self._extract_field(self.content, r"Risoluzione:\s([\dx]+)")
        self.data["video_codec"] = self._extract_field(self.content, r"Codec ID:\s(V_.+)")
        self.data["audio_tracks"] = self._extract_audio_tracks(self.content)
        self.data["chapters"] = self._extract_chapters(self.content)

    def _extract_field(self, text, pattern):
        match = re.search(pattern, text)
        return match.group(1) if match else None

    def _extract_audio_tracks(self, text):
        tracks = re.findall(r"\[ Traccia audio nr\.\s(\d+)\s\].*?Codec ID:\s(.+?)\n.*?Canali:\s(\d+)", text, re.DOTALL)
        return [{"track_number": int(track[0]), "codec": track[1], "channels": int(track[2])} for track in tracks]

    def _extract_chapters(self, text):
        chapters = re.findall(r"(\d{2}:\d{2}:\d{2},\d{3})-(\d{2}:\d{2}:\d{2},\d{3}):\sCapitolo\s\d+\s{.+}", text)
        return [{"start_time": chapter[0], "end_time": chapter[1]} for chapter in chapters]

    def get_summary(self):
        return {
            "File Name": self.data.get("file_name"),
            "File Size": self.data.get("file_size"),
            "Duration": self.data.get("duration"),
            "Resolution": self.data.get("resolution"),
            "Video Codec": self.data.get("video_codec"),
            "Audio Tracks": len(self.data.get("audio_tracks", [])),
            "Chapters": len(self.data.get("chapters", [])),
        }

    def __repr__(self):
        return f"VideoReportParser({self.data})"

