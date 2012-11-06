![linkitup](https://raw.github.com/Data2Semantics/linkitup/master/src/static/img/linkitup-logo-72dpi.png) 

<!--=**Author**=
	Rinke Hoekstra
=**Date**=
	2012-10-15
=**URL**=
	[http://github.com/Data2Semantics/linkitup](https://github.com/Data2Semantics/linkitup/commit/21eb445d7d2da2b935de5219e4625b518900d121)-->
	
## About
**Linki**tup is a Web-based dashboard for **enrichment** of research output published via the [Figshare.com](http://figshare.com) repository service. For license terms, see below.

**Linki**tup currently does two things:

* it takes metadata entered through [Figshare.com](http://figshare.com) and tries to find equivalent terms, categories, persons or entities on the Linked Data cloud and several Web 2.0 services.
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

### Linked Data Repository

The LDR plugin takes all *tags* from a Figshare publication, and does a literal string match to concepts in the Elsevier Linked Data Repository. Currently this repository only contains a vocabulary of funding agencies.

Users are presented with a list of LDR concepts that match the tags of their publication. They can select the matches they feel are appropriate, and add them as *links* to the Figshare repository.

Corresponding LDR URIs are added to the RDF representation via `skos:exactMatch` properties to the related tag.

### ORCID

The ORCID plugin takes all *authors* from a Figshare publication, and does a search for these authors using the ORCID search API.

Users are presented with a list of potential matches. They can select the matches they feel are appropriate, and add them as *links* to the Figshare repository.

Corresponding ORCID URIs are added to the RDF representation via `owl:sameAs` to the matching author.

## License
**Linki**tup is free software, you can redistribute it and/or modify it under the terms of GNU [Affero General Public License](http://www.gnu.org/licenses/agpl-3.0.html) as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

You should have received a copy of the the GNU Affero General Public License along with **Linki**tup (in the file `AGPL_LICENSE`). If not, see <http://www.gnu.org/licenses/agpl-3.0.html>

**Additional permission** under the GNU Affero GPL version 3 section 7:

If you modify this Program, or any covered work, by linking or
combining it with other code, such other code is not for that reason
alone subject to any of the requirements of the GNU Affero GPL
version 3.

**Paraphrased**: the additional permission removes the *copyleft* obligation of AGPL, and thereby ensures compatibility with the LGPL while maintaining the extension of the GPL to web services, as provided by the AGPL.

## Installation

### Dependencies
**Linki**tup uses the following libraries:

* [Python 2.7](http://docs.python.org/2/)
* [Django 1.3](https://www.djangoproject.com/)
* [RDFLib](https://github.com/RDFLib/rdflib)
* [SPARQLWrapper](http://sparql-wrapper.sourceforge.net/)
* [requests](http://docs.python-requests.org/en/latest/)
* [requests-oauth](https://github.com/maraujop/requests-oauth)
* [PyYAML](http://pyyaml.org/)
* Optional:
	* Linkitup includes its own reference extraction functionality, but this may perform sub-optimally for non-standard PDF layouts. You could try using [pdf-extract](https://github.com/CrossRef/pdfextract) instead (the code for calling pdf-extract is ready to use)
	
### Setup
**Linki**tup is a [Django](https://www.djangoproject.com) project. Django uses absolute paths for the `templates` and `static` folders. Be sure to set the proper paths for your system in the `settings.py` file.

You can test run **Linki**tup by running `python manage.py runserver` in the `src` folder of the **Linki**tup installation.

A more permanent (scalable) option is to use [mod_python](http://www.modpython.org/) in [Apache](http://httpd.apache.org). Use a site configuration that is something akin to e.g.:

	<Virtualhost *:80>
        ServerName YOUR.SERVER.NAME
        DocumentRoot /PATH/TO/LINKITUP/

			Alias /static /PATH/TO/LINKITUP/src/static
				
			<Location "/">
	              SetHandler mod_python
	              PythonHandler django.core.handlers.modpython
	              SetEnv DJANGO_SETTINGS_MODULE settings
	              PythonOption django.root /linkitup
	              PythonDebug On
	              PythonPath "['/PATH/TO/LINKITUP/src','/PATH/TO/LINKITUP/'] + sys.path"
	      </Location>
	      <Location "/static/">
	              SetHandler None
	      </Location>
	</VirtualHost>
	





