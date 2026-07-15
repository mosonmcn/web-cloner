import os

def save_content(file_path, content):
    folder = os.path.dirname(file_path)
    os.makedirs(folder, exist_ok=True)

    # Idan rubutu ne (str), mu canza shi zuwa bytes ta hanyar utf-8
    if isinstance(content, str):
        with open(file_path, "wb") as f:
            f.write(content.encode("utf-8"))
    else:
        # Idan danyen bytes ne (Hoto ko Video)
        with open(file_path, "wb") as f:
            f.write(content)
