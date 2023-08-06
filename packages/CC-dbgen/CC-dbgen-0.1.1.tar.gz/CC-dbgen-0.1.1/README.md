# DbGen - A database generator

Note that this is very much a work in progress.

## Summary

This library is geared towards facilitating scientific modeling by providing an
interface between a domain expert's knowledge (a set of facts that can be
extended) and a knowledge base that integrates these facts, computing their net
effect and storing analysis in a queryable medium.

Thus the purpose is not to generate a single/static database, but rather to
create something that is responsive to incoming streams of data that reflects
the sum total of the scientist's knowledge.

As our field continues to discover the capability of machine learning for scientific and
engineering applications, it will be paramount to have flexible and declarative
tools for generating structured data from heterogeneous and/or unstructured
sources.

## Motivation

Many challenges in [computational science](https://www.biorxiv.org/content/early/2017/02/28/045104)
arise from the fact that, in practice, it is overwhelming to try to provide a
formal models for our systems of interest. When a scientific publication is able to
present a formal object that encapsulates its advancement to the field, our
idealization of how science ought work (observers can interrogate the formal object,
such that its inner workings can be properly criticized/comprehended/reproduced)
becomes not too far from reality. In practice there is so much flexibility and
heterogeneity in both data sources and data analysis (scripts) that computational
science practices employ informal reasoning and informal descriptions;
consequently, there can arise profound mistrust and miscommunication among
colleagues.

Scientific models characteristically are complex due to multi-scale
effects as well as ambiguous in how one ought best represent physical phenomena. For
example, chemical engineers have different theories to describe the behavior of
matter at subatomic, atomic, chemical species, chemical reaction, and reactor-scale
levels of granularity - we often are forced to employ all of these theories in
the course of writing a publication, even if each level of theory is describing
the same underlying stuff: we might have simulation data at one level, experimental
data at another, useful equations on a third level, and need to say something
profound at a fourth level (with other levels of theory serving as bridges between
what we have and what we want).

Although a domain expert can describe (precisely) particular relations between
elements of this this complex web of theories, it is too challenging to find a
single convenient framework in which they all reside, which must be overcome if
scientific theorists are to be able to present formal models in conjunction with
their conclusions.

A relational database may seem like an ideal structure to capture this complexity
of objects and relations. If there were a single schema that could faithfully represent the physical world,
"use a database" would be a reasonable response to scientists complaining about data/information management problems.
However, there are widely differing perspectives (even within the mind of a single
scientist) on what objects and relations exist and are significant -
so conventional usage of a relational database is not as feasible of a solution
as it may be for analogous enterprise information management problems.
Our strategy aims to provide, for a practicing scientist, an interface to relational databases -
hopefully overcoming their inherent inflexibility and the gap between low-level query
languages and high-level scientific knowledge.


## Strategy
One ought be able to declare `Objects` and `Relations` (defined in
this module), as a convenient API for someone with a scientific but not a
technical background. These Objects can be converted into a schema, while the
Relations can be converted into a data structure that we'll refer to as a `Rule`.

A driving insight for the strategy this module takes is that any database can be
interpreted as the composition of series of `Rules` (applied to an empty database),
where a `Rule` is an abstraction describing how a database can go from `State N` to `State N+1`. The abstraction
has three components:
1. _**Query**_: In general we need to get information about the current state of
the database in order to generate values to update it. A `Rule` with a trivial
query is one that introduces constants or one that performs I/O to 'seed' the
database with data from an external source
2. _**Transform**_: In general, we need to upgrade the existing state information
with a user-defined data pipeline.
3. _**InsertUpdate**_: The upgraded data from `State N` gets used in **INSERT** or  
**UPDATE** commands to yield the new database state.

These `Rules` are composable but not order-independent. Luckily, by analyzing their
first and third components, we can find what a given `Rule` depends on and what
depends on it, respectively. This allows us to sort a (growing) set of `Rules`
declared by a scientist and produce a functioning, executable program which
applies them in sequence.

`Rule` is a very broad abstraction which can range from enforcing `E=mc^2` to
providing instructions on how to parse a chemical simulation log file (and how to
insert the results into multiple tables).

Currently, scientists communicate via informal (but data-informed) arguments -
often achieving the best communication of insight via figures. Equipped with the
tools of this module, scientists can communicate their model of the world in the
form of a set of Objects and a set of Relations, and figures are simply queries
to the database uniquely generated by these Objects/Relations. By effectively
providing a workflow-management system in the course of generating the database,
we also have the ability to see the provenance of suspicious values, observing
the responsible data sources and analysis scripts.

## Integration with AQL

[AQL](http://catinf.com/) (Algebraic Query Language) poses a solution to a long standing problem of
heterogeneous data integration. The project as described above achieves modularity
and extensibility by describing the database *building* procedure in terms of a
single composable unit. However, for existing databases at a scale where rebuilding from scratch is not feasible, AQL offers hope as a high level query language that excels in specifying data migration in a declarative way.

## Related Work

This solution was proposed because alternatives had been studied and deemed inadequate for this precise problem. Descriptions of these alternatives (e.g. Django, Spark, Pegasus) will eventually be written here...

## Documentation/Tutorials

There is no good documentation / tutorial written yet. The current version is being
used 'in production' in my research group, but this is likely dauntingly complex and
confusing for outsiders (and does not make use the 'high level' Object/Relation
interface, instead opting directly writing `Rules` for convenience).
These files are found in the `inputs` and `scripts` folders. Conversely, an
uninteresting, trivial example using the 'high level' interface is found in the
`example` folder.
