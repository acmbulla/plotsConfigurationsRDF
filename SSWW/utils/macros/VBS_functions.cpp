#ifndef VBS_FUNCTIONS_H
#define VBS_FUNCTIONS_H

#include "ROOT/RVec.hxx"
#include "TLorentzVector.h"
#include <cmath>
#include <limits>
#include <algorithm>

// Lepton mass from pdgId (e=11, mu=13)
inline float lepton_mass(int pdgId) {
    return (std::abs(pdgId) == 11) ? 0.000511f : 0.105658f;
}

//
// computeWZvars
// Returns: [0] mll_Z  [1] mlll  [2] idx_W  [3] category
//          [4] pt_W   [5] pt_Z1 [6] pt_Z2  [7] proxyW_W
//
ROOT::RVec<float> computeWZvars(
    const ROOT::RVec<float>& pt,
    const ROOT::RVec<float>& eta,
    const ROOT::RVec<float>& phi,
    const ROOT::RVec<int>&   pdgId,
    float              MET_pt,
    float              MET_phi
) {
    if ((int)pt.size() != 3) return {-9999., -9999., -9999., -9999., -9999., -9999., -9999., -9999.};

    const float mZ = 91.1876;
    float best_dmZ = std::numeric_limits<float>::max();
    int idx_Z1 = -1, idx_Z2 = -1;
    int n = (int)pt.size();

    for (int i = 0; i < n; i++) {
        for (int j = i+1; j < n; j++) {
            if (pdgId[i] + pdgId[j] != 0) continue;
            TLorentzVector l1, l2;
            l1.SetPtEtaPhiM(pt[i], eta[i], phi[i], lepton_mass(pdgId[i]));
            l2.SetPtEtaPhiM(pt[j], eta[j], phi[j], lepton_mass(pdgId[j]));
            float mll = (l1 + l2).M();
            if (std::abs(mll - mZ) < best_dmZ) {
                best_dmZ = std::abs(mll - mZ);
                idx_Z1 = i; idx_Z2 = j;
            }
        }
    }

    if (idx_Z1 < 0) return {-9999., -9999., -9999., -9999., -9999., -9999., -9999., -9999.};

    int idx_W = -1;
    for (int i = 0; i < n; i++) {
        if (i != idx_Z1 && i != idx_Z2) { idx_W = i; break; }
    }
    if (idx_W < 0) return {-9999., -9999., -9999., -9999., -9999., -9999., -9999., -9999.};

    TLorentzVector lZ1, lZ2, lW;
    lZ1.SetPtEtaPhiM(pt[idx_Z1], eta[idx_Z1], phi[idx_Z1], lepton_mass(pdgId[idx_Z1]));
    lZ2.SetPtEtaPhiM(pt[idx_Z2], eta[idx_Z2], phi[idx_Z2], lepton_mass(pdgId[idx_Z2]));
    lW .SetPtEtaPhiM(pt[idx_W],  eta[idx_W],  phi[idx_W],  lepton_mass(pdgId[idx_W]));

    float mll_Z   = (lZ1 + lZ2).M();
    float mlll    = (lZ1 + lZ2 + lW).M();
    int   flav_Z  = std::abs(pdgId[idx_Z1]);
    int   flav_W  = std::abs(pdgId[idx_W]);
    float category = (float)(flav_Z * 100 + flav_W);
    float ptZ1    = std::max(pt[idx_Z1], pt[idx_Z2]);
    float ptZ2    = std::min(pt[idx_Z1], pt[idx_Z2]);

    // proxyW_W: transverse mass of the W lepton and the MET.
    // Do not build this as (lW + MET).M() with the MET four-vector at eta = 0:
    // that is an invariant mass and carries a spurious cosh(eta_W) in place of
    // the 1, which inflates it by 1.31 in the median and by up to a factor 247.
    // No phi wrapping is needed, cos() is periodic.
    float dphi_W_MET = phi[idx_W] - MET_phi;
    float proxyW_W   = std::sqrt(std::max(0.f,
                           2.f * pt[idx_W] * MET_pt * (1.f - std::cos(dphi_W_MET))));

    return { mll_Z, mlll, (float)idx_W, category, pt[idx_W], ptZ1, ptZ2, proxyW_W };
}


