
#%%
from utility import step1, step2
import os
import shutil
#%%
# lancer l'env python : source ../venv/bin/activate

#necessary to install it and set the path to it
dcm2niix = "/workspace_QMRI/USERS_CODE/vozenne/dcm2niix"


#folder where are dicom images of a specific patient and exam (for example, the CT dicom images of patient X)
dicom_folder = "/workspace_QMRI/PROJECTS_DATA/2025_RECH_MD/test_olaf_dicm_to_nifti/MWA_20251002a_CT/IMAGES/" 

#folder where the futur nifti exams will be stocked as /nifti_patient_folder_out/PatientName/Date-exam/RAW-NIFTI
nifti_patient_folder_out="/workspace_QMRI/PROJECTS_DATA/2025_RECH_MD/test_olaf_dicm_to_nifti/out_to_export/" 


# step1(dicom_folder, os.path.join(nifti_patient_folder_out, 'tmp'))
step2(os.path.join(nifti_patient_folder_out, 'tmp'),nifti_patient_folder_out, dcm2niix)


if os.path.exists(os.path.join(nifti_patient_folder_out, 'tmp')) :
    shutil.rmtree(os.path.join(nifti_patient_folder_out, 'tmp'))


print("Finished")