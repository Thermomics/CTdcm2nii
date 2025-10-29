import glob
import os
import pydicom
import shutil
import subprocess
import numpy as np
import datetime
from dicom_csv import join_tree
import warnings
from pathlib import Path

def contains_word_insensitive(string, words):
    
    """
    Function to check if any word from a list is contained in a string, case-insensitive.
    :param string: The string to search within.
    :param words: The list of words to search for.
    :return: Boolean indicating whether any word from the list was found in the string.
    """
    string_lower = string.lower()
    words_lower = [word.lower() for word in words]
    for word in words_lower:
        if word in string_lower:
            return True
    return False


def correct_separator(s):

    # Vérifier si "__" existe quelque part dans la chaîne
    if "__" not in s:
        print(" before separator correction: ",s)
        # Vérifier si un "_" est présent en position 4
        if len(s) > 3 and s[3] == '_':
            # Ajouter un "_" en position 5
            s = s[:4] + '_' + s[4:]
            
        else:
            # Si aucun "_" n'est en position 4, ajouter "__" à partir de la position 4
            s = s[:3] + '__' + s[3:]
        print(" after separator correction: ",s)    

    return s


def simplified_nifti_or_json_filename(str_in, theme,  double_separator):
    # remplace les parenthèses par des tirets
    str_in = str_in.replace("(", "").replace(")", "")
    # remplace les crochets par des tirets
    str_in = str_in.replace("[", "").replace("]", "")

    # remplace les espaces par des tirets
    str_in = str_in.replace(" ", "-")

    # supprime les doublons    
    str_in = str_in.replace("--", "-")

    str_extract=str.split(str_in, "/")
    #on extrait le noms de fichier
    description=str_extract[-1]
    
    # on supprime la nouvelle nomenclature de siemens
    str_in = str_in.replace("___", "__")
    str_in = str_in.replace("__", "_")

    description_lower=description.lower()   
    description_split=str.split(description, "_")

    series_number=description_split[0]
    sequence_name=description_split[1]
    description= "-".join(description_split[2:])
    series_number_filled=series_number.zfill(3)
    #if (theme=="Clinical"):
    new_name=series_number_filled+"__"+sequence_name+"_"+description.lower()
    #else:
    #    new_name=series_number_filled+"_"+sequence_name+"_"+description.lower() 

    new_name = new_name.replace("____", "___")
    new_name = new_name.replace("___", "__")
    
    # ici on va rajouter un check sur les séparateurs
    if double_separator==True:        
        new_name=correct_separator(new_name)        

    return new_name

def rename_nifti_in_lower(old_file_name, suffix):
    # Trouver la dernière occurrence de "/"
    last_slash_index = old_file_name.rfind('/')
    # Extraire la partie après le dernier "/"
    last_part = old_file_name[last_slash_index + 1:]    
    print(last_part) 
    # Trouver la dernière occurrence de "_"
    last_underscore_index = last_part.rfind('_')
    # Extraire la partie après le dernier "/"
    last_description_part = last_part[0:last_underscore_index]    
    print(last_description_part, last_description_part.islower())  
    if (last_description_part.islower()==False):
        print("condition remplie on va chnager le nom")
        new_file_name=old_file_name[0:last_slash_index]+"/"+last_description_part.lower()+suffix
        print(old_file_name)
        print(new_file_name)
        if (os.path.exists(old_file_name)==True and os.path.exists(new_file_name)==False):   
            print("condition remplie, on change le nom des dossiers")
            os.rename(old_file_name, new_file_name)