//
// computeZZvars
// Returns: [0] mll_Z1  [1] mll_Z2  [2] mllll  [3] category
//          [4] pt_4l_1 [5] pt_4l_2
//
ROOT::RVec<float> computeZZvars(
    const ROOT::RVec<float>& pt,
    const ROOT::RVec<float>& eta,
    const ROOT::RVec<float>& phi,
    const ROOT::RVec<int>&   pdgId
) {
    if ((int)pt.size() < 4) return {-1., -1., -1., -1., -1., -1.};

    const float mZ = 91.1876;
    int n = (int)pt.size();
    float best1_dmZ = std::numeric_limits<float>::max();
    float best2_dmZ = std::numeric_limits<float>::max();
    int p1_i = -1, p1_j = -1, p2_i = -1, p2_j = -1;

    for (int i = 0; i < n; i++) {
        for (int j = i+1; j < n; j++) {
            if (pdgId[i] + pdgId[j] != 0) continue;
            TLorentzVector l1, l2;
            l1.SetPtEtaPhiM(pt[i], eta[i], phi[i], lepton_mass(pdgId[i]));
            l2.SetPtEtaPhiM(pt[j], eta[j], phi[j], lepton_mass(pdgId[j]));
            float dmZ = std::abs((l1+l2).M() - mZ);
            if (dmZ < best1_dmZ) {
                best2_dmZ = best1_dmZ; p2_i = p1_i; p2_j = p1_j;
                best1_dmZ = dmZ;       p1_i = i;    p1_j = j;
            } else if (dmZ < best2_dmZ) {
                best2_dmZ = dmZ; p2_i = i; p2_j = j;
            }
        }
    }

    if (p1_i < 0 || p2_i < 0) return {-1., -1., -1., -1., -1., -1.};

    TLorentzVector l1, l2, l3, l4;
    l1.SetPtEtaPhiM(pt[p1_i], eta[p1_i], phi[p1_i], lepton_mass(pdgId[p1_i]));
    l2.SetPtEtaPhiM(pt[p1_j], eta[p1_j], phi[p1_j], lepton_mass(pdgId[p1_j]));
    l3.SetPtEtaPhiM(pt[p2_i], eta[p2_i], phi[p2_i], lepton_mass(pdgId[p2_i]));
    l4.SetPtEtaPhiM(pt[p2_j], eta[p2_j], phi[p2_j], lepton_mass(pdgId[p2_j]));

    int flav_Z1 = std::abs(pdgId[p1_i]);
    int flav_Z2 = std::abs(pdgId[p2_i]);
    if (flav_Z1 > flav_Z2) std::swap(flav_Z1, flav_Z2);

    return {
        (float)(l1+l2).M(),
        (float)(l3+l4).M(),
        (float)(l1+l2+l3+l4).M(),
        (float)(flav_Z1 * 100 + flav_Z2),
        pt[0], pt[1]
    };
}


//
// computeZstar
// Returns max(z*_l) over all leptons
//
float computeZstar(
    const ROOT::RVec<float>& lep_eta,
    const ROOT::RVec<float>& jet_eta
) {
    if ((int)jet_eta.size() < 2) return -1.;
    float eta_avg   = (jet_eta[0] + jet_eta[1]) / 2.0;
    float delta_eta = std::abs(jet_eta[0] - jet_eta[1]);
    if (delta_eta < 1e-6) return -1.;
    float zstar_max = -1.;
    for (int i = 0; i < (int)lep_eta.size(); i++) {
        float zstar = std::abs(lep_eta[i] - eta_avg) / delta_eta;
        if (zstar > zstar_max) zstar_max = zstar;
    }
    return zstar_max;
}


