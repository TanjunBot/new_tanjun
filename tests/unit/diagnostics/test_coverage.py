from __future__ import annotations

import diagnostics.registry as registry_mod


def test_manifest_coverage_reports_when_paths_exist() -> None:
    from diagnostics.coverage import check_manifest_spec_coverage
    from diagnostics.tree import load_manifest

    registry_mod.clear_spec_cache()
    manifest = load_manifest()
    if not manifest.get("paths"):
        return
    outcomes = check_manifest_spec_coverage()
    assert outcomes
    ids = {o.check_id for o in outcomes}
    assert "coverage.manifest" in ids or any(x.startswith("coverage.missing_spec.") for x in ids)


def test_duplicate_spec_ids_check() -> None:
    from diagnostics.coverage import check_duplicate_spec_ids

    registry_mod.clear_spec_cache()
    outcomes = check_duplicate_spec_ids()
    assert any(o.check_id == "coverage.duplicate_ids" for o in outcomes)