def simplify_nifti_or_json_filename(liste_of_files,nifti_fullpath_out, theme, double_separator):
   
    for old_file in liste_of_files:
        
        # condition pour ne pas écraser ce qui a été fait   
        #  on va faire une nouvelle condition pour indiquer  
        if old_file.endswith("_P.nii.gz"):
            rename_nifti_in_lower(old_file, "_P.nii.gz")
        elif old_file.endswith("_M.nii.gz"):
            rename_nifti_in_lower(old_file, "_M.nii.gz")
        elif old_file.endswith("_P.json"):
            rename_nifti_in_lower(old_file, "_P.json")
        elif old_file.endswith("_M.json"):
            rename_nifti_in_lower(old_file, "_M.json")
        else:
            #get new filename
            new_name=simplified_nifti_or_json_filename(old_file, theme,  False)
            old_pathname=old_file
            new_pathname=nifti_fullpath_out+new_name  
            # si le nom est different
            if new_pathname != old_pathname:
                #si le nouveau nom n existe pas
                if not os.path.exists(new_pathname):
                    print("simplify old", old_pathname)
                    print("simplify new", new_pathname)
                    os.rename(old_pathname, new_pathname)
 

def copy_dicom_files_from_local_to_sh(liste_dicom_file, series_description_simplified_dicom_fullpath_out):
    """
    Cette fonction copie une liste de fichiers DICOM vers un répertoire de destination.

    Paramètres:
    - liste_dicom_file: Une liste de chemins de fichiers à copier.
    - series_description_simplified_dicom_fullpath_out: Le chemin de destination complet où les fichiers doivent être copiés.

    Retourne:
    - Affiche le nombre de fichiers copiés et un message de fin de copie.
    """
    compteur_copy = 0

    for file in liste_dicom_file:
        # Séparer le chemin du fichier pour obtenir le nom du fichier
        files_split = str.split(file, "/")
        filename_out = files_split[-1]
        filename_fullpath_out = series_description_simplified_dicom_fullpath_out + filename_out

        # Vérifier si le fichier existe déjà, sinon le copier
        if not os.path.exists(filename_fullpath_out):
            compteur_copy += 1
            shutil.copy(file, filename_fullpath_out)

    if (compteur_copy!=0):
        print("          -> DICOM nombre de fichiers copiés: ", compteur_copy)
        print("          -> DICOM fin de la copie")



def simplify_description(str_in):
    # remplace les parenthèses par des tirets
    str_in = str_in.replace("(", "-").replace(")", "-")
    # remplace les crochets par des tirets
    str_in = str_in.replace("[", "-").replace("]", "-")
    # remplace les espaces par des tirets
    str_in = str_in.replace(" ", "-")

    #remplace / par un -
    str_in = str_in.replace("/", "-")
    # supprime les doublons    
    str_in = str_in.replace("--", "-")

    # Supprimer le premier caractère s'il  commence  par un tiret
    if str_in.startswith("-"):
        str_in = str_in[1:]
        
    return str_in 


def get_exam_type_and_date(liste_dossier_examen):

    exam_dates={}
    liste_des_mots_a_chercher_pour_intervention = ["intervention", "imrt", "kontrolle", "del^"] 
    for dossier_examen in liste_dossier_examen:
        print("         dossier_examen: ",dossier_examen)
        liste_dossier_acquisition=glob.glob(dossier_examen+'/*')
        a=str.split(dossier_examen,"/")
        nom_du_dossier_examen=a[-2]
        # Go through dicom series for this exam for this patient (folder containing sorted dicoms) (ex: OO1)
        for dossier_acq in liste_dossier_acquisition:
            acquisition_name=get_acquisition_name(dossier_acq)
            print("             dossier_acquisition:",acquisition_name)
        
            liste_dicom_file=glob.glob(f"{dossier_acq}/*")
            if (len(liste_dicom_file)>0):
                get_first_dicom=liste_dicom_file[0]
                ds = pydicom.dcmread(get_first_dicom)
                # extraction des champs DICOM nécessaires
                modality = ds[0x0008, 0x0060].value
                study_date=ds[0x0008, 0x0020].value  
                Study_description=ds[0x0008, 0x1030].value
                exam_dates[nom_du_dossier_examen] = (study_date , modality, contains_word_insensitive(Study_description, liste_des_mots_a_chercher_pour_intervention))
                break
    return exam_dates



