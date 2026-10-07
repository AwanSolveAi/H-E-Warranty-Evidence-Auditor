from pathlib import Path
import json

from src.auditor import audit_claim_folder


PROJECT_ROOT = Path(__file__).resolve().parent

SET_D_ROOT = (
    PROJECT_ROOT.parent
    / "AwanSolveAi_External_Validation_Set_D_V1"
)


def main() -> int:
    print("=" * 72)
    print("AWANSOLVEAI V0.6 - EXTERNAL SET D VALIDATION")
    print("=" * 72)
    print(f"Project: {PROJECT_ROOT}")
    print(f"Set D:   {SET_D_ROOT}")
    print()

    if not SET_D_ROOT.exists():
        print("FAIL: External Set D folder was not found.")
        return 1

    ground_truth_file = (
        SET_D_ROOT
        / "external_set_d_ground_truth.json"
    )

    claims_root = SET_D_ROOT / "claims"

    if not ground_truth_file.exists():
        print(
            "FAIL: external_set_d_ground_truth.json "
            "was not found."
        )
        return 1

    if not claims_root.exists():
        print("FAIL: claims folder was not found.")
        return 1

    ground_truth = json.loads(
        ground_truth_file.read_text(
            encoding="utf-8"
        )
    )

    total = 0
    passed = 0
    critical_false_ready = 0
    failures = []

    for item in ground_truth:
        claim_id = item["claim_id"]
        expected = item["expected_status"]

        profile = item.get(
            "profile",
            "general_heavy_equipment",
        )

        claim_folder = claims_root / claim_id

        if not claim_folder.exists():
            total += 1

            failures.append(
                (
                    claim_id,
                    expected,
                    "CLAIM_FOLDER_MISSING",
                )
            )

            print(
                f"FAIL | {claim_id:10} | "
                "Claim folder missing"
            )

            continue

        result = audit_claim_folder(
            claim_folder,
            profile=profile,
        )

        actual = result.overall_status

        total += 1

        if actual == expected:
            passed += 1
            marker = "PASS"
        else:
            marker = "FAIL"

            failures.append(
                (
                    claim_id,
                    expected,
                    actual,
                )
            )

        if (
            actual == "READY"
            and expected != "READY"
        ):
            critical_false_ready += 1

        print(
            f"{marker:4} | "
            f"{claim_id:10} | "
            f"Expected: {expected:18} | "
            f"Actual: {actual}"
        )

    print()
    print("=" * 72)
    print("SUMMARY")
    print("=" * 72)

    accuracy = (
        (passed / total) * 100
        if total
        else 0.0
    )

    print(
        f"Overall status: "
        f"{passed}/{total} = "
        f"{accuracy:.1f}%"
    )

    print(
        f"Critical false READY: "
        f"{critical_false_ready}"
    )

    if failures:
        print()
        print("FAILURES:")

        for failure in failures:
            print("  ", failure)

    print()

    if (
        passed == total
        and critical_false_ready == 0
    ):
        print(
            "EXTERNAL SET D VERDICT: PASS"
        )
        return 0

    print(
        "EXTERNAL SET D VERDICT: FAIL"
    )

    return 1


if __name__ == "__main__":
    raise SystemExit(main())