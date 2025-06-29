from PIL import Image

# A short, easy-to-spot end-of-message marker
SENTINEL = "#####"

# -------------------------------------------------
# ENCODE
# -------------------------------------------------
def encode_text(image_path: str, message: str, output_path: str) -> None:
    """Hide <message> inside <image_path> and save to <output_path>."""
    img = Image.open(image_path)
    # 1. Add sentinel, then convert to one long binary string
    payload = message + SENTINEL
    binary_msg = "".join(format(ord(ch), "08b") for ch in payload)

    # 2. Replace the least-significant bit of each colour channel
    pixels = list(img.getdata())
    i = 0
    for idx, pixel in enumerate(pixels):
        pixel = list(pixel)           # (R, G, B) → mutable
        for j in range(3):            # each channel
            if i < len(binary_msg):
                pixel[j] = pixel[j] & ~1 | int(binary_msg[i])
                i += 1
        pixels[idx] = tuple(pixel)
        if i >= len(binary_msg):
            break                     # finished embedding

    # 3. Save stego-image
    img.putdata(pixels)
    img.save(output_path)
    print(f"✅ Message encoded and saved in: {output_path}")


# -------------------------------------------------
# DECODE
# -------------------------------------------------
def decode_text(image_path: str) -> str:
    """Extract and return the hidden message from <image_path>."""
    img = Image.open(image_path)
    bits = ""

    # 1. Read the LSB of every channel
    for pixel in img.getdata():
        for val in pixel[:3]:
            bits += str(val & 1)

    # 2. Re-group into bytes → chars until sentinel appears
    chars = [chr(int(bits[i : i + 8], 2)) for i in range(0, len(bits), 8)]
    message = ""
    for ch in chars:
        message += ch
        if message.endswith(SENTINEL):
            return message[:-len(SENTINEL)]   # strip sentinel

    return "(No hidden message found)"


# -------------------------------------------------
# QUICK DEMO
# -------------------------------------------------
if __name__ == "__main__":
    # Put a PNG named 'input.png' in the same folder first ↓
    encode_text("input.png", "Hello, this is secret!", "output.png")
    print("📩 Decoded message:", decode_text("output.png"))

