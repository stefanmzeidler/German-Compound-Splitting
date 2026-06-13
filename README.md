**German Compound Noun Segmentation**

Department of Computer Science, University of Wisconsin - Milwaukee
Andrew Lin, Peter Li, and Stefan Zeidler
CS 723: Natural Language Processing
Dr. Susan McRoy
December 20, 2024

# Introduction

This project compares different models for splitting German compounds into their component words. To begin, we will discuss the motivating problem for this comparison. Next, we will review related work on the topic. Then, we will describe the models we tested, how we evaluated them, and our conclusions. We will also describe limitations and other approaches that could be tested in the future.

## Motivating Problem

Within the translation industry, a core aspect of any project is effective terminology management or mapping one term to one concept. As Keiran Dunne explains, having an explicit terminology management process prevents ambiguity and inconsistency across documents and ensures that the same concept is referred to across languages. Above all, using different terms for the same concept or the same term for different concepts should be avoided [1, p. 33].

In practical terms, inconsistent terminology often makes a business’s products or services more difficult to use. Imagine, for instance, a product manual that refers to a part with one name, while the actual product has it labeled differently. It would be quite difficult to understand what to do. Unfortunately, issues such as this are not only reproduced within translation but may be compounded, where meaning can be “lost” but also have new meanings gained, where a term with neutral connotations in the source language may have a non-neutral translation in the target language. In fact, improper terminology management may result in the propagation of an error across many target documents; fixing this issue is a much harder and costly endeavor than ensuring consistency at the outset [1, pp. 33–35]. As Childress notes, performing systemic terminology standardization represents a fixed cost per term, whereas not-performing standardization risks high variable costs associated with redundant tasks and corrective efforts after the fact [2, pp. 43–46].

Terminology management in translation involves two distinct stages: extraction and validation. Extraction involves identifying important words within documents to be translated and building a multilingual glossary from those terms. However, since this is relatively easily accomplished using methods such as term frequency-inverse document frequency measures and existing tools, our focus in this project will be on validation. For the purposes of this project, we define validation as ensuring that the correct terms from the glossary generated during extraction are used during translation. Many of the most widely used computer-assisted translation programs have integrated terminology management, such as Trados Studio’s MultiTerm and MemoQ’s QTerm. Within these programs, translators work on individual segments (translation units) in which the tokens within each segment are compared against the glossary. The threshold for a match can be decreased, for instance, from 100% to 80% to account for different lexemes of a particular lemma that arise from morphology, such as plurals. However, one area that is still difficult for systems to manage is compound nouns.

As an example, in American Express’s International Merchant Regulations [3], [4], the term “Agreement” must always be translated as “Vertrag”, but this word can become embedded in the noun-noun compound “Vertragsänderungen”. The above terminology management systems do not identify that the term in question is embedded as part of a larger noun-noun compound unless the noun-noun compound is manually added to the glossary. Considering that there are no syntactic restrictions on how noun-noun compounds may be formed in German, it would be unfeasible to add all possible combinations to a glossary. Furthermore, as Clematide et al. explain, German uses compounding as a means of word formation that can account for a significant portion of nouns within a text [5, p. 126]. In fact, Baroni et al., as cited by Ziering and van der Plas, found that nearly half of the unique words in German corpora were compounds, but at the same time, each of the words occurred very infrequently [6, p. 644]. This means that German compounds are a vital part of the German language and expression, but in the context of our paper, the system’s terminology is likely to miss many of the terminology matches within the text when embedded in compounds.

In addition to being costly in terms of human time, it would also be prohibitively computationally expensive to compare every substring within a token to every word in a glossary. To match already existing methods of identifying terminology within a text, it would be useful to be able to automatically split German compounds into their constituent words to compare against the required terminology glossary. Therefore, for our project, we plan to evaluate and compare the efficiency and accuracy of two models for splitting German compound nouns in the context of possible use in terminology validation. We value high accuracy to improve terminology validation and efficiency since terminology validation occurs in real time during the translation process.

## Compound Definition

In order to accomplish our task, it is necessary to provide a working definition of what we mean by a compound in German. For this, we borrow the definition provided by Donalies in her work “Kombinatorische Begriffsbildung” (Combinatorial Concept Construction). Donalies lists three defining characteristics of compounds:

