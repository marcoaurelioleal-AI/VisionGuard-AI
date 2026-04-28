import json
import sqlite3
from collections import Counter

from app.schemas.analysis import AnalysisHistoryItem, ImageAnalysisResponse
from app.schemas.face import FaceBox
from app.schemas.object import DetectedObject


class AnalysisService:
    def generate_summary(
        self,
        faces: list[FaceBox],
        objects: list[DetectedObject],
    ) -> tuple[str, str, str, list[str], float | None]:
        average_confidence = self.calculate_average_confidence(objects)
        labels = [detected_object.label for detected_object in objects]
        label_counts = Counter(labels)
        context = self.detect_context(label_counts)
        risk_level = self.estimate_risk_level(faces, label_counts, average_confidence)
        recommendations = self.generate_recommendations(
            faces,
            objects,
            risk_level,
            average_confidence,
        )

        if labels:
            top_labels = ", ".join(
                f"{label} ({count})" for label, count in label_counts.most_common(4)
            )
        else:
            top_labels = "nenhum objeto relevante"

        summary = (
            f"A análise encontrou {len(faces)} face(s) e {len(objects)} objeto(s). "
            f"Principais detecções: {top_labels}. "
            f"O contexto visual estimado é '{context}' com nível de atenção '{risk_level}'."
        )

        return summary, risk_level, context, recommendations, average_confidence

    @staticmethod
    def calculate_average_confidence(objects: list[DetectedObject]) -> float | None:
        if not objects:
            return None

        average = sum(detected_object.confidence for detected_object in objects) / len(
            objects
        )
        return round(average, 2)

    @staticmethod
    def detect_context(label_counts: Counter[str]) -> str:
        labels = set(label_counts)

        if {"car", "bus", "truck", "motorcycle", "bicycle"} & labels:
            return "cena urbana ou de trânsito"

        if {"dog", "cat", "bird", "horse", "sheep", "cow"} & labels:
            return "cena com animal ou ambiente externo"

        if {"laptop", "keyboard", "mouse", "cell phone", "tv"} & labels:
            return "cena de tecnologia ou ambiente de trabalho"

        if "person" in labels:
            return "cena com foco em pessoas"

        return "imagem geral"

    @staticmethod
    def estimate_risk_level(
        faces: list[FaceBox],
        label_counts: Counter[str],
        average_confidence: float | None,
    ) -> str:
        attention_labels = {"knife", "scissors", "sports ball", "baseball bat"}

        if attention_labels & set(label_counts):
            return "atenção"

        if label_counts.get("person", 0) >= 5 or len(faces) >= 5:
            return "médio"

        if average_confidence is not None and average_confidence < 0.5:
            return "baixa confiança"

        return "baixo"

    @staticmethod
    def generate_recommendations(
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
            recommendations.append("Nenhum objeto passou pelo filtro de confianca.")
        else:
            recommendations.append("Objetos detectados com labels e confianca YOLO.")

        if average_confidence is not None and average_confidence < 0.5:
            recommendations.append("Considere reduzir o threshold ou usar uma imagem mais nítida.")

        if risk_level in {"atenção", "médio"}:
            recommendations.append("Revise a cena manualmente antes de tomar decisões.")

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