def convert_CT_dicom_to_nifti(dcm2niix, dicom_input_folder, nifti_ouptut_folder):

    os.makedirs(nifti_ouptut_folder, exist_ok=True)
    # Créer un dossier temporaire à côté du dossier de base
    tmp_reject = os.path.join(os.path.dirname(dicom_input_folder.rstrip(os.sep)), "tmp_reject")
    os.makedirs(tmp_reject, exist_ok=True)

    moved_files = []
    # Regrouper les DICOM par SeriesInstanceUID
    for root, _, files in os.walk(dicom_input_folder):
        for f in files:
            path = os.path.join(root, f)
            try:
                ds = pydicom.dcmread(path, stop_before_pixels=True)
                image_type = "\\".join(ds.get("ImageType", []))
                modality = getattr(ds, "Modality", "").upper()
                if any(x in image_type for x in ["LOCALIZER", "ROI"]) or modality == "SEG":
                    shutil.move(path, os.path.join(tmp_reject, f))
                    moved_files.append((os.path.join(tmp_reject, f), path))
            except Exception as e:
                print("Erreur lecture:", f, e)

    # Lancer dcm2niix  

    command_to_run=dcm2niix + " -f %s_%z_%d -o "+nifti_ouptut_folder+" --progress y -z y "+dicom_input_folder
    print(command_to_run)
    result = subprocess.run([command_to_run], shell=True, capture_output=True, text=True) 
                            
    # Suppression des fichiers avec "ROI" dans le nom
    for f in os.listdir(nifti_ouptut_folder):
        if "ROI" in f and f.endswith(".nii.gz"):
            os.remove(os.path.join(nifti_ouptut_folder, f))

    # Remettre les fichiers déplacés dans le dossier d'origine
    for src, dst in moved_files:
        shutil.move(src, dst)

    # Supprimer le dossier tmp s'il est vide
    if os.path.exists(tmp_reject) and not os.listdir(tmp_reject):
        os.rmdir(tmp_reject)


def rename_phase_files_wip_version(nifti_fullpath_out, series_number):
    """
    Renomme et déplace les fichiers NIfTI et JSON en ajoutant '-ph' avant l'extension si nécessaire.

    Paramètres:
    - nifti_fullpath_out: Chemin complet vers le répertoire contenant les fichiers NIfTI et JSON.
    - series_number: Numéro de série utilisé pour filtrer les fichiers.

    Retourne:
    - Aucun retour, mais affiche les anciens et nouveaux noms de fichiers et effectue les déplacements.
    """
    # Générer les listes des fichiers NIfTI et JSON correspondant au numéro de série
    list_nifti_phase_series = glob.glob(os.path.join(nifti_fullpath_out, f"{series_number}*.nii.gz"))
    list_json_phase_series = glob.glob(os.path.join(nifti_fullpath_out, f"{series_number}*.json"))

    # Filtrer les fichiers qui ne se terminent pas par "-ph.nii.gz" ou "-ph.json"
    generator_nifti_phase_series_i_care_about = filter(lambda x: not x.endswith("-ph.nii.gz") , list_nifti_phase_series)
    generator_json_phase_series_i_care_about = filter(lambda x: not x.endswith("-ph.json") , list_json_phase_series)

    generator_nifti_phase_series_i_care_about = filter(lambda x: not x.endswith("_ph.nii.gz") , generator_nifti_phase_series_i_care_about)
    generator_json_phase_series_i_care_about = filter(lambda x: not x.endswith("_ph.json") , generator_json_phase_series_i_care_about)

    # Convertir les générateurs en listes
    liste_nifti_phase_series_i_care_about = list(generator_nifti_phase_series_i_care_about)
    liste_json_phase_series_i_care_about = list(generator_json_phase_series_i_care_about)

    # Vérifier que les listes contiennent exactement un fichier
    if len(liste_nifti_phase_series_i_care_about) != 1 or len(liste_json_phase_series_i_care_about) != 1:
        print(len(liste_nifti_phase_series_i_care_about))
        print(len(liste_json_phase_series_i_care_about))
        warnings.warn("Warning: Le nombre de fichiers NITTI ou JSON ne correspond pas à 1, ancun nifti ne sera modifié")
    else:
        # Afficher les anciens noms
        print("old name", liste_nifti_phase_series_i_care_about[0])
        print("old json name", liste_json_phase_series_i_care_about[0])

        # Générer les nouveaux noms de fichiers
        new_nifti_name = str.replace(liste_nifti_phase_series_i_care_about[0], ".nii.gz", "-ph.nii.gz")
        new_json_name = str.replace(liste_json_phase_series_i_care_about[0], ".json", "-ph.json")

        # Afficher les nouveaux noms
        print("new name", new_nifti_name)
        print("new json name", new_json_name)

        # Déplacer et renommer les fichiers s'ils n'existent pas déjà
        if not os.path.exists(new_nifti_name):
            shutil.move(liste_nifti_phase_series_i_care_about[0], new_nifti_name)
        if not os.path.exists(new_json_name):
            shutil.move(liste_json_phase_series_i_care_about[0], new_json_name)


