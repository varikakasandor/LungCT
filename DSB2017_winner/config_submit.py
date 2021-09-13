config = {
    'datapath':'/mnt/idms/PROJECTS/Lung/LIDC-IDRI-Samples',
    'preprocess_result_path':'/mnt/idms/PROJECTS/Lung/LungCT/DSB2017_winner/prep_result/',
    'bbox_result_path':'/mnt/idms/PROJECTS/Lung/LungCT/DSB2017_winner/bbox_result/',
    'outputfile':'/mnt/idms/home/andor/prediction-samples.csv',
    'detector_model':'net_detector',
    'detector_param':'/mnt/idms/PROJECTS/Lung/LungCT/DSB2017_winner/model/detector.ckpt',
    'classifier_model':'net_classifier',
    'classifier_param':'/mnt/idms/PROJECTS/Lung/LungCT/DSB2017_winner/model/classifier.ckpt',
    'n_gpu':10, #Too big would run out of CUDA memory
    'n_worker_preprocessing':40,
    'use_exsiting_preprocessing':True,#False,
    'skip_preprocessing': False, #False, #If the _clean and _label files are already present, then can be set to True. Otherwise MUST be False.
    'use_exsiting_detection':True,
    'skip_detect': False, #If the _pbb and _lbb files are already present, then can be set to True. Otherwise MUST be False.
}
