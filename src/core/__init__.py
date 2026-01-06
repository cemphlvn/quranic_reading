# Core research API
#
# All tests MUST go through this API. No escape from methodology.

from core.api import (
    # Registration
    register_encoding,
    register_null,
    register_metric,
    register_corpus,

    # Test specs
    TestSpec,
    LengthScaleSpec,

    # Test execution
    run_test,
    run_length_scale_test,
    run_robustness_test,
    quick_test,

    # Utilities
    list_registered,

    # Types
    NullType,
    MetricDirection,

    # Results
    TestResult,
    LengthScaleResult,
    RobustnessResult,
)


def load_quran_corpus():
    """Load Quran and register it as a corpus."""
    from core.binary_analysis import load_quran, extract_text

    quran = load_quran("data/quran/quran.json")
    text = extract_text(quran, "full")

    register_corpus(
        name="quran",
        text=text,
        source="data/quran/quran.json",
        language="Classical Arabic"
    )
    return text