* Compounds are created from at least two components, which differentiates them from non-combinatorial processes such as acronym formation or conversion.
* Compounds can contain affixes resulting from word-formation of the individual components, but do not use affixes in and of themselves in formation.’
* Compounds are constructed according to rules for word structure. For instance, they contain a head component that is inflected rather than each component. Per the example provided by Donalies, the plural of “palmtree” in English is not “palmstrees” but rather “palmtree”. Here, only the headword “tree” is inflected [7, p. 8].

Thus, for this paper, we do not consider any acronyms as compounds. We do consider components that have different affixes from their base form (lemma) as distinct, and in the context of terminology management, they should remain distinct. However, to evaluate the performance of the models on a somewhat noisy dataset, we found it more expedient to lemmatize the words as a form of normalization. Finally, the Gold Standard dataset labeled the head noun of each compound, which would be important to identify, as we discuss in our future work section below.

## Related Work

Koehn and Knight provide an overview of earlier approaches towards compound splitting. Brown, as cited by them, suggested an approach specific to translation in which compounds are broken down into component words as found in a translation lexicon, which itself could be derived through statistical machine translation methods [8, p. 2], [9]. Other lexicon-based approaches, developed by Monz and de Rijke and Hedlund et al., as cited by Koehn and Knight, broke words into the largest and smallest that could be found in the lexicon [8, p. 2], [10], [11]. Finally, they mention morphological analyzers such as Morphix proposed by Finkler and Neumann [8, p. 2]. Taking advantage of the fact that their morphological transformations both exhibit regularities and can proceed back and forth between forms, they proposed the use of finite state automata for the classification of words and then for further segmentation of words into their constituents [12, pp. 2–4].

In their paper, Koehn and Knight themselves propose a statistical approach which splits words according to which components have the highest geometric mean of frequencies in a given corpus [8, p. 3], since there are several options for how a word can be split, as encountered below in our evaluation section.

# Resources

## Datasets and Preprocessing

Two datasets were used for this paper: the gold standard dataset and a large dataset that contained more noise. The gold standard dataset, known as *GhoSt-NN*, was obtained from Dr. Sabine Schulte at the University of Stuttgart. This dataset was provided directly by Dr. Schulte via email upon request [13] and contains 868 entries. Dr. Schulte and her colleagues were motivated to create this dataset to address limitations in existing gold standards for German compounds, particularly those related to compositionality. As described in their paper “*Ghost-NN: A Representative Gold Standard of German Noun-Noun Compounds*”, their goal was to design a dataset that balanced critical linguistic properties such as frequency, productivity, and ambiguity while also capturing diverse semantic relations between compound constituents [13, p. 2286]. This work was inspired by the growing importance of compositionality in both cognitive and computational linguistics, where compounds like Feuerwerk (“fireworks”) and Ahornblatt (“maple leaf”) present challenges in representation and analysis [13]. The dataset draws from extensive corpus resources and systematic methodologies to ensure high-quality input for computational experiments [13].

Our second dataset, “*German Compound Database*” was obtained via the German-NLP GitHub repository maintained by Adrien Barbaresi [14]. While this repository provided links to various resources related to German natural language processing, the specific dataset we used is no longer available as of this writing. This dataset introduced variability and noise, which contributed to a broader analysis of compound structures and contained approximately 22 million entries. Because we had lost access to this repository, we no longer have access to their metadata.

The preprocessing stage is critical for ensuring the quality and consistency of the data used in training and evaluating our models for German compound noun segmentation. This stage involves transforming raw textual data into a structured, standardized format compatible with our NLP tools and models. The raw text corpus is first processed to extract compound nouns and apply transformation rules that standardize their format for further analysis.

The preprocessing begins by identifying compound nouns from the input data and splitting them into their constituent parts. These components within the dataset are separated based on specific delimiters, such as underscores, to facilitate accurate extraction of the base nouns and their modifiers. The extracted text is saved into a target column for later model training. Once the components are identified, transformation rules are applied to adjust the structure of the compound nouns. These are:

• Umlaut Transformation: Umlauts are introduced for specific characters (e.g., a to ä) based on predefined mappings to reflect German linguistic patterns accurately.

• Deletion and Replacement: Certain parts of the compound nouns are removed or replaced according to markers embedded in the data. These are denoted via a plus (+) sign for adding and a minus (-) sign for deletion.

