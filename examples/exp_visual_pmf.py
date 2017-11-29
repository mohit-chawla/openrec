import os
import sys
sys.path.append(os.getcwd())

from openrec import ModelTrainer
from openrec.utils import Dataset
from openrec.recommenders import VisualPMF
from openrec.utils.evaluators import AUC, Recall
from openrec.utils.samplers import PointwiseSampler
from config import sess_config
import dataloader

raw_data = dataloader.load_amazon_book()
batch_size = 1000
test_batch_size = 100
item_serving_size = 1000
display_itr = 10000

train_dataset = Dataset(raw_data['train_data'], raw_data['max_user'], raw_data['max_item'], name='Train')
val_dataset = Dataset(raw_data['val_data'], raw_data['max_user'], raw_data['max_item'], name='Val')
test_dataset = Dataset(raw_data['test_data'], raw_data['max_user'], raw_data['max_item'], name='Test')

model = VisualPMF(batch_size=batch_size, max_user=raw_data['max_user'], max_item=raw_data['max_item'], 
                dim_embed=50, item_f_source=raw_data['item_features'], dims=[1028, 128, 50], sess_config=sess_config, opt='Adam')
sampler = PointwiseSampler(batch_size=batch_size, dataset=train_dataset, pos_ratio=0.2, num_process=1)
model_trainer = ModelTrainer(batch_size=batch_size, test_batch_size=test_batch_size, item_serving_size=item_serving_size,
    train_dataset=train_dataset, model=model, sampler=sampler)

auc_evaluator = AUC()
recall_evaluator = Recall(recall_at=[10, 20, 30, 40, 50, 60, 70, 80, 90, 100])

model_trainer.train(num_itr=int(1e6), display_itr=display_itr, eval_datasets=[val_dataset, test_dataset],
                    evaluators=[auc_evaluator, recall_evaluator], num_negatives=1000)