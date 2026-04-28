from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import requests
import streamlit as st

API_BASE_URL = "http://127.0.0.1:8001"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
REQUEST_TIMEOUT_SECONDS = 120
MAX_HISTORY_ITEMS = 5
LOW_CONFIDENCE_WARNING_THRESHOLD = 0.50

PRECISION_MODES = {
    "Rápido": "yolo11n.pt",
    "Balanceado": "yolo11s.pt",
    "Preciso": "yolo11m.pt",
}

COCO_OBJECT_CLASSES_WITHOUT_PERSON = [
    "bicycle",
    "car",
    "motorcycle",
    "airplane",
    "bus",
    "train",
    "truck",
    "boat",
    "traffic light",
    "fire hydrant",
    "stop sign",
    "parking meter",
    "bench",
    "bird",
    "cat",
    "dog",
    "horse",
    "sheep",
    "cow",
    "elephant",
    "bear",
    "zebra",
    "giraffe",
    "backpack",
    "umbrella",
    "handbag",
    "tie",
    "suitcase",
    "frisbee",
    "skis",
    "snowboard",
    "sports ball",
    "kite",
    "baseball bat",
    "baseball glove",
    "skateboard",
    "surfboard",
    "tennis racket",
    "bottle",
    "wine glass",
    "cup",
    "fork",
    "knife",
    "spoon",
    "bowl",
    "banana",
    "apple",
    "sandwich",
    "orange",
    "broccoli",
    "carrot",
    "hot dog",
    "pizza",
    "donut",
    "cake",
    "chair",
    "couch",
    "potted plant",
    "bed",
    "dining table",
    "toilet",
    "tv",
    "laptop",
    "mouse",
    "remote",
    "keyboard",
    "cell phone",
    "microwave",
    "oven",
    "toaster",
    "sink",
    "refrigerator",
    "book",
    "clock",
    "vase",
    "scissors",
    "teddy bear",
    "hair drier",
    "toothbrush",
]

HANDHELD_OBJECT_CLASSES = [
    "cell phone",
    "book",
    "laptop",
    "remote",
    "keyboard",
    "mouse",
    "bottle",
    "cup",
    "fork",
    "knife",
    "spoon",
    "handbag",
    "backpack",
    "umbrella",
    "tie",
    "suitcase",
]

CLASS_FILTERS = {
    "Todos (inclui pessoas)": None,
    "Objetos sem pessoas": COCO_OBJECT_CLASSES_WITHOUT_PERSON,
    "Itens nas mãos": HANDHELD_OBJECT_CLASSES,
    "Pessoas": ["person"],
    "Animais": [
        "bird",
        "cat",
        "dog",
        "horse",
        "sheep",
        "cow",
        "elephant",
        "bear",
        "zebra",
        "giraffe",
    ],
    "Veículos": [
        "bicycle",
        "car",
        "motorcycle",
        "airplane",
        "bus",
        "train",
        "truck",
        "boat",
    ],
    "Alimentos": [
        "banana",
        "apple",
        "sandwich",
        "orange",
        "broccoli",
        "carrot",
        "hot dog",
        "pizza",
        "donut",
        "cake",
    ],
    "Eletrônicos": ["tv", "laptop", "mouse", "remote", "keyboard", "cell phone"],
}

OBJECT_MODE = "Detectar objetos"
FACE_MODE = "Detectar faces"
COMBINED_MODE = "Detectar objetos e faces"
ANNOTATED_OBJECT_MODE = "Gerar imagem anotada de objetos"
ANNOTATED_FACE_MODE = "Gerar imagem anotada de faces"
ANNOTATED_COMBINED_MODE = "Gerar imagem anotada completa"
AI_ANALYSIS_MODE = "Análise inteligente com IA"

DETECTION_MODES = [
    OBJECT_MODE,
    FACE_MODE,
    COMBINED_MODE,
    ANNOTATED_OBJECT_MODE,
    ANNOTATED_FACE_MODE,
    ANNOTATED_COMBINED_MODE,
    AI_ANALYSIS_MODE,
]


