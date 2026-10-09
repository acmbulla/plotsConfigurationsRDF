
#include <cmath>
float calculate_mass(float pt1, float eta1, float phi1, float pt2, float eta2, float phi2) {
  return std::sqrt(2 * pt1 * pt2 * (std::cosh(eta1 - eta2) - std::cos(phi1-phi2)));
}


