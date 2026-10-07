from PIL import Image, ImageChops, ImageEnhance
import matplotlib.pyplot as plt
import os


def perform_ela(image_path, output_path, heatmap_path, quality=90):
    # Load original image
    original = Image.open(image_path).convert("RGB")

    # Create JPEG-compressed copy
    temp_path = "temp_ela.jpg"
    original.save(temp_path, "JPEG", quality=quality)

    # Load compressed image
    compressed = Image.open(temp_path).convert("RGB")

    # Calculate pixel differences
    difference = ImageChops.difference(original, compressed)

    # Find maximum difference
    extrema = difference.getextrema()
    max_difference = max(max(channel) for channel in extrema)

    if max_difference == 0:
        max_difference = 1

    # Enhance ELA differences
    scale = 255.0 / max_difference
    ela_image = ImageEnhance.Brightness(difference).enhance(scale)

    # Save ELA output
    ela_image.save(output_path)

    # Create heatmap
    gray_image = ela_image.convert("L")

    plt.figure(figsize=(10, 7))
    plt.imshow(gray_image, cmap="hot")
    plt.colorbar(label="ELA Difference")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(heatmap_path, bbox_inches="tight")
    plt.close()

    # Remove temporary file
    os.remove(temp_path)

    print("ELA processing completed successfully.")
    print(f"ELA output: {output_path}")
    print(f"Heatmap: {heatmap_path}")