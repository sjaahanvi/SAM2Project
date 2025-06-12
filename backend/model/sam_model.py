import numpy as np
import torch
from PIL import Image
import cv2
from segment_anything import SamPredictor, sam_model_registry

class SAMSegmentor:
    def __init__(self, checkpoint_path="sam_vit_h_4b8939.pth"):
        model_type = "vit_h"
        sam = sam_model_registry[model_type](checkpoint=checkpoint_path)
        sam.to(device="cpu")
        self.predictor = SamPredictor(sam)

    def segment_image(self, image_pil, points, labels):
        try:
            print("Running segmentation...")
            image_np = np.array(image_pil)
            clone = image_np.copy()

            points_np = np.array(points)
            input_labels = np.array(labels)

            print("Setting image to predictor...")
            self.predictor.set_image(clone)

            print("Predicting mask...");
            masks, scores, _ = self.predictor.predict(
                point_coords=points_np,
                point_labels=input_labels,
                multimask_output=False
            )
            
            if masks is None or len(masks) == 0:
                raise ValueError("No mask was returned by predictor")

            seg_mask = masks[0].astype(np.uint8)
            print("Mask shape:", seg_mask.shape)

            seg_mask_3ch = np.stack([seg_mask] * 3, axis=-1)

            main_obj = clone * seg_mask_3ch
            bg_part = clone * (1 - seg_mask_3ch)

            bright_bg = cv2.convertScaleAbs(bg_part, alpha=1.2, beta=30)

            img_h, img_w = clone.shape[:2]
            bright_bg_up = cv2.resize(bright_bg, (img_w * 2, img_h * 2), interpolation=cv2.INTER_CUBIC)
            mask_resized = cv2.resize(seg_mask, (img_w * 2, img_h * 2), interpolation=cv2.INTER_NEAREST)

            img_upscaled = cv2.resize(clone, (img_w * 2, img_h * 2), interpolation=cv2.INTER_LINEAR)
            mask_resized_3ch = np.stack([mask_resized] * 3, axis=-1)

            highlight_color = np.array([255, 0, 0], dtype=np.uint8)
            blend_ratio = 0.4
            highlight_layer = np.ones_like(img_upscaled, dtype=np.uint8) * highlight_color

            highlighted_obj = (
                img_upscaled * mask_resized_3ch * (1 - blend_ratio) +
                highlight_layer * mask_resized_3ch * blend_ratio
            ).astype(np.uint8)

            enhanced_output = (
                bright_bg_up * (1 - mask_resized_3ch) +
                highlighted_obj
            ).astype(np.uint8)

            final_result = Image.fromarray(enhanced_output.astype(np.uint8))
            print("Segmentation successful.")
            return final_result, scores[0]

        except Exception as e:
            print("Error in segment_image():", str(e))
            raise e