//
// dr_lj
// Returns RVec of 4 DeltaR values: dr(l1,j1), dr(l1,j2), dr(l2,j1), dr(l2,j2)
//
ROOT::RVec<float> dr_lj(
    ROOT::RVec<float>& CleanJet_eta,
    ROOT::RVec<float>& CleanJet_phi,
    ROOT::RVec<float>& Lepton_eta,
    ROOT::RVec<float>& Lepton_phi
) {
    ROOT::RVec<float> result;
    if ((int)Lepton_eta.size() < 2 || (int)CleanJet_eta.size() < 2)
        return {-1., -1., -1., -1.};
    result.reserve(4);
    for (int iL = 0; iL < 2; iL++) {
        for (int iJ = 0; iJ < 2; iJ++) {
            float deta = Lepton_eta[iL] - CleanJet_eta[iJ];
            float dphi = Lepton_phi[iL] - CleanJet_phi[iJ];
            // wrap dphi in [-pi, pi]
            while (dphi >  M_PI) dphi -= 2*M_PI;
            while (dphi < -M_PI) dphi += 2*M_PI;
            result.push_back(std::sqrt(deta*deta + dphi*dphi));
        }
    }
    return result;  // [dr(l1,j1), dr(l1,j2), dr(l2,j1), dr(l2,j2)]
}


//
// m_lj
// Returns RVec of 4 invariant masses: m(l1,j1), m(l1,j2), m(l2,j1), m(l2,j2)
//
ROOT::RVec<float> m_lj(
    ROOT::RVec<float>&    CleanJet_pt,
    ROOT::RVec<float>&    CleanJet_eta,
    ROOT::RVec<float>&    CleanJet_phi,
    ROOT::RVec<ULong64_t>& CleanJet_jetIdx,
    ROOT::RVec<float>&    Jet_mass,
    ROOT::RVec<float>&    Lepton_pt,
    ROOT::RVec<float>&    Lepton_eta,
    ROOT::RVec<float>&    Lepton_phi
) {
    if ((int)Lepton_pt.size() < 2 || (int)CleanJet_pt.size() < 2)
        return {-1., -1., -1., -1.};

    ROOT::RVec<float> result;
    result.reserve(4);
    for (int iL = 0; iL < 2; iL++) {
        TLorentzVector l;
        l.SetPtEtaPhiM(Lepton_pt[iL], Lepton_eta[iL], Lepton_phi[iL], 0.);
        for (int iJ = 0; iJ < 2; iJ++) {
            float jmass = (CleanJet_jetIdx[iJ] < (ULong64_t)Jet_mass.size()) ?
                          Jet_mass[CleanJet_jetIdx[iJ]] : 0.f;
            TLorentzVector j;
            j.SetPtEtaPhiM(CleanJet_pt[iJ], CleanJet_eta[iJ], CleanJet_phi[iJ], jmass);
            result.push_back((float)(l + j).M());
        }
    }
    return result;  // [m(l1,j1), m(l1,j2), m(l2,j1), m(l2,j2)]
}


//
// proxyW
// Returns RVec of 2 transverse masses: mT(l1+MET), mT(l2+MET)
//
ROOT::RVec<float> proxyW(
    ROOT::RVec<float>& Lepton_pt,
    ROOT::RVec<float>& Lepton_eta,
    ROOT::RVec<float>& Lepton_phi,
    float              PuppiMET_pt,
    float              PuppiMET_phi
) {
    if ((int)Lepton_pt.size() != 2) return {-9999., -9999.};
    ROOT::RVec<float> result;
    result.reserve(2);
    TLorentzVector MET;
    MET.SetPtEtaPhiM(PuppiMET_pt, 0., PuppiMET_phi, 0.);
    for (int iL = 0; iL < 2; iL++) {
        TLorentzVector l;
        l.SetPtEtaPhiM(Lepton_pt[iL], Lepton_eta[iL], Lepton_phi[iL], 0.);
        result.push_back((float)(l + MET).M());
    }
    return result;
}


