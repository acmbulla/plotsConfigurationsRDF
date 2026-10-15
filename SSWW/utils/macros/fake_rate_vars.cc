#ifndef FAKERATEVARS
#define FAKERATEVARS

// Per-lepton jet-proximity variables for the fake-rate measurement.
//
// The fake rate is not a function of (pT, eta) alone: a lepton faked by a jet
// carries the rest of its parent jet nearby, so dR to the closest jet and the
// lepton/jet pT ratio are the two variables the rate depends on most strongly
// after pT. They are computed here rather than in a string expression because
// finding the closest jet needs a loop, and because a typed callable keeps the
// type checking at compile time (see CLAUDE.md section 7).
//
// Both functors return one entry per lepton, aligned with the SelLep_* arrays,
// and -1 for a lepton with no jet above threshold.

#include "ROOT/RVec.hxx"
#include <cmath>
#include <cstddef>
#include <type_traits>

// Index of the jet above ptMin closest in dR to (eta, phi); -1 if none.
inline int fr_closest_jet_index(float eta, float phi,
                                const ROOT::VecOps::RVec<float> &jet_pt,
                                const ROOT::VecOps::RVec<float> &jet_eta,
                                const ROOT::VecOps::RVec<float> &jet_phi,
                                float ptMin) {
    int best = -1;
    float bestDR2 = 1.e9f;
    for (std::size_t j = 0; j < jet_pt.size(); ++j) {
        if (jet_pt[j] < ptMin) continue;
        const float dEta = jet_eta[j] - eta;
        const float dPhi = ROOT::VecOps::DeltaPhi(jet_phi[j], phi);
        const float dr2 = dEta * dEta + dPhi * dPhi;
        if (dr2 < bestDR2) { bestDR2 = dr2; best = static_cast<int>(j); }
    }
    return best;
}

// dR from each lepton to its closest jet above ptMin_.
struct closestJetDR {
    float ptMin_;
    explicit closestJetDR(float ptMin = 20.f) : ptMin_(ptMin) {}

    ROOT::VecOps::RVec<float> operator()(const ROOT::VecOps::RVec<float> &lep_eta,
                                         const ROOT::VecOps::RVec<float> &lep_phi,
                                         const ROOT::VecOps::RVec<float> &jet_pt,
                                         const ROOT::VecOps::RVec<float> &jet_eta,
                                         const ROOT::VecOps::RVec<float> &jet_phi) const {
        ROOT::VecOps::RVec<float> out(lep_eta.size(), -1.f);
        for (std::size_t i = 0; i < lep_eta.size(); ++i) {
            const int j = fr_closest_jet_index(lep_eta[i], lep_phi[i],
                                               jet_pt, jet_eta, jet_phi, ptMin_);
            if (j < 0) continue;
            const float dEta = jet_eta[j] - lep_eta[i];
            const float dPhi = ROOT::VecOps::DeltaPhi(jet_phi[j], lep_phi[i]);
            out[i] = std::sqrt(dEta * dEta + dPhi * dPhi);
        }
        return out;
    }
};

// pT of that same closest jet.
struct closestJetPt {
    float ptMin_;
    explicit closestJetPt(float ptMin = 20.f) : ptMin_(ptMin) {}

    ROOT::VecOps::RVec<float> operator()(const ROOT::VecOps::RVec<float> &lep_eta,
                                         const ROOT::VecOps::RVec<float> &lep_phi,
                                         const ROOT::VecOps::RVec<float> &jet_pt,
                                         const ROOT::VecOps::RVec<float> &jet_eta,
                                         const ROOT::VecOps::RVec<float> &jet_phi) const {
        ROOT::VecOps::RVec<float> out(lep_eta.size(), -1.f);
        for (std::size_t i = 0; i < lep_eta.size(); ++i) {
            const int j = fr_closest_jet_index(lep_eta[i], lep_phi[i],
                                               jet_pt, jet_eta, jet_phi, ptMin_);
            if (j >= 0) out[i] = jet_pt[j];
        }
        return out;
    }
};

static_assert(std::is_copy_constructible_v<closestJetDR>, "Define takes the callable by value");
static_assert(std::is_copy_constructible_v<closestJetPt>, "Define takes the callable by value");

#endif
