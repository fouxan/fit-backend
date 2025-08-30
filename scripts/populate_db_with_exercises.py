#!/usr/bin/env python3
import argparse
import json
import os
import re
import uuid
from pathlib import Path
from typing import Dict, List, Optional

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models.exercise import (
    ExerciseCatalog,
    ExerciseCategory,
    MuscleGroup,
    Equipment,
    MovementPattern,
    ExerciseMuscleGroup,
    ExerciseEquipment,
    DifficultyLevel,
)
import mimetypes
from app.config.settings import get_settings
from app.services.s3 import S3Service

settings = get_settings()

# ---------- helpers ----------

ALT_UNILATERAL_PATTERNS = [
    r"\balternate\b",
    r"\balternating\b",
    r"\bone[-\s]?arm\b",
    r"\bsingle[-\s]?arm\b",
    r"\bone[-\s]?leg\b",
    r"\bsingle[-\s]?leg\b",
    r"\bunilateral\b",
]

CARDIO_CATEGORIES = {
    "cardio": {
        "supports_gps": False,
        "supports_hr": True,
        "cadence_metric": None,
        "sport": None,
    },
    "outdoor_run": {
        "supports_gps": True,
        "supports_hr": True,
        "cadence_metric": "steps/min",
        "sport": "outdoor_run",
    },
    "treadmill_run": {
        "supports_gps": False,
        "supports_hr": True,
        "cadence_metric": "steps/min",
        "sport": "treadmill_run",
    },
    "outdoor_cycle": {
        "supports_gps": True,
        "supports_hr": True,
        "cadence_metric": "rpm",
        "sport": "outdoor_ride",
    },
    "indoor_cycle": {
        "supports_gps": False,
        "supports_hr": True,
        "cadence_metric": "rpm",
        "sport": "indoor_ride",
    },
    "pool_swim": {
        "supports_gps": False,
        "supports_hr": True,
        "supports_pool": True,
        "cadence_metric": "strokes/min",
        "sport": "pool_swim",
    },
    "open_water_swim": {
        "supports_gps": True,
        "supports_hr": True,
        "cadence_metric": "strokes/min",
        "sport": "open_water_swim",
    },
}


def infer_unilateral(name: str, id_: str) -> bool:
    text = f"{name} {id_}".lower().replace("_", " ")
    return any(re.search(pat, text) for pat in ALT_UNILATERAL_PATTERNS)


def map_difficulty(raw: Optional[str]) -> DifficultyLevel:
    # default beginner if missing/unknown
    if not raw:
        return DifficultyLevel.BEGINNER
    raw = raw.lower()
    if raw in ("beginner", "easy"):
        return DifficultyLevel.BEGINNER
    if raw in ("intermediate", "inter"):
        return DifficultyLevel.INTERMEDIATE
    if raw in ("advanced", "hard"):
        return DifficultyLevel.ADVANCED
    return DifficultyLevel.BEGINNER


def normalize_mechanics(raw: Optional[str]) -> str:
    # fall back to 'compound'
    if not raw:
        return "compound"
    raw = raw.lower()
    return "isolation" if raw == "isolation" else "compound"


def is_bodyweight(equipment_list: List[str]) -> bool:
    normalized = {e.lower() for e in equipment_list}
    return (
        any(
            kw in normalized
            for kw in {"body only", "bodyweight", "no equipment", "none"}
        )
        or len(normalized) == 0
    )


def cardio_flags_from_category(category_name: str):
    key = category_name.lower().replace(" ", "_")
    info = CARDIO_CATEGORIES.get(key, {})
    return {
        "supports_gps": bool(info.get("supports_gps", False)),
        "supports_pool": bool(info.get("supports_pool", False)),
        "supports_hr": bool(info.get("supports_hr", True)),
        "cadence_metric": info.get("cadence_metric"),
        "default_sport_profile": info.get("sport"),
    }


def ensure_row(session, model, name: str, description: Optional[str] = None):
    row = session.execute(
        select(model).where(model.name.ilike(name))
    ).scalar_one_or_none()
    if row:
        return row
    row = model(name=name, description=description)
    session.add(row)
    session.flush()  # to get id
    return row


def ensure_many(session, model, names: List[str]) -> List:
    rows = []
    for n in names:
        if not n:
            continue
        rows.append(ensure_row(session, model, n))
    return rows


