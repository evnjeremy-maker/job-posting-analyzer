"""Validated source claims and self-reported profile data."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

Text = Annotated[str, Field(min_length=1, pattern=r"\S")]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class EvidenceItem(StrictModel):
    text: Text
    quote: Text


class Overview(StrictModel):
    title: EvidenceItem | None = None
    employer: EvidenceItem | None = None
    location: EvidenceItem | None = None
    work_arrangement: EvidenceItem | None = None
    employment_type: EvidenceItem | None = None
    salary: EvidenceItem | None = None
    deadline: EvidenceItem | None = None
    working_hours: EvidenceItem | None = None


class Conflict(StrictModel):
    text: Text
    quotes: Annotated[list[Text], Field(min_length=2)]


class JobAnalysis(StrictModel):
    overview: Overview
    required: list[EvidenceItem]
    preferred: list[EvidenceItem]
    responsibilities: list[EvidenceItem]
    application_materials: list[EvidenceItem]
    ambiguities: list[Conflict]


class Profile(StrictModel):
    education: list[Text] = Field(default_factory=list)
    skills: list[Text] = Field(default_factory=list)
    projects: list[Text] = Field(default_factory=list)
    experience: list[Text] = Field(default_factory=list)
    preferences: list[Text] = Field(default_factory=list)
    explicitly_missing: list[Text] = Field(default_factory=list)
    portfolio: Text | None = None


class ProfileEvidence(StrictModel):
    pointer: Text
    quote: Text


class ComparisonItem(StrictModel):
    requirement_id: Text
    status: Literal["matched", "partial", "missing", "unclear"]
    evidence: list[ProfileEvidence]
    explanation: Text


class Report(StrictModel):
    schema_version: Literal["1.0"] = "1.0"
    analysis: JobAnalysis
    comparison: list[ComparisonItem] | None = None
    provider: Text
    model: Text
    prompt: Text
    simulated: bool
    portfolio_availability: Text | None = None
    usage: dict[str, int | None] | None = None
