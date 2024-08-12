# Machine Reading Comprehension dataset

Code for training and evaluation is taken from `https://github.com/huggingface/transformers/tree/main/examples/pytorch/question-answering` and addopted to our MRC dataset.

The extractive baseline models:
- `allegro/herbert-base-cased`
- `allegro/herbert-large-cased`

You can run the script `eval_extractive.sh`, run dvc stage `baseline_mrc_extractive_evaluate` or the following command:

```
PYTHONPATH=. python3 baselines/mrc/hf_qa/qa_eval_extractive.py
            --model_name_or_path ${item.model_path}
            --use_auth_token False
            --do_predict True
            --do_train True
            --output_dir data/baselines/mrc/models/${item.model_name}-pugg-mrc
            --overwrite_output_dir True
            --test_file data/datasets/final/mrc/test.json
            --train_file data/datasets/final/mrc/train.json
```


The generative baseline models:
- `allegro/plt5-base`
- `allegro/plt5-large`

You can run the script `eval_generative.sh`, run dvc stage `baseline_mrc_generative_evaluate` or the following command:

```
PYTHONPATH=. python3 baselines/mrc/hf_qa/qa_eval_generative.py 
            --model_name_or_path ${item.model_path}
            --use_auth_token False
            --do_predict True
            --do_train True
            --output_dir data/baselines/mrc/models/${item.model_name}-pugg-mrc
            --overwrite_output_dir True
            --test_file data/datasets/final/mrc/test.json
            --train_file data/datasets/final/mrc/train.json
            --answer_column answer
            --question_column question
            --predict_with_generate True
```


The evalatuon results are saved in `predict_results.json' file.
The results for the baselines:

`allegro/herbert-base-cased`
```
{
    "predict_samples": 1742,
    "test_exact_match": 42.90637564618036,
    "test_f1": 66.41167977025412,
    "test_runtime": 9.8249,
    "test_samples_per_second": 177.304,
    "test_steps_per_second": 11.094
}
```
`allegro/herbert-large-cased`
```
{
    "predict_samples": 1742,
    "test_exact_match": 46.81217690982194,
    "test_f1": 70.4190309623006,
    "test_runtime": 44.6977,
    "test_samples_per_second": 38.973,
    "test_steps_per_second": 2.439
}
```


`allegro/plt5-base`
```
{
    "predict_samples": 1743,
    "test_exact_match": 22.860425043078692,
    "test_f1": 57.6297689925804,
    "test_runtime": 59.2366,
    "test_samples_per_second": 29.424,
    "test_steps_per_second": 1.84
}
```


`allegro/plt5-large`
```
{
    "predict_samples": 1743,
    "test_exact_match": 38.880482481332566,
    "test_f1": 71.51546501218891,
    "test_loss": 0.3219578266143799,
    "test_runtime": 271.8377,
    "test_samples_per_second": 6.412,
    "test_steps_per_second": 1.604
}
```


