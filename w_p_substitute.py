import os
import argparse
import yaml
from glob import glob
import shutil

if __name__=='__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run substitute of window and plate car processing.")
    parser.add_argument("--input_dir", type=str, required=True, help="Directory containing n folders of sam masks.")
    parser.add_argument("--output_dir", type=str, required=True, help="Directory for output.")

    args = parser.parse_args()

    sam_dir = args.input_dir
    result_dir = args.output_dir
    os.makedirs(result_dir, exist_ok=True)

    input_folders = sorted(glob(os.path.join(sam_dir, "*")))

    for input_folder in input_folders:
        with open(os.path.join(input_folder, "mask_class.yaml"), encoding="utf-8") as s:
            yd = yaml.safe_load(s)
            car_names = {i[0]:i[1] for i in yd.items() if i[1]["class"] == "car"}
            input_file = sorted(car_names.items(), key=lambda item: int(item[1]["size"]), reverse=True)[0][0]
            shutil.copy(os.path.join(sam_dir, input_folder, input_file), os.path.join(result_dir, os.path.splitext(os.path.basename(input_folder))[0]) + '.png')