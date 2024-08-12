python3 hf_qa/qa_eval_extractive.py \
--model_name_or_path allegro/herbert-base-cased \
--use_auth_token False \
--do_predict True \
--do_train True \
--output_dir data/baselines/mrc/models/herbert-base-cased-pugg-mrc \
--overwrite_output_dir True \
--test_file data/datasets/final/mrc/test.json \
--train_file data/datasets/final/mrc/train.json
