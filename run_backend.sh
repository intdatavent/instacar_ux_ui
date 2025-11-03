#!/bin/bash

FOLDER_NAME=$1
DIR_PATH=$2

FOLDER=${DIR_PATH}/"uploads"/${FOLDER_NAME}
IMGS_FOLDER=${FOLDER}/"exterior"/
IMGS_INTERIOR_FOLDER=${FOLDER}/"interior"/
YOLO_FOLDER=${DIR_PATH}/../yolo_onnx_inference/

DATA_YAML=${DIR_PATH}/"yolo_cfg"/"car.yaml"
WEIGHTS=${DIR_PATH}/"yolo_cfg"/"model.onnx"

#SAM_FOLDER=${DIR_PATH}/../segment-anything-comunian/
SAM_FOLDER=${DIR_PATH}/../sam2/
SAM_CONFIG=${DIR_PATH}/../sam2/sam2/configs/sam2.1/

DEREFLEC_FOLDER=${DIR_PATH}/../Dereflection-Any-Image/
W_P_FOLDER=${DIR_PATH}/../window_plate_processing
BLENDING_FOLDER=${DIR_PATH}/../instacar_postprocessing
SS_FOLDER=${DIR_PATH}/../semantic-segmentation

OUT_PROJECT_YOLO=${FOLDER}/"tmp"
OUT_YOLO_FOLDERNAME="yolo_output"
OUT_YOLO=${OUT_PROJECT_YOLO}/${OUT_YOLO_FOLDERNAME}
OUT_SAM=${FOLDER}/"tmp"/"sam_output"/
OUT_WP=${FOLDER}/"tmp"/"w_p_output"/
OUT_FINAL=${FOLDER}/"final_exterior"/
OUT_INTERIOR_FINAL=${FOLDER}/"final_interior"/


### RUN YOLO
cd ${YOLO_FOLDER}


echo "RUN YOLO..."
python run_inference.py --input ${IMGS_FOLDER}  --onnx ${WEIGHTS} --output ${OUT_PROJECT_YOLO}/${OUT_YOLO_FOLDERNAME}/"labels" --labels ${DATA_YAML}
echo "RUN YOLO:DONE"



### RUN SAM refinement

cd ${SAM_FOLDER}


echo "RUN SAM..."
python scripts/refine_yolo.py --checkpoint ${SAM_FOLDER}/"sam2.1_hiera_base_plus.pt" --cfg ${SAM_CONFIG}/"sam2.1_hiera_b+.yaml" --input_img ${IMGS_FOLDER} --input_txt ${OUT_PROJECT_YOLO}/${OUT_YOLO_FOLDERNAME}/"labels" --output ${OUT_SAM} --data_yaml ${DATA_YAML}
echo "RUN SAM:DONE"



### /<TODO: RUN DEREFLECTION

#cd ${DEREFLEC_FOLDER}

#
#python run.py ...
#

### />TODO: RUN DEREFLECTION

### />TODO: RUN correct W&P

### RUN Window & Plate processing
#cd ${W_P_FOLDER}



### />TODO: RUN correct W&P


### RUN Blending

cd ${BLENDING_FOLDER}
echo "RUN BLENDING..."
python post_process_fg.py --input_dir ${OUT_SAM} --output_dir ${OUT_WP} --logo ${DIR_PATH}/"images"/"logo.png"
python post_process_bg.py --input_dir ${OUT_WP} --output_dir ${OUT_FINAL} --bkg ${DIR_PATH}/"images/bkg/bkg.png"
echo "RUN BLENDING:DONE"

echo "RUN INTERIOR SEGMENTATION..."
cd ${SS_FOLDER}
python tools/infer_instacar.py --input_dir ${IMGS_INTERIOR_FOLDER} --output_dir ${OUT_INTERIOR_FINAL}

