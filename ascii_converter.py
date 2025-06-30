#ascii_converter.py
import os
from PIL import Image, ImageFont, ImageDraw

class UnicodeArt:
    def __init__(self, lang='ascii'):
        self.lang = lang
        self.chars = self.sorted_ascii_chars(lang=self.lang)

    def to_grayscale(self, image_path, width=100):
        char_aspect_ratio = self.lang_check()
        img = Image.open(image_path)
        original_aspect_ratio = img.height / img.width
        new_height = int(original_aspect_ratio * width / char_aspect_ratio)
        img = img.resize((width, new_height))
        return img.convert("L")  # 8비트 그레이스케일

    def lang_check(self):
        if self.lang == 'ascii':
            return 2.0
        else:
            return 1.0

    def get_char_brightness(self, char, font_size=16):
        font = ImageFont.load_default()
        img = Image.new("L", (font_size, font_size), 255)
        draw = ImageDraw.Draw(img)
        draw.text((0, 0), char, font=font, fill=0)
        pixels = list(img.getdata())
        return sum(pixels) / len(pixels)

    def sorted_ascii_chars(self, lang='ascii'):
        language = {'ascii': [chr(i) for i in range(32, 127)],
                    # 'korean': [i for i in "흑암깊검밤밝꽃꿈힘갓땅곰강불살문글달별술산집문눈발끝산하심길바람사랑빛손가하이여우눈아웃일가자"],
                    # 'japan_h': [chr(i) for i in range(0x3040, 0x309F)],
                    # 'japan_k': [chr(i) for i in range(0x30A0, 0x30FF)],
                    # 'chinaese': [chr(i) for i in range(0x4E00, 0x9FFF)],
                    }
        font = {'ascii': 'consola.ttf',
                    # 'korean': 'gulim.ttc',
                    # 'japan_h': 'msgothic.ttc',
                    # 'japan_k': 'msgothic.ttc',
                    # 'chinaese': 'simsun.ttc',
                    }
        self.font = font[lang]
        chars = language[lang]
        chars.sort(key=self.get_char_brightness)
        return ''.join(chars)

    def pixel_to_ascii(self, pixel):
        return self.chars[pixel * len(self.chars) // 256]

    def image_to_ascii(self, image_path, width=100):
        gray_img = self.to_grayscale(image_path, width)
        pixels = gray_img.getdata()
        ascii_str = ''.join(self.pixel_to_ascii(p) for p in pixels)
        ascii_lines = [
            ascii_str[index:index + gray_img.width]
            for index in range(0, len(ascii_str), gray_img.width)
        ]
        return "\n".join(ascii_lines)

    def get_absolute_file_paths(self, folder_path):
        absolute_paths = []
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                # 파일 확장자 체크 (이미지 파일만 고려하도록 개선 가능)
                if os.path.isfile(file_path) and filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    absolute_paths.append(os.path.abspath(file_path))
        return absolute_paths

    def ascii_to_image(self, ascii_text, font_size=12, font_path=None, bg_color="white", text_color="black"):
        lines = ascii_text.strip().split('\n')
        if self.lang == 'ascii':
            line_spacing = int(font_size * 0.11)
        else:
            line_spacing = 0
        if not lines or not lines[0]:
            print("Warning: Empty ASCII text provided.")
            return Image.new("RGB", (100, 50), bg_color)

        # 폰트 설정
        try:
            if font_path and os.path.exists(font_path):
                font = ImageFont.truetype(font_path, font_size)
                print(f"Using font: {font_path}")
            else:
                try:
                    font = ImageFont.truetype(self.font, font_size)
                except IOError:
                    font = ImageFont.load_default()
        except Exception as e:
            print(f"Font loading error: {e}")
            font = ImageFont.load_default()

        padding = 20
        dummy_img = Image.new("RGB", (10, 10))
        draw = ImageDraw.Draw(dummy_img)

        total_height = 0
        max_width = 0

        # 각 줄별 실제 사이즈 측정
        line_sizes = []
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            line_sizes.append((w, h))
            total_height += h
            if w > max_width:
                max_width = w

        img_width = max_width + 2 * padding
        img_height = total_height + 2 * padding + (len(lines) - 1) * line_spacing

        img = Image.new("RGB", (img_width, img_height), bg_color)
        draw = ImageDraw.Draw(img)

        y = padding
        for (line, (w, h)) in zip(lines, line_sizes):
            draw.text((padding, y), line, fill=text_color, font=font)
            y += h + line_spacing  # 다음 줄 위치로 이동

        return img