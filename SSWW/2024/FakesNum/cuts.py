# ===========================================================================
# Fake-rate measurement: one region.
#
#     FR(pT, |eta|) = ( N_tight^data - N_tight^prompt MC )
#                     / ( N_loose^data - N_loose^prompt MC )
#
# built per lepton, from every selected lepton in turn, in plotFake.py. The
# tight/loose split is not a cut and not a weight: it is the per-lepton flag
# SelLep_isTight{Electron,Muon}, so one pass holds both terms of the ratio.
#
# Cuts are kept to the minimum that defines a QCD-enriched space. mjj, detajj,
# njet, the away-jet threshold and the b-tag are branches in the snapshot, so
# their variations are a re-run of plotFake.py, not new jobs.
# ===========================================================================

supercut = (
    '  nLepSel >= 1'
    ' && nLepSel <= 2'
    ' && ROOT::VecOps::All(abs(SelLep_eta) < 2.5)'
)

# ------------------------------------------------
# The requirements depend on the lepton multiplicity, which is why this is one
# region and not two configurations.
#
# 1 lepton -- the simple case. The prompt background is W -> l nu, with some DY
#   and top, and MET < 30 together with mT < 30 removes most of it before the
#   subtraction has to.
#
#   NB on the skims: l2loose does *not* require two loose leptons. The chain
#   selection is "((nElectron+nMuon)>1)", i.e. two objects of the raw nanoAOD
#   collections with no ID, and lepSel is LeptonSel("Loose", 1, era), which
#   requires one. So this branch is not empty on l2loose -- it just needs a
#   second soft reco object, which is a requirement whose efficiency differs
#   between data and MC, so it is not a base to measure on.
#
#   The blocking problem is on the MC side instead: the production in use,
#   MCl2loose2024v15__MCCorr2024v15__JERFrom23BPix__l2tight, ends with the
#   l2tight step, a filter demanding both Lepton_[0] and Lepton_[1] tight. The
#   loose denominator does not exist in that MC at all, so the prompt
#   subtraction of the denominator is impossible. The data skim
#   (DATAl2loose2024v15__l2loose) has no such filter and is fine.
#
#   Both branches want an l1loose production without fakeSel; l1loose is a
#   superset of l2loose in multiplicity, so one covers both.
#
# 2 leptons -- needed to reach low pT, because only the dilepton triggers go
#   down to 8-12 GeV. Same-sign does here what MET and mT do above: it removes
#   DY, dileptonic top and WW at the level of the process rather than
#   statistically. What survives as prompt is WZ/ZZ, which really do give
#   same-sign prompt pairs, plus charge-mis-identified DY in ee -- hence the Z
#   veto on ee alone. No MET or mT cut: in a W+jets event the MET belongs to
#   the prompt lepton's W, so a cut on it would sculpt the spectrum of the
#   lepton whose rate is being measured.
#
# No away-jet requirement. nAwayJet20/30/40 stay in the snapshot, so requiring
# one -- and varying its threshold -- is a re-run of plotFake.py. Dropping it
# here keeps the denominator as inclusive as the region allows; it costs some
# QCD purity, which the prompt subtraction has to absorb instead.
# ------------------------------------------------
cuts['FR'] = {
    'expr': (
        '('
        '   (nLepSel == 1 && PuppiMET_pt < 30 && mt_l0 < 30)'
        ' || (nLepSel == 2 && isSS'
        '     && !(isEE && abs(mll - 91.2) < 15)'
        '     && mll > 12)'
        ')'
    ),
}

# ------------------------------------------------
# DY region: the prompt rate.
#
# Same per-lepton loop, same tight/loose flags, different sample: here the
# leptons are prompt by construction, so the ratio measures the tight
# efficiency of a real lepton rather than the fake rate. The reader needs both.
#
# Opposite sign and same flavour in the Z window is as clean a source of prompt
# leptons as exists. b-vetoed downstream like the QCD region, to drop top,
# which is the one background that gives OS same-flavour pairs under the peak.
#
# mll is a branch, so the window can be widened or moved off-peak later -- for
# the fake contamination under the peak, which is what the sidebands are for.
# ------------------------------------------------
cuts['DY'] = {
    'expr': (
        'nLepSel == 2'
        ' && isOS'
        ' && isSF'
        ' && abs(mll - 91.2) < 15'
    ),
}


# ------------------------------------------------
# The three b-tag regions, and the gap between two of them.
#
# They are NOT cuts here, because nBJet_loose / nBJet_medium and the whole
# CleanJet collection are branches: measureFakeRate.py cuts on them, so the
# three regions cost one re-run of that script and no new jobs. They are
# written down here because the definitions have to match the analysis, and
# the analysis is in ../cuts.py:
#
#   bveto   nBJet(pT > 20, |eta| < 2.5, btag > WP) == 0       <- 2024 bVeto
#   btag    nBJet(pT > 30, |eta| < 2.5, btag > WP) >= 1       <- 2024 bReq
#   incl    no requirement
#
# bveto and btag are mutually exclusive but NOT exhaustive: an event whose only
# b-tagged jet has 20 < pT < 30 fails both. That gap is the analysis', not
# ours -- bVeto and bReq are written at different thresholds there -- and it is
# accepted deliberately, so that `btag` here is the same region as the
# analysis top CR and the comparison means something. The alternative, moving
# the btag threshold down to 20 to close the gap, would measure the rate in a
# region the analysis does not have.
#
# Both multiplicities get all three: the b-tag is a property of the event, so
# nothing about it depends on nLepSel.
# ------------------------------------------------

# ------------------------------------------------
# Orthogonality, to settle once the statistics are known.
#
# With no b-tag or mjj requirement, the tight-tight same-sign part of FR
# overlaps the analysis: WW_SR is 2 tight SS leptons with mjj > 500 and
# detajj > 2.5, and the VRs sit at 200 < mjj < 500. Same events, both places.
#
# mjj is a branch, so this can be decided downstream rather than here -- but it
# does have to be decided before the map is used. 'mjj < 200' is orthogonal to
# WW_SR, to both VRs and to nonprompt_CR at once, and costs little, since the
# rate lives at low mjj.
# ------------------------------------------------
# ------------------------------------------------
# The region the snapshot is dumped from: the union of the two above.
# mkSnapshot takes a single cut, so without this the DY events would simply not
# be in the tree. Keeping it as the union rather than as a third, looser
# selection means the ntuple holds exactly the two regions and nothing else.
# ------------------------------------------------
cuts['dump'] = {
    'expr': '(%s) || (%s)' % (cuts['FR']['expr'], cuts['DY']['expr']),
}
