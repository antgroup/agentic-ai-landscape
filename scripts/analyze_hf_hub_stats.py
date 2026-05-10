#!/usr/bin/env python3
"""Query Hugging Face hub-stats for the agentic landscape report."""

import json
from pathlib import Path

import duckdb


BASE = Path(__file__).resolve().parents[1]
OUT_DIR = BASE / "reports" / "260601-agentic_landscape"
OUT_FILE = OUT_DIR / "hf-hub-stats-summary.json"
PARQUET = "hf://datasets/cfahlgren1/hub-stats/models.parquet"


def rows_to_dicts(cursor):
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def main():
    con = duckdb.connect()
    con.execute("SET enable_progress_bar=false")

    total_models = con.execute(f"SELECT count(*) FROM '{PARQUET}'").fetchone()[0]

    models_by_created_year = rows_to_dicts(
        con.execute(
            f"""
            SELECT
                year(createdAt) AS year,
                count(*) AS model_count
            FROM '{PARQUET}'
            WHERE createdAt IS NOT NULL
            GROUP BY year
            ORDER BY year
            """
        )
    )

    models_by_modality = rows_to_dicts(
        con.execute(
            f"""
            WITH models AS (
                SELECT
                    CASE
                        WHEN pipeline_tag IN ('text-generation', 'text2text-generation', 'fill-mask',
                            'text-classification', 'token-classification', 'question-answering',
                            'translation', 'summarization', 'sentence-similarity', 'feature-extraction',
                            'text-ranking', 'zero-shot-classification', 'table-question-answering')
                            THEN 'Text & code'
                        WHEN pipeline_tag IN ('image-classification', 'object-detection', 'image-segmentation',
                            'text-to-image', 'image-to-image', 'image-to-text',
                            'zero-shot-image-classification', 'unconditional-image-generation',
                            'depth-estimation', 'text-to-3d', 'image-to-3d')
                            THEN 'Image & vision'
                        WHEN pipeline_tag IN ('automatic-speech-recognition', 'text-to-speech',
                            'audio-classification', 'audio-to-audio', 'voice-activity-detection')
                            THEN 'Audio & speech'
                        WHEN pipeline_tag IN ('image-text-to-text', 'visual-question-answering',
                            'document-question-answering', 'video-text-to-text', 'video-classification',
                            'text-to-video', 'text-to-audio')
                            THEN 'Multimodal & video'
                        WHEN pipeline_tag IN ('tabular-classification', 'tabular-regression',
                            'time-series-forecasting')
                            THEN 'Tabular & time series'
                        WHEN pipeline_tag IN ('reinforcement-learning', 'robotics')
                            THEN 'RL & robotics'
                        WHEN pipeline_tag IS NULL THEN 'Unknown / not tagged'
                        ELSE 'Other'
                    END AS modality
                FROM '{PARQUET}'
            )
            SELECT modality, count(*) AS model_count
            FROM models
            GROUP BY modality
            ORDER BY model_count DESC
            """
        )
    )

    top_downloads_all_time = rows_to_dicts(
        con.execute(
            f"""
            SELECT
                id,
                author,
                downloadsAllTime,
                downloads,
                likes,
                pipeline_tag,
                list_filter(tags, tag -> starts_with(tag, 'license:'))[1] AS license
            FROM '{PARQUET}'
            WHERE downloadsAllTime IS NOT NULL
            ORDER BY downloadsAllTime DESC
            LIMIT 20
            """
        )
    )

    top_authors_by_model_count = rows_to_dicts(
        con.execute(
            f"""
            SELECT
                author,
                count(*) AS model_count,
                count_if(list_filter(tags, tag -> starts_with(tag, 'license:'))[1] IS NOT NULL) AS models_with_license,
                sum(coalesce(downloads, 0)) AS downloads_30d,
                sum(coalesce(downloadsAllTime, 0)) AS downloads_all_time
            FROM '{PARQUET}'
            WHERE author IS NOT NULL AND author <> ''
            GROUP BY author
            ORDER BY model_count DESC
            LIMIT 20
            """
        )
    )

    top_base_models = rows_to_dicts(
        con.execute(
            f"""
            WITH derived AS (
                SELECT
                    model.id AS base_model,
                    baseModels.relation AS relation,
                    id AS derived_model,
                    downloads,
                    likes
                FROM '{PARQUET}',
                UNNEST(baseModels.models) AS t(model)
                WHERE model.id IS NOT NULL
            )
            SELECT
                base_model,
                count(*) AS derived_count,
                count_if(relation = 'finetune') AS finetune_count,
                count_if(relation = 'adapter') AS adapter_count,
                count_if(relation = 'quantized') AS quantized_count,
                sum(coalesce(downloads, 0)) AS derived_downloads_30d,
                sum(coalesce(likes, 0)) AS derived_likes
            FROM derived
            GROUP BY base_model
            ORDER BY derived_count DESC
            LIMIT 20
            """
        )
    )

    summary = {
        "source": "cfahlgren1/hub-stats models.parquet",
        "queried_at": "2026-05-09",
        "total_models": total_models,
        "models_by_created_year": models_by_created_year,
        "models_by_modality": models_by_modality,
        "top_downloads_all_time": top_downloads_all_time,
        "top_authors_by_model_count": top_authors_by_model_count,
        "top_base_models": top_base_models,
    }
    OUT_FILE.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
