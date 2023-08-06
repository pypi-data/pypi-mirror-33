from PIL import Image
import face_recognition as fr
import numpy as np
import math
import cv2


def PIL2CV(img_array):
    """
    PIL读取的图片转为OpenCV所能读取的图片
    :param img_array: PIL将图片转化成的数组
    :return: OpenCV中的图片数组
    """
    return cv2.cvtColor(np.asarray(img_array), cv2.COLOR_RGB2BGR)


def CV2PIL(img_array):
    """
    OpenCV读取的图片转为PIL所能读取的图片
    :param img_array: OpenCV将图片转化成的数组
    :return: PIL中的图片数组
    """
    return Image.fromarray(cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB))


def CV2FR(img_array):
    """
    OpenCV读取的图片转为face_recognition库所能读取的图片
    :param img_array: OpenCV将图片转化成的数组
    :return: face_recognition库中的图片数组
    """
    return cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)


def PIL2FR(img_array):
    """
    PIL读取的图片转为face_recognition库所能读取的图片
    :param img_array: PIL将图片转化成的数组
    :return: face_recognition库中的图片数组
    """
    return np.array(img_array)


def FR2PIL(img_array):
    """
    face_recognition读取的图片转为face_recognition库所能读取的图片
    :param img_array: face_recognition库中的图片数组
    :return: PIL中的图片数组
    """
    return Image.fromarray(np.uint8(img_array))


def image_preproccessing(cv_img_array):
    """
    调整图片大小
    :param cv_img_array: cv2.imread函数处理后的返回值
    :return: 脸部cv2图片数组和眼睛坐标
    """
    if cv_img_array.shape[1] > 500:
        cv_img_array = cv2.resize(cv_img_array, (0, 0), fx=0.4, fy=0.4)
    fr_img_array = CV2FR(cv_img_array)
    face_location = get_face_location(fr_img_array)
    if face_location:
        cv_img_array = cv_img_array[face_location[0][0]:face_location[0][2], face_location[0][3]:face_location[0][1]]
        eye_locations = get_eye_locations(fr_img_array, face_location)

        for i in range(6):
            height = eye_locations["left_eye"][i][0] - face_location[0][3]
            width = eye_locations["left_eye"][i][1] - face_location[0][0]
            eye_locations["left_eye"][i] = (height, width)

        for i in range(6):
            height = eye_locations["right_eye"][i][0] - face_location[0][3]
            width = eye_locations["right_eye"][i][1] - face_location[0][0]
            eye_locations["right_eye"][i] = (height, width)

        result = {"cv_img_array": cv_img_array, "eye_locations": eye_locations}
        return result
    else:
        return None


def nine_grid(width, height, center):
    """
    传入眼眶矩形的宽度和高度与眼球中心点， 返回眼球中心点在九宫的哪个位置
    :param width: 眼眶矩形的宽度
    :param height: 眼眶矩形的高度
    :param center: 眼球中心的坐标
    :return:  返回根据眼球中心坐标得到的眼球中心所在的九宫格位置
    """
    width_trisection = int(width / 3)
    height_trisection = int(height / 3)

    if (center["x"] < width_trisection) & (center["y"] < height_trisection):
        return 0
    elif (center["x"] > width_trisection * 2) & (center["y"] < height_trisection):
        return 2
    elif center["y"] < height_trisection:
        return 1
    elif (center["x"] < width_trisection) & (center["y"] > height_trisection * 2):
        return 6
    elif (center["x"] > width_trisection * 2) & (center["y"] > height_trisection * 2):
        return 8
    elif center["y"] > height_trisection * 2:
        return 7
    elif center["x"] < width_trisection:
        return 3
    elif center["x"] > width_trisection * 2:
        return 5
    else:
        return 4


def get_face_location(fr_img_array):
    """
    :param fr_img_array: face_recognition中所能使用的图片数组
    :return: A list of tuples of found face locations in css (top, right, bottom, left) order like [(171, 409, 439, 141)]
    """
    face_location = fr.api.face_locations(fr_img_array)
    return face_location


def eyeball_direction(cv_img_array, eye_locations):
    """
    :param cv_img_array: OpenCV中所能使用的图片数组
    :param eye_locations: 眼睛坐标
    :return: 左眼的九宫位置, 左眼用于判断眼球位置的有效的像素占总数的比例,
             右眼的九宫位置, 右眼用于判断眼球位置的有效的像素占总数的比例.
    """
    cv_img_array = np.uint8(np.clip(1.1 * cv_img_array + 30, 0, 255))  # 调节亮度与对比度
    left_coordinate = rect_eye(eye_locations["left_eye"])
    right_coordinate = rect_eye(eye_locations["right_eye"])

    left_eyeball = get_eyeball_location(cv_img_array, left_coordinate)
    left_percent = left_eyeball["percent"]
    left_result = left_eyeball["nine_grid_result"]

    right_eyeball = get_eyeball_location(cv_img_array, right_coordinate)
    right_percent = right_eyeball["percent"]
    right_result = right_eyeball["nine_grid_result"]

    return [left_result, left_percent, right_result, right_percent]


def get_eye_locations(fr_img_array, face_location):
    """
    :param fr_img_array: An image (as a numpy array)
    :param face_location: face location
    :return: dict include eyes locations
    """
    face_landmarks = fr.api.face_landmarks(fr_img_array, face_locations=face_location)
    if face_landmarks:
        left_eye = face_landmarks[0]["left_eye"]
        right_eye = face_landmarks[0]["right_eye"]
        eye_locations = {"left_eye": left_eye, "right_eye": right_eye}
        return eye_locations
    else:
        return None


