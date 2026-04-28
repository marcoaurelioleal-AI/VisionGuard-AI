from app.schemas.face import FaceBox
from app.schemas.object import DetectedObject, ObjectBox
from app.services.analysis_service import analysis_service


def test_analysis_service_generates_visual_insight() -> None:
    faces = [FaceBox(x=10, y=20, width=80, height=80)]
    objects = [
        DetectedObject(
            label="person",
            confidence=0.9,
            box=ObjectBox(x1=5, y1=5, x2=100, y2=200),
        ),
        DetectedObject(
            label="car",
            confidence=0.8,
            box=ObjectBox(x1=120, y1=40, x2=300, y2=220),
        ),
    ]

    summary, risk_level, context, recommendations, average_confidence = (
        analysis_service.generate_summary(faces, objects)
    )

    assert "1 face" in summary
    assert "2 objeto" in summary
    assert risk_level == "baixo"
    assert context == "cena urbana ou de trânsito"
    assert average_confidence == 0.85
    assert recommendations
