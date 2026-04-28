from types import SimpleNamespace

from app.services.object_detection_service import ObjectDetectionService


class FakeValue:
    def __init__(self, value: float) -> None:
        self.value = value

    def __getitem__(self, index: int) -> float:
        return self.value


class FakeCoordinates:
    def __init__(self, coordinates: list[float]) -> None:
        self.coordinates = coordinates

    def __getitem__(self, index: int) -> "FakeCoordinates":
        return self

    def tolist(self) -> list[float]:
        return self.coordinates


def make_fake_box(confidence: float, class_id: int = 0) -> SimpleNamespace:
    return SimpleNamespace(
        xyxy=FakeCoordinates([10.0, 20.0, 110.0, 220.0]),
        conf=FakeValue(confidence),
        cls=FakeValue(class_id),
    )


def test_results_below_confidence_threshold_are_filtered() -> None:
    service = ObjectDetectionService()
    fake_results = [
        SimpleNamespace(
            names={0: "person"},
            boxes=[
                make_fake_box(confidence=0.39),
                make_fake_box(confidence=0.40),
                make_fake_box(confidence=0.91),
            ],
        )
    ]

    objects = service._results_to_objects(fake_results, confidence_threshold=0.40)

    assert len(objects) == 2
    assert [detected_object.confidence for detected_object in objects] == [0.4, 0.91]


def test_results_are_filtered_by_allowed_classes() -> None:
    service = ObjectDetectionService()
    fake_results = [
        SimpleNamespace(
            names={0: "person", 1: "car", 2: "dog"},
            boxes=[
                make_fake_box(confidence=0.95, class_id=0),
                make_fake_box(confidence=0.95, class_id=1),
                make_fake_box(confidence=0.95, class_id=2),
            ],
        )
    ]

    objects = service._results_to_objects(
        fake_results,
        confidence_threshold=0.40,
        allowed_classes={"person", "dog"},
    )

    assert [detected_object.label for detected_object in objects] == ["person", "dog"]
