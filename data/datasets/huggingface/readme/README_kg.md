---
{{ card_data }}
---
# PUGG: KBQA, MRC, IR Dataset for Polish

## Description

This repository contains the **knowledge graph** dedicated for 
the KBQA (Knowledge Base Question Answering) task within the PUGG dataset. This repository does not 
contain directly any task, but it provides the knowledge graph that can be used to solve the KBQA 
task from the PUGG dataset.


### Graphs

We provide sampled versions of the knowledge graph based on Wikidata:

- **Wikidata1H**: A subgraph created by traversing 1 relation from each answer and topic entity.
- **Wikidata2H**: A subgraph created by traversing 2 relations from each answer and topic entity.

### How We Created the Graphs

1. We used the Wikidata dump from 2023-10-16. The dump is available on S3 via the DVC tool (see [code repository](https://github.com/CLARIN-PL/PUGG)).
2. We collected all answer and topic entities from the PUGG dataset.
3. We traversed the graph from each answer and topic entity for *n* hops.
4. We filtered out entities that do not have labels in Polish.
5. We saved the subgraphs in various structures:
    * triples
    * labels_pl
    * labels_en
    * aliases (Polish) 
    * descriptions (Polish)
    * attributes
    * times

See [Usage](#usage) for more information on how to load the graphs.

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
  
The paper was accepted for ACL 2024 (findings).

## Repositories

The PUGG dataset is available in the following repositories:

* [General](https://huggingface.co/datasets/clarin-pl/PUGG_KBQA) {{general_pointer}} - contains all tasks (KBQA, MRC, IR)

For more straightforward usage, the tasks are also available in separate repositories:

* [KBQA](https://huggingface.co/datasets/clarin-pl/PUGG_KBQA) {{kbqa_pointer| default("", true)}}
* [MRC](https://huggingface.co/datasets/clarin-pl/PUGG_MRC) {{mrc_pointer | default("", true)}}
* [IR](https://huggingface.co/datasets/clarin-pl/PUGG_IR) {{ir_pointer | default("", true)}}

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