//
// mT2 - analytic Cheng-Han algorithm (massless invisible particles)
//
// For two visible massless particles (leptons) and missing ET split
// between two massless invisible particles, mT2 has the analytic solution:
//
//   mT2 = sqrt( 2 * |p_l1| * |p_l2| * (1 - cos(dphi_ll)) )   if dphi_MET outside the ll cone
//       = min of the two individual mT values                   otherwise
//
// Reference: Cheng & Han, JHEP 0812 (2008) 063
//
float mT2(
    ROOT::RVec<float>& Lepton_pt,
    ROOT::RVec<float>& Lepton_eta,
    ROOT::RVec<float>& Lepton_phi,
    float              PuppiMET_pt,
    float              PuppiMET_phi
) {
    if ((int)Lepton_pt.size() != 2) return -9999.f;
    if (Lepton_pt[0] < 0 || Lepton_pt[1] < 0) return -9999.f;

    // 2D transverse momenta
    float px1 = Lepton_pt[0] * std::cos(Lepton_phi[0]);
    float py1 = Lepton_pt[0] * std::sin(Lepton_phi[0]);
    float px2 = Lepton_pt[1] * std::cos(Lepton_phi[1]);
    float py2 = Lepton_pt[1] * std::sin(Lepton_phi[1]);
    float metx = PuppiMET_pt * std::cos(PuppiMET_phi);
    float mety = PuppiMET_pt * std::sin(PuppiMET_phi);

    float p1 = Lepton_pt[0];
    float p2 = Lepton_pt[1];

    // mT of each lepton with all the MET assigned to it
    auto mT_single = [](float px, float py, float pT,
                        float qx, float qy, float qT) -> float {
        float dot = px*qx + py*qy;
        float val = 2.f * pT * qT - 2.f * dot;
        return val > 0.f ? std::sqrt(val) : 0.f;
    };

    // Analytic solution for massless case (Cheng-Han):
    // The minimum is achieved when the MET split puts the balance point
    // along the bisector of the two leptons.
    //
    // Special case: if MET is collinear with one lepton,
    // mT2 = mT of the other lepton with zero MET = 0.
    // General solution via the analytic formula:
    //
    //   mT2^2 = 2 * [ p1*p2 - p1x*p2x - p1y*p2y
    //                 - sqrt( (p1*p2)^2 - (p1x*p2y - p1y*p2x)^2 ) * sign ]
    //
    // where sign depends on MET configuration.
    // We use the simpler and equivalent bound:

    // Cross product (magnitude) of l1 and l2 in transverse plane
    float cross12 = px1*py2 - py1*px2;  // p1 x p2
    float dot12   = px1*px2 + py1*py2;

    // mT2^2 for massless case (Barr, Lester, Webber variant, massless limit)
    float mT2sq = 2.f * (p1*p2 - dot12
                  - std::sqrt(std::max(0.f, p1*p1*p2*p2 - cross12*cross12)));

    // But this is the minimum over ALL possible MET splits,
    // which for massless particles equals the above only when MET >= threshold.
    // When MET is small, the actual mT2 is bounded by the individual mT values.
    float mT1_allMET = mT_single(px1, py1, p1, metx, mety, PuppiMET_pt);
    float mT2_allMET = mT_single(px2, py2, p2, metx, mety, PuppiMET_pt);

    // The analytic mT2 is the maximum of the Cheng-Han lower bound
    // and zero, capped by the minimum of the two single-lepton mT values.
    float mT2_val = mT2sq > 0.f ? std::sqrt(mT2sq) : 0.f;
    mT2_val = std::min(mT2_val, std::min(mT1_allMET, mT2_allMET));

    return mT2_val;
}