def rect_eye(eye_landmarks):
    """
    传入face_recognition.face_landmarks函数返回的眼部定位六坐标list,
    返回左上角和右下角的坐标, 构成眼部矩形
    :param eye_landmarks: 眼睛坐标,如[(193, 251), (205, 242), (223, 244), (235, 258), (220, 261), (203, 259)]
    :return: 一个含有四个键值对的dict, 分别为图片左上角的x,y坐标和图片右下角的x,y坐标
    """
    width = eye_landmarks[3][0] - eye_landmarks[0][0]
    height = int((eye_landmarks[4][1] + eye_landmarks[5][1] - eye_landmarks[1][1] - eye_landmarks[2][1]) / 2)
    x = eye_landmarks[0][0]
    y = int((eye_landmarks[1][1] + eye_landmarks[2][1]) / 2)
    return {"x1": x, "y1": y, "x2": x + width, "y2": y + height}


def get_eyeball_location(cv_image_array, eye_coordinate):
    """
    返回在眼部矩形中眼球的位置
    :param cv_image_array: opencv中cv2.imread函数读取的图片
    :param eye_coordinate: 眼部矩形的坐标, rect_eye返回的结果
    :return: percent: 用于判断眼球位置的有效的像素占总数的比例;
             eyeball_center: 眼球中心的坐标;
             nine_grid_result: 眼球九宫位置判断结果;
    """
    eyeball_roi = cv_image_array[eye_coordinate["y1"]:eye_coordinate["y2"], eye_coordinate["x1"]:eye_coordinate["x2"]]
    eyeball_roi = cv2.cvtColor(eyeball_roi, cv2.COLOR_BGR2GRAY)  # 灰度化
    gray_val_total = 0  # 眼部矩形中所有像素灰度值的总值
    gray_val_min = 255  # 眼部矩形中所有像素灰度值中的最小值

    for i in range(eyeball_roi.shape[0]):  # height
        for j in range(eyeball_roi.shape[1]):  # width
            gray_val_total += eyeball_roi[i][j]
            if gray_val_min > eyeball_roi[i][j]:
                gray_val_min = eyeball_roi[i][j]
    # 得到整个眼部矩形中所有像素灰度值的平均值
    gray_val_avg = int(gray_val_total / (eyeball_roi.shape[0] * eyeball_roi.shape[1]))

    eyeball_center_x = 0
    eyeball_center_y = 0
    counter = 0

    if ((gray_val_avg * 2) / 3) > gray_val_min:
        for i in range(eyeball_roi.shape[0]):  # height
            for j in range(eyeball_roi.shape[1]):  # width
                if eyeball_roi[i][j] <= ((gray_val_avg * 2) / 3):
                    eyeball_center_y += i
                    eyeball_center_x += j
                    counter += 1
    # 如果有意外发生: 没有一个像素的灰度值小于灰度平均值的2/3, 则按照最小值的标准来算
    else:
        for i in range(eyeball_roi.shape[0]):  # height
            for j in range(eyeball_roi.shape[1]):  # width
                if eyeball_roi[i][j] <= gray_val_min:
                    eyeball_center_y += i
                    eyeball_center_x += j
                    counter += 1

    # 用于判断眼球位置的有效的像素占总数的比例
    percent = counter / (eyeball_roi.shape[0] * eyeball_roi.shape[1])

    eyeball_center_x = math.ceil(eyeball_center_x / counter)
    eyeball_center_y = math.ceil(eyeball_center_y / counter)
    eyeball_center = {"x": eyeball_center_x, "y": eyeball_center_y}
    nine_grid_result = nine_grid(eyeball_roi.shape[1], eyeball_roi.shape[0], eyeball_center)
    return {"percent": percent, "eyeball_center": eyeball_center, "nine_grid_result": nine_grid_result}


def judge_direction(left_result, left_percent, right_result, right_percent):
    """
    根据左/右眼的九宫位置, 左/右眼用于判断眼球位置的有效的像素占总数的比例,给出双眼方向判定
    :param left_result: 左眼的九宫位置
    :param left_percent: 左眼用于判断眼球位置的有效的像素占总数的比例
    :param right_result: 右眼的九宫位置
    :param right_percent: 右眼用于判断眼球位置的有效的像素占总数的比例
    :return: 给出最终的双眼方向, 一个结果
    """
    if ((left_result == 4) & (right_result != 4)) | ((right_result == 4) & (left_result != 4)):
        return right_result if left_result == 4 else left_result
    elif ((left_result == 1) & ((right_result == 0) | (right_result == 2))) | (
            (right_result == 1) & ((left_result == 0) | (left_result == 2))):
        return right_result if left_result == 1 else left_result
    elif ((left_result == 7) & ((right_result == 6) | (right_result == 8))) | (
            (right_result == 7) & ((left_result == 6) | (left_result == 8))):
        return right_result if left_result == 7 else left_result
    elif ((left_result == 3) & ((right_result == 0) | (right_result == 6))) | (
            (right_result == 3) & ((left_result == 0) | (left_result == 6))):
        return right_result if left_result == 3 else left_result
    elif ((left_result == 5) & ((right_result == 2) | (right_result == 8))) | (
            (right_result == 5) & ((left_result == 2) | (left_result == 8))):
        return right_result if left_result == 7 else left_result
    else:
        return right_result if left_percent < right_percent else left_result


def result_direction(result):
    """
    根据九宫结果给出最终方向
    :param result: 九宫位置
    :return: 翻译九宫位置为中文结果
    """
    if result == 0:
        return "upper left"
    elif result == 1:
        return "up"
    elif result == 2:
        return "upper right"
    elif result == 3:
        return "left"
    elif result == 4:
        return "center"
    elif result == 5:
        return "right"
    elif result == 6:
        return "lower left"
    elif result == 7:
        return "down"
    else:
        return "lower right"
