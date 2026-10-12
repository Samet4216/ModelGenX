import os

IMG_EXTS = (".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff", ".tif")

# Klasör adı olarak kabul edilen split isimleri (Roboflow "valid" kullanır)
SPLIT_NAMES = ("train", "val", "valid", "validation", "test")

# Görsel boyutu okunamazsa bbox piksel boyutunu tahmin etmek için varsayılan
ASSUMED_IMG_SIZE = 640

try:
    from PIL import Image as _PILImage
except ImportError:
    _PILImage = None

try:
    from PyQt6.QtGui import QImageReader as _QImageReader
except ImportError:
    _QImageReader = None


def analyze_dataset(dataset_path):
    """
    YOLO formatındaki bir veri setini analiz eder.

    Desteklenen yapılar:
      1) YOLO standart:   dataset/images/{train,val,test}  +  dataset/labels/{train,val,test}
      2) Roboflow:        dataset/{train,valid,test}/images  +  dataset/{train,valid,test}/labels
      3) Tek split:       images/ + labels/ (veya doğrudan bir split klasörü seçildiğinde)
      4) Düz yapı:        *.jpg / *.png  +  *.txt aynı klasörde

    Etiket formatları: bbox (cls cx cy w h [conf]) ve segmentasyon poligonu (cls x1 y1 x2 y2 ...).
    """
    result = {
        "path": dataset_path,
        "name": os.path.basename(os.path.normpath(dataset_path)),
        "layout": "",          # Algılanan klasör yapısı (log için)
        "splits": {},          # {"train": {...}, "valid": {...}, "test": {...}}
        "class_counts": {},    # {"car": 1234, "person": 567, ...}
        "class_names": [],     # data.yaml'dan veya label'lardan
        "total_images": 0,
        "total_labels": 0,
        "total_annotations": 0,
        "missing_labels": [],  # Label dosyası olmayan görseller
        "empty_labels": [],    # Boş .txt dosyaları (negatif örnek olabilir)
        "bbox_sizes": [],      # (w_px, h_px) listesi - küçük/orta/büyük analizi için
        "estimated_bbox_count": 0,  # Görsel boyutu okunamayıp tahmin edilen kutu sayısı
        "errors": []
    }

    # data.yaml varsa sınıf isimlerini oku
    yaml_path = _find_yaml(dataset_path)
    if yaml_path:
        result["class_names"] = _parse_yaml_classes(yaml_path)

    # Yapıyı otomatik algıla
    pairs, layout = _detect_layout(dataset_path)
    result["layout"] = layout

    if not pairs:
        result["errors"].append(
            "Seçilen klasörde görsel bulunamadı. Klasör yapısını kontrol edin "
            "(images/train, train/images veya düz yapı)."
        )

    for split_name, img_dir, lbl_dir in pairs:
        result["splits"][split_name] = _analyze_split(img_dir, lbl_dir, result)

    # Toplamları hesapla
    for split_data in result["splits"].values():
        result["total_images"] += split_data["image_count"]
        result["total_labels"] += split_data["label_count"]
        result["total_annotations"] += split_data["annotation_count"]

    return result


# =============================================================================
# YAPI ALGILAMA
# =============================================================================
def _has_images(folder):
    try:
        return any(f.lower().endswith(IMG_EXTS) for f in os.listdir(folder))
    except OSError:
        return False


def _split_subdirs(folder):
    """folder altındaki split isimli klasörleri (train/val/valid/test) sıralı döner."""
    found = []
    try:
        for entry in os.listdir(folder):
            full = os.path.join(folder, entry)
            if entry.lower() in SPLIT_NAMES and os.path.isdir(full):
                found.append((SPLIT_NAMES.index(entry.lower()), entry))
    except OSError:
        return []
    return [name for _, name in sorted(found)]


def _detect_layout(root):
    """[(split_adı, görsel_klasörü, etiket_klasörü), ...] ve yapı açıklaması döner."""
    images_dir = os.path.join(root, "images")
    labels_dir = os.path.join(root, "labels")

    # 1) YOLO standart: images/train, labels/train ...
    if os.path.isdir(images_dir):
        pairs = []
        for name in _split_subdirs(images_dir):
            lbl = os.path.join(labels_dir, name)
            if not os.path.isdir(lbl):
                # labels tarafında klasör adı farklı yazılmış olabilir (Valid / valid)
                for alt in _split_subdirs(labels_dir):
                    if alt.lower() == name.lower():
                        lbl = os.path.join(labels_dir, alt)
            pairs.append((name, os.path.join(images_dir, name), lbl))
        if pairs:
            return pairs, "YOLO standart (images/split + labels/split)"

        # images/ içinde doğrudan görseller var (tek split)
        if _has_images(images_dir):
            lbl = labels_dir if os.path.isdir(labels_dir) else images_dir
            base = os.path.basename(os.path.normpath(root))
            name = base if base.lower() in SPLIT_NAMES else "tümü"
            return [(name, images_dir, lbl)], "Tek split (images + labels)"

    # 2) Roboflow: train/images, train/labels ...
    pairs = []
    for name in _split_subdirs(root):
        img = os.path.join(root, name, "images")
        if os.path.isdir(img):
            pairs.append((name, img, os.path.join(root, name, "labels")))
    if pairs:
        return pairs, "Roboflow (split/images + split/labels)"

    # 3) Düz yapı: görseller ve txt'ler aynı klasörde
    if _has_images(root):
        return [("tümü", root, root)], "Düz yapı (görsel + txt aynı klasörde)"

    return [], "Algılanamadı"