def find_image_folders(parent_folder_path):
    # Liste pour stocker les chemins des dossiers "IMAGE" trouvés
    image_folders = []

    # Parcourir récursivement le dossier parent et ses sous-dossiers
    for root, dirs, files in os.walk(parent_folder_path):
        for dir_name in dirs:
            if dir_name == 'IMAGES':
                # Construire le chemin complet du dossier "IMAGE"
                full_path = os.path.join(root, dir_name)
                image_folders.append(full_path)


    # Traitement des dossiers "IMAGE" trouvés
    for folder in image_folders:
        # Vérifier si le dossier est vide
        if not os.listdir(folder):
            # Supprimer le dossier s'il est vide
            os.rmdir(folder)
            print(f"Supprimé le dossier IMAGE vide : {folder}")
        else:
            print(f"Le dossier IMAGE n'est pas vide : {folder}")

    return image_folders


def find_dicom_exam_folders(patient_folder):
    """Returns a filtered list of exam folders excluding the 'Zip' folders."""
    exam_folders = glob.glob(patient_folder + '/*/')
    return filter(lambda x: not x.endswith("/Zip/") and "meas_" not in x, exam_folders)

def get_acquisition_name(folder_name):
    last_slash_index = folder_name.rfind('/')
    # Extraire la partie après le dernier "/"
    last_part = folder_name[last_slash_index + 1:]    
    return last_part 


def get_standardized_patient_id(ds, dossier_patient_str):

    """
    Function to retrieve and standardize patient IDs.
    Removes underscores and adjusts the ID according to specific conditions.
    :param ds: The dataset containing the patient's original ID.
    :param dossier_patient: The folder directory which might contain necessary patient information.
    :return: standardized_patient_id, the standardized patient ID.
    """
    patient_id=ds[0x0010, 0x0020].value
    standardized_patient_id = patient_id.replace("_", "")    

    if "MWA" not in patient_id:
        # on prend le nom du dossier où sont stockés les données 
        a=str.split(dossier_patient_str,"/")
        mwa_patient_folder_name=a[-1]
        standardized_patient_id=mwa_patient_folder_name
    else:
        pass
    return  standardized_patient_id


