//
// Jet Energy Resolution application on the fly
//

#include "correction.h"

// --- JER Evaluator Helper Class ---
class JERSmearer {
public:
  JERSmearer(const std::string& jsonPath, const std::string& algo) {
    // Load the centralized JERC correction set
    auto cset = correction::CorrectionSet::from_file(jsonPath);

    // Use the official CMS 2018 UL JER keys
    std::string jer_tag = "Summer19UL18_JRV2_MC";

    cl_res = cset->at(jer_tag + "_PtResolution_" + algo); // e.g. Summer19UL18_JRV2_MC_PtResolution_AK4PFchs
    cl_sf  = cset->at(jer_tag + "_ScaleFactor_"  + algo); // e.g. Summer19UL18_JRV2_MC_ScaleFactor_AK4PFchs

  }

  // Hybrid Smearing Method
  ROOT::RVecF smear(const ROOT::RVecF& jet_pt,
                    const ROOT::RVecF& jet_eta,
                    const ROOT::RVecF& jet_phi,
                    const ROOT::RVecF& gen_pt,
                    double rho,
                    const std::string& systematic,
                    int seed
  ) {

    ROOT::RVecF smeared_pt;
    smeared_pt.reserve(jet_pt.size());

    for (size_t i = 0; i < jet_pt.size(); ++i) {
      float pt = jet_pt[i];
      float eta = jet_eta[i];

      // 1. Get the resolution (sigma_MC)
      float sigma_mc = cl_res->evaluate({eta, pt, rho});

      // 2. Get the Scale Factor (nominal, up, or down)
      float sf = cl_sf->evaluate({eta, systematic});

      float smear_factor = 1.0;

      // 3. Apply Hybrid Smearing (Gen-matching vs Stochastic)
      if (i < gen_pt.size() && gen_pt[i] > 0) {
        // Gen-matched method
        float dpt = pt - gen_pt[i];
        if (std::abs(dpt) < 3.0 * sigma_mc * pt) {
          smear_factor = 1.0 + (sf - 1.0) * dpt / pt;
        }
      } else {
        //
        // https://github.com/latinos/mkShapesRDF/blob/master/mkShapesRDF/processor/modules/JMECalculator.py#L208
        // f"(run<<20) + (luminosityBlock<<10) + event + 1 + int(Jet_eta.size()>0 ? Jet_eta[0]/.01 : 0)"
        //
        // Stochastic/Data-saving method (using a dummy deterministic hash for reproducible results per event)
        // float pseudo_random = std::sin(jet_phi[i] * 1000.0 ) * std::cos(pt);
        float pseudo_random = std::sin(jet_phi[i] * (1000.0 + seed) ) * std::cos(pt);
        if (sf > 1.0) {
          smear_factor = 1.0 + pseudo_random * sigma_mc * std::sqrt(sf * sf - 1.0);
        }
      }

      // Guard against negative/unphysical values
      smeared_pt.push_back(std::max(float(0.0), pt * smear_factor));
    }
    return smeared_pt;
  }

private:
  std::shared_ptr<const correction::Correction> cl_res;
  std::shared_ptr<const correction::Correction> cl_sf;
};


auto get_sorting_indices = [](const ROOT::RVecF& pt) {
  auto indices = ROOT::VecOps::Argsort(pt);
  std::reverse(indices.begin(), indices.end()); // Flips to highest pt first
  return indices;
};


