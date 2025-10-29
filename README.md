# Setup Virtual Environment for DICOM to NIfTI Conversion of CT exams

This guide explains how to set up a Python virtual environment with the required dependencies for the DICOM to NIfTI conversion script.

---

## Prerequisites

- Python 3.8 or higher installed on your system.
- `pip` (Python package manager) installed.
- dcm2niix (`sudo apt-get install  dcm2niix` if necessary)
- then find the location of dcm2niix using `which dcm2niix`
---

## Step 1: Create a Virtual Environment

Open a terminal and navigate to your project directory. Run the following command to create a virtual environment:

```bash
python -m venv PyEnvCTdcm2nii

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


