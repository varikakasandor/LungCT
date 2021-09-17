config = {
    'datapath':'/mnt/idms/PROJECTS/Lung/LIDC-IDRI-SuperResoluted',
    'preprocess_result_path':'/mnt/idms/home/andor/prep_result/',
    'bbox_result_path':'/mnt/idms/home/andor/bbox_result/',
    'outputfile':'/mnt/idms/home/andor/prediction-super.csv',
    'detector_model':'net_detector',
    'detector_param':'/mnt/idms/PROJECTS/Lung/LungCT/DSB2017_winner/model/detector.ckpt',
    'classifier_model':'net_classifier',
    'classifier_param':'/mnt/idms/PROJECTS/Lung/LungCT/DSB2017_winner/model/classifier.ckpt',
    'n_gpu':10, #Too big would run out of CUDA memory
    'n_worker_preprocessing':10,
    'use_exsiting_preprocessing':True,#False,
    'skip_preprocessing': False, #True, #If the _clean and _label files are already present, then can be set to True. Otherwise MUST be False.
    'use_exsiting_detection':True,
    'skip_detect': False, #If the _pbb and _lbb files are already present, then can be set to True. Otherwise MUST be False.
}