• Handling Modifiers: Certain components enclosed within markers like parentheses or introduced with specific prefixes (such as # for omitting endings) are processed to ensure proper representation.

The preprocessing outputs a standardized representation of each compound noun – the individual decomposed components that are the target label and the fully assembled compound nouns post-transformation. To maintain focus and data quality, hyphenated compound nouns were excluded from our dataset as the decomposed nouns from these can stand on their own.

For evaluation, the preprocessed data is compared against a gold-standard dataset of compound nouns. Preprocessing also included using the Pandas library for efficient data manipulation, enabling the transformation and storage of large datasets in a structured format. Pandas was instrumental in reading the data, applying the transformation rules to each compound noun, and ensuring the output is structured into our compound and target noun columns, which simplifies its integration into the model for training and evaluation.

Our preprocessing ensures that the compound noun segmentation models receive consistent and accurate input, which is critical for improving terminology validation and translation systems. For example, the compound noun “Bund\_+es\_Regierung” is parsed during preprocessing into its components “Bund” (federation) and “Regierung” (government) and stored in the target column. The preprocessing then applies the transformation rules, incorporating the genitive marker “+es” in between the nouns to produce the final compound noun “Bundesregierung” (federal government).

## Models

For this project, we tested two models: Stuttgarter Morphologisches Analysewerkzeug (SMOR) from the University of Stuttgart and german\_compound\_splitter as taken from GitHub. We also attempted to test another model from a different researcher at the University of Stuttgart but were unable to provide a useful analysis, which we describe below.

### Stuttgarter Morphologisches Analysewerkzeug (SMOR)

The **S**tuttgarter **Mor**phologisches Analysewerkzeug (Stuttgart Morphological Analysis Tool) is a German morphological analyzer developed at the University of Stuttgart from 2003-2013 [15]. The implementation is based on the Stuttgart Finite State Transducer (SFST) toolbox [16]. It uses an approach based on finite state machines to address productive word formation and avoid the need for excessively large lexicons as compared to the lexicon-based models we discussed earlier. As part of its analysis, it must be able to handle complex words, including compound nouns. For this project, we are primarily interested in how it separates these compound nouns.

SMOR’s approach revolves around concatenation of word stems with prefixes and suffixes. As such, its lexicon includes entries for prefixes and suffixes as well as different types of stems. These affix entries also include selection constraints for which bases they can be attached to. In total, the lexicon contains 47,761 base stems, 528 compound stems, 1691 derivational stems, 323 prefixes, and 208 suffixes.

The analysis is implemented using SFST to map an input string to a sequence of morphemes with labeled features. A transducer, a type of finite state machine that also produces an output stream, is built step by step from the lexicon and compiled into a minimized form for use by the analyzer. Derived forms are created from the stems and affixes and go through several filters that check features to make sure the form is valid. These are concatenated along with the simple stems to create compounds. Then, more filters are applied to make sure these are valid compounds. The final step applies phonological rules to the analysis.

### german\_compound\_splitter

german\_compound\_splitter is a Python-based tool developed by GitHub user repodiac [17]. It uses the Pyahocorasick library [18] to search compound words for substrings from an external dictionary. The dictionary used for this project is the Free German Dictionary by Jan Schriber [19], which provides a list of 2,152,639 German words of various forms.

The pyahocorasick library used by this tool implements the Aho-Corasick algorithm to match elements from a provided dictionary within the input string. This algorithm constructs a finite state machine using the dictionary, which can efficiently search through the input string for all strings in the dictionary simultaneously. This finite state machine only needs to be constructed once and can then be used to search any given input string. Pyahocorasick implements the algorithm in C and supports Linux, macOS, and Windows.

### Morphological Operation Pattern Compound Splitter (MCS)

MCS was developed by Patrick Ziering at the University of Stuttgart. This tool aims to be language-independent by automatically learning morphological compounding operations from lemmatized corpora and word inflection.

In their paper discussing the basis for MCS, Ziering and van der Plas explain that since most languages that compound use closed compounding (where words are joined to form one word) and compounding is done through morphological transformation, they have decided to use these transformations to determine splits for binary compound words. Since morphological operations can occur at different locations within a word, the transformation process was encoded into a pattern, hence the name morphological operation pattern. Using the patterns, they generate a series of possible binary splits for compound words and implement a ranking system to determine the best split. The MOPs and lemma sets used for the tool are derived from Wikipedia entries for the target language, in this case, German. In addition, the model aims to lemmatize the split compounds, as dedicated lemmatizers often fail when encountering linking components left over from the splitting [6].

# Methods and Metrics

## Integration for Comparison

To run our comparison between these different models, we placed each into a wrapper class using an interface called Model that included several predefined methods and methods that were required to be implemented. This allowed us to iterate through the models in our evaluation class without having to worry about the specifics of how each model received input and returned output.

## Measuring Efficiency

Since terminology management in translation requires real-time access to terminology matches, we measured the time for each model to process different amounts of compound words. We split the data into folds of 10%, then measured the clock time for each model to process 10%, 20%, and up to 100% of the data. Each model was run 10 times for each split, and the average time was calculated to prevent any issues resulting from run-specific circumstances, such as a process interruption. We also manually called garbage collection before each run to avoid having it executed during the run. Clock time was selected over process time since two of the model’s spawn child processes, whose time would not have been taken into account otherwise.

## Measuring accuracy

To measure accuracy, we needed to define how true positives, true negatives, false positives, and false negatives should be interpreted for this task. Given a dataset of compounds and expected components, we define the following:

* True positives are compounds that were correctly split into their components.
* True negatives were words that had not been split and should not have been split.
* False positives were words that were split when they should not have been or split into the incorrect components.
* False negatives are words that should have been split but were not.

Identifying exactly which components were incorrectly split or not split is outside of the scope of our project since we are interested in overall accuracy. To that end, we first determined if there was an oversplit or undersplit by comparing the number of expected tokens vs the number of actual tokens. We then checked for true positives and negatives by comparing each token in our generated components. True/false negatives were determined by including simple (non-compound) words in the dataset and seeing if the models did or did not split that word. We also kept track of the number of words that were incorrect. If undersplit had occurred, we calculated that:

* false negatives = total targets – total predictions – true positives
* false positives = incorrect words – false negatives.

This allowed us to calculate totals without specifying exactly which token was wrong. As an example, if we are given the German compound *Deutschlandkarte* with expected targets *Deutsch, Land,* and *Karte,* but the model produced *Deutschland* and *Karte*, then we would know a false negative occurred since there were too few words but also a true positive since *Karte* was correct. This method also allowed us to account for instances where there was an undersplit and all words were incorrect. That would give us false negatives proportional to the amount of undersplit, and the remainder of incorrect words would be considered false positives.

# Evaluation and Discussion

In the following sections, we present the results of 100,000 randomly selected entries from the large German Compound Database dataset and the full Ghost NN dataset.

## Efficiency

Below are tables from our efficiency analysis showing the number of words tested, and the elapsed time in milliseconds.

German Compound Database

| Words | Comp Splitter (ms) | SMOR (ms) |
| --- | --- | --- |
| 1 | 8 | 7082 |
| 11111 | 393 | 7867 |
| 22222 | 787 | 8819 |
| 33333 | 1131 | 9808 |
| 44444 | 1546 | 10461 |
| 55555 | 1905 | 11482 |
| 66666 | 2286 | 12074 |
| 77777 | 2644 | 13387 |
| 88888 | 3049 | 16151 |
| 99999 | 3397 | 15112 |

Ghost NN Dataset


| Words | Comp Splitter | SMOR |
| --- | --- | --- |
| 1 | 2 | 7842 |
| 97 | 10 | 7208 |
| 193 | 19 | 7151 |
| 289 | 13 | 7218 |
| 385 | 14 | 7028 |
| 482 | 20 | 7029 |
| 578 | 21 | 7204 |
| 674 | 41 | 7430 |
| 770 | 27 | 7260 |
| 867 | 33 | 7502 |

## Accuracy

Below are the results of accuracy metrics for each model for each dataset.

German Compound Database

|  |  |  |
| --- | --- | --- |
| Metric | Comp Splitter | SMOR |
| True Positives | 42967 | 49985 |
| False Negatives | 95021 | 19581 |
| True Negatives | 49842 | 60276 |
| False Negatives | 894 | 13700 |
| accuracy | 0.49 | 0.77 |
| precision | 0.31 | 0.72 |
| recall | 0.98 | 0.78 |
| F1 | 0.47 | 0.75 |

Ghost NN

|  |  |  |
| --- | --- | --- |
| Metric | Comp Splitter | SMOR |
| True Positives | 1027 | 1633 |
| False Negatives | 200 | 55 |
| True Negatives | 0 | 0 |
| False Negatives | 285 | 25 |
| accuracy | 0.68 | 0.95 |
| precision | 0.84 | 0.97 |
| recall | 0.78 | 0.98 |
| F1 | 0.81 | 0.98 |

## Discussion

The runtime analysis reveals a significant difference in processing efficiency between the german\_compound\_splitter and SMOR models as the dataset size increases. For smaller datasets, such as testing one word, german\_compound\_splitter demonstrates exceptional efficiency, processing in just 8 milliseconds compared to SMOR’s 7082 milliseconds. However, as the dataset scales up, the difference in runtimes grows more pronounced. At 99,999 words, the german\_compound\_splitter maintains relatively low processing times at 3,397 milliseconds, whereas SMOR’s runtime increases drastically to 15,112 milliseconds. This disparity can be attributed to SMOR’s reliance on finite-state transducer initialization for every analysis cycle, introducing significant overhead. In contrast, the german\_compound\_splitter benefits from its efficient use of preloaded assets and optimized string-matching algorithms, allowing it to scale effectively with larger datasets. While SMOR’s higher runtimes might be justified by its robust morphological analysis capabilities, the efficiency gap suggests that the german\_compound\_splitter is better suited for real-time terminology tasks.

Regarding accuracy, SMOR is substantially outperforms german\_compound\_splitter across almost all metrics for both datasets. However, both datasets see a large reduction in accuracy for the German Compound Database dataset. This may be due to noise or incorrect labels in the dataset. One outlier is german\_compound\_splitter’s recall on the German Compound Database dataset. This means german\_compound\_splitter had far fewer instances where it did not split a word where it should have. This may mean that the german\_compound\_splitter may achieve an artificially high recall by aggressively splitting words.

## Challenges and Limitations

When running the models, we ran into one issue with SMOR that affected our ability to create an accurate and generalizable comparison. We were also unable to run MCS, as discussed below.

### MCS

When trying to implement MCS, we ran into several issues. Firstly, since it was a self-contained jar file with limited arguments, we could not control the input and output behavior as much as we would have liked. Second, the model would crash on certain words, and we could not determine the root cause. We changed the dataset and observed the model crashing on different words. Third, to make a meaningful comparison to SMOR, we would have had to run it on a Linux system. However, it seems that the model is unable to correctly determine the file paths in a Linux system and could not access input or output. We ultimately decided not to include this tool in our comparison.

### SMOR

For the SMOR model, each time we wished to run an analysis, the transducers had to be loaded first. We are unable to control this behavior. This is in comparison to german\_compound\_splitter, which only needed to load its assets once and then could reuse them for each run. This meant that SMOR had a significant amount of additional time, as can be seen in our data.

### german\_compound\_splitter

For German compound splitter, we note that the accuracy of the model appears to be largely dependent on the size of the supplied dictionary. The dictionary we used contained over 2 million entries, but a larger

## Limitations

For this analysis, we normalized the outputs of the models to make a comparison since each model may output components in a different format (capitalization, plural vs singular, etc.). To normalize, we made each token lowercase and lemmatized it – both the targets and the components. However, in the context of terminology management, it is important to match lexemes rather than base forms.

We also limited ourselves to only comparing general accuracy than a fine-grained analysis of types of errors and specific word classes.

# Conclusion and future work

## Conclusion

Given the performance of both tested models regarding the stated task of performing terminology management, we can say that german\_compound\_splitter performs much better in terms of efficiency. However, its overall accuracy was lower than SMOR’s, leading to a tradeoff between the two models. We believe that we could address the accuracy issue of german\_compound\_splitter by using a larger dictionary or improve SMOR’s efficiency if we were able to keep the transducers loaded in memory to use as needed.

## Future Work

There are several possible avenues we could proceed along in the future. We would certainly like to get MCS working, and the paper by Ziering and van der Plas provides an outline of how their model is constructed. The authors may also update the model, or we could reach out to them with questions regarding implementation.

The larger dataset may also be sufficiently large (22 million entries) to allow for deep learning using a transformer architecture. However, we would need to determine how to create the dense embeddings necessary for processing and how to determine the outputs. For example, should there be an output node for each possible component word, or should there be a sequence of vector outputs that could be matched to their most similar words.

A third option would be to make sure of transfer learning to fine-tune a pre-trained model to the task. We would need to determine what kind of pre-trained model would be best and then the best way to fine-tune it.

Regarding analysis, one could perform a deeper analysis into the kinds of errors that occurred most often. For instance, are adjective-noun compounds more likely to be split incorrectly than noun-noun compounds? Are there differences in the ways models handle compounds containing linking characters that do not belong to any component?

One could also potentially make use of the distinction of a head component within a compound to determine which words could or should be changed to their lemmatized form for comparison. As mentioned earlier, only the headword is modified when the compound is inflected – the other components should remain the same.

**Works Cited**

[1] K. J. Dunne, “Terminology: Ignore it at your peril,” *MultiLingual*, vol. 18, no. 3, pp. 32–38, May 2007.

[2] M. D. Childress, “Terminology work saves more than it costs,” *MultiLingual*, pp. 43–46, May 2007.

[3] American Express, “Merchant Regulations: International.” Apr. 2024.

[4] American Express, “Regularien für Akzeptanz Partner.” Apr. 2024.

[5] S. Clematide *et al.*, *A multilingual gold standard for translation spotting of German compounds and their corresponding multiword units in English, French, Italian and Spanish*, vol. 341. in Multiword Units in Machine Translation and Translation Technology, vol. 341. AMSTERDAM ME: John Benjamins Publishing Company, 2018.

[6] P. Ziering and L. van der Plas, “Towards Unsupervised and Language-independent Compound Splitting using Inflectional Morphological Transformations,” in *Proceedings of the 2016 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies*, K. Knight, A. Nenkova, and O. Rambow, Eds., San Diego, California: Association for Computational Linguistics, Jun. 2016, pp. 644–653. doi: 10.18653/v1/N16-1078.

[7] E. Donalies, “Grammatik des Deutschen im europäischen Vergleich: Kombinatorische Begriffsbildung: Teil I : Substantivkomposition,” *Arbeitspapiere Mater. Zur Dtsch. Sprache*, vol. 2, no. 04, Jun. 2004.

[8] P. Koehn and K. Knight, “Empirical Methods for Compound Splitting,” Feb. 22, 2003, *arXiv*: arXiv:cs/0302032. doi: 10.48550/arXiv.cs/0302032.

[9] P. F. Brown *et al.*, “A statistical approach to machine translation,” *Comput Linguist*, vol. 16, no. 2, pp. 79–85, Jun. 1990.

[10] C. Monz and M. de Rijke, “Shallow Morphological Analysis in Monolingual Information Retrieval for Dutch, German, and Italian,” in *Evaluation of Cross-Language Information Retrieval Systems*, C. Peters, M. Braschler, J. Gonzalo, and M. Kluck, Eds., Berlin, Heidelberg: Springer, 2002, pp. 262–277. doi: 10.1007/3-540-45691-0\_24.

[11] T. Hedlund, H. Keskustalo, A. Pirkola, E. Airio, and K. Järvelin, “Utaclir @ CLEF 2001 — Effects of Compound Splitting and N-Gram Techniques,” in *Evaluation of Cross-Language Information Retrieval Systems*, C. Peters, M. Braschler, J. Gonzalo, and M. Kluck, Eds., Berlin, Heidelberg: Springer, 2002, pp. 118–136. doi: 10.1007/3-540-45691-0\_10.

[12] W. Finkler and G. Neumann, “MORPHIX: A Fast Realization of a Classification-Based Approach to Morphology,” in *4. Österreichische Artificial-Intelligence-Tagung*, H. Trost, Ed., Berlin, Heidelberg: Springer, 1988, pp. 11–19. doi: 10.1007/978-3-642-73998-9\_3.

[13] Sabine Schulte im Walde, Anna Hätty, Stefan Bott, and Nana Khvtisavrishvili, “GhoSt-NN: A Representative Gold Standard of German Noun-Noun Compounds,” University of Stuttgart, Stuttgart, Germany. [Online]. Available: http://www.ims.uni-stuttgart.de/data/ghost-nn

[14] A. Barbaresi, *adbar/German-NLP*. (Dec. 12, 2024). Accessed: Dec. 20, 2024. [Online]. Available: https://github.com/adbar/German-NLP

[15] H. Schmid, A. Fitschen, and U. Heid, “SMOR: A German Computational Morphology Covering Derivation, Composition, and Inflection,” in *Proceedings of the IVth International Conference on Language Resources and Evaluation (LREC 2004)*, Lisbon, Portugal, pp. 1263–1266.

[16] H. Schmid, “A Programming Language for Finite State Transducers,” in *Proceedings of the 5th International Workshop on Finite State Methods in Natural Language Processing (FSMNLP 2005)*, Helsinki, Finland.

[17] repodiac, *repodiac/german\_compound\_splitter*. (Sep. 03, 2024). Python. Accessed: Dec. 20, 2024. [Online]. Available: https://github.com/repodiac/german\_compound\_splitter

[18] W. Muła and Ombredanne, *pyahocorasick*. C, Python. Accessed: Dec. 20, 2024. [Online]. Available: http://github.com/WojciechMula/pyahocorasick

[19] “Free German Dictionary,” SourceForge. Accessed: Dec. 20, 2024. [Online]. Available: https://sourceforge.net/projects/germandict/
