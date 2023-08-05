# Introduction
The retrieval unit in the [NTCIR-10 Math][paper:aizawaetal13-ntcir10] task
[dataset][www:ntcir-10-math-data] is an arXiv document and the judgement unit
in the [relevance judgements][www:ntcir-task-data] is an XML element.
On the other hand, the retrieval and judgement units in the [NTCIR-11
Math-2][paper:aizawaetal14-ntcir11], and [NTCIR-12
MathIR][paper:zanibbi16-ntcir12] task [dataset][www:ntcir-12-mathir-data], and
[relevance judgements][www:ntcir-task-data] is an arXiv document paragraph.
This makes it difficult to use both datasets together in a single evaluation.

NTCIR Math converter is a Python 3 command-line utility that converts the
NTCIR-10 Math XHTML5 dataset and relevance judgements to the NTCIR-11 Math-2,
and NTCIR-12 MathIR XHTML5 format by splitting the dataset into paragraphs and
redirecting the relevance judgements from elements to their ancestral
paragraphs. As a result, the NTCIR-10 Math dataset, and relevance judgements
can be easily used together with the NTCIR-11 Math-2, and NTCIR-12 MathIR
dataset, and relevance judgements in a single workflow.

[paper:aizawaetal13-ntcir10]: https://ntcir-math.nii.ac.jp/wp-content/blogs.dir/23/files/2013/10/01-NTCIR10-OV-MATH-AizawaA.pdf (NTCIR-10 Math Pilot Task Overview)
[paper:aizawaetal14-ntcir11]: https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.686.444&rep=rep1&type=pdf (NTCIR-11 Math-2 Task Overview)
[paper:zanibbi16-ntcir12]: https://research.nii.ac.jp/ntcir/workshop/OnlineProceedings12/pdf/ntcir/OVERVIEW/01-NTCIR12-OV-MathIR-ZanibbiR.pdf (NTCIR-12 MathIR Task Overview)

[www:ntcir-task-data]: https://www.nii.ac.jp/dsc/idr/en/ntcir/ntcir-taskdata.html (Downloading NTCIR Test Collections Task Data)
[www:ntcir-10-math-data]: https://ntcir-math.nii.ac.jp/data/ (NTCIR-12 MathIR » Data » NTCIR-10 Math Pilot Task)
[www:ntcir-12-mathir-data]: https://ntcir-math.nii.ac.jp/data/ (NTCIR-12 MathIR » Data » NTCIR-12 MathIR Task)

# Usage
Installing:

    $ pip install ntcir10-math-converter

Displaying the usage:

    $ ntcir10-math-converter --help
    usage: ntcir10-math-converter [-h] --dataset DATASET [DATASET ...]
                                  [--judgements JUDGEMENTS [JUDGEMENTS ...]]
                                  [--num-workers NUM_WORKERS]

    Convert NTCIR-10 Math XHTML5 dataset and relevance judgements to the NTCIR-11
    Math-2, and NTCIR-12 MathIR XHTML5 format.

    optional arguments:
      -h, --help            show this help message and exit
      --dataset DATASET [DATASET ...]
                            A path to a directory containing the NTCIR-10 Math
                            XHTML5 dataset, and a path to a non-existent directory
                            that will contain resulting dataset in the NTCIR-11
                            Math-2, and NTCIR-12 MathIR XHTML5 format. If only the
                            path to the NTCIR-10 Math dataset is specified, the
                            dataset will be read to find out the mapping between
                            element identifiers, and paragraph identifiers. This
                            is required for converting the relevance judgements.
      --judgements JUDGEMENTS [JUDGEMENTS ...]
                            Paths to the files containing NTCIR-10 Math relevance
                            judgements (odd arguments), followed by paths to the
                            files that will contain resulting relevance judgements
                            in the NTCIR-11 Math-2, and NTCIR-12 MathIR format
                            (even arguments).
      --num-workers NUM_WORKERS
                            The number of processes that will be used for
                            processing the NTCIR-10 Math dataset. Defaults to 1.

