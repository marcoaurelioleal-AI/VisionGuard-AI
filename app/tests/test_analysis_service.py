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
    assert context == "cena urbana ou de transito"
    assert average_confidence == 0.85
    assert recommendations


def test_analysis_service_generates_specific_tech_insight() -> None:
    faces = [FaceBox(x=20, y=30, width=90, height=90)]
    objects = [
        DetectedObject(
            label="person",
            confidence=0.9,
            box=ObjectBox(x1=10, y1=10, x2=200, y2=400),
        ),
        DetectedObject(
            label="cell phone",
            confidence=0.45,
            box=ObjectBox(x1=60, y1=220, x2=130, y2=270),
        ),
        DetectedObject(
            label="tv",
            confidence=0.31,
            box=ObjectBox(x1=300, y1=30, x2=600, y2=260),
        ),
    ]

    summary, risk_level, context, recommendations, average_confidence = (
        analysis_service.generate_summary(faces, objects)
    )

    assert "celular/tablet" in summary
    assert "tela/TV" in summary
    assert "tela/TV ao fundo" in summary
    assert context == "ambiente corporativo ou tecnologico com pessoas"
    assert risk_level == "baixa confianca"
    assert average_confidence == 0.55
    assert any("Objetos relevantes" in item for item in recommendations)
