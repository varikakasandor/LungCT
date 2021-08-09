config = {
    'datapath':'/mnt/idms/PROJECTS/Lung/LIDC-IDRI',
    'preprocess_result_path':'/mnt/idms/PROJECTS/Lung/LungCT/DSB2017/prep_result/',
    'outputfile':'/mnt/idms/PROJECTS/Lung/LungCT/DSB2017/prediction.csv',
    'detector_model':'net_detector',
    'detector_param':'/mnt/idms/PROJECTS/Lung/LungCT/DSB2017/model/detector.ckpt',
    'classifier_model':'net_classifier',
    'classifier_param':'/mnt/idms/PROJECTS/Lung/LungCT/DSB2017/model/classifier.ckpt',
    'n_gpu':10, #Too big would run out of CUDA memory
    'n_worker_preprocessing':60,
    'use_exsiting_preprocessing':True,
    'skip_preprocessing': False, #If the _clean and _label files are already present, then can be set to True
    'skip_detect': True
}
