import argparse
from utility import step1, step2
import os
import shutil

def main():
    parser = argparse.ArgumentParser(description="Script to convert DICOM images to NIfTI.")

    # Add arguments for paths
    parser.add_argument("--dicom_folder", type=str, required=True,
                        help="Folder containing DICOM images.")
    parser.add_argument("--nifti_patient_folder_out", type=str, required=True,
                        help="Output folder for NIfTI images.")
    parser.add_argument("--dcm2niix", type=str, required=True,
                        help="Path to the dcm2niix executable.")

    # Add arguments to choose steps
    parser.add_argument("--step1", action="store_true",
                        help="Run only step 1.")
    parser.add_argument("--step2", action="store_true",
                        help="Run only step 2.")
    parser.add_argument("--both", action="store_true",
                        help="Run both steps.")

    args = parser.parse_args()

    # Check which steps to run
    if args.both:
        args.step1 = True
        args.step2 = True

    if not (args.step1 or args.step2):
        print("Error: You must specify at least one step (--step1, --step2, or --both).")
        return

    # Create temporary folder path
    tmp_folder = os.path.join(args.nifti_patient_folder_out, 'tmp')

    # Run the selected steps
    if args.step1:
        print("=========Step 1 Starting =======================")
        step1(args.dicom_folder, tmp_folder)
        print("=========Step 1 Done=======================")

    if args.step2:
        print("=========Step 2 Starting=======================")
        step2(tmp_folder, args.nifti_patient_folder_out, args.dcm2niix)
        print("=========Step 2 Done=======================")

        # Clean up temporary folder
        if os.path.exists(tmp_folder):
           shutil.rmtree(tmp_folder)

    print("Finished.")

if __name__ == "__main__":
    
    main()

