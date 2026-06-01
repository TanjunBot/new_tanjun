from __future__ import annotations

from unittest.mock import patch

import diagnostics.registry as registry_mod


def test_manifest_coverage_no_paths() -> None:
    from diagnostics.coverage import check_manifest_spec_coverage

    with patch("diagnostics.coverage.load_manifest", return_value={"paths": []}):
        outcomes = check_manifest_spec_coverage()
    assert outcomes[0].check_id == "coverage.manifest"
    assert outcomes[0].passed


def test_manifest_coverage_missing_spec() -> None:
    from diagnostics.coverage import check_manifest_spec_coverage

    with (
        patch("diagnostics.coverage.load_manifest", return_value={"paths": ["missing path"]}),
        patch("diagnostics.coverage.all_specs", return_value=[]),
    ):
        outcomes = check_manifest_spec_coverage()
    assert any(o.check_id.startswith("coverage.missing_spec.") for o in outcomes)


def test_manifest_coverage_success() -> None:
    from diagnostics.coverage import check_manifest_spec_coverage
    from diagnostics.models import CommandBehaviorSpec

    spec = CommandBehaviorSpec(
        id="utility.Foo.bar",
        extension="extensions.utility",
        group_cls=object,
        method_name="bar",
        tree_path="utility foo",
    )
    with (
        patch("diagnostics.coverage.load_manifest", return_value={"paths": ["utility foo"]}),
        patch("diagnostics.coverage.all_specs", return_value=[spec]),
    ):
        outcomes = check_manifest_spec_coverage()
    manifest = [o for o in outcomes if o.check_id == "coverage.manifest"]
    assert len(manifest) == 1
    assert manifest[0].passed


def test_duplicate_spec_ids_none() -> None:
    from diagnostics.coverage import check_duplicate_spec_ids
    from diagnostics.models import CommandBehaviorSpec

    spec = CommandBehaviorSpec(
        id="unique.id",
        extension="extensions.utility",
        group_cls=object,
        method_name="a",
    )
    with patch("diagnostics.coverage.all_specs", return_value=[spec]):
        outcomes = check_duplicate_spec_ids()
    assert any(o.check_id == "coverage.duplicate_ids" and o.passed for o in outcomes)
