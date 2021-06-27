# hello
import os
from werkzeug.serving import run_simple
from api import API
import mimetypes
import json
from PIL import Image
from io import BytesIO

from utils.torch_utils import select_device, time_synchronized
from utils.plots import colors, plot_one_box
from utils.general import check_img_size, non_max_suppression, scale_coords
from utils.datasets import LoadImages
from models.experimental import attempt_load
import sys
import time
from pathlib import Path

#from tools import *

import cv2
import torch

FILE = Path(__file__).absolute()
sys.path.append(FILE.parents[0].as_posix())  # add yolov5/ to path


SITE_PATH = os.getcwd()
SITE_ADDRESS = 'http://localhost:8080'

# Init model
weights = 'yolov5s.pt'  # model.pt path(s)
imgsz = 640  # inference size (pixels)
conf_thres = 0.25  # confidence threshold
iou_thres = 0.45  # NMS IOU threshold
max_det = 100  # maximum detections per image
device = ''  # cuda device, i.e. 0 or 0,1,2,3 or cpu
save_img = True  # do not save images/videos
classes = None  # filter by class: --class 0, or --class 0 2 3
agnostic_nms = False  # class-agnostic NMS
augment = False  # augmented inference
line_thickness = 3  # bounding box thickness (pixels)
hide_labels = False  # hide labels
hide_conf = False  # hide confidences

# Directories
save_dir = "./images/processed"  # increment run

# Initialize
device = select_device(device)

# Load model
model = attempt_load(weights, map_location=device)  # load FP32 model
stride = int(model.stride.max())  # model stride
imgsz = check_img_size(imgsz, s=stride)  # check image size
names = model.module.names if hasattr(
    model, 'module') else model.names  # get class names

# Run inference
if device.type != 'cpu':
    model(torch.zeros(1, 3, imgsz, imgsz).to(device).type_as(
        next(model.parameters())))  # run once
# End init model

app = API()
    
def custom_exception_handler(request, response, exception_cls):
    response.text = "Oops! Something went wrong. Please, contact our customer support at +1-202-555-0127."


app.add_exception_handler(custom_exception_handler)


@app.route(r".+\.(css|js|jpg|png|jpeg|svg|eot|ttf|woff|woff2|ico)$")
def static_handler(request, response):
    path = SITE_PATH + request.path
    if os.path.exists(path) and not os.path.isdir(path):

        # if request.if_none_match.__str__()[1:-1] == caching[request.path]:
        #     response.status = 304
        # else:
        response.status = 200
        # response.etag = caching[request.path]
        content_type = mimetypes.guess_type(path)[0]

        response.content_type = content_type

        response.cache_control = "max-age=86400; public"

        with open(path, 'rb') as f:
            response.body = f.read()
    else:
        response.status = 404


def detector(image_data):
    print("Detector")
    img = Image.open(BytesIO(image_data))

    image_number = len(os.listdir("./images/original")) + 1
    print("image_number:", image_number)
    source = f"./images/original/{image_number}.jpg"
    img = img.convert('RGB')
    img.save(source)

    dataset = LoadImages(source, img_size=imgsz, stride=stride)
    t0 = time.time()
    for path, img, im0s, _ in dataset:
        img = torch.from_numpy(img).to(device)
        img = img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        # Inference
        t1 = time_synchronized()
        pred = model(img, augment=augment)[0]

        # Apply NMS
        pred = non_max_suppression(
            pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)
        t2 = time_synchronized()

        # Process detections
        for i, det in enumerate(pred):  # detections per image
            p, s, im0, frame = path, '', im0s.copy(), getattr(dataset, 'frame', 0)

            p = Path(p)  # to Path
            save_path = f"{save_dir}/{p.name}"  # img.jpg
            s += '%gx%g ' % img.shape[2:]  # print string
            # normalization gain whwh
            if len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_coords(
                    img.shape[2:], det[:, :4], im0.shape).round()

                # Print results
                for c in det[:, -1].unique():
                    n = (det[:, -1] == c).sum()  # detections per class
                    # add to string
                    s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "

                # Write results
                for *xyxy, conf, cls in reversed(det):

                    if save_img:  # Add bbox to image
                        c = int(cls)  # integer class
                        label = None if hide_labels else (
                            names[c] if hide_conf else f'{names[c]} {conf:.2f}')
                        plot_one_box(xyxy, im0, label=label, color=colors(
                            c, True), line_thickness=line_thickness)

            # Print time (inference + NMS)
            print(f'Done. ({t2 - t1:.3f}s)')

            # Save results (image with detections)
            if save_img:
                cv2.imwrite(save_path, im0)

    print(f'Done. ({time.time() - t0:.3f}s)')
    return True, image_number

@app.route("/detect-object")
def detect_object(request, response):
    print("detect object")
    POST = request.POST
    image_data = POST['image']

    ok, n = detector(image_data.value)

    resp_obj = {
        'ok': ok,
        'path': f"/images/processed/{n}.jpg"
    }

    response.text = json.dumps(resp_obj)


@app.route("/")
def main(request, response):
    response.status_code = 200
    with open("./index.html", 'rb') as f:
        response.body = f.read()

@app.route(r".+")
def page404(request, response):
    response.status = 301
    response.location = f"{SITE_ADDRESS}/"
    
run_simple("http://localhost/", 80, app, use_reloader=True,
           reloader_type="watchdog")  # , use_debugger=True