def extract_dicom_metadata(dcm_file_path):
    """Extracts and returns specific metadata from a DICOM file."""
    ds = pydicom.dcmread(dcm_file_path)
    metadata = {
        "Id": ds.get((0x0010, 0x0020), None),
        "BirthDate": ds.get((0x0010, 0x0030), None),
        "Sexe": ds.get((0x0010, 0x0040), None),
        "Age": ds.get((0x0010, 0x1010), None),
        "Size": ds.get((0x0010, 0x1020), 0),
        "Weight": ds.get((0x0010, 0x1030), 0),
        "Modalite": ds.get((0x0008, 0x0060), None),
        "StudyDescription": ds.get((0x0008, 0x1030), None)
    }
    # Handle optional fields
    metadata["Size"] = metadata["Size"].value if metadata["Size"] else 0
    metadata["Weight"] = metadata["Weight"].value if metadata["Weight"] else 0
    return ds, metadata



def update_magnitude_and_phase_image_nifti_name(nifti_fullpath_out):        
    
    suffix_to_catch="ph.nii.gz"
    suffixes_to_exclude = ["opp-ph.nii.gz", "in-ph.nii.gz", "opp_ph.nii.gz", "in_ph.nii.gz"]
    filtered_files = get_filtered_files(nifti_fullpath_out, suffix_to_catch, suffixes_to_exclude)
    #print(filtered_files)              

    if (len(filtered_files)>0 ):                                            
        rename_magnitude_and_phase(filtered_files,nifti_fullpath_out, ".nii.gz")

    suffix_to_catch="ph.json"
    suffixes_to_exclude = ["opp-ph.json", "in-ph.json", "opp_ph.json", "in_ph.json"]
    filtered_files = get_filtered_files(nifti_fullpath_out, suffix_to_catch, suffixes_to_exclude)
    #print(filtered_files)

    if (len(filtered_files)>0 ):                     
        rename_magnitude_and_phase(filtered_files,nifti_fullpath_out, ".json")



def rename_magnitude_and_phase(liste_of_files,nifti_fullpath_out, extension):
    """
    modifie les fichiers nifti magnitude et phase afin d'avoir la nomenclature suivante
    X_....._M.nii.gz
    X+1_....._P.nii.gz
    X étant le numéro de série

    :liste_of_files: liste des niftis à modifieir.
    :nifti_fullpath_out: dossier dans lesquel ils sont (redondant).
    :extension : cela peut-être .nii.gz ou .json
    """

    if extension == ".json":
        pass
    elif extension == ".nii.gz":
        pass
    else:
        raise("erreur dans l'extension")

    for old_phase_file in liste_of_files:

        if old_phase_file.endswith("_P.nii.gz"):
            pass        
        elif old_phase_file.endswith("_P.json"):
            pass
        else:    
            
            if ((old_phase_file.endswith("_ph"+extension))  or (old_phase_file.endswith("-ph"+extension)) ):
                
                if old_phase_file.endswith("-ph"+extension):   
                    #print("c'est une image de phase ", old_phase_file)
                    new_phase_file= old_phase_file.replace("-ph"+extension, "_P"+extension)
                elif  old_phase_file.endswith("_ph"+extension):

                    new_phase_file= old_phase_file.replace("_ph"+extension, "_P"+extension)  
                    
                a=str.split(old_phase_file,"/")
                b=a[-1]
                
                series_number=b[0:3]
                series_number_magnitude=str(int(series_number)-1).zfill(3)
                #print(b, series_number, series_number_magnitude)

                if not os.path.exists(new_phase_file):   
                        os.rename(old_phase_file,new_phase_file)   
                        print("changing to :", new_phase_file)

                #print(f"{nifti_fullpath_out}/{series_number_magnitude}*"+extension)
                list_magnitude_file=glob.glob(f"{nifti_fullpath_out}/{series_number_magnitude}*"+extension)

                # pour une raison que j'ignore , parfois l'image de magnitude n'est pas présente
                if (len(list_magnitude_file)>0):
                    old_magnitude_file=list_magnitude_file[0]
                    new_magnitude_file= old_magnitude_file.replace(extension, "_M"+extension)

                    if not os.path.exists(new_magnitude_file): 
                        os.rename(old_magnitude_file,new_magnitude_file)
                        print("changing to :", new_magnitude_file)
                

