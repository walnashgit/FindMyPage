
import os
from markitdown import MarkItDown


def convert(str):
    converter = MarkItDown()
    # result = converter.convert(str)
    result = converter.convert_url(str)
    markdown = result.text_content
    print(markdown)

if __name__ == "__main__":
    # file_path = os.path.join('sample.html')
    file_path = "https://playbooks.com/mcp/lane83-telegram"
    convert(file_path)