import json
import sqlite3
from collections import Counter

from app.schemas.analysis import AnalysisHistoryItem, ImageAnalysisResponse
from app.schemas.face import FaceBox
from app.schemas.object import DetectedObject

LABEL_TRANSLATIONS = {
    "person": "pessoa",
    "cell phone": "celular/tablet",
    "laptop": "notebook/tablet",
    "tv": "tela/TV",
    "book": "livro/caderno",
    "potted plant": "planta",
    "chair": "cadeira",
    "dining table": "mesa",
    "handbag": "bolsa",
    "backpack": "mochila",
    "bottle": "garrafa",
    "cup": "copo",
    "keyboard": "teclado",
    "mouse": "mouse",
    "remote": "controle remoto",
    "car": "carro",
    "bus": "onibus",
    "truck": "caminhao",
    "motorcycle": "moto",
    "bicycle": "bicicleta",
    "dog": "cachorro",
    "cat": "gato",
}

HANDHELD_LABELS = {
    "cell phone",
    "laptop",
    "book",
    "handbag",
    "backpack",
    "bottle",
    "cup",
    "remote",
}
TECH_LABELS = {"cell phone", "laptop", "keyboard", "mouse", "tv", "remote"}
FURNITURE_LABELS = {"chair", "dining table", "couch", "bed"}
VEHICLE_LABELS = {"car", "bus", "truck", "motorcycle", "bicycle"}
ANIMAL_LABELS = {"dog", "cat", "bird", "horse", "sheep", "cow"}


