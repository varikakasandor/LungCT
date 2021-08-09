config = {
    'datapath':'/mnt/idms/PROJECTS/Lung/LIDC-IDRI',
    'preprocess_result_path':'/mnt/idms/home/andor/DSB2017/prep_result/',
    'outputfile':'/mnt/idms/home/andor/DSB2017/prediction.csv',
    'detector_model':'net_detector',
    'detector_param':'/mnt/idms/home/andor/DSB2017/model/detector.ckpt',
    'classifier_model':'net_classifier',
    'classifier_param':'/mnt/idms/home/andor/DSB2017/model/classifier.ckpt',
    'n_gpu':10,
    'n_worker_preprocessing':1,
    'use_exsiting_preprocessing':True,
    'skip_preprocessing': True, #False,
    'skip_detect': True
}