def get_filtered_files(nifti_fullpath_out, suffix_to_catch, suffixes_to_exclude):
    """
    Récupère une liste filtrée de fichiers qui se terminent par "-ph.nii.gz",
    mais exclut ceux se terminant par l'un des suffixes spécifiés.

    Paramètres:
    - nifti_fullpath_out: Le chemin vers le répertoire contenant les fichiers.
    - suffixes_to_exclude: Une liste de suffixes à exclure.

    Retourne:
    - Une liste des fichiers filtrés.
    """
    # Générer la liste des fichiers terminant par "-ph.nii.gz"
    liste_nifti_file_out = glob.glob(f"{nifti_fullpath_out}/*"+suffix_to_catch)
    
    # Filtrer la liste pour exclure les fichiers qui se terminent par l'un des suffixes spécifiés
    liste_nifti_file_out_filtre = [
        f for f in liste_nifti_file_out
        if not any(f.endswith(suffix) for suffix in suffixes_to_exclude)
    ]

    return liste_nifti_file_out_filtre


def get_global_folder_name(path_in):
    path = Path(path_in)

    # Cherche le dossier IMAGES à une ou deux profondeurs
    images_paths = list(path.glob('IMAGES')) + list(path.glob('*/IMAGES'))

    if not images_paths:
        raise FileNotFoundError("Aucun dossier 'IMAGES' trouvé dans ou sous ce chemin")

    # Prend le premier trouvé
    img_path = images_paths[0]

    # Si IMAGES est directement dans path_in
    if img_path.parent == path:
        return path.name
    else:
        # Sinon, inclure le dossier intermédiaire
        return f"{path.name}/{img_path.parent.name}"
    


def step1(dossier_images, folder_move):
    print("     ",dossier_images)
    liste_of_IMA=glob.glob(dossier_images+"/*")
    print("         contains ",len(liste_of_IMA), " images files")

    if not os.path.exists(folder_move):
        os.makedirs(folder_move)  


    # Examine one IMAGES folder "dossier_images" if not empty
    if (len(liste_of_IMA)!=0):
        meta = join_tree(dossier_images, verbose=2) #Returns a dataframe containing metadata for each file in all the subfolders of ``top`` (top = dossier_images).

        number_of_series=np.max(meta.SeriesNumber) #get total number of series in "dossier_images"
        print("         that are from", number_of_series, "different series", )

        # Go through series and get associated images files 
        for series_number in range (1,number_of_series+1):
            meta.loc[meta.SeriesNumber==series_number]
            meta_of_interest=meta.loc[meta.SeriesNumber==series_number]            

            #check that the serie's got images 
            if (len(meta_of_interest)!=0):
                # creation du nouveau dossier de type serie number en 3 chiffres
                new_directory=os.path.join(folder_move,str(series_number).zfill(3))
                if not os.path.exists(new_directory):
                    os.makedirs(new_directory)    

                #get list of images filename corresponding to the serie
                list_of_files=meta_of_interest['FileName'].values
                print('             ===========================')
                print('             moving ',len(list_of_files) ,' images of serie n°', series_number)
                #go through images of the serie
                for num in range(0, len(list_of_files)):
                    file=list_of_files[num]
                    # filename_full=str(dossier_images)+'/'+file
                    filename_full = os.path.join(dossier_images, file)

                    if os.path.exists(filename_full):
                        #print(filename_full)
                        source = filename_full
                        # destination = new_directory +'/' +file
                        destination = os.path.join(new_directory, file)
                        # print(source,destination)                
                        shutil.copy2(source, destination)
                    # else:
                    #    print("not exist anymore ",file)     
            else:
                print('===========================')
                print('not moving : ',series_number, ' series')  






