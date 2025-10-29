# DICOM to NIfTI Conversion of CT exams

This guide explains how to set up a Python virtual environment with the required dependencies for the DICOM to NIfTI conversion script and then use the conversion script.

# Context

For a given folder containing CT images in DICOM format stored in `MWA_20250918a_CT/IMAGES/`, the script will produce the corresponding arborescence with the NIFTI and JSON files. Then, everything is zipped up and to be sent or uploaded.

```
├── MWA20250918a
│   └── 2025-09-08_CT-pre-ablation
│       ├── RAW-DICOM
│       ├── RAW-NIFTI
│       │   ├── 004__leber-art.-0.75-wt-via.json
│       │   ├── 004__leber-art.-0.75-wt-via.nii.gz
│       │   ├── 005__leber-art.-3.0-wt.json
│       │   ├── 005__leber-art.-3.0-wt.nii.gz
│       │   ├── 013__equilibriumphas-0.75-wt-via.json
│       │   ├── 013__equilibriumphas-0.75-wt-via.nii.gz
│       │   ├── 014__equilibriumphas-3.0-wt.json
│       │   └── 014__equilibriumphas-3.0-wt.nii.gz
│       └── RAW-NRRD
└── MWA20250918a_CT_nii_ready.zip
```

---

## Prerequisites

- Python 3.8 or higher installed on your system.
- `pip` (Python package manager) installed.
- dcm2niix (`sudo apt-get install  dcm2niix` if necessary)
- find the location of dcm2niix using `which dcm2niix`
---

## Step 1: Create a Virtual Environment

Open a terminal and navigate to your project directory. Run the following command to create a virtual environment:

```bash
python3 -m venv PyEnvCTdcm2nii

```
---

## 2. Activate the Virtual Environment

### Linux/MacOS

```bash
source PyEnvCTdcm2nii/bin/activate
```

After activation, your terminal prompt should show `(PyEnvCTdcm2nii)`.

---

## 3. Install Required Dependencies

With the virtual environment activated, install the required packages:

```bash
pip install DateTime==5.5 dicom_csv==0.4.0 numpy==2.3.4 pandas==2.3.3 pydicom==3.0.1
```

or if you get a message error about numpy, pick

```bash
pip install DateTime==5.5 dicom_csv==0.4.0 numpy==2.2.6 pandas==2.3.3 pydicom==3.0.1
```

---

## 4. Verify the Installation

Check the installed packages and their versions:

```bash
pip list
```

---

## 5. Deactivate the Virtual Environment

When you are done, deactivate the environment:

```bash
deactivate
```


## 6. Use the script

You must define:

* dicom_folder: the folder containing DICOM images  
* nifti_patient_folder_out : the output folder for NIfTI images
* dcm2niix : the location of dcm2niix on your system
* step 1: will sort all DICOM files per sequence in temporary folder /nifti_patient_folder_out/tmp/001/ [...]/tmp/002/ [...]/tmp/003/
  step 2: will convert each sequence in nifti and delete the temporary folder
* both will do step 1 and step 2


> **Note:** the folder `IMAGES` being hard coded, make sure everything is in MWA_XXXXXXXXa_CT/IMAGES/ otherwise it won't work. 


```
python3 convert_dicom_to_nifti.py --dicom_folder /home/vozenne/Bureau/ToBeDeleted/MWA_20250918a_CT/IMAGES/ \
                      --nifti_patient_folder_out /home/vozenne/Bureau/ToBeDeleted/OUTPUT_CT/ \
                      --dcm2niix /usr/bin/dcm2niix \
                      --step1
```

or

```
python3 convert_dicom_to_nifti.py --dicom_folder /home/vozenne/Bureau/ToBeDeleted/MWA_20250918a_CT/IMAGES/ \
                      --nifti_patient_folder_out /home/vozenne/Bureau/ToBeDeleted/OUTPUT_CT/ \
                      --dcm2niix /usr/bin/dcm2niix \
                      --both
```

option `both` should end with 
```

A zip file with all converted data is available ,   /home/vozenne/Bureau/ToBeDeleted/OUTPUT_CT/MWA20250918a_CT_nii_ready.zip
=========Step 2 Done=======================
Finished.

```

option `step 1` should return

```
=========Step 1 Starting =======================
      /home/vozenne/Bureau/ToBeDeleted/MWA_20250918a_CT/IMAGES/
         contains  986  images files
IM00868: : 986it [00:01, 565.10it/s]
         that are from 14 different series
===========================
not moving :  1  series
===========================
not moving :  2  series
===========================
not moving :  3  series
             ===========================
             moving  336  images of serie n° 4
             ===========================
             moving  157  images of serie n° 5
===========================
not moving :  6  series
===========================
not moving :  7  series
===========================
not moving :  8  series
===========================
not moving :  9  series
===========================
not moving :  10  series
===========================
not moving :  11  series
===========================
not moving :  12  series
             ===========================
             moving  336  images of serie n° 13
             ===========================
             moving  157  images of serie n° 14
=========Step 1 Done=======================
Finished.
```