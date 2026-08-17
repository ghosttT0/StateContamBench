"""Stable fingerprints for benchmark sequences and run inputs."""
from __future__ import annotations

import hashlib
import json

from .dataset import Sequence


def sequence_record(sequence: Sequence) -> dict:
    return {
        "sid": sequence.sid,
        "attack_type": sequence.attack_type,
        "polarity": sequence.polarity,
        "host": sequence.host,
        "trigger_q": sequence.trigger_q,
        "expected_w1": sequence.expected_w1,
        "expected_final": sequence.expected_final,
        "payload_kind": sequence.payload_kind,
        "payload_trust": sequence.payload_trust,
        "trigger_distance": sequence.trigger_distance,
        "windows": [
            {
                "idx": window.idx,
                "malicious": window.malicious,
                "lines": [
                    {
                        "text": line.text,
                        "malicious": line.malicious,
                        "injected": line.injected,
                    }
                    for line in window.lines
                ],
            }
            for window in sequence.windows
        ],
    }


def stable_sha256(value: object) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def sequence_sha256(sequence: Sequence) -> str:
    return stable_sha256(sequence_record(sequence))


def trigger_sha256(sequence: Sequence) -> str:
    window = sequence.windows[-1]
    return stable_sha256({
        "trigger_q": sequence.trigger_q,
        "expected_final": sequence.expected_final,
        "window": sequence_record(sequence)["windows"][-1],
    })
