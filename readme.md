![linkitup](https://raw.github.com/Data2Semantics/linkitup/master/src/app/static/img/linkitup-logo-72dpi.png) 

Copyright © 2012,2013, Data2Semantics Team
VU University Amsterdam/University of Amsterdam/Data2Semantics Project

![COMMIT/](https://raw.github.com/Data2Semantics/linkitup/linkitup-hackathon/src/app/static/img/COMMIT_logo_subtitle_small_RGB.jpg)


## Golden Demo

This is the first release of the Golden Demo of the Data2Semantics project. It is an augmented version of the Linkitup workbench, which was largely developed during a Hackathon in which all partners participated. 

Compared to Linkitup, it has a number of additional dependencies:

* [SWI-Prolog](http://www.swi-prolog.org), the latest development version. 
* Java 1.6 or up
* LibreOffice (for translating MSOffice formats to OpenOffice)
* The latest version of [CAT](https://dl.dropboxusercontent.com/s/2pdbggrtw9umcmh/cat.jar?token_hash=AAFxo7TPwkPCCgDCSef5soDr_lLn_jBFyK1CF89zXo_xlg&dl=1)
* The latest version of [PLSheet](https://github.com/JanWielemaker/plsheet)
* The NLTK stopwords corpus (`nltk.download()`) 


## About
**Linki**tup is a Web-based dashboard for **enrichment** of research output published via the [Figshare.com](http://figshare.com) repository service. For license terms, see below.

**Linki**tup currently does two things:

* it takes metadata entered through [Figshare.com](http://figshare.com) and tries to find equivalent terms, categories, persons or entities on the Linked Data cloud and several Web 2.0 services.
* it extracts references from publications in [Figshare.com](http://figshare.com), and tries to find the corresponding [Digital Object Identifier](http://doi.org) (DOI).

The **Golden Demo** adds in-place conversion, analysis, enrichment and publication of datasets and documents directly from the popular Dropbox cloud service.

The video below shows how this works:

<iframe width="480" height="360" src="//www.youtube.com/embed/EGpcHPz1VBw?rel=0" frameborder="0" allowfullscreen></iframe>

**Linki**tup is developed within the COMMIT [Data2Semantics](http://www.data2semantics.org) project, a research project that develops technology for adding semantics to research data.  
	
Using Figshare allows Data2Semantics to:

* tap into a wealth of research data already published
* provide state-of-the art data enrichment services on a prominent platform with a significant user base, and
* bring RDF data publishing to a mainstream platform.
* And lastly, Figshare removes the need for a Data2Semantics data repository

**Linki**tup feeds the enriched metadata back as links to the original article in Figshare, but also builds a **RDF representation** of the metadata that can be downloaded separately, or **published** as research output on Figshare.











