from typing import Dict, Any
import json
from PIL import Image

from consts import CROP_DIR, CROP_RESULT, SEQ, IS_TRUE, IGNOR, CROP_PATH, X0, X1, Y0, Y1, COLOR, SEQ_IMAG, \
    COL, X, Y, RADIUS, GTIM_PATH, IMAG_PATH, NAME, JSON_PATH, ZOOM

from pandas import DataFrame


def make_crop(x_coord, y_coord, color, image, radius):
    """
    The function that creates the crops from the image.
    Your return values from here should be the coordinates of the crops in this format (x0, x1, y0, y1, crop content):
    'x0'  The bigger x value (the right corner)
    'x1'  The smaller x value (the left corner)
    'y0'  The smaller y value (the lower corner)
    'y1'  The bigger y value (the higher corner)
    """
    crop_size = (radius * 2.8, radius * 8.4)  # Specify the crop size (width, height)
    if color == 'g':
        y1 = y_coord + radius * 1.4
        y0 = y_coord - crop_size[1]
    elif color == 'r':
        y1 = y_coord + crop_size[1]
        y0 = y_coord - radius * 1.4

    x0 = x_coord + crop_size[0] // 2
    x1 = x_coord - crop_size[0] // 2
    crop_content = image.crop((x1, y0, x0, y1))

    return x0, x1, y0, y1, crop_content


def check_crop(filename, x0, x1, y0, y1, *args, **kwargs):
    """
    Here you check if your crop contains a traffic light or not.
    Try using the ground truth to do that (Hint: easier than you think for the simple cases, and if you found a hard
    one, just ignore it for now :). )
    """
    with open(filename) as json_file:
        data = json.load(json_file)
    for i in range(len(data["objects"])):
        if data["objects"][i]["label"] == "traffic light":
            list_point = data["objects"][i]["polygon"]
            min_x = min(point[0] for point in list_point)
            max_x = max(point[0] for point in list_point)
            min_y = min(point[1] for point in list_point)
            max_y = max(point[1] for point in list_point)
            if x0 <= min_x and x1 >= max_x:
                if y0 <= min_y and y1 >= max_y:
                    return True, False
    return False, False


def create_crops(df: DataFrame) -> DataFrame:
    # Your goal in this part is to take the coordinates you have in the df, run on it, create crops from them, save them
    # in the 'data' folder, then check if crop you have found is correct (meaning the TFL is fully contained in the
    # crop) by comparing it to the ground truth and in the end right all the result data you have in the following
    # DataFrame (for doc about each field and its input, look at 'CROP_RESULT')
    #
    # *** IMPORTANT ***
    # All crops should be the same size or smaller!!!

    # creates a folder for you to save the crops in, recommended not must
    if not CROP_DIR.exists():
        CROP_DIR.mkdir()

    # For documentation about each key end what it means, click on 'CROP_RESULT' and see for each value what it means.
    # You want to stick with this DataFrame structure because its output is the same as the input for the next stages.
    result_df = DataFrame(columns=CROP_RESULT)

    # A dict containing the row you want to insert into the result DataFrame.
    result_template: Dict[Any] = {SEQ: '', IS_TRUE: '', IGNOR: '', CROP_PATH: '',
                                  X0: '', X1: '', Y0: '', Y1: '', COL: '', ZOOM: ''}
    for index, row in df.iterrows():
        result_template[SEQ] = row[SEQ_IMAG]
        result_template[COL] = row[COLOR]

        # example code:
        # ******* rewrite ONLY FROM HERE *******
        image_path = row[IMAG_PATH]
        original_image = Image.open(image_path)

        x0, x1, y0, y1, crop = make_crop(row[X], row[Y], row[COLOR], original_image, row[RADIUS])
        result_template[X0], result_template[X1], result_template[Y0], result_template[Y1] = x0, x1, y0, y1

        # Define the path for the crop image
        crop_path: str = f'{row[NAME]}_{row[SEQ_IMAG]}_{index}.png'
        desired_size = (32, 96)
        resized_crop_content = crop.resize(desired_size)
        resized_crop_content.save(CROP_DIR / crop_path)
        # crop.save(CROP_DIR / crop_path)
        result_template[CROP_PATH] = crop_path
        # result_template[IS_TRUE], result_template[IGNOR] = check_crop(df[GTIM_PATH], x0, x1, y0, y1, crop)
        result_template[IS_TRUE], result_template[IGNOR] = check_crop(row[JSON_PATH], x0, x1, y0, y1)

        # TODO: make sure this is good
        result_template[ZOOM] = 32 / (y1 - y0)

        # ******* TO HERE *******

        # added to current row to the result DataFrame that will serve you as the input to part 2 B).
        result_df = result_df._append(result_template, ignore_index=True)
    return result_df
