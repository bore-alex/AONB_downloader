import requests
import os
import time
import random
from PIL import Image
import logging
import certifi

# Настройка логирования
logging.basicConfig(level=logging.INFO)

def download_image(url, save_path, retries=3):
    for attempt in range(retries):
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10, verify=certifi.where())
            response.raise_for_status()
            with open(save_path, 'wb') as file:
                file.write(response.content)
            logging.info(f"Изображение сохранено: {save_path}")
            return True
        except requests.HTTPError:
            logging.warning(f"Попытка {attempt + 1}: Изображение по ссылке {url} не найдено.")
        except requests.exceptions.RequestException as e:
            logging.error(f"Ошибка: {e}")

    logging.error(f"Изображение не найдено после {retries} попыток: {url}")
    return False

def create_pdf(image_paths, output_pdf_path):
    images = []
    for image_path in image_paths:
        try:
            img = Image.open(image_path)
            images.append(img.convert('RGB'))
        except Exception as e:
            logging.error(f"Не удалось открыть изображение {image_path}: {e}")
            return False

    if images:
        images[0].save(output_pdf_path, save_all=True, append_images=images[1:])
        logging.info(f"PDF-документ создан: {output_pdf_path}")
        return True
    return False

def main():
    base_url = "https://webirbis.aonb.ru/irbisdoc/kr/2016/16ps117/files/assets/common/page-substrates/"  # Базовый URL, по которому лежат jpg-сканы страниц книги
    folder_path = "D:/new_book/"
    os.makedirs(folder_path, exist_ok=True)

    image_paths = []
    all_downloaded = True

    for i in range(1, 28):  # Указываем число страниц книги
        page_number = f"page{i:04d}_5.jpg"  # Нумерация страниц согласно паттерну, принятому в АОНБ
        image_url = f"{base_url}{page_number}"
        save_path = os.path.join(folder_path, page_number)

        if os.path.exists(save_path):
            logging.info(f"Файл уже существует: {save_path}, пропускаем загрузку.")
            image_paths.append(save_path)
            continue

        if download_image(image_url, save_path):
            image_paths.append(save_path)
        else:
            all_downloaded = False

        # Пауза между запросами
        time.sleep(random.uniform(0.5, 1))

    if all_downloaded:
        output_pdf_path = os.path.join(folder_path, "output.pdf")
        create_pdf(image_paths, output_pdf_path)
    else:
        logging.error("Некоторые изображения не были загружены. PDF-документ не создан.")

if __name__ == "__main__":
    main()