def upload_images_s3(
    local_dir: Path, s3svc: S3Service, prefix: str, public: bool
) -> List[str]:
    urls: List[str] = []
    for path in sorted(local_dir.glob("**/*")):
        if path.is_dir():
            continue
        # keep subfolder structure under the exercise directory
        key = (
            "/".join([prefix.strip("/"), *path.parts[-2:]])
            if path.parent != local_dir
            else "/".join([prefix.strip("/"), path.name])
        )
        content_type = guess_content_type(path)
        with open(path, "rb") as f:
            # ACL only if public is requested
            s3svc.upload_fileobj(
                f,
                key=key,
                content_type=content_type,
                cache_control="public, max-age=31536000" if public else None,
            )
        urls.append(build_public_url(s3svc.bucket, key))
    return urls


def guess_content_type(path: Path) -> Optional[str]:
    ctype, _ = mimetypes.guess_type(str(path))
    return ctype


def build_public_url(bucket: str, key: str) -> str:
    """
    Construct a public URL for the uploaded object.
    - If S3_ENDPOINT_URL is set, use it (works for LocalStack/MinIO).
    - Else assume AWS and use virtual-hosted style with region.
    """
    region = settings.AWS_REGION or "us-east-1"
    return f"https://{bucket}.s3.{region}.amazonaws.com/{key}"


# ---------- main loader ----------


