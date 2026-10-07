import os
from PIL import Image, ImageDraw, ImageFont
import uuid

OUTPUT_DIR = "generated_certificates"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_certificate_image(name: str, course: str) -> str:
    """
    Generates a simple certificate and returns the file path.
    Raises an exception to simulate failure if the name is 'FAIL_ME'.
    """
    if name == "FAIL_ME":
        raise ValueError("Simulated generation failure for testing.")

    # Create a blank white image (Our "Predefined Template")
    img = Image.new('RGB', (800, 600), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Draw a simple border
    draw.rectangle([20, 20, 780, 580], outline="gold", width=10)

    # Use default font since we don't know what fonts are on the host OS
    font = ImageFont.load_default()

    # Draw text
    draw.text((300, 150), "Certificate of Completion", fill="black", font=font)
    draw.text((350, 250), "Presented to:", fill="black", font=font)
    draw.text((350, 300), name, fill="blue", font=font)
    draw.text((350, 400), f"For completing: {course}", fill="black", font=font)

    file_name = f"cert_{uuid.uuid4().hex}.png"
    file_path = os.path.join(OUTPUT_DIR, file_name)
    img.save(file_path)
    
    return file_path