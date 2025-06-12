from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from model.sam_model import SAMSegmentor
from io import BytesIO
from PIL import Image
import ast 

app = Flask(__name__)
# CORS(app)
CORS(app, origins=["http://localhost:5173"])

segmentor = SAMSegmentor("sam_vit_h_4b8939.pth")

@app.route("/segment", methods=["POST"])
def segment():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    try:
        file = request.files["image"]
        image = Image.open(file.stream).convert("RGB")

        data = request.form
        points_str = data.get("points", "[]")
        labels_str = data.get("labels", "[]")

        # Use ast.literal_eval instead of eval
        points = ast.literal_eval(points_str)
        labels = ast.literal_eval(labels_str)

        print("Received points:", points)
        print("Received labels:", labels)

        if not points or not labels:
            return jsonify({"error": "Points or labels missing"}), 400

        segmented_image, score = segmentor.segment_image(image, points, labels)

        buffer = BytesIO()
        segmented_image.save(buffer, format="PNG")
        buffer.seek(0)

        print("Segmented image successfully created.")
        return send_file(buffer, mimetype="image/png")

    except Exception as e:
        print("Segmentation Error:", str(e))
        return jsonify({"error": "Failed to segment image", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
