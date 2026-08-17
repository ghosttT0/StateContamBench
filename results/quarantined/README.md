# Quarantined Legacy Result

`guard_real8_items.jsonl` is preserved byte-for-byte from the historical run
family but excluded from all paper aggregates. It contains 480 rows for only
208 unique `(sid, mode)` keys; each key occurs two or three times. The old
report averaged all duplicate rows and therefore did not represent 104
independent sequences per carrier.

No deduplicated result is substituted because first-write, last-write, and
all-row aggregation produce different rates. A corrected rerun must regenerate
this condition from one frozen manifest.