def load_one_exercise_json(json_path: Path) -> Dict:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def main():
    parser = argparse.ArgumentParser(
        description="Populate exercise catalog from JSON + images"
    )
    parser.add_argument(
        "--db-url",
        required=True,
        help="SQLAlchemy DB URL (e.g., postgresql+psycopg2://user:pass@host/db)",
    )
    parser.add_argument(
        "--input-root",
        required=True,
        help="Root folder containing exercise JSON + image folders",
    )
    parser.add_argument(
        "--prefix", default="exercises", help="S3 key prefix (default: exercises)"
    )
    parser.add_argument(
        "--created-by-id",
        default=None,
        help="UUID of the user creating these entries (optional)",
    )
    parser.add_argument(
        "--default-category",
        default="strength",
        help="Default category to use if missing",
    )
    parser.add_argument(
        "--default-tempo", default="2-1-2-0", help="Default tempo for strength"
    )
    parser.add_argument(
        "--public-urls",
        action="store_true",
        help="Assume bucket is public-read; URLs formed as https://bucket.s3.amazonaws.com/key",
    )
    args = parser.parse_args()

    engine = create_engine(args.db_url)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    s3 = S3Service()

    root = Path(args.input_root)

    # Find all JSON files (1 per exercise)
    json_files = list(root.glob("**/*.json"))
    if not json_files:
        print(f"No JSON files found under {root}")
        return

    # Ensure default category exists
    default_category = ensure_row(session, ExerciseCategory, args.default_category)

    created_count = 0

    try:
        for jf in json_files:
            data = load_one_exercise_json(jf)

            # --- Parse incoming JSON fields (with safe defaults) ---
            ex_id = data.get("id") or uuid.uuid4().hex
            name = data.get("name") or ex_id.replace("_", " ")
            difficulty = data.get("level")
            mechanics = normalize_mechanics(data.get("mechanic"))
            category_name = data.get("category") or args.default_category

            # Instructions can be array; store as normalized joined text
            instr_list = data.get("instructions") or []
            if isinstance(instr_list, list):
                instructions = "\n".join(
                    [i.strip() for i in instr_list if i and i.strip()]
                )
            else:
                instructions = str(instr_list) if instr_list else None

            # Description (optional); if absent, derive from name
            description = data.get("description") or None

            # Video & Images (images are local paths; we will upload and replace with S3 URLs)
            video_url = data.get("videoURL") or data.get("video_url") or None

            # Primary/secondary muscles from sample JSON
            primary_muscles = data.get("primaryMuscles") or []
            secondary_muscles = data.get("secondaryMuscles") or []
            all_muscles = list(
                dict.fromkeys([*(primary_muscles or []), *(secondary_muscles or [])])
            )  # uniq keep order

            # Equipment list
            equipment_list = []
            raw_equipment = data.get("equipment")
            if isinstance(raw_equipment, list):
                equipment_list = raw_equipment
            elif isinstance(raw_equipment, str) and raw_equipment.strip():
                equipment_list = [raw_equipment.strip()]

            # Optional movement patterns (let the JSON include "movementPatterns": ["hinge", "squat"])
            movement_patterns = data.get("movementPatterns") or []

            # Heuristics for derived fields
            unilateral = infer_unilateral(name, ex_id)
            is_bw = is_bodyweight(equipment_list)

            # Category ensure
            category = ensure_row(session, ExerciseCategory, category_name)

            # Cardio flags (only really applied for cardio-like categories)
            cardio = cardio_flags_from_category(category_name)
            supports_gps = cardio.get("supports_gps", False)
            supports_pool = cardio.get("supports_pool", False)
            supports_hr = cardio.get("supports_hr", True)
            cadence_metric = cardio.get("cadence_metric")
            default_sport_profile = cardio.get("default_sport_profile")

            # Default tempo – use when likely strength/resistance work
            default_tempo = None
            if category_name.lower() in (
                "strength",
                "powerlifting",
                "olympic_weightlifting",
                "hypertrophy",
            ):
                default_tempo = os.getenv("DEFAULT_TEMPO", args.default_tempo)

            # --- S3 uploads for images ---
            # We assume images live alongside JSON in a folder named by the JSON's id, or any "images" key pointing to paths.
            image_s3_urls: List[str] = []
            # from JSON "images": ["Alternate_Incline_Dumbbell_Curl/0.jpg", ...]
            img_paths = data.get("images") or []
            # also check a sibling dir with same stem as id or file stem
            candidates: List[Path] = []

            if img_paths:
                for rel in img_paths:
                    p = (jf.parent / rel).resolve()
                    if p.exists():
                        candidates.append(p)
            else:
                # try a folder with exercise id or file stem
                guess_dirs = [jf.parent / ex_id, jf.parent / jf.stem]
                for gd in guess_dirs:
                    if gd.exists() and gd.is_dir():
                        # upload all files inside that folder
                        for f in gd.glob("*"):
                            candidates.append(f)

            # Upload – keep a neat S3 prefix per exercise
            # Put all images beneath <prefix>/<ex_id>/
            uploaded_any = False
            if candidates:
                # If candidates contain files from different folders, we still flatten into the exercise folder.
                for fpath in sorted(set(candidates)):
                    if fpath.is_dir():
                        urls = upload_images_s3(
                            fpath, s3, f"{args.prefix}/{ex_id}", args.public_urls
                        )
                        image_s3_urls.extend(urls)
                        uploaded_any = True
                    else:
                        key = f"{args.prefix.strip('/')}/{ex_id}/{fpath.name}"
                        content_type = guess_content_type(fpath)
                        with open(fpath, "rb") as f:
                            s3.upload_fileobj(
                                f,
                                key=key,
                                content_type=content_type,
                                cache_control=(
                                    "public, max-age=31536000"
                                    if args.public_urls
                                    else None
                                ),
                            )
                        image_s3_urls.append(build_public_url(s3.bucket, key))
                        uploaded_any = True

            # --- Upserts for lookup tables ---
            mg_rows = ensure_many(session, MuscleGroup, all_muscles)
            eq_rows = ensure_many(session, Equipment, equipment_list)
            mp_rows = ensure_many(session, MovementPattern, movement_patterns)

            session.flush()

            # --- Upsert the exercise by (name, category) or by normalized id in notes tag ---
            # Simpler approach: unique by (name, category_id)
            existing = (
                session.query(ExerciseCatalog)
                .filter(
                    ExerciseCatalog.name.ilike(name),
                    ExerciseCatalog.category_id == category.id,
                )
                .one_or_none()
            )

            if existing:
                ex = existing
                ex.description = description
                ex.instructions = instructions
                ex.difficulty = difficulty
                ex.video_url = video_url
                ex.image_urls = image_s3_urls or ex.image_urls
                ex.mechanics = mechanics
                ex.unilateral = unilateral
                ex.is_bodyweight = is_bw
                ex.supports_gps = supports_gps
                ex.supports_pool = supports_pool
                ex.supports_hr = supports_hr
                ex.cadence_metric = cadence_metric
                ex.default_sport_profile = default_sport_profile
                ex.default_tempo = default_tempo or ex.default_tempo
            else:
                ex = ExerciseCatalog(
                    name=name,
                    description=description,
                    instructions=instructions,
                    difficulty=difficulty,
                    is_custom=False,
                    created_by_id=(
                        uuid.UUID(args.created_by_id) if args.created_by_id else None
                    ),
                    category_id=category.id,
                    video_url=video_url,
                    image_urls=image_s3_urls if uploaded_any else None,
                    mechanics=mechanics,
                    unilateral=unilateral,
                    default_tempo=default_tempo,
                    is_bodyweight=is_bw,
                    supports_gps=supports_gps,
                    supports_pool=supports_pool,
                    supports_hr=supports_hr,
                    cadence_metric=cadence_metric,
                    default_sport_profile=default_sport_profile,
                )
                session.add(ex)
                session.flush()

            # Junctions – clear & set (idempotent-ish handling)
            # Muscle groups
            ex.muscle_groups = mg_rows
            # Equipment
            ex.equipment = eq_rows
            # Movement patterns
            ex.movement_patterns = mp_rows

            created_count += 1
            print(f"Upserted: {name} (category: {category_name})")

        session.commit()
        print(f"Done. Upserted {created_count} exercises.")
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