def configure_page() -> None:
    st.set_page_config(
        page_title="VisionGuard AI",
        page_icon="VG",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def apply_custom_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --vg-bg: #0e1117;
            --vg-card: rgba(18, 22, 34, 0.82);
            --vg-card-strong: rgba(25, 30, 45, 0.94);
            --vg-border: rgba(255, 255, 255, 0.12);
            --vg-text: #f8fafc;
            --vg-muted: #a7adbb;
            --vg-red: #ff3158;
            --vg-purple: #945cff;
            --vg-cyan: #42d9ff;
            --vg-green: #36f58a;
        }

        .stApp {
            color: var(--vg-text);
            background:
                radial-gradient(circle at 15% 8%, rgba(255, 49, 88, 0.22), transparent 30%),
                radial-gradient(circle at 85% 12%, rgba(148, 92, 255, 0.20), transparent 28%),
                radial-gradient(circle at 45% 85%, rgba(66, 217, 255, 0.10), transparent 30%),
                linear-gradient(135deg, #07080d 0%, #0e1117 54%, #160819 100%);
        }

        [data-testid="stHeader"] {
            background: rgba(7, 8, 13, 0.18);
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(10, 12, 20, 0.98), rgba(14, 17, 25, 0.98));
            border-right: 1px solid var(--vg-border);
        }

        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] label {
            color: var(--vg-text) !important;
        }

        .block-container {
            max-width: 1320px;
            padding-top: 2rem;
            padding-bottom: 4rem;
        }

        .hero-card {
            position: relative;
            overflow: hidden;
            padding: 2.8rem;
            min-height: 360px;
            border: 1px solid var(--vg-border);
            border-radius: 34px;
            background:
                linear-gradient(135deg, rgba(17, 20, 31, 0.98), rgba(10, 10, 16, 0.78)),
                radial-gradient(circle at 75% 40%, rgba(255, 49, 88, 0.24), transparent 34%);
            box-shadow: 0 28px 76px rgba(0, 0, 0, 0.42);
        }

        .hero-kicker {
            display: inline-flex;
            padding: 0.42rem 0.82rem;
            border: 1px solid rgba(255, 49, 88, 0.42);
            border-radius: 999px;
            color: #ffd6df;
            background: rgba(255, 49, 88, 0.10);
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.09em;
            text-transform: uppercase;
        }

        .hero-title {
            margin: 1.1rem 0 0.8rem;
            max-width: 760px;
            color: #ffffff;
            font-size: clamp(3rem, 6.4vw, 6.4rem);
            font-weight: 850;
            line-height: 0.94;
            letter-spacing: -0.08em;
        }

        .hero-subtitle {
            max-width: 720px;
            color: #f8fafc;
            font-size: clamp(1.15rem, 2.2vw, 1.9rem);
            line-height: 1.18;
            letter-spacing: -0.035em;
        }

        .muted-text {
            color: var(--vg-muted);
            line-height: 1.7;
        }

        .hero-orb {
            position: absolute;
            right: 7%;
            top: 18%;
            width: min(28vw, 330px);
            height: min(28vw, 330px);
            border-radius: 999px;
            background:
                radial-gradient(circle at 50% 45%, rgba(255, 255, 255, 0.88), transparent 4%),
                radial-gradient(circle at 50% 50%, rgba(255, 49, 88, 0.95), transparent 28%),
                radial-gradient(circle at 55% 55%, rgba(148, 92, 255, 0.55), transparent 52%),
                radial-gradient(circle at 50% 50%, rgba(66, 217, 255, 0.20), transparent 68%);
            filter: drop-shadow(0 0 58px rgba(255, 49, 88, 0.62));
        }

        .section-card,
        .insight-card {
            padding: 1.25rem;
            border: 1px solid var(--vg-border);
            border-radius: 24px;
            background: var(--vg-card);
            box-shadow: 0 22px 56px rgba(0, 0, 0, 0.28);
        }

        .insight-card {
            border-color: rgba(66, 217, 255, 0.22);
            background:
                linear-gradient(135deg, rgba(66, 217, 255, 0.08), rgba(148, 92, 255, 0.08)),
                var(--vg-card);
        }

        .section-title {
            margin: 1.9rem 0 0.8rem;
            color: #ffffff;
            font-size: 1.45rem;
            font-weight: 800;
            letter-spacing: -0.035em;
        }

        .empty-state {
            padding: 1.6rem;
            border: 1px dashed rgba(255, 255, 255, 0.18);
            border-radius: 22px;
            color: var(--vg-muted);
            background: rgba(255, 255, 255, 0.035);
            text-align: center;
        }

        .stImage img {
            max-height: 620px;
            object-fit: contain;
            border-radius: 22px;
            border: 1px solid var(--vg-border);
            box-shadow: 0 22px 58px rgba(0, 0, 0, 0.40);
        }

        div[data-testid="stMetric"] {
            padding: 1rem 1.1rem;
            border: 1px solid var(--vg-border);
            border-radius: 22px;
            background: linear-gradient(180deg, rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0.035));
            box-shadow: 0 16px 42px rgba(0, 0, 0, 0.23);
        }

        div[data-testid="stMetric"] label,
        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            color: #ffffff !important;
        }

        .stButton > button {
            width: 100%;
            border: 0;
            border-radius: 999px;
            color: #ffffff;
            font-weight: 800;
            background: linear-gradient(135deg, var(--vg-red), var(--vg-purple));
            box-shadow: 0 0 30px rgba(255, 49, 88, 0.26);
        }

        .stButton > button:hover {
            border: 0;
            color: #ffffff;
            filter: brightness(1.08);
        }

        div[data-testid="stExpander"] {
            border: 1px solid var(--vg-border);
            border-radius: 20px;
            background: rgba(255, 255, 255, 0.04);
        }

        @media (max-width: 900px) {
            .hero-card {
                padding: 1.8rem;
                min-height: 300px;
            }

            .hero-orb {
                opacity: 0.25;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def mode_uses_objects(mode: str) -> bool:
    return mode in {
        OBJECT_MODE,
        COMBINED_MODE,
        ANNOTATED_OBJECT_MODE,
        ANNOTATED_COMBINED_MODE,
        AI_ANALYSIS_MODE,
    }


def mode_uses_faces(mode: str) -> bool:
    return mode in {
        FACE_MODE,
        COMBINED_MODE,
        ANNOTATED_FACE_MODE,
        ANNOTATED_COMBINED_MODE,
        AI_ANALYSIS_MODE,
    }


def initialize_session_state() -> None:
    defaults: dict[str, Any] = {
        "analysis_result": None,
        "analyzed_image_bytes": None,
        "uploaded_file_key": None,
        "session_history": [],
        "last_error": None,
        "last_mode": None,
    }

    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def render_history() -> None:
    history: list[dict[str, Any]] = st.session_state.session_history

    st.markdown("### 📌 Histórico")
    if not history:
        st.caption("Nenhuma análise feita nesta sessão.")
        return

    for item in history[-MAX_HISTORY_ITEMS:][::-1]:
        st.caption(
            f"{item['time']} | {item['filename']} | {item['mode']} | "
            f"{item['total_objects']} obj / {item['total_faces']} faces"
        )


def render_sidebar() -> tuple[Any | None, str, bool]:
    with st.sidebar:
        st.markdown("## Painel VisionGuard")
        st.caption("Configure a análise e envie sua imagem.")

        st.markdown("---")
        st.markdown("### 📷 Envio de imagem")
        uploaded_file = st.file_uploader(
            "Selecione uma imagem",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=False,
        )

        st.markdown("---")
        st.markdown("### 🎯 Modo de análise")
        mode = st.selectbox("Escolha o tipo de análise", DETECTION_MODES)

        st.markdown("---")
        st.markdown("### ⚙️ Parâmetros")
        if mode_uses_objects(mode):
            precision_mode = st.selectbox(
                "Modo de precisão",
                list(PRECISION_MODES),
                key="precision_mode",
                help=(
                    "Mostra opções de modelos YOLO. Nesta versão do MVP, "
                    "a troca real do modelo é feita no backend, em app/core/config.py."
                ),
            )
            selected_model = PRECISION_MODES[precision_mode]
            st.info(
                f"Modo selecionado: {precision_mode} ({selected_model}). "
                "Nesta versão, esse campo é uma recomendação. "
                "O modelo ativo da API continua sendo o definido em `YOLO_MODEL_NAME`."
            )
            st.slider(
                "confidence_threshold",
                min_value=0.0,
                max_value=1.0,
                value=0.4,
                step=0.05,
                key="confidence_threshold",
                help=(
                    "Confiança mínima para aceitar uma detecção do YOLO. "
                    "Valores maiores deixam o resultado mais rigoroso; valores menores mostram mais itens, "
                    "mas podem incluir detecções menos confiáveis."
                ),
            )
            filter_options = list(CLASS_FILTERS)
            if st.session_state.get("class_filter") not in filter_options:
                st.session_state.class_filter = "Objetos sem pessoas"

            st.selectbox(
                "Filtro de classes",
                filter_options,
                index=filter_options.index("Objetos sem pessoas"),
                key="class_filter",
                help=(
                    "Filtra os objetos detectados por grupos comuns. "
                    "Use 'Itens nas mãos' para tentar focar em celular, livro, laptop, garrafa e itens semelhantes."
                ),
            )
            if st.session_state.get("class_filter") == "Itens nas mãos":
                st.caption(
                    "Observação: YOLO não possui uma classe específica para tablet. "
                    "Ele pode aparecer como cell phone, book, laptop ou não ser detectado."
                )

        if mode_uses_faces(mode):
            st.number_input(
                "scale_factor",
                min_value=1.01,
                value=1.1,
                step=0.05,
                key="scale_factor",
                help="Controla a escala usada pelo detector de faces Haar Cascade.",
            )
            st.number_input(
                "min_neighbors",
                min_value=1,
                value=5,
                step=1,
                key="min_neighbors",
                help="Quanto maior, mais rigorosa fica a confirmação de uma face.",
            )
            st.number_input(
                "min_size",
                min_value=20,
                value=30,
                step=1,
                key="min_size",
                help="Tamanho mínimo da face, em pixels.",
            )

        st.markdown("---")
        analyze_clicked = st.button("Analisar imagem", type="primary", width="stretch")

        st.markdown("---")
        render_history()

    return uploaded_file, mode, analyze_clicked


def render_hero() -> None:
    st.markdown(
        """
        <section class="hero-card">
            <div class="hero-kicker">Plataforma de Visão Computacional</div>
            <h1 class="hero-title">VisionGuard AI</h1>
            <div class="hero-subtitle">
                Análise inteligente de imagens com detecção de faces, objetos e geração de insights.
            </div>
            <p class="muted-text" style="max-width: 660px; margin-top: 1rem;">
                Envie uma imagem, escolha o modo de análise e deixe o VisionGuard transformar pixels
                em informação visual clara, com métricas, resultado anotado e detalhes técnicos sob demanda.
            </p>
            <div class="hero-orb"></div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_upload_status(uploaded_file: Any | None, mode: str) -> None:
    if uploaded_file is None:
        st.markdown(
            """
            <div class="section-card">
                <strong>Como usar</strong>
                <p class="muted-text">
                    1. Envie uma imagem na sidebar. 2. Escolha o modo de análise.
                    3. Clique em <strong>Analisar imagem</strong>.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    st.markdown('<div class="section-title">Envio + configurações</div>', unsafe_allow_html=True)
    st.success(f"Imagem carregada: {uploaded_file.name}")
    st.caption(f"Modo selecionado: {mode}")


def build_request(mode: str) -> tuple[str, dict[str, float | int | str]]:
    params: dict[str, float | int | str] = {}

    if mode_uses_objects(mode):
        params["confidence_threshold"] = st.session_state.confidence_threshold
        selected_filter = st.session_state.get("class_filter", "Objetos sem pessoas")
        selected_classes = CLASS_FILTERS.get(selected_filter)
        if selected_classes:
            params["classes"] = ",".join(selected_classes)

    if mode_uses_faces(mode):
        params["scale_factor"] = st.session_state.scale_factor
        params["min_neighbors"] = st.session_state.min_neighbors
        params["min_size"] = st.session_state.min_size

    endpoint_by_mode = {
        OBJECT_MODE: "/detect/objects",
        FACE_MODE: "/detect/faces",
        COMBINED_MODE: "/detect/all",
        ANNOTATED_OBJECT_MODE: "/detect/objects/annotated",
        ANNOTATED_FACE_MODE: "/detect/faces/annotated",
        ANNOTATED_COMBINED_MODE: "/detect/all/annotated",
        AI_ANALYSIS_MODE: "/analyze/image",
    }

    return endpoint_by_mode[mode], params


def call_api(
    endpoint: str,
    params: dict[str, float | int | str],
    image_name: str,
    image_bytes: bytes,
    content_type: str,
) -> dict[str, Any] | None:
    files = {"file": (image_name, image_bytes, content_type)}

    try:
        response = requests.post(
            f"{API_BASE_URL}{endpoint}",
            params=params,
            files=files,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except requests.ConnectionError:
        st.session_state.last_error = {
            "message": (
                "Não foi possível conectar à API FastAPI. Verifique se o backend está "
                f"rodando em {API_BASE_URL}."
            )
        }
        return None
    except requests.Timeout:
        st.session_state.last_error = {
            "message": "A requisição demorou demais. Tente uma imagem menor ou execute novamente."
        }
        return None
    except requests.RequestException as exc:
        st.session_state.last_error = {"message": f"Erro inesperado ao chamar a API: {exc}"}
        return None

    try:
        data = response.json()
    except ValueError:
        st.session_state.last_error = {
            "message": "A API retornou uma resposta que não está em JSON.",
            "status_code": response.status_code,
            "response_text": response.text,
        }
        return None

    if not response.ok:
        st.session_state.last_error = {
            "message": "A API retornou um erro. Confira os detalhes técnicos abaixo.",
            "status_code": response.status_code,
            "response_json": data,
        }
        return None

    st.session_state.last_error = None
    return data


def get_annotated_image_path(result: dict[str, Any]) -> Path | None:
    output_path = result.get("output_path")
    if not output_path:
        return None

    annotated_path = PROJECT_ROOT / output_path
    return annotated_path if annotated_path.exists() else None


def calculate_average_confidence(result: dict[str, Any]) -> float | None:
    if result.get("average_confidence") is not None:
        return float(result["average_confidence"])

    objects = result.get("objects", [])
    confidences = [
        obj["confidence"]
        for obj in objects
        if isinstance(obj, dict) and isinstance(obj.get("confidence"), int | float)
    ]

    if not confidences:
        return None

    return sum(confidences) / len(confidences)


def generate_local_insight(result: dict[str, Any]) -> str:
    total_objects = int(result.get("total_objects", 0) or 0)
    total_faces = int(result.get("total_faces", 0) or 0)
    objects = result.get("objects", [])
    labels = [
        obj.get("label")
        for obj in objects
        if isinstance(obj, dict) and obj.get("label")
    ]
    top_labels = list(dict.fromkeys(labels))[:3]

    if result.get("summary"):
        return str(result["summary"])

    if total_objects and total_faces:
        return f"A imagem possui {total_faces} face(s) e {total_objects} objeto(s) detectados."

    if total_objects:
        highlights = ", ".join(top_labels) if top_labels else "objetos detectados"
        return (
            f"A imagem contém {total_objects} objeto(s) detectado(s), "
            f"com destaque para: {highlights}."
        )

    if total_faces:
        return f"A análise encontrou {total_faces} face(s) na imagem."

    return (
        "Nenhum objeto ou face foi detectado com os parâmetros atuais. "
        "Tente reduzir o threshold ou ajustar os parâmetros."
    )


def render_metrics(result: dict[str, Any], mode: str) -> None:
    st.markdown('<div class="section-title">Métricas</div>', unsafe_allow_html=True)

    average_confidence = calculate_average_confidence(result)
    columns = st.columns(4)
    columns[0].metric("Total de objetos", int(result.get("total_objects", 0) or 0))
    columns[1].metric("Total de faces", int(result.get("total_faces", 0) or 0))
    columns[2].metric(
        "Confiança média",
        f"{average_confidence:.2f}" if average_confidence is not None else "N/A",
    )
    columns[3].metric("Tipo de análise", mode)


def render_insight(result: dict[str, Any]) -> None:
    st.markdown('<div class="section-title">🧠 Insight da análise</div>', unsafe_allow_html=True)
    st.info(generate_local_insight(result))
    if detects_only_people_as_objects(result):
        st.warning(
            "O YOLO está detectando pessoas como objetos. "
            "Para focar no que está nas mãos ou ao redor delas, use o filtro "
            "'Itens nas mãos' ou 'Objetos sem pessoas'."
        )
    if has_low_confidence_detections(result):
        st.warning(
            "Algumas detecções possuem baixa confiança. "
            "Aumente o threshold ou use uma imagem mais nítida."
        )


def get_detected_object_labels(result: dict[str, Any]) -> list[str]:
    objects = result.get("objects", [])

    return [
        str(obj["label"])
        for obj in objects
        if isinstance(obj, dict) and obj.get("label")
    ]


def detects_only_people_as_objects(result: dict[str, Any]) -> bool:
    labels = get_detected_object_labels(result)
    return bool(labels) and set(labels) == {"person"}


def has_low_confidence_detections(result: dict[str, Any]) -> bool:
    objects = result.get("objects", [])

    return any(
        isinstance(obj, dict)
        and isinstance(obj.get("confidence"), int | float)
        and float(obj["confidence"]) < LOW_CONFIDENCE_WARNING_THRESHOLD
        for obj in objects
    )


def render_result_images(image_bytes: bytes | None, result: dict[str, Any] | None) -> None:
    st.markdown('<div class="section-title">Resultado visual</div>', unsafe_allow_html=True)

    left_column, right_column = st.columns(2)

    with left_column:
        with st.container(border=True):
            st.subheader("Imagem enviada")
            if image_bytes is None:
                st.markdown(
                    '<div class="empty-state">A imagem enviada aparecerá aqui.</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.image(image_bytes, use_container_width=True)

    with right_column:
        with st.container(border=True):
            st.subheader("Imagem anotada")
            if result is None:
                st.markdown(
                    '<div class="empty-state">A imagem anotada aparecerá aqui quando o modo selecionado gerar saída visual.</div>',
                    unsafe_allow_html=True,
                )
                return

            annotated_path = get_annotated_image_path(result)
            if annotated_path is None:
                output_path = result.get("output_path")
                if output_path:
                    st.warning(
                        "A API retornou um caminho de imagem anotada, mas o arquivo não foi encontrado."
                    )
                else:
                    st.markdown(
                        '<div class="empty-state">Este modo retorna resultados em JSON. Use um modo anotado para gerar saída visual.</div>',
                        unsafe_allow_html=True,
                    )
                return

            st.image(str(annotated_path), use_container_width=True)


def render_technical_details(result: dict[str, Any] | None) -> None:
    if result is None and st.session_state.last_error is None:
        return

    with st.expander("Ver detalhes técnicos da resposta"):
        if st.session_state.last_error is not None:
            st.json(st.session_state.last_error)
        elif result is not None:
            st.json(result)


def update_session_history(filename: str, mode: str, result: dict[str, Any]) -> None:
    history_item = {
        "filename": filename,
        "mode": mode,
        "total_objects": int(result.get("total_objects", 0) or 0),
        "total_faces": int(result.get("total_faces", 0) or 0),
        "time": datetime.now().strftime("%H:%M"),
    }

    history = [*st.session_state.session_history, history_item]
    st.session_state.session_history = history[-MAX_HISTORY_ITEMS:]


def get_uploaded_file_key(uploaded_file: Any | None, image_bytes: bytes | None) -> str | None:
    if uploaded_file is None or image_bytes is None:
        return None

    return f"{uploaded_file.name}:{len(image_bytes)}"


def run_analysis(uploaded_file: Any, image_bytes: bytes, mode: str) -> None:
    endpoint, params = build_request(mode)
    content_type = uploaded_file.type or "image/jpeg"

    try:
        spinner_context = st.spinner(
            "Analisando imagem com VisionGuard AI...",
            show_time=True,
        )
    except TypeError:
        spinner_context = st.spinner("Analisando imagem com VisionGuard AI...")

    with spinner_context:
        result = call_api(
            endpoint=endpoint,
            params=params,
            image_name=uploaded_file.name,
            image_bytes=image_bytes,
            content_type=content_type,
        )

    if result is None:
        st.session_state.analysis_result = None
        st.error("A análise não foi concluída. Confira os detalhes técnicos e tente novamente.")
        return

    st.session_state.analysis_result = result
    st.session_state.analyzed_image_bytes = image_bytes
    st.session_state.last_mode = mode
    update_session_history(uploaded_file.name, mode, result)
    st.success("Análise concluída com sucesso.")


def main() -> None:
    configure_page()
    initialize_session_state()
    apply_custom_css()

    uploaded_file, mode, analyze_clicked = render_sidebar()

    render_hero()
    st.markdown("<br>", unsafe_allow_html=True)
    render_upload_status(uploaded_file, mode)

    image_bytes = uploaded_file.getvalue() if uploaded_file is not None else None
    uploaded_file_key = get_uploaded_file_key(uploaded_file, image_bytes)

    if uploaded_file_key != st.session_state.uploaded_file_key:
        st.session_state.uploaded_file_key = uploaded_file_key
        st.session_state.analysis_result = None
        st.session_state.analyzed_image_bytes = image_bytes
        st.session_state.last_error = None

    if analyze_clicked:
        if uploaded_file is None or image_bytes is None:
            st.warning("Envie uma imagem na sidebar antes de iniciar a análise.")
        else:
            run_analysis(uploaded_file, image_bytes, mode)

    result = st.session_state.analysis_result
    result_image_bytes = image_bytes or st.session_state.analyzed_image_bytes

    if result is not None:
        render_metrics(result, st.session_state.last_mode or mode)
        render_insight(result)
        render_result_images(result_image_bytes, result)
    else:
        render_result_images(result_image_bytes, None)

    render_technical_details(result)


if __name__ == "__main__":
    main()
