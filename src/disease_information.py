from typing import Any


DISEASE_INFORMATION: dict[str, dict[str, Any]] = {
    "Pepper,_bell___Bacterial_spot": {
        "crop": "Bell Pepper",
        "disease": "Bacterial Spot",
        "status": "diseased",
        "risk_level": "High",
        "description": (
            "Bacterial spot causes small, dark, water-soaked spots on leaves "
            "and fruits. Severe infection may cause leaf drop and reduced yield."
        ),
        "treatment": [
            "Remove and destroy heavily infected leaves.",
            "Avoid working with plants when leaves are wet.",
            "Use an approved copper-based bactericide after expert consultation.",
            "Avoid overhead watering.",
        ],
        "prevention": [
            "Use disease-free and certified seeds.",
            "Maintain proper spacing between plants.",
            "Disinfect farming tools regularly.",
            "Rotate crops and avoid planting peppers in the same soil repeatedly.",
        ],
    },

    "Pepper,_bell___healthy": {
        "crop": "Bell Pepper",
        "disease": "Healthy",
        "status": "healthy",
        "risk_level": "Low",
        "description": (
            "The leaf appears healthy with no strong visual symptoms of the "
            "diseases currently supported by the model."
        ),
        "treatment": [
            "No disease treatment is currently required.",
            "Continue normal crop monitoring.",
        ],
        "prevention": [
            "Use balanced fertilization.",
            "Maintain proper irrigation.",
            "Inspect leaves regularly for new spots or discoloration.",
        ],
    },

    "Potato___Early_blight": {
        "crop": "Potato",
        "disease": "Early Blight",
        "status": "diseased",
        "risk_level": "Medium",
        "description": (
            "Early blight commonly creates brown circular lesions with "
            "concentric ring patterns, usually on older leaves."
        ),
        "treatment": [
            "Remove severely infected leaves.",
            "Apply an approved fungicide after consulting an agricultural expert.",
            "Avoid wetting foliage during irrigation.",
            "Improve air circulation around plants.",
        ],
        "prevention": [
            "Rotate potatoes with non-solanaceous crops.",
            "Use healthy and certified seed potatoes.",
            "Maintain balanced soil nutrition.",
            "Remove infected plant debris after harvesting.",
        ],
    },

    "Potato___healthy": {
        "crop": "Potato",
        "disease": "Healthy",
        "status": "healthy",
        "risk_level": "Low",
        "description": (
            "The potato leaf appears healthy based on the supported model classes."
        ),
        "treatment": [
            "No disease treatment is currently required.",
            "Continue routine crop observation.",
        ],
        "prevention": [
            "Use certified seed potatoes.",
            "Maintain proper irrigation and drainage.",
            "Inspect crops regularly.",
        ],
    },

    "Potato___Late_blight": {
        "crop": "Potato",
        "disease": "Late Blight",
        "status": "diseased",
        "risk_level": "High",
        "description": (
            "Late blight may cause dark, water-soaked lesions that expand rapidly "
            "during cool and humid weather."
        ),
        "treatment": [
            "Remove and safely destroy infected plant material.",
            "Avoid overhead irrigation.",
            "Apply an approved late-blight fungicide under expert guidance.",
            "Separate infected plants where practical.",
        ],
        "prevention": [
            "Use resistant potato varieties when available.",
            "Use certified disease-free seed potatoes.",
            "Provide proper field drainage.",
            "Monitor crops closely during humid and rainy weather.",
        ],
    },

    "Tomato___Early_blight": {
        "crop": "Tomato",
        "disease": "Early Blight",
        "status": "diseased",
        "risk_level": "Medium",
        "description": (
            "Early blight produces brown spots with circular ring patterns, "
            "especially on older tomato leaves."
        ),
        "treatment": [
            "Remove infected lower leaves.",
            "Keep leaves dry during irrigation.",
            "Use an approved fungicide after expert consultation.",
            "Add mulch to reduce soil splash.",
        ],
        "prevention": [
            "Rotate tomato crops regularly.",
            "Maintain suitable spacing between plants.",
            "Remove infected plant debris.",
            "Avoid watering leaves directly.",
        ],
    },

    "Tomato___healthy": {
        "crop": "Tomato",
        "disease": "Healthy",
        "status": "healthy",
        "risk_level": "Low",
        "description": (
            "The tomato leaf appears healthy based on the diseases supported "
            "by the current model."
        ),
        "treatment": [
            "No disease treatment is currently required.",
            "Continue regular plant monitoring.",
        ],
        "prevention": [
            "Maintain balanced watering and fertilization.",
            "Ensure suitable plant spacing.",
            "Inspect leaves regularly for spots, yellowing, or curling.",
        ],
    },

    "Tomato___Late_blight": {
        "crop": "Tomato",
        "disease": "Late Blight",
        "status": "diseased",
        "risk_level": "High",
        "description": (
            "Late blight can cause irregular dark lesions on leaves and stems. "
            "It may spread quickly under cool, wet, and humid conditions."
        ),
        "treatment": [
            "Remove and destroy infected leaves and plants.",
            "Avoid overhead watering.",
            "Apply an approved fungicide under agricultural expert guidance.",
            "Do not compost heavily infected plant material.",
        ],
        "prevention": [
            "Use resistant tomato varieties when available.",
            "Improve spacing and airflow.",
            "Avoid prolonged leaf wetness.",
            "Monitor crops frequently during humid weather.",
        ],
    },
}


def get_disease_information(class_name: str) -> dict[str, Any]:
    """
    Return agricultural information for a predicted model class.

    Args:
        class_name: Exact class name produced by the model.

    Returns:
        Disease information dictionary.
    """

    information = DISEASE_INFORMATION.get(class_name)

    if information is None:
        return {
            "crop": "Unknown",
            "disease": "Unknown",
            "status": "unknown",
            "risk_level": "Unknown",
            "description": (
                "No agricultural information is currently available "
                "for this prediction."
            ),
            "treatment": [
                "Consult a qualified agricultural expert.",
            ],
            "prevention": [
                "Continue monitoring the plant carefully.",
            ],
        }

    return information.copy()