def step2(dossier_examen,out_folder, dcm2niix):
    mw_patient_folder_out = out_folder
    liste_dossier_examen = [dossier_examen]
    
    exams_type_and_date = get_exam_type_and_date(liste_dossier_examen)
    print(exams_type_and_date)
    # Go through exams of this patient ) 
    print("         dossier_examen: ",dossier_examen)
    liste_dossier_acquisition=glob.glob(dossier_examen+'/*')
    a=str.split(dossier_examen,"/")
    nom_du_dossier_examen=a[-2]

    # Go through dicom series for this exam for this patient (folder containing sorted dicoms) (ex: OO1)
    for dossier_acq in liste_dossier_acquisition:
        acquisition_name=get_acquisition_name(dossier_acq)
        print("             dossier_acquisition:",acquisition_name)
    
        liste_dicom_file=glob.glob(f"{dossier_acq}/*")
        if (len(liste_dicom_file)>0):
            get_first_dicom=liste_dicom_file[0]
            ds, metadata = extract_dicom_metadata(get_first_dicom)
            # extraction des champs DICOM nécessaires
            study_date=ds[0x0008, 0x0020].value
            series_number=str(ds[0x0020, 0x0011].value)
            series_number_filled=series_number.zfill(3)
            series_description=str(ds[0x0008, 0x103e].value)                      
                                        
            if "phoenix" in series_description.lower() or "report" in series_description.lower() or "gsps" in series_description.lower():
                pass
                #print("atttttttttttttttttetion PHOENIX REPORT skipping dicom")
            else:
                series_description_simplified=str(simplify_description(series_description))
                CorrectPatientId=get_standardized_patient_id(ds, dossier_examen)
                Modalite=ds[0x0008,0x0060].value
                StudyDate=ds[0x0008,0x0020].value
                Study_description=ds[0x0008, 0x1030].value
                try:
                    Intercept=ds[0x0028,0x1052].value
                except:
                    Intercept=None
                try:
                    Slope=ds[0x0028,0x1053].value
                except:
                    Slope=None

                
                phase_image_detected=False
                if (Intercept==-4096 and Slope==2):
                    print("Intercept and Slope:", Intercept, Slope ) 
                    phase_image_detected=True
                
                series_description_simplified_name=series_number_filled+"__"+series_description_simplified.lower()
                examen_name_out=StudyDate[0:4]+"-"+StudyDate[4:6]+"-"+StudyDate[6:8]+"_"+"CT-pre-ablation"
                    
                print("             new name: ",CorrectPatientId+'/'+examen_name_out+ "/"+ series_description_simplified_name)
                patient_name_out=CorrectPatientId
                patient_fullpath_out=mw_patient_folder_out+patient_name_out
                print("             patient path: ",patient_fullpath_out)
                
                
                if not os.path.exists(patient_fullpath_out):
                    os.makedirs(patient_fullpath_out)
                
                examen_fullpath_out=mw_patient_folder_out+patient_name_out+"/"+examen_name_out
                print("             exam path: ",examen_fullpath_out)
                if not os.path.exists(examen_fullpath_out):
                    os.makedirs(examen_fullpath_out)

                # création du dossier DICOM
                dicom_fullpath_out=examen_fullpath_out+"/RAW-DICOM/"
                if not os.path.exists(dicom_fullpath_out):
                    os.makedirs(dicom_fullpath_out)
                
                # création du dossier NIFTI
                nifti_fullpath_out=examen_fullpath_out+"/RAW-NIFTI/"
                if not os.path.exists(nifti_fullpath_out):
                    os.makedirs(nifti_fullpath_out)  

                # création du dossier NRRD
                nrrd_fullpath_out=examen_fullpath_out+"/RAW-NRRD/"
                if not os.path.exists(nrrd_fullpath_out):
                    os.makedirs(nrrd_fullpath_out)   

                # création des dossiers séries dans le répertoire DICOM
                series_description_simplified_dicom_fullpath_out=dicom_fullpath_out+series_description_simplified_name+'/'
                print("             series_description_simplified_dicom_fullpath_out: ",series_description_simplified_dicom_fullpath_out)
                if not os.path.exists(series_description_simplified_dicom_fullpath_out):
                    os.makedirs(series_description_simplified_dicom_fullpath_out)              

                # copie des fichiers DICOMs
                copy_dicom_files_from_local_to_sh(liste_dicom_file, series_description_simplified_dicom_fullpath_out)

                #il faut d'abord vérifier si des fichiers commençant par le numéro de série existe
                list_nifti_series=glob.glob(nifti_fullpath_out+"/"+series_number+"*")
                #il faut d'abord vérifier si des fichiers commençant par le numéro de série existe
                list_nrrd_series=glob.glob(nrrd_fullpath_out+"/"+series_number+"*")

                # Lister tous les fichiers dans le répertoire
                fichiers_nifti = os.listdir(nifti_fullpath_out)


                # Vérifier si aucun fichier ne commence par '010_' ou '10_'
                fichier_nii_010_existe = any(fichier.startswith(series_number_filled+'_') for fichier in fichiers_nifti)
                fichier_nii_10_existe = any(fichier.startswith(series_number+'_') for fichier in fichiers_nifti)

                
                # Condition pour effectuer une opération si aucun des fichiers n'existe
                if not fichier_nii_010_existe and not fichier_nii_10_existe:    
                    if (Modalite=="MR"):
                        command_to_run=dcm2niix+" -f %s_%z_%d -o "+nifti_fullpath_out+" --progress y -z y "+series_description_simplified_dicom_fullpath_out
                        result = subprocess.run([command_to_run], shell=True, capture_output=True, text=True) 
                        print("         Aucun fichier commençant par ",series_number," ou ",series_number_filled," n'existe. Effectuer l'opération.")            
                        print("         -> NIFTI - fin conversion ")

                        # si on sait que c'est une image de phase et que -ph n'est pas présent on l'ajoute
                        # c'est un fix pour le wip epi single shot de siemens
                        if (phase_image_detected==True):
                            rename_phase_files_wip_version(nifti_fullpath_out, series_number)    

                    elif (Modalite=="CT"):
                        print("CT modality")
                        print("         Aucun fichier commençant par ",series_number," ou ",series_number_filled," n'existe. Effectuer l'opération.")            
                        convert_CT_dicom_to_nifti(dcm2niix,series_description_simplified_dicom_fullpath_out, nifti_fullpath_out)
                        print("         -> NIFTI - fin conversion ")

                    else:
                        pass    
                else:
                    print("         Un fichier commençant par ",series_number," ou ",series_number_filled," existe. Aucune opération effectuée, conversion déjà effectuée")
                    pass

                if os.path.exists(series_description_simplified_dicom_fullpath_out) :
                    shutil.rmtree(series_description_simplified_dicom_fullpath_out)

        
                    
        # on regarde tous les niftis     
        nifti_fullpath_out=examen_fullpath_out+"/RAW-NIFTI/"
        
        liste_nifti_file_out=glob.glob(f"{nifti_fullpath_out}/*.nii.gz")
        liste_json_file_out=glob.glob(f"{nifti_fullpath_out}/*.json")
        
        if (len(liste_nifti_file_out)>0 and len(liste_json_file_out)):
            simplify_nifti_or_json_filename(liste_nifti_file_out,nifti_fullpath_out, "Clinical" , double_separator=True)
            simplify_nifti_or_json_filename(liste_json_file_out,nifti_fullpath_out, "Clinical" , double_separator=True)
            pass
        print("         -> NIFTI - renommage partie 1 ") 

        update_magnitude_and_phase_image_nifti_name(nifti_fullpath_out)
        print("         -> NIFTI - renommage partie 2 ")     

    shutil.make_archive(patient_fullpath_out, 'zip', patient_fullpath_out)
        


                    