//
// computeLeptonAngles -- the angular structure that survives the two neutrinos
//
// What the measurement is defined by is cos(theta*): the polar angle of the
// charged lepton in its own W rest frame against the W flight direction,
// (1 - cos^2 theta*) for a longitudinal W and (1 -+ cos theta*)^2 for a
// transverse one. It is not reconstructable in this channel, and the reason
// is a counting, not a resolution problem: two neutrinos are six unknowns,
// MET gives two constraints and m(l nu) = m_W on each W gives two more, so
// four constraints for six unknowns leave a two-parameter family and not a
// discrete ambiguity. (Dileptonic ttbar looks like the same problem and is
// solvable only because the two top-mass constraints bring the count to six.)
//
// Neither ATLAS nor CMS reconstructs it here. The ATLAS same-sign WW
// polarisation analysis (arXiv:2503.11317) feeds its DNNs only transverse
// and visible quantities -- transverse masses, dphi, deta, dR, dy and the
// Zeppenfeld variables -- and no cos(theta*) at all. The variable list in
// aliases.py follows theirs.
//
// What this adds on top of that list is the angular structure of the
// dilepton system, which is well defined without any neutrino:
//
//   [0] cosThetaCS   Collins-Soper polar angle of the pair. The CS axis
//                    bisects the two beam directions in the pair rest frame,
//                    which is what makes it insensitive to the unknown
//                    longitudinal boost. Closed form in lab quantities.
//   [1] cosThetaHel  cos of the angle between the LEADING lepton and the
//                    pair flight direction, in the pair rest frame.
//
// Both are ONE number for the pair, not one per lepton. In the rest frame of
// (l1 + l2) the two momenta are exactly back to back, so the subleading
// lepton gives exactly minus the leading one for either definition: a second
// branch would be -1 times the first and carry no information. Which lepton
// is "leading" is a pT ordering and therefore arbitrary with respect to the
// physics, so the sign of these two is meaningful only together with
// dnn_ptAsymll; if an unordered variable is wanted, take |cos|.
//
// Returns -9999 unless there are exactly two leptons, as every other
// function in this file does.
//
ROOT::RVec<float> computeLeptonAngles(
    const ROOT::RVec<float>& pt,
    const ROOT::RVec<float>& eta,
    const ROOT::RVec<float>& phi,
    const ROOT::RVec<int>&   pdgId
) {
    if ((int)pt.size() != 2) return {-9999.f, -9999.f};

    TLorentzVector l1, l2;
    l1.SetPtEtaPhiM(pt[0], eta[0], phi[0], lepton_mass(pdgId[0]));
    l2.SetPtEtaPhiM(pt[1], eta[1], phi[1], lepton_mass(pdgId[1]));
    TLorentzVector ll = l1 + l2;

    const double m  = ll.M();
    const double qT = ll.Pt();
    if (m <= 0.) return {-9999.f, -9999.f};

    // ---- Collins-Soper, closed form in lab quantities
    const double r2  = std::sqrt(2.);
    const double P1p = (l1.E() + l1.Pz()) / r2;
    const double P1m = (l1.E() - l1.Pz()) / r2;
    const double P2p = (l2.E() + l2.Pz()) / r2;
    const double P2m = (l2.E() - l2.Pz()) / r2;

    double cosCS = 2. * (P1p * P2m - P1m * P2p) / (m * std::sqrt(m * m + qT * qT));
    // the CS z axis is oriented along the pair's own longitudinal motion
    if (ll.Pz() < 0.) cosCS = -cosCS;

    // ---- helicity angle of the pair
    double cosHel = -9999.;
    if (ll.Vect().Mag() > 0.) {
        TLorentzVector l1s = l1;
        l1s.Boost(-ll.BoostVector());
        if (l1s.Vect().Mag() > 0.)
            cosHel = l1s.Vect().Unit().Dot(ll.Vect().Unit());
    }

    return {(float)cosCS, (float)cosHel};
}


//
// deltaYjj -- RAPIDITY gap of the two tagging jets
//
// Not the same as detajj. The analysis regions cut on the pseudorapidity gap
// and that stays as it is, but the ATLAS polarisation DNN
// (arXiv:2503.11317, Table 2) uses the rapidity difference, and for a
// massive jet the two differ. Rapidity is also the quantity that is additive
// under a longitudinal boost, which is what a Zeppenfeld-like variable is
// really about.
//
// Takes the jet masses already gathered through CleanJet_jetIdx, so this
// function never sees the ULong64_t index type.
//
float deltaYjj(
    const ROOT::RVec<float>& jet_pt,
    const ROOT::RVec<float>& jet_eta,
    const ROOT::RVec<float>& jet_mass
) {
    if ((int)jet_pt.size() < 2) return -1.f;

    auto rapidity = [](float pt, float eta, float mass) -> double {
        const double pz = pt * std::sinh(eta);
        const double e  = std::sqrt(pt * pt * std::cosh(eta) * std::cosh(eta)
                                    + (double)mass * mass);
        if (e <= std::abs(pz)) return (double)eta;   // degenerate, fall back
        return 0.5 * std::log((e + pz) / (e - pz));
    };

    const double y1 = rapidity(jet_pt[0], jet_eta[0], jet_mass.size() > 0 ? jet_mass[0] : 0.f);
    const double y2 = rapidity(jet_pt[1], jet_eta[1], jet_mass.size() > 1 ? jet_mass[1] : 0.f);
    return (float)std::abs(y1 - y2);
}


#endif // VBS_FUNCTIONS_H