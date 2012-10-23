![linkitup](https://raw.github.com/Data2Semantics/linkitup/master/src/static/img/linkitup-logo-72dpi.png) 

<!--=**Author**=
	Rinke Hoekstra
=**Date**=
	2012-10-15
=**URL**=
	[http://github.com/Data2Semantics/linkitup](https://github.com/Data2Semantics/linkitup/commit/21eb445d7d2da2b935de5219e4625b518900d121)-->

## About
**Linki**tup is a Web-based dashboard for **enrichment** of research output published via the [Figshare.com](http://figshare.com) repository service. 

**Linki**tup currently does two things:

* it takes metadata entered through [Figshare.com](http://figshare.com) and tries to find equivalent terms, categories, persons or entities on the Linked Data cloud.
* it extracts references from publications in [Figshare.com](http://figshare.com), and tries to find the corresponding [Digital Object Identifier](http://doi.org) (DOI).

**Linki**tup is developed within the COMMIT [Data2Semantics](http://www.data2semantics.org) project, a research project that develops technology for adding semantics to research data.  
	
Using Figshare allows Data2Semantics to:

* tap into a wealth of research data already published
* provide state-of-the art data enrichment services on a prominent platform with a significant user base, and
* bring RDF data publishing to a mainstream platform.
* And lastly, Figshare removes the need for a Data2Semantics data repository

**Linki**tup feeds the enriched metadata back as links to the original article in Figshare, but also builds a **RDF representation** of the metadata that can be downloaded separately, or **published** as research output on Figshare.[^1]

[^1]: Publishing RDF to Figshare is future work and will be included in the next version of **linki**tup.

We aim to extend **linki**tup to connect to other research repositories such as [EASY](http://easy.dans.knaw.nl) and the [Dataverse Network](http://thedata.org).

### Figshare

>	Figshare allows researchers to publish all of their research outputs in seconds in an easily citable, sharable and discoverable manner. All file formats can be published, including videos and datasets that are often demoted to the supplemental materials section in current publishing models. By opening up the peer review process, researchers can easily publish null results, avoiding the [file drawer effect](http://en.wikipedia.org/wiki/Publication_bias) and helping to make scientific research more efficient. figshare uses [creative commons](http://creativecommons.org/) licensing to allow frictionless sharing of research data whilst allowing users to maintain their ownership.

<span style="margin-left: 10em;">From</span> <http://figshare.com/about>

Figshare is ideal for our purposes as it combines an extremely lightweight and user friendly publishing process with a convenient [application programming interface](http://api.figshare.com) (API) on their repository.


Furthermore, Figshare assigns a [DOI](http://doi.org) and standard citation to every data item in their repository, allowing for **data integration in publications**. 

Figshare allows the annotation of five types of research output ('*articles*' in their terminology):  

* **Dataset**, tables, statistics
* **Paper**, publication document
* **Poster**, illustration, diagram
* **Figure**, image files
* **Media**, videos, audio

These file types can be assigned:

* **Categories**, taken from a taxonomy of research (individual data publishers can add categories to the taxonomy if needed)
* **Tags**, simple keywords that describe the research output
* **Links**, links to relevant other material.
* **Authors**, the authors of the publication

## Features

The functionality of **linki**tup is provided through a plugin mechanism. This version of **linki**tup is shipped with three plugins.

### Wikipedia/DBPedia

The Wikipedia/DBPedia plugin takes all *tags* from a Figshare publication, and does a literal string match to `rdfs:label` values in DBPedia. 

Users are presented with a list of Wikipedia URLs that match the tags for their publication. They can select the matches they feel are appropriate, and add them as *links* to the Figshare repository.

Corresponding DBPedia URIs are added to the RDF representation with `skos:exactMatch` properties to the related tag.

### DBLP

The DBLP plugin takes all *author* names and attempts to find authors with the same name published in the Linked Data version of the DBLP bibliography of computer science.

Users are presented with a list of DBLP URIs that match the authors for their publication. They can select the matches they feel are appropriate, and add them as *links* to the Figshare repository.

The selected DBLP URIs are added to the RDF representation as `owl:sameAs` to the matching author.

### CrossRef

The CrossRef plugin extracts references from a PDF publication (if applicable) and matches them to publications in the CrossRef metadata search. 

Users are presented with a list of three matches per reference. They can select the matches they feel are appropriate, and add the associated DOI URIs as *links* to the Figshare repository.

The selected DOI URIs are added to the RDF representation using `act:references` links from the Figshare DOI URI.

## Requirements

**Linki**tup uses the following libraries:

* Python 2.7
* Django 1.3
* [RDFLib](https://github.com/RDFLib/rdflib)
* SPARQLWrapper
* Optional:
	* Linkitup includes its own reference extraction functionality, but this may perform sub-optimally for non-standard PDF layouts. You could try using [pdf-extract](https://github.com/CrossRef/pdfextract) instead (the code for calling pdf-extract is ready to use)
