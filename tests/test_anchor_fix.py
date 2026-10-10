from atlasrag.bench.generate_v2 import specific_scientific_signals, assess_cross_paper_pair


def test_bare_numbers_are_not_specific_anchors():
    s = specific_scientific_signals("We find 73.04 +/- 1.04 in 2023 with 10 samples, i.e. H0 and Neff1 and DESI.")
    assert not any(a.isdigit() for a in s)
    assert {"h0", "neff1", "desi"} <= s


def test_two_passages_sharing_only_numbers_are_rejected_for_lack_of_a_specific_anchor():
    a = "Constraints improve markedly across 2023 measurements using 10 samples and 5 bins of redshift evolution here"
    b = "Observations spanning 2023 targets processed through 10 pipelines producing 5 catalogues of galaxies instead"
    r = assess_cross_paper_pair(a * 5, b * 5, qtype="multi_hop", dense_similarity=0.5)
    assert r.reason in ("no_shared_scientific_signal", "no_shared_specific_signal")
