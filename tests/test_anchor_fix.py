from atlasrag.bench.generate_v2 import (
    specific_scientific_signals, scientific_signals, assess_cross_paper_pair,
)


def test_bare_numbers_are_not_specific_anchors():
    s = specific_scientific_signals("We find 73.04 +/- 1.04 in 2023 with 10 samples, i.e. H0 and Neff1 and DESI.")
    assert not any(a.isdigit() for a in s)
    assert {"h0", "neff1", "desi"} <= s


def test_two_passages_sharing_only_numbers_are_rejected_for_lack_of_a_specific_anchor():
    a = "Constraints improve markedly across 2023 measurements using 10 samples and 5 bins of redshift evolution here"
    b = "Observations spanning 2023 targets processed through 10 pipelines producing 5 catalogues of galaxies instead"
    r = assess_cross_paper_pair(a * 5, b * 5, qtype="multi_hop", dense_similarity=0.5)
    assert r.reason in ("no_shared_scientific_signal", "no_shared_specific_signal")



def test_unicode_latex_and_plain_parameter_aliases_normalize_to_the_same_anchor():
    pairs = [
        ("Ω_m", r"\Omega_m", "omega_m"),
        ("α_s", r"\alpha_s", "alpha_s"),
        ("βs", "beta_s", "beta_s"),
        ("σ₈", "sigma_8", "sigma_8"),
        ("fσ8", "f_sigma_8", "f_sigma_8"),
        ("H₀", "H0", "h0"),
        ("n_s", "n_s", "n_s"),
        ("S_8", "S_8", "s_8"),
        ("ΔNeff", "delta_neff", "delta_neff"),
    ]
    for unicode_or_latex, plain, canonical in pairs:
        assert canonical in specific_scientific_signals(unicode_or_latex), unicode_or_latex
        assert canonical in specific_scientific_signals(plain), plain
        assert canonical in scientific_signals(unicode_or_latex), unicode_or_latex
        assert canonical in scientific_signals(plain), plain


def test_unicode_parameter_anchors_allow_complementary_pairing_without_weakening_the_gate():
    a = "The posterior for Ω_m and σ₈ from DESI BAO constrains early-universe structure."
    b = "Independent Omega_m and sigma_8 estimates compare CMB observations with neutrino models."
    shared = specific_scientific_signals(a) & specific_scientific_signals(b)
    assert {"omega_m", "sigma_8"} <= shared
    assessed = assess_cross_paper_pair(a, b, qtype="multi_hop", dense_similarity=0.6)
    assert assessed.reason is None



def test_common_ascii_and_tex_parameter_aliases_share_canonical_anchors():
    pairs = [
        ("H_0", "H0", "h0"),
        ("N_eff", "Neff", "neff"),
        ("sigma_8", "sigma8", "sigma8"),
        (r"\Omega_m", "Ω_m", "omega_m"),
        (r"\sigma_8", "σ₈", "sigma8"),
        ("f_sigma_8", "fσ₈", "f_sigma8"),
    ]
    for left, right, canonical in pairs:
        assert canonical in specific_scientific_signals(left), left
        assert canonical in specific_scientific_signals(right), right
        assert canonical in scientific_signals(left), left
        assert canonical in scientific_signals(right), right