class AnalysisService:
    def generate_summary(
        self,
        faces: list[FaceBox],
        objects: list[DetectedObject],
    ) -> tuple[str, str, str, list[str], float | None]:
        average_confidence = self.calculate_average_confidence(objects)
        has_low_confidence_object = any(
            detected_object.confidence < 0.5 for detected_object in objects
        )
        labels = [detected_object.label for detected_object in objects]
        label_counts = Counter(labels)
        context = self.detect_context(label_counts)
        risk_level = self.estimate_risk_level(
            faces,
            label_counts,
            average_confidence,
            has_low_confidence_object,
        )
        recommendations = self.generate_recommendations(
            faces,
            objects,
            risk_level,
            average_confidence,
        )
        top_labels = self.format_detected_labels(label_counts)
        scene_notes = self.generate_scene_notes(label_counts)

        summary = (
            f"A analise encontrou {len(faces)} face(s) e {len(objects)} objeto(s). "
            f"Principais achados: {top_labels}. "
            f"Contexto provavel: {context}. "
            f"Nivel de atencao: {risk_level}."
        )

        if scene_notes:
            summary = f"{summary} {' '.join(scene_notes)}"

        return summary, risk_level, context, recommendations, average_confidence

    @staticmethod
    def calculate_average_confidence(objects: list[DetectedObject]) -> float | None:
        if not objects:
            return None

        average = sum(detected_object.confidence for detected_object in objects) / len(
            objects
        )
        return round(average, 2)

    @classmethod
    def translate_label(cls, label: str) -> str:
        return LABEL_TRANSLATIONS.get(label, label)

    @classmethod
    def format_detected_labels(cls, label_counts: Counter[str]) -> str:
        if not label_counts:
            return "nenhum objeto relevante acima do limite de confianca"

        return ", ".join(
            f"{cls.translate_label(label)} ({count})"
            for label, count in label_counts.most_common(5)
        )

    @staticmethod
    def generate_scene_notes(label_counts: Counter[str]) -> list[str]:
        labels = set(label_counts)
        notes: list[str] = []

        if "person" in labels and HANDHELD_LABELS & labels:
            notes.append(
                "Ha pessoas na cena com itens proximos as maos, como dispositivos ou objetos pessoais."
            )

        if "tv" in labels:
            notes.append("Tambem foi identificada uma tela/TV ao fundo da imagem.")

        if "person" in labels and labels == {"person"}:
            notes.append(
                "Somente pessoas passaram pelo filtro atual; reduza o threshold ou use filtros de objetos para buscar itens menores."
            )

        return notes

    @staticmethod
    def detect_context(label_counts: Counter[str]) -> str:
        labels = set(label_counts)

        if TECH_LABELS & labels and "person" in labels:
            return "ambiente corporativo ou tecnologico com pessoas"

        if TECH_LABELS & labels:
            return "cena de tecnologia ou ambiente de trabalho"

        if VEHICLE_LABELS & labels:
            return "cena urbana ou de transito"

        if ANIMAL_LABELS & labels:
            return "cena com animal ou ambiente externo"

        if FURNITURE_LABELS & labels and "person" in labels:
            return "ambiente interno com pessoas"

        if "person" in labels:
            return "cena com foco em pessoas"

        return "imagem geral"

    @staticmethod
    def estimate_risk_level(
        faces: list[FaceBox],
        label_counts: Counter[str],
        average_confidence: float | None,
        has_low_confidence_object: bool = False,
    ) -> str:
        attention_labels = {"knife", "scissors", "sports ball", "baseball bat"}

        if attention_labels & set(label_counts):
            return "atencao"

        if label_counts.get("person", 0) >= 5 or len(faces) >= 5:
            return "medio"

        if has_low_confidence_object or (
            average_confidence is not None and average_confidence < 0.5
        ):
            return "baixa confianca"

        return "baixo"

    def generate_recommendations(
        self,
        faces: list[FaceBox],
        objects: list[DetectedObject],
        risk_level: str,
        average_confidence: float | None,
    ) -> list[str]:
        recommendations: list[str] = []

        if not faces:
            recommendations.append("Nenhuma face foi detectada na imagem.")
        else:
            recommendations.append("Faces detectadas com coordenadas prontas para uso.")

        if not objects:
            recommendations.append(
                "Nenhum objeto passou pelo filtro atual. Para objetos pequenos, teste threshold entre 0.25 e 0.35."
            )
        else:
            label_counts = Counter(detected_object.label for detected_object in objects)
            readable_labels = self.format_detected_labels(label_counts)
            recommendations.append(f"Objetos relevantes identificados: {readable_labels}.")

        labels = {detected_object.label for detected_object in objects}
        if "person" in labels and HANDHELD_LABELS & labels:
            recommendations.append(
                "A cena indica pessoas segurando ou proximas de itens detectaveis; revise a imagem anotada para confirmar."
            )

        if average_confidence is not None and average_confidence < 0.5:
            recommendations.append(
                "Ha deteccoes com confianca moderada/baixa. Use imagem mais nitida ou confirme manualmente."
            )

        if risk_level in {"atencao", "medio"}:
            recommendations.append("Revise a cena manualmente antes de tomar decisoes.")

        return recommendations

    def save_analysis(
        self,
        connection: sqlite3.Connection,
        filename: str,
        faces: list[FaceBox],
        objects: list[DetectedObject],
        output_path: str | None,
    ) -> ImageAnalysisResponse:
        summary, risk_level, context, recommendations, average_confidence = (
            self.generate_summary(faces, objects)
        )
        cursor = connection.execute(
            """
            INSERT INTO analysis_records (
                filename,
                summary,
                risk_level,
                detected_context,
                recommendations,
                total_faces,
                total_objects,
                average_confidence,
                output_path
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                filename,
                summary,
                risk_level,
                context,
                json.dumps(recommendations),
                len(faces),
                len(objects),
                average_confidence,
                output_path,
            ),
        )
        connection.commit()

        return ImageAnalysisResponse(
            id=int(cursor.lastrowid),
            filename=filename,
            summary=summary,
            risk_level=risk_level,
            detected_context=context,
            recommendations=recommendations,
            total_faces=len(faces),
            total_objects=len(objects),
            average_confidence=average_confidence,
            output_path=output_path,
            faces=faces,
            objects=objects,
        )

    @staticmethod
    def list_history(
        connection: sqlite3.Connection,
        limit: int,
    ) -> list[AnalysisHistoryItem]:
        rows = connection.execute(
            """
            SELECT
                id,
                filename,
                summary,
                risk_level,
                detected_context,
                total_faces,
                total_objects,
                average_confidence,
                output_path,
                created_at
            FROM analysis_records
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

        return [AnalysisHistoryItem(**dict(row)) for row in rows]


analysis_service = AnalysisService()
