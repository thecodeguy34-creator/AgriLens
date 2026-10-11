export const DISEASE_DATA = {
  "early_blight": {
    name: "Early Blight",
    scientificName: "Alternaria solani",
    severity: "High",
    badgeColor: "#ef4444",
    description: "Dark brown concentric ring spots ('target board') surrounded by yellow halos, starting on lower leaf foliage.",
    organicTreatment: [
      "Prune affected lower leaves to halt spore splashback.",
      "Spray copper octanoate or neem oil once every 7 to 10 days."
    ],
    chemicalTreatment: [
      "Apply chlorothalonil or mancozeb at first sign of leaf spots."
    ],
    prevention: [
      "Practice 3-year crop rotation.",
      "Use drip irrigation to keep leaf surfaces dry."
    ]
  },
  "septoria_leaf_spot": {
    name: "Septoria Leaf Spot",
    scientificName: "Septoria lycopersici",
    severity: "Medium",
    badgeColor: "#f59e0b",
    description: "Small circular spots with greyish centers and dark brown margins.",
    organicTreatment: [
      "Remove diseased leaves immediately.",
      "Apply bio-fungicides containing Bacillus subtilis."
    ],
    chemicalTreatment: [
      "Apply broad-spectrum copper fungicides."
    ],
    prevention: [
      "Destroy all crop debris post-harvest.",
      "Stake plants to keep foliage elevated."
    ]
  },
  "yellow_leaf_curl_virus": {
    name: "Yellow Leaf Curl Virus",
    scientificName: "TYLCV (Begomovirus)",
    severity: "Critical",
    badgeColor: "#dc2626",
    description: "Severe upward leaf curling, yellowing leaf margins, stunted growth, and flower drop caused by whitefly transmission.",
    organicTreatment: [
      "Apply insecticidal soaps or horticultural oils to suppress whiteflies.",
      "Hang yellow sticky traps around plant canopies."
    ],
    chemicalTreatment: [
      "Apply systemic insecticides targeting whiteflies (e.g., imidacloprid)."
    ],
    prevention: [
      "Use fine mesh insect netting over nursery beds.",
      "Plant TYLCV-resistant hybrids."
    ]
  },
  "healthy": {
    name: "Healthy Foliage",
    scientificName: "Solanum lycopersicum",
    severity: "None",
    badgeColor: "#10b981",
    description: "Vibrant leaf pigmentation with no pathogen presence detected.",
    organicTreatment: ["Maintain regular soil hydration."],
    chemicalTreatment: ["No chemical application needed."],
    prevention: ["Continue weekly visual foliage checks."]
  }
};