# =============================================================================
# YAML
# =============================================================================
def _find_yaml(dataset_path):
    """data.yaml veya benzeri YAML dosyasını bul."""
    for name in ["data.yaml", "data.yml", "dataset.yaml", "dataset.yml"]:
        path = os.path.join(dataset_path, name)
        if os.path.exists(path):
            return path
    # Bir üst dizinde de arayalım
    parent = os.path.dirname(os.path.normpath(dataset_path))
    for name in ["data.yaml", "data.yml"]:
        path = os.path.join(parent, name)
        if os.path.exists(path):
            return path
    return None


def _parse_yaml_classes(yaml_path):
    """YAML dosyasından sınıf isimlerini çıkar (PyYAML bağımlılığı olmadan)."""
    classes = []
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        in_names = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("names:"):
                rest = stripped[len("names:"):].strip()
                # names: ['car', 'person'] formatı
                if rest.startswith("["):
                    items = rest.strip("[]").split(",")
                    classes = [item.strip().strip("'\"") for item in items if item.strip()]
                    return classes
                in_names = True
                continue
            if in_names:
                if stripped.startswith("- "):
                    classes.append(stripped[2:].strip().strip("'\""))
                elif stripped and not stripped.startswith("#") and ":" in stripped:
                    # "0: car" formatı
                    parts = stripped.split(":", 1)
                    try:
                        int(parts[0].strip())
                        classes.append(parts[1].strip().strip("'\""))
                    except ValueError:
                        break
                elif not stripped or (not stripped.startswith("-") and ":" not in stripped):
                    break
    except Exception:
        pass
    return classes


# =============================================================================
# SPLIT ANALİZİ
# =============================================================================
def _read_image_size(path):
    """Görselin (genişlik, yükseklik) değerini piksel olarak döner; okunamazsa None."""
    if _PILImage is not None:
        try:
            with _PILImage.open(path) as im:
                return im.size
        except Exception:
            pass
    if _QImageReader is not None:
        try:
            size = _QImageReader(path).size()
            if size.isValid():
                return size.width(), size.height()
        except Exception:
            pass
    return None


def _parse_label_line(parts):
    """
    Bir etiket satırından (sınıf, w_norm, h_norm) çıkarır.
    - bbox:       cls cx cy w h [conf]        (5 veya 6 alan)
    - poligon:    cls x1 y1 x2 y2 x3 y3 ...   (en az 3 nokta; bbox poligondan türetilir)
    Satır anotasyon değilse None, boyut hesaplanamazsa (sınıf, None, None) döner.
    """
    n = len(parts)
    if n < 5:
        return None
    try:
        if n in (5, 6):
            return parts[0], float(parts[3]), float(parts[4])
        if n >= 7 and (n - 1) % 2 == 0:
            xs = [float(v) for v in parts[1::2]]
            ys = [float(v) for v in parts[2::2]]
            return parts[0], max(xs) - min(xs), max(ys) - min(ys)
    except ValueError:
        pass
    return parts[0], None, None


def _analyze_split(img_dir, lbl_dir, result):
    """Tek bir split (train/val/test) klasörünü analiz et."""
    split_data = {
        "image_count": 0,
        "label_count": 0,
        "annotation_count": 0,
        "class_distribution": {},
        "images_without_labels": [],
        "empty_labels": [],
        "bbox_widths": [],
        "bbox_heights": [],
    }

    # Görsel dosyalarını bul
    image_files = []
    if os.path.isdir(img_dir):
        for f in os.listdir(img_dir):
            if f.lower().endswith(IMG_EXTS):
                image_files.append(f)

    split_data["image_count"] = len(image_files)

    # Her görsel için eşleşen label dosyasını kontrol et
    for img_file in image_files:
        base_name = os.path.splitext(img_file)[0]
        label_file = os.path.join(lbl_dir, base_name + ".txt")

        if not os.path.exists(label_file):
            split_data["images_without_labels"].append(img_file)
            result["missing_labels"].append(os.path.join(img_dir, img_file))
            continue

        split_data["label_count"] += 1

        # Label dosyasını oku ve anotasyonları say
        try:
            with open(label_file, 'r', encoding='utf-8') as f:
                lines = [l.strip() for l in f.readlines() if l.strip()]

            if not lines:
                split_data["empty_labels"].append(img_file)
                result["empty_labels"].append(label_file)
                continue

            # Görsel boyutu (piksel) - sadece anotasyonu olan görseller için, bir kez okunur
            img_size = _read_image_size(os.path.join(img_dir, img_file))

            for line in lines:
                parsed = _parse_label_line(line.split())
                if parsed is None:
                    continue

                class_id, w, h = parsed
                split_data["annotation_count"] += 1

                # Sınıf ismine çevir
                try:
                    idx = int(class_id)
                    if result["class_names"] and 0 <= idx < len(result["class_names"]):
                        class_name = result["class_names"][idx]
                    else:
                        class_name = f"class_{idx}"
                except ValueError:
                    class_name = class_id

                split_data["class_distribution"][class_name] = \
                    split_data["class_distribution"].get(class_name, 0) + 1
                result["class_counts"][class_name] = \
                    result["class_counts"].get(class_name, 0) + 1

                # BBox boyutları: normalize değerler split'te, piksel değerler genel sonuçta
                if w is not None and h is not None:
                    split_data["bbox_widths"].append(w)
                    split_data["bbox_heights"].append(h)
                    if img_size:
                        result["bbox_sizes"].append((w * img_size[0], h * img_size[1]))
                    else:
                        result["bbox_sizes"].append(
                            (w * ASSUMED_IMG_SIZE, h * ASSUMED_IMG_SIZE)
                        )
                        result["estimated_bbox_count"] += 1
        except Exception as e:
            result["errors"].append(f"{label_file}: {str(e)}")

    return split_data