Converting both a dataset, and relevance judgements using 64 worker processes:

    $ ntcir10-math-converter --num-workers 64 \
    >     --dataset ntcir-10 ntcir-10-converted \
    >     --judgements \
    >         NTCIR_10_Math-qrels_ft.dat NTCIR_10_Math-qrels_ft-converted.dat \
    >         NTCIR_10_Math-qrels_fs.dat NTCIR_10_Math-qrels_fs-converted.dat
    Retrieving judged document names, and element identifiers from NTCIR_10_Math-qrels_ft.dat
    100%|███████████████████████████████████████████████████████| 1425/1425 [00:00<00:00, 9634.03it/s]
    Retrieving judged document names, and element identifiers from NTCIR_10_Math-qrels_fs.dat
    100%|███████████████████████████████████████████████████████| 2129/2129 [00:00<00:00, 9671.33it/s]
    Processing dataset ntcir-10
    Converting dataset ntcir-10 -> ntcir-10-converted/xhtml5
    Building a mapping between element identifiers, and paragraph identifiers
    100%|████████████████████████████████████████████████████| 100000/100000 [06:45<00:00, 246.50it/s]
    Converting relevance judgements NTCIR_10_Math-qrels_ft.dat -> NTCIR_10_Math-qrels_ft-converted.dat
    Skipping identifier f080935#idp57072, as it appears outside a paragraph
    Skipping identifier f039264#id60072, as it appears outside a paragraph
    Skipping identifier f059698#id58538, as it appears outside a paragraph
    ...
    Skipping identifier f023353#idp65840, as it appears outside a paragraph
    Skipping identifier f048268#id53551, as it appears outside a paragraph
    100%|█████████████████████████████████████████████████████| 1425/1425 [00:00<00:00, 252199.81it/s]
    1425 / 1394 input / output relevance judgements
    Converting relevance judgements NTCIR_10_Math-qrels_fs.dat -> NTCIR_10_Math-qrels_fs-converted.dat
    Skipping identifier f095981#id72919, as it appears outside a paragraph
    Skipping identifier f061190#id56357, as it appears outside a paragraph
    Skipping identifier f033738#id116089, as it appears outside a paragraph
    ...
    Skipping identifier f019052#id54515, as it appears outside a paragraph
    Skipping identifier f021845#id53581, as it appears outside a paragraph
    100%|█████████████████████████████████████████████████████| 2129/2129 [00:00<00:00, 291048.96it/s]
    2129 / 2076 input / output relevance judgements

Converting only a dataset using 64 worker processes:

    $ ntcir10-math-converter --num-workers 64 \
    >     --dataset ntcir-10 ntcir-10-converted
    Processing dataset ntcir-10
    Converting dataset ntcir-10 -> ntcir-10-converted/xhtml5
    100%|████████████████████████████████████████████████████| 100000/100000 [07:34<00:00, 220.10it/s]

Converting only relevance judgements using 64 worker processes:

    $ ntcir10-math-converter --num-workers 64 \
    >     --dataset ntcir-10 \
    >     --judgements \
    >         NTCIR_10_Math-qrels_ft.dat NTCIR_10_Math-qrels_ft-converted.dat \
    >         NTCIR_10_Math-qrels_fs.dat NTCIR_10_Math-qrels_fs-converted.dat
    Retrieving judged document names, and element identifiers from NTCIR_10_Math-qrels_ft.dat
    100%|███████████████████████████████████████████████████████| 1425/1425 [00:00<00:00, 9539.55it/s]
    Retrieving judged document names, and element identifiers from NTCIR_10_Math-qrels_fs.dat
    100%|███████████████████████████████████████████████████████| 2129/2129 [00:00<00:00, 9332.81it/s]
    Processing dataset ntcir-10
    Building a mapping between element identifiers, and paragraph identifiers
    100%|████████████████████████████████████████████████████████| 2405/2405 [00:16<00:00, 144.41it/s]
    Converting relevance judgements NTCIR_10_Math-qrels_ft.dat -> NTCIR_10_Math-qrels_ft-converted.dat
    Skipping identifier f080935#idp57072, as it appears outside a paragraph
    Skipping identifier f039264#id60072, as it appears outside a paragraph
    Skipping identifier f059698#id58538, as it appears outside a paragraph
    ...
    Skipping identifier f023353#idp65840, as it appears outside a paragraph
    Skipping identifier f048268#id53551, as it appears outside a paragraph
    100%|█████████████████████████████████████████████████████| 1425/1425 [00:00<00:00, 252199.81it/s]
    1425 / 1394 input / output relevance judgements
    Converting relevance judgements NTCIR_10_Math-qrels_fs.dat -> NTCIR_10_Math-qrels_fs-converted.dat
    Skipping identifier f095981#id72919, as it appears outside a paragraph
    Skipping identifier f061190#id56357, as it appears outside a paragraph
    Skipping identifier f033738#id116089, as it appears outside a paragraph
    ...
    Skipping identifier f019052#id54515, as it appears outside a paragraph
    Skipping identifier f021845#id53581, as it appears outside a paragraph
    100%|█████████████████████████████████████████████████████| 2129/2129 [00:00<00:00, 291048.96it/s]
    2129 / 2076 input / output relevance judgements
