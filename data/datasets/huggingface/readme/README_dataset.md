---
{{ card_data }}
---
# PUGG: KBQA, MRC, IR Dataset for Polish

## Description

This repository contains the PUGG dataset designed for three NLP tasks in the Polish language:

- KBQA (Knowledge Base Question Answering)
- MRC (Machine Reading Comprehension)
- IR (Information Retrieval)

## Paper

For more detailed information, please refer to our research paper titled:

**"Developing PUGG for Polish: A Modern Approach to KBQA, MRC, and IR Dataset Construction"** 

Authored by:
* Albert Sawczyn
* Katsiaryna Viarenich
* Konrad Wojtasik
* Aleksandra Domogała
* Marcin Oleksy
* Maciej Piasecki
* Tomasz Kajdanowicz
  
**The paper was accepted for ACL 2024 (findings).**

## Repositories

The dataset is available in the following repositories:

* [General](https://huggingface.co/datasets/clarin-pl/PUGG_KBQA) {{general_pointer}} - contains all tasks (KBQA, MRC, IR*)

For more straightforward usage, the tasks are also available in separate repositories:

* [KBQA](https://huggingface.co/datasets/clarin-pl/PUGG_KBQA) {{kbqa_pointer}}
* [MRC](https://huggingface.co/datasets/clarin-pl/PUGG_MRC) {{mrc_pointer}}
* [IR](https://huggingface.co/datasets/clarin-pl/PUGG_IR) {{ir_pointer}}

The knowledge graph for KBQA task is available in the following repository:

* [Knowledge Graph](https://huggingface.co/datasets/clarin-pl/PUGG_KG) {{kg_pointer | default("", true)}}

Note: If you want to utilize the IR task in the BEIR format (`qrels` in `.tsv` format), please 
download the [IR](https://huggingface.co/datasets/clarin-pl/PUGG_IR) repository.

## Links

* Code:
  * [Github](https://github.com/CLARIN-PL/PUGG)
* Paper:
  * ACL - TBA
  * [Arxiv](https://arxiv.org/abs/2408.02337)

## Citation

```bibtex
@misc{sawczyn2024developingpuggpolishmodern,
      title={Developing PUGG for Polish: A Modern Approach to KBQA, MRC, and IR Dataset Construction}, 
      author={Albert Sawczyn and Katsiaryna Viarenich and Konrad Wojtasik and Aleksandra Domogała and Marcin Oleksy and Maciej Piasecki and Tomasz Kajdanowicz},
      year={2024},
      eprint={2408.02337},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2408.02337}, 
}
```

## Contact

albert.sawczyn@pwr.edu.pl

## Usage 

{{usage}}
