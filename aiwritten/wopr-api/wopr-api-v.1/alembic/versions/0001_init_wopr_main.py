# Copyright 2026 Bob Bomar
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""init wopr_main

Revision ID: 0001_init_wopr_main
Revises:
Create Date: 2025-12-19
"""
from alembic import op
import sqlalchemy as sa


revision = "0001_init_wopr_main"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    game_status = sa.Enum("ACTIVE", "PAUSED", "FINISHED", "ARCHIVED", name="gamestatus")
    capture_status = sa.Enum("CREATED", "STORED", "ANALYZING", "COMPLETE", "ERROR", name="capturestatus")
    job_type = sa.Enum("VISION", "VALIDATE", "THUMB", "REPLAY", name="jobtype")
    job_status = sa.Enum("QUEUED", "RUNNING", "SUCCEEDED", "FAILED", "CANCELED", name="jobstatus")

    game_status.create(op.get_bind(), checkfirst=True)
    capture_status.create(op.get_bind(), checkfirst=True)
    job_type.create(op.get_bind(), checkfirst=True)
    job_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "games",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("game_type", sa.String(length=64), nullable=False),
        sa.Column("status", game_status, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
    )

    op.create_table(
        "players",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("game_id", sa.Uuid(), sa.ForeignKey("games.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("color", sa.String(length=32), nullable=True),
        sa.Column("seat", sa.Integer(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.UniqueConstraint("game_id", "seat", name="uq_players_game_seat"),
    )

    op.create_table(
        "captures",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("game_id", sa.Uuid(), sa.ForeignKey("games.id", ondelete="CASCADE"), nullable=False),
        sa.Column("seq", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("source_device_id", sa.String(length=128), nullable=True),
        sa.Column("image_path", sa.Text(), nullable=True),
        sa.Column("thumb_path", sa.Text(), nullable=True),
        sa.Column("sha256", sa.String(length=64), nullable=True),
        sa.Column("status", capture_status, nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.UniqueConstraint("game_id", "seq", name="uq_captures_game_seq"),
    )

    op.create_table(
        "jobs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("game_id", sa.Uuid(), sa.ForeignKey("games.id", ondelete="CASCADE"), nullable=False),
        sa.Column("capture_id", sa.Uuid(), sa.ForeignKey("captures.id", ondelete="CASCADE"), nullable=True),
        sa.Column("type", job_type, nullable=False),
        sa.Column("status", job_status, nullable=False),
        sa.Column("queued_at", sa.DateTime(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("attempt", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("result_json", sa.JSON(), nullable=False),
        sa.Column("cancel_requested", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )

    op.create_table(
        "events",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("game_id", sa.Uuid(), sa.ForeignKey("games.id", ondelete="CASCADE"), nullable=False),
        sa.Column("capture_id", sa.Uuid(), sa.ForeignKey("captures.id", ondelete="SET NULL"), nullable=True),
        sa.Column("type", sa.String(length=64), nullable=False),
        sa.Column("ts", sa.DateTime(), nullable=False),
        sa.Column("actor", sa.String(length=64), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=False),
    )
    op.create_index("ix_events_game_ts", "events", ["game_id", "ts"])

    op.create_table(
        "state_snapshots",
        sa.Column("game_id", sa.Uuid(), sa.ForeignKey("games.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("computed_at", sa.DateTime(), nullable=False),
        sa.Column("state_json", sa.JSON(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("state_snapshots")
    op.drop_index("ix_events_game_ts", table_name="events")
    op.drop_table("events")
    op.drop_table("jobs")
    op.drop_table("captures")
    op.drop_table("players")
    op.drop_table("games")

    op.execute("DROP TYPE IF EXISTS gamestatus")
    op.execute("DROP TYPE IF EXISTS capturestatus")
    op.execute("DROP TYPE IF EXISTS jobtype")
    op.execute("DROP TYPE IF EXISTS jobstatus")
