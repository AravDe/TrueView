import hashlib, cv2
# from PIL import Image

def normalizedImage(path):
    img = cv2.imread(path)

    gr_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    norm_gr_img = cv2.normalize(
        gr_img, None, alpha= 0.0, beta= 256.0, norm_type= cv2.NORM_MINMAX)

    norm_cl_img = cv2.cvtColor(norm_gr_img, cv2.COLOR_GRAY2BGR)
    
    cv2.imwrite(path, norm_cl_img)

    return path

def cryptoHashGenerator(path):
    norm_img_path = normalizedImage(path)
    sh256 = hashlib.sha256()

    with open(norm_img_path, mode= rb) as f:
        while chunk := f.read(4096):
            sh256.update(chunk)
            chunk = f.read(4096)

    return sh256.hexdigest()