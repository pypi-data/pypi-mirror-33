~~~~~~~~~~~~~~~
zc.relationship
~~~~~~~~~~~~~~~

The zc.relationship package currently contains two main types of
components: a relationship index, and some relationship containers.
Both are designed to be used within the ZODB, although the index is
flexible enough to be used in other contexts.  They share the model that
relationships are full-fledged objects that are indexed for optimized
searches.  They also share the ability to perform optimized intransitive
and transitive relationship searches, and to support arbitrary filter
searches on relationship tokens.

The index is a very generic component that can be used to optimize searches
for N-ary relationships, can be used standalone or within a catalog, can be
used with pluggable token generation schemes, and generally tries to provide
a relatively policy-free tool.  It is expected to be used primarily as an
engine for more specialized and constrained tools and APIs.

The relationship containers use the index to manage two-way
relationships, using a derived mapping interface.  It is a reasonable
example of the index in standalone use.

Another example, using the container model but supporting five-way
relationships ("sources", "targets", "relation", "getContext", "state"), can
be found in plone.relations.  Its README is a good read.

http://dev.plone.org/plone/browser/plone.relations/trunk/plone/relations

This current document describes the relationship index.  See
container.rst for documentation of the relationship container.

**PLEASE NOTE: the index in zc.relationship, described below, now exists for
backwards compatibility.  zc.relation.catalog now contains the most recent,
backward-incompatible version of the index code.**

=====
Index
=====

.. contents::

Overview
========

The index takes a very precise view of the world: instantiation requires
multiple arguments specifying the configuration; and using the index
requires that you acknowledge that the relationships and their
associated indexed values are usually tokenized within the index.  This
precision trades some ease-of-use for the possibility of flexibility,
power, and efficiency.  That said, the index's API is intended to be
consistent, and to largely adhere to "there's only one way to do it"
[#apply]_.

Simplest Example
----------------

Before diving into the N-way flexibility and the other more complex
bits, then, let's have a quick basic demonstration: a two way
relationship from one value to another.  This will give you a taste of
the relationship index, and let you use it reasonably well for
light-to-medium usage.  If you are going to use more of its features or
use it more in a potentially high-volume capacity, please consider
trying to understand the entire document.

Let's say that we are modeling a relationship of people to their
supervisors: an employee may have a single supervisor.

Let's say further that employee names are unique and can be used to
represent employees.  We can use names as our "tokens".  Tokens are
similar to the primary key in a relational database, or in intid or
keyreference in Zope 3--some way to uniquely identify an object, which
sorts reliably and can be resolved to the object given the right context.

    >>> from __future__ import print_function
    >>> from functools import total_ordering
    >>> employees = {} # we'll use this to resolve the "name" tokens
    >>> @total_ordering
    ... class Employee(object):
    ...     def __init__(self, name, supervisor=None):
    ...         if name in employees:
    ...             raise ValueError('employee with same name already exists')
    ...         self.name = name # expect this to be readonly
    ...         self.supervisor = supervisor
    ...         employees[name] = self
    ...     def __repr__(self): # to make the tests prettier...
    ...         return '<' + self.name + '>'
    ...     def __eq__(self, other):
    ...         return self is other
    ...     def __lt__(self, other): # to make the tests prettier...
    ...         # pukes if other doesn't have name
    ...         return self.name < other.name
    ...

So, we need to define how to turn employees into their tokens.  That's
trivial.  (We explain the arguments to this function in detail below,
but for now we're aiming for "breezy overview".)

    >>> def dumpEmployees(emp, index, cache):
    ...     return emp.name
    ...

We also need a way to turn tokens into employees.  We use our dict for that.

    >>> def loadEmployees(token, index, cache):
    ...     return employees[token]
    ...

We also need a way to tell the index to find the supervisor for indexing:

    >>> def supervisor(emp, index):
    ...     return emp.supervisor # None or another employee
    ...

Now we have enough to get started with an index.  The first argument to
Index is the attributes to index: we pass the `supervisor` function
(which is also used in this case to define the index's name, since we do
not pass one explicitly), the dump and load functions, and a BTree
module that specifies sets that can hold our tokens (OO or OL should
also work).  As keyword arguments, we tell the index how to dump and
load our relationship tokens--the same functions in this case--and what
a reasonable BTree module is for sets (again, we choose OI, but OO or OL
should work).

    >>> from zc.relationship import index
    >>> import BTrees
    >>> ix = index.Index(
    ...     ({'callable': supervisor, 'dump': dumpEmployees,
    ...       'load': loadEmployees, 'btree': BTrees.family32.OI},),
    ...     dumpRel=dumpEmployees, loadRel=loadEmployees,
    ...     relFamily=BTrees.family32.OI)

Now let's create a few employees.

    >>> a = Employee('Alice')
    >>> b = Employee('Betty', a)
    >>> c = Employee('Chuck', a)
    >>> d = Employee('Duane', b)
    >>> e = Employee('Edgar', b)
    >>> f = Employee('Frank', c)
    >>> g = Employee('Grant', c)
    >>> h = Employee('Howie', d)

In a diagram style with which you will become familiar if you make it to
the end of this document, let's show the hierarchy.

::

                Alice
             __/     \__
        Betty           Chuck
        /   \           /   \
    Duane   Edgar   Frank   Grant
      |
    Howie

So who works for Alice?  To ask the index, we need to tell it about them.

    >>> for emp in (a,b,c,d,e,f,g,h):
    ...     ix.index(emp)
    ...

Now we can ask.  We always need to ask with tokens.  The index provides
a method to try and make this more convenient: `tokenizeQuery`
[#resolveQuery]_.

.. [#resolveQuery] You can also resolve queries.

    >>> ix.resolveQuery({None: 'Alice'})
    {None: <Alice>}
    >>> ix.resolveQuery({'supervisor': 'Alice'})
    {'supervisor': <Alice>}

The spelling of the query is described in more detail
later, but the idea is simply that keys in a dictionary specify
attribute names, and the values specify the constraints.

    >>> t = ix.tokenizeQuery
    >>> sorted(ix.findRelationshipTokens(t({'supervisor': a})))
    ['Betty', 'Chuck']
    >>> sorted(ix.findRelationships(t({'supervisor': a})))
    [<Betty>, <Chuck>]

How do we find what the employee's supervisor is?  Well, in this case,
look at the attribute!  If you can use an attribute that will usually be
a win in the ZODB.  If you want to look at the data in the index,
though, that's easy enough.  Who is Howie's supervisor?  The None key in
the query indicates that we are matching against the relationship token
itself [#None_details]_.

.. [#None_details] You can search for relations that haven't been indexed.

    >>> list(ix.findRelationshipTokens({None: 'Ygritte'}))
    []

    You can also combine searches with None, just for completeness.

    >>> list(ix.findRelationshipTokens({None: 'Alice', 'supervisor': None}))
    ['Alice']
    >>> list(ix.findRelationshipTokens({None: 'Alice', 'supervisor': 'Betty'}))
    []
    >>> list(ix.findRelationshipTokens({None: 'Betty', 'supervisor': 'Alice'}))
    ['Betty']

    >>> h.supervisor
    <Duane>
    >>> list(ix.findValueTokens('supervisor', t({None: h})))
    ['Duane']
    >>> list(ix.findValues('supervisor', t({None: h})))
    [<Duane>]

What about transitive searching?  Well, you need to tell the index how to
walk the tree.  In simple cases like this, the index's
TransposingTransitiveQueriesFactory will do the trick.  We just want to tell
the factory to transpose the two keys, None and 'supervisor'.  We can then use
it in queries for transitive searches.

    >>> factory = index.TransposingTransitiveQueriesFactory(None, 'supervisor')

Who are all of Howie's supervisors transitively (this looks up in the
diagram)?

    >>> list(ix.findValueTokens('supervisor', t({None: h}),
    ...      transitiveQueriesFactory=factory))
    ['Duane', 'Betty', 'Alice']
    >>> list(ix.findValues('supervisor', t({None: h}),
    ...      transitiveQueriesFactory=factory))
    [<Duane>, <Betty>, <Alice>]

Who are all of the people Betty supervises transitively, breadth first (this
looks down in the diagram)?

    >>> people = list(ix.findRelationshipTokens(
    ...     t({'supervisor': b}), transitiveQueriesFactory=factory))
    >>> sorted(people[:2])
    ['Duane', 'Edgar']
    >>> people[2]
    'Howie'
    >>> people = list(ix.findRelationships(
    ...     t({'supervisor': b}), transitiveQueriesFactory=factory))
    >>> sorted(people[:2])
    [<Duane>, <Edgar>]
    >>> people[2]
    <Howie>

This transitive search is really the only transitive factory you would want
here, so it probably is safe to wire it in as a default.  While most
attributes on the index must be set at instantiation, this happens to be one
we can set after the fact.

    >>> ix.defaultTransitiveQueriesFactory = factory

Now all searches are transitive.

    >>> list(ix.findValueTokens('supervisor', t({None: h})))
    ['Duane', 'Betty', 'Alice']
    >>> list(ix.findValues('supervisor', t({None: h})))
    [<Duane>, <Betty>, <Alice>]
    >>> people = list(ix.findRelationshipTokens(t({'supervisor': b})))
    >>> sorted(people[:2])
    ['Duane', 'Edgar']
    >>> people[2]
    'Howie'
    >>> people = list(ix.findRelationships(t({'supervisor': b})))
    >>> sorted(people[:2])
    [<Duane>, <Edgar>]
    >>> people[2]
    <Howie>

We can force a non-transitive search, or a specific search depth, with
maxDepth [#needs_a_transitive_queries_factory]_.

.. [#needs_a_transitive_queries_factory] A search with a maxDepth > 1 but
    no transitiveQueriesFactory raises an error.

    >>> ix.defaultTransitiveQueriesFactory = None
    >>> ix.findRelationshipTokens({'supervisor': 'Duane'}, maxDepth=3)
    Traceback (most recent call last):
    ...
    ValueError: if maxDepth not in (None, 1), queryFactory must be available

    >>> ix.defaultTransitiveQueriesFactory = factory

    >>> list(ix.findValueTokens('supervisor', t({None: h}), maxDepth=1))
    ['Duane']
    >>> list(ix.findValues('supervisor', t({None: h}), maxDepth=1))
    [<Duane>]
    >>> sorted(ix.findRelationshipTokens(t({'supervisor': b}), maxDepth=1))
    ['Duane', 'Edgar']
    >>> sorted(ix.findRelationships(t({'supervisor': b}), maxDepth=1))
    [<Duane>, <Edgar>]

Transitive searches can handle recursive loops and have other features as
discussed in the larger example and the interface.

Our last two introductory examples show off three other methods: `isLinked`
`findRelationshipTokenChains` and `findRelationshipChains`.

isLinked lets you answer whether two queries are linked.  Is Alice a
supervisor of Howie? What about Chuck?  (Note that, if your
relationships describe a hierarchy, searching up a hierarchy is usually
more efficient, so the second pair of questions is generally preferable
to the first in that case.)

    >>> ix.isLinked(t({'supervisor': a}), targetQuery=t({None: h}))
    True
    >>> ix.isLinked(t({'supervisor': c}), targetQuery=t({None: h}))
    False
    >>> ix.isLinked(t({None: h}), targetQuery=t({'supervisor': a}))
    True
    >>> ix.isLinked(t({None: h}), targetQuery=t({'supervisor': c}))
    False

`findRelationshipTokenChains` and `findRelationshipChains` help you discover
*how* things are transitively related.  A "chain" is a transitive path of
relationships.  For instance, what's the chain of command between Alice and
Howie?

    >>> list(ix.findRelationshipTokenChains(
    ...     t({'supervisor': a}), targetQuery=t({None: h})))
    [('Betty', 'Duane', 'Howie')]
    >>> list(ix.findRelationshipChains(
    ...     t({'supervisor': a}), targetQuery=t({None: h})))
    [(<Betty>, <Duane>, <Howie>)]

This gives you a quick overview of the basic index features.  This should be
enough to get you going.  Now we'll dig in some more, if you want to know the
details.

Starting the N-Way Examples
===========================

To exercise the index further, we'll come up with a somewhat complex
relationship to index. Let's say we are modeling a generic set-up like
SUBJECT RELATIONSHIPTYPE OBJECT in CONTEXT.  This could let you let
users define relationship types, then index them on the fly.  The
context can be something like a project, so we could say

"Fred" "has the role of" "Project Manager" on the "zope.org redesign project".

Mapped to the parts of the relationship object, that's

["Fred" (SUBJECT)] ["has the role of" (RELATIONSHIPTYPE)]
["Project Manager" (OBJECT)] on the ["zope.org redesign project" (CONTEXT)].

Without the context, you can still do interesting things like

["Ygritte" (SUBJECT)] ["manages" (RELATIONSHIPTYPE)] ["Uther" (OBJECT)]

In our new example, we'll leverage the fact that the index can accept
interface attributes to index.  So let's define a basic interface
without the context, and then an extended interface with the context.

    >>> from zope import interface
    >>> class IRelationship(interface.Interface):
    ...     subjects = interface.Attribute(
    ...         'The sources of the relationship; the subject of the sentence')
    ...     relationshiptype = interface.Attribute(
    ...         '''unicode: the single relationship type of this relationship;
    ...         usually contains the verb of the sentence.''')
    ...     objects = interface.Attribute(
    ...         '''the targets of the relationship; usually a direct or
    ...         indirect object in the sentence''')
    ...
    >>> class IContextAwareRelationship(IRelationship):
    ...     def getContext():
    ...         '''return a context for the relationship'''
    ...

Now we'll create an index.  To do that, we must minimally pass in an
iterable describing the indexed values.  Each item in the iterable must
either be an interface element (a zope.interface.Attribute or
zope.interface.Method associated with an interface, typically obtained
using a spelling like `IRelationship['subjects']`) or a dict.  Each dict
must have either the 'element' key, which is the interface element to be
indexed; or the 'callable' key, which is the callable shown in the
simpler, introductory example above [#there_can_be_only_one]_.

.. [#there_can_be_only_one] instantiating an index with a dictionary containing
    both the 'element' and the 'callable' key is an error:

    >>> def subjects(obj, index, cache):
    ...     return obj.subjects
    ...
    >>> ix = index.Index(
    ...     ({'element': IRelationship['subjects'],
    ...       'callable': subjects, 'multiple': True},
    ...      IRelationship['relationshiptype'],
    ...      {'element': IRelationship['objects'], 'multiple': True},
    ...      IContextAwareRelationship['getContext']),
    ...     index.TransposingTransitiveQueriesFactory('subjects', 'objects'))
    Traceback (most recent call last):
    ...
    ValueError: cannot provide both callable and element

    While we're at it, as you might expect, you must provide one of them.

    >>> ix = index.Index(
    ...     ({'multiple': True},
    ...      IRelationship['relationshiptype'],
    ...      {'element': IRelationship['objects'], 'multiple': True},
    ...      IContextAwareRelationship['getContext']),
    ...     index.TransposingTransitiveQueriesFactory('subjects', 'objects'))
    Traceback (most recent call last):
    ...
    ValueError: must provide element or callable

It then
can contain other keys to override the default indexing behavior for the
element.

The element's or callable's __name__ will be used to refer to this
element in queries, unless the dict has a 'name' key, which must be a
non-empty string [#name_errors]_.

.. [#name_errors] It's possible to pass a callable without a name, in which
    case you must explicitly specify a name.

    >>> @total_ordering
    ... class AttrGetter(object):
    ...     def __init__(self, attr):
    ...         self.attr = attr
    ...     def __eq__(self, other):
    ...         return self is other
    ...     def __lt__(self, other):
    ...         return self.attr < getattr(other, 'attr', other)
    ...     def __call__(self, obj, index, cache):
    ...         return getattr(obj, self.attr, None)
    ...
    >>> subjects = AttrGetter('subjects')
    >>> ix = index.Index(
    ...     ({'callable': subjects, 'multiple': True},
    ...      IRelationship['relationshiptype'],
    ...      {'element': IRelationship['objects'], 'multiple': True},
    ...      IContextAwareRelationship['getContext']),
    ...     index.TransposingTransitiveQueriesFactory('subjects', 'objects'))
    Traceback (most recent call last):
    ...
    ValueError: no name specified
    >>> ix = index.Index(
    ...     ({'callable': subjects, 'multiple': True, 'name': subjects},
    ...      IRelationship['relationshiptype'],
    ...      {'element': IRelationship['objects'], 'multiple': True},
    ...      IContextAwareRelationship['getContext']),
    ...     index.TransposingTransitiveQueriesFactory('subjects', 'objects'))

    It's also an error to specify the same name or element twice,
    however you do it.

    >>> ix = index.Index(
    ...     ({'callable': subjects, 'multiple': True, 'name': 'objects'},
    ...      IRelationship['relationshiptype'],
    ...      {'element': IRelationship['objects'], 'multiple': True},
    ...      IContextAwareRelationship['getContext']),
    ...     index.TransposingTransitiveQueriesFactory('subjects', 'objects'))
    ... # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: ('name already used', 'objects')

    >>> ix = index.Index(
    ...     ({'callable': subjects, 'multiple': True, 'name': 'subjects'},
    ...      IRelationship['relationshiptype'],
    ...      {'callable': subjects, 'multiple': True, 'name': 'objects'},
    ...      IContextAwareRelationship['getContext']),
    ...     index.TransposingTransitiveQueriesFactory('subjects', 'objects'))
    ... # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
    ...
    ValueError: ('element already indexed',
                 <zc.relationship.README.AttrGetter object at ...>)

    >>> ix = index.Index(
    ...     ({'element': IRelationship['objects'], 'multiple': True,
    ...       'name': 'subjects'},
    ...      IRelationship['relationshiptype'],
    ...      {'element': IRelationship['objects'], 'multiple': True},
    ...      IContextAwareRelationship['getContext']),
    ...     index.TransposingTransitiveQueriesFactory('subjects', 'objects'))
    ... # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
    ...
    ValueError: ('element already indexed',
                 <zope.interface.interface.Attribute object at ...>)

The element is assumed to be a single value, unless the dict has a 'multiple'
key with a value equivalent True.  In our example, "subjects" and "objects" are
potentially multiple values, while "relationshiptype" and "getContext" are
single values.

By default, the values for the element will be tokenized and resolved using an
intid utility, and stored in a BTrees.IFBTree.  This is a good choice if you
want to make object tokens easily mergable with typical Zope 3 catalog
results.  If you need different behavior for any element, you can specify
three keys per dict:

- 'dump', the tokenizer, a callable taking (obj, index, cache) and returning a
  token;

- 'load' the token resolver, a callable taking (token, index, cache) to return
  the object which the token represents; and

- 'btree', the btree module to use to store and process the tokens, such as
  BTrees.OOBTree.

If you provide a custom 'dump' you will almost certainly need to provide a
custom 'load'; and if your tokens are not integers then you will need to
specify a different 'btree' (either BTrees.OOBTree or BTrees.OIBTree, as of
this writing).

The tokenizing function ('dump') *must* return homogenous, immutable tokens:
that is, any given tokenizer should only return tokens that sort
unambiguously, across Python versions, which usually mean that they are all of
the same type.  For instance, a tokenizer should only return ints, or only
return strings, or only tuples of strings, and so on.  Different tokenizers
used for different elements in the same index may return different types. They
also may return the same value as the other tokenizers to mean different
objects: the stores are separate.

Note that both dump and load may also be explicitly None in the dictionary:
this will mean that the values are already appropriate to be used as tokens.
It enables an optimization described in the
`Optimizing relationship index use`_ section [#neither_or_both]_.

.. [#neither_or_both] It is not allowed to provide only one or the other of
    'load' and 'dump'.

    >>> ix = index.Index(
    ...     ({'element': IRelationship['subjects'], 'multiple': True,
    ...       'name': 'subjects','dump': None},
    ...      IRelationship['relationshiptype'],
    ...      {'element': IRelationship['objects'], 'multiple': True},
    ...      IContextAwareRelationship['getContext']),
    ...     index.TransposingTransitiveQueriesFactory('subjects', 'objects'))
    ... # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: either both of 'dump' and 'load' must be None, or neither

    >>> ix = index.Index(
    ...     ({'element': IRelationship['objects'], 'multiple': True,
    ...       'name': 'subjects','load': None},
    ...      IRelationship['relationshiptype'],
    ...      {'element': IRelationship['objects'], 'multiple': True},
    ...      IContextAwareRelationship['getContext']),
    ...     index.TransposingTransitiveQueriesFactory('subjects', 'objects'))
    ... # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: either both of 'dump' and 'load' must be None, or neither


In addition to the one required argument to the class, the signature contains
four optional arguments.  The 'defaultTransitiveQueriesFactory' is the next,
and allows you to specify a callable as described in
interfaces.ITransitiveQueriesFactory.  Without it transitive searches will
require an explicit factory every time, which can be tedious.  The index
package provides a simple implementation that supports transitive searches
following two indexed elements (TransposingTransitiveQueriesFactory) and this
document describes more complex possible transitive behaviors that can be
modeled.  For our example, "subjects" and "objects" are the default transitive
fields, so if Ygritte (SUBJECT) manages Uther (OBJECT), and Uther (SUBJECT)
manages Emily (OBJECT), a search for all those transitively managed by Ygritte
will transpose Uther from OBJECT to SUBJECT and find that Uther manages Emily.
Similarly, to find all transitive managers of Emily, Uther will change place
from SUBJECT to OBJECT in the search [#TransposingTransitiveQueriesFactory]_.

.. [#TransposingTransitiveQueriesFactory] The factory lets you specify two
    names, which are transposed for transitive walks.  This is usually what
    you want for a hierarchy and similar variations: as the text describes
    later, more complicated traversal might be desired in more complicated
    relationships, as found in genealogy.

    It supports both transposing values and relationship tokens, as seen in
    the text.

    In this footnote, we'll explore the factory in the small, with index
    stubs.

    >>> factory = index.TransposingTransitiveQueriesFactory(
    ...     'subjects', 'objects')
    >>> class StubIndex(object):
    ...     def findValueTokenSet(self, rel, name):
    ...         return {
    ...             ('foo', 'objects'): ('bar',),
    ...             ('bar', 'subjects'): ('foo',)}[(rel, name)]
    ...
    >>> ix = StubIndex()
    >>> list(factory(['foo'], {'subjects': 'foo'}, ix, {}))
    [{'subjects': 'bar'}]
    >>> list(factory(['bar'], {'objects': 'bar'}, ix, {}))
    [{'objects': 'foo'}]

    If you specify both fields then it won't transpose.

    >>> list(factory(['foo'], {'objects': 'bar', 'subjects': 'foo'}, ix, {}))
    []

    If you specify additional fields then it keeps them statically.

    >>> list(factory(['foo'], {'subjects': 'foo', 'getContext': 'shazam'},
    ...      ix, {})) == [{'subjects': 'bar', 'getContext': 'shazam'}]
    True

The next three arguments, 'dumpRel', 'loadRel' and 'relFamily', have
to do with the relationship tokens.  The default values assume that you will
be using intid tokens for the relationships, and so 'dumpRel' and
'loadRel' tokenize and resolve, respectively, using the intid utility; and
'relFamily' defaults to BTrees.IFBTree.

If relationship tokens (from 'findRelationshipChains' or 'apply' or
'findRelationshipTokenSet', or in a filter to most of the search methods) are
to be merged with other catalog results, relationship tokens should be based
on intids, as in the default.  For instance, if some relationships are only
available to some users on the basis of security, and you keep an index of
this, then you will want to use a filter based on the relationship tokens
viewable by the current user as kept by the catalog index.

If you are unable or unwilling to use intid relationship tokens, tokens must
still be homogenous and immutable as described above for indexed values tokens.

The last argument is 'family', which effectively defaults to BTrees.family32.
If you don't expicitly specify BTree modules for your value and relationship
sets, this value will determine whether you use the 32 bit or the 64 bit
IFBTrees [#family64]_.

.. [#family64] Here's an example of specifying the family64.  This is a "white
    box" demonstration that looks at some of the internals.

    >>> ix = index.Index( # 32 bit default
    ...     ({'element': IRelationship['subjects'], 'multiple': True},
    ...      IRelationship['relationshiptype'],
    ...      {'element': IRelationship['objects'], 'multiple': True},
    ...      IContextAwareRelationship['getContext']),
    ...     index.TransposingTransitiveQueriesFactory('subjects', 'objects'))
    >>> ix._relTools['BTree'] is BTrees.family32.IF.BTree
    True
    >>> ix._attrs['subjects']['BTree'] is BTrees.family32.IF.BTree
    True
    >>> ix._attrs['objects']['BTree'] is BTrees.family32.IF.BTree
    True
    >>> ix._attrs['getContext']['BTree'] is BTrees.family32.IF.BTree
    True

    >>> ix = index.Index( # explicit 32 bit
    ...     ({'element': IRelationship['subjects'], 'multiple': True},
    ...      IRelationship['relationshiptype'],
    ...      {'element': IRelationship['objects'], 'multiple': True},
    ...      IContextAwareRelationship['getContext']),
    ...     index.TransposingTransitiveQueriesFactory('subjects', 'objects'),
    ...     family=BTrees.family32)
    >>> ix._relTools['BTree'] is BTrees.family32.IF.BTree
    True
    >>> ix._attrs['subjects']['BTree'] is BTrees.family32.IF.BTree
    True
    >>> ix._attrs['objects']['BTree'] is BTrees.family32.IF.BTree
    True
    >>> ix._attrs['getContext']['BTree'] is BTrees.family32.IF.BTree
    True

    >>> ix = index.Index( # explicit 64 bit
    ...     ({'element': IRelationship['subjects'], 'multiple': True},
    ...      IRelationship['relationshiptype'],
    ...      {'element': IRelationship['objects'], 'multiple': True},
    ...      IContextAwareRelationship['getContext']),
    ...     index.TransposingTransitiveQueriesFactory('subjects', 'objects'),
    ...     family=BTrees.family64)
    >>> ix._relTools['BTree'] is BTrees.family64.IF.BTree
    True
    >>> ix._attrs['subjects']['BTree'] is BTrees.family64.IF.BTree
    True
    >>> ix._attrs['objects']['BTree'] is BTrees.family64.IF.BTree
    True
    >>> ix._attrs['getContext']['BTree'] is BTrees.family64.IF.BTree
    True

If we had an IIntId utility registered and wanted to use the defaults, then
instantiation  of an index for our relationship would look like this:

    >>> ix = index.Index(
    ...     ({'element': IRelationship['subjects'], 'multiple': True},
    ...      IRelationship['relationshiptype'],
    ...      {'element': IRelationship['objects'], 'multiple': True},
    ...      IContextAwareRelationship['getContext']),
    ...     index.TransposingTransitiveQueriesFactory('subjects', 'objects'))

That's the simple case.  With relatively little fuss, we have an IIndex, and a
defaultTransitiveQueriesFactory, implementing ITransitiveQueriesFactory, that
switches subjects and objects as described above.

    >>> from zc.relationship import interfaces
    >>> from zope.interface.verify import verifyObject
    >>> verifyObject(interfaces.IIndex, ix)
    True
    >>> verifyObject(
    ...     interfaces.ITransitiveQueriesFactory,
    ...     ix.defaultTransitiveQueriesFactory)
    True

For the purposes of a more complex example, though, we are going to exercise
more of the index's options--we'll use at least one of 'name', 'dump', 'load',
and 'btree'.

- 'subjects' and 'objects' will use a custom integer-based token generator.
  They will share tokens, which will let us use the default
  TransposingTransitiveQueriesFactory.  We can keep using the IFBTree sets,
  because the tokens are still integers.

- 'relationshiptype' will use a name 'reltype' and will just use the unicode
  value as the token, without translation but with a registration check.

- 'getContext' will use a name 'context' but will continue to use the intid
  utility and use the names from their interface.  We will see later that
  making transitive walks between different token sources must be handled with
  care.

We will also use the intid utility to resolve relationship tokens.  See the
relationship container (and container.rst) for examples of changing the
relationship type, especially in keyref.py.

Here are the methods we'll use for the 'subjects' and 'objects' tokens,
followed by the methods we'll use for the 'relationshiptypes' tokens.

    >>> lookup = {}
    >>> counter = [0]
    >>> prefix = '_z_token__'
    >>> def dump(obj, index, cache):
    ...     assert (interfaces.IIndex.providedBy(index) and
    ...             isinstance(cache, dict)), (
    ...         'did not receive correct arguments')
    ...     token = getattr(obj, prefix, None)
    ...     if token is None:
    ...         token = counter[0]
    ...         counter[0] += 1
    ...         if counter[0] >= 2147483647:
    ...             raise RuntimeError("Whoa!  That's a lot of ids!")
    ...         assert token not in lookup
    ...         setattr(obj, prefix, token)
    ...         lookup[token] = obj
    ...     return token
    ...
    >>> def load(token, index, cache):
    ...     assert (interfaces.IIndex.providedBy(index) and
    ...             isinstance(cache, dict)), (
    ...         'did not receive correct arguments')
    ...     return lookup[token]
    ...
    >>> relTypes = []
    >>> def relTypeDump(obj, index, cache):
    ...     assert obj in relTypes, 'unknown relationshiptype'
    ...     return obj
    ...
    >>> def relTypeLoad(token, index, cache):
    ...     assert token in relTypes, 'unknown relationshiptype'
    ...     return token
    ...

Note that these implementations are completely silly if we actually cared about
ZODB-based persistence: to even make it half-acceptable we should make the
counter, lookup, and and relTypes persistently stored somewhere using a
reasonable persistent data structure.  This is just a demonstration example.

Now we can make an index.

As in our initial example, we are going to use the simple transitive query
factory defined in the index module for our default transitive behavior: when
you want to do transitive searches, transpose 'subjects' with 'objects' and
keep everything else; and if both subjects and objects are provided, don't do
any transitive search.

    >>> from BTrees import OIBTree # could also be OOBTree
    >>> ix = index.Index(
    ...     ({'element': IRelationship['subjects'], 'multiple': True,
    ...       'dump': dump, 'load': load},
    ...      {'element': IRelationship['relationshiptype'],
    ...       'dump': relTypeDump, 'load': relTypeLoad, 'btree': OIBTree,
    ...       'name': 'reltype'},
    ...      {'element': IRelationship['objects'], 'multiple': True,
    ...       'dump': dump, 'load': load},
    ...      {'element': IContextAwareRelationship['getContext'],
    ...       'name': 'context'}),
    ...     index.TransposingTransitiveQueriesFactory('subjects', 'objects'))

We'll want to put the index somewhere in the system so it can find the intid
utility.  We'll add it as a utility just as part of the example.  As long as
the index has a valid __parent__ that is itself connected transitively to a
site manager with the desired intid utility, everything should work fine, so
no need to install it as utility.  This is just an example.

    >>> from zope import interface
    >>> sm = app.getSiteManager()
    >>> sm['rel_index'] = ix
    >>> import zope.component.interfaces
    >>> registry = zope.component.interfaces.IComponentRegistry(sm)
    >>> registry.registerUtility(ix, interfaces.IIndex)
    >>> import transaction
    >>> transaction.commit()

Now we'll create some representative objects that we can relate, and create
and index our first example relationship.

In the example, note that the context will only be available as an adapter to
ISpecialRelationship objects: the index tries to adapt objects to the
appropriate interface, and considers the value to be empty if it cannot adapt.

    >>> import persistent
    >>> from zope.app.container.contained import Contained
    >>> class Base(persistent.Persistent, Contained):
    ...     def __init__(self, name):
    ...         self.name = name
    ...     def __repr__(self):
    ...         return '<%s %r>' % (self.__class__.__name__, self.name)
    ...
    >>> class Person(Base): pass
    ...
    >>> class Role(Base): pass
    ...
    >>> class Project(Base): pass
    ...
    >>> class Company(Base): pass
    ...
    >>> @interface.implementer(IRelationship)
    ... class Relationship(persistent.Persistent, Contained):
    ...     def __init__(self, subjects, relationshiptype, objects):
    ...         self.subjects = subjects
    ...         assert relationshiptype in relTypes
    ...         self.relationshiptype = relationshiptype
    ...         self.objects = objects
    ...     def __repr__(self):
    ...         return '<%r %s %r>' % (
    ...             self.subjects, self.relationshiptype, self.objects)
    ...
    >>> class ISpecialRelationship(interface.Interface):
    ...     pass
    ...
    >>> from zope import component
    >>> @component.adapter(ISpecialRelationship)
    ... @interface.implementer(IContextAwareRelationship)
    ... class ContextRelationshipAdapter(object):
    ...     def __init__(self, adapted):
    ...         self.adapted = adapted
    ...     def getContext(self):
    ...         return getattr(self.adapted, '_z_context__', None)
    ...     def setContext(self, value):
    ...         self.adapted._z_context__ = value
    ...     def __getattr__(self, name):
    ...         return getattr(self.adapted, name)
    ...
    >>> component.provideAdapter(ContextRelationshipAdapter)
    >>> @interface.implementer(ISpecialRelationship)
    ... class SpecialRelationship(Relationship):
    ...     pass
    ...
    >>> people = {}
    >>> for p in ['Abe', 'Bran', 'Cathy', 'David', 'Emily', 'Fred', 'Gary',
    ...           'Heather', 'Ingrid', 'Jim', 'Karyn', 'Lee', 'Mary',
    ...           'Nancy', 'Olaf', 'Perry', 'Quince', 'Rob', 'Sam', 'Terry',
    ...           'Uther', 'Van', 'Warren', 'Xen', 'Ygritte', 'Zane']:
    ...     app[p] = people[p] = Person(p)
    ...
    >>> relTypes.extend(
    ...     ['has the role of', 'manages', 'taught', 'commissioned'])
    >>> roles = {}
    >>> for r in ['Project Manager', 'Software Engineer', 'Designer',
    ...           'Systems Administrator', 'Team Leader', 'Mascot']:
    ...     app[r] = roles[r] = Role(r)
    ...
    >>> projects = {}
    >>> for p in ['zope.org redesign', 'Zope 3 manual',
    ...           'improved test coverage', 'Vault design and implementation']:
    ...     app[p] = projects[p] = Project(p)
    ...
    >>> companies = {}
    >>> for c in ['Ynod Corporation', 'HAL, Inc.', 'Zookd']:
    ...     app[c] = companies[c] = Company(c)
    ...

    >>> app['fredisprojectmanager'] = rel = SpecialRelationship(
    ...     (people['Fred'],), 'has the role of', (roles['Project Manager'],))
    >>> IContextAwareRelationship(rel).setContext(
    ...     projects['zope.org redesign'])
    >>> ix.index(rel)
    >>> transaction.commit()

Token conversion
================

Before we examine the searching features, we should quickly discuss the
tokenizing API on the index.  All search queries must use value tokens, and
search results can sometimes be value or relationship tokens.  Therefore
converting between tokens and real values can be important.  The index
provides a number of conversion methods for this purpose.

Arguably the most important is `tokenizeQuery`: it takes a query, in which
each key and value are the name of an indexed value and an actual value,
respectively; and returns a query in which the actual values have been
converted to tokens.  For instance, consider the following example.  It's a
bit hard to show the conversion reliably (we can't know what the intid tokens
will be, for instance) so we just show that the result's values are tokenized
versions of the inputs.

    >>> res = ix.tokenizeQuery(
    ...     {'objects': roles['Project Manager'],
    ...      'context': projects['zope.org redesign']})
    >>> res['objects'] == dump(roles['Project Manager'], ix, {})
    True
    >>> from zope.app.intid.interfaces import IIntIds
    >>> intids = component.getUtility(IIntIds, context=ix)
    >>> res['context'] == intids.getId(projects['zope.org redesign'])
    True

Tokenized queries can be resolved to values again using resolveQuery.

    >>> sorted(ix.resolveQuery(res).items()) # doctest: +NORMALIZE_WHITESPACE
    [('context', <Project 'zope.org redesign'>),
     ('objects', <Role 'Project Manager'>)]

Other useful conversions are `tokenizeValues`, which returns an iterable of
tokens for the values of the given index name;

    >>> examples = (people['Abe'], people['Bran'], people['Cathy'])
    >>> res = list(ix.tokenizeValues(examples, 'subjects'))
    >>> res == [dump(o, ix, {}) for o in examples]
    True

`resolveValueTokens`, which returns an iterable of values for the tokens of
the given index name;

    >>> list(ix.resolveValueTokens(res, 'subjects'))
    [<Person 'Abe'>, <Person 'Bran'>, <Person 'Cathy'>]

`tokenizeRelationship`, which returns a token for the given relationship;

    >>> res = ix.tokenizeRelationship(rel)
    >>> res == intids.getId(rel)
    True

`resolveRelationshipToken`, which returns a relationship for the given token;

    >>> ix.resolveRelationshipToken(res) is rel
    True

`tokenizeRelationships`, which returns an iterable of tokens for the relations
given; and

    >>> app['another_rel'] = another_rel = Relationship(
    ...     (companies['Ynod Corporation'],), 'commissioned',
    ...     (projects['Vault design and implementation'],))
    >>> res = list(ix.tokenizeRelationships((another_rel, rel)))
    >>> res == [intids.getId(r) for r in (another_rel, rel)]
    True

`resolveRelationshipTokens`, which returns an iterable of relations for the
tokens given.

    >>> list(ix.resolveRelationshipTokens(res)) == [another_rel, rel]
    True

Basic searching
===============

Now we move to the meat of the interface: searching.  The index interface
defines several searching methods:

- `findValues` and `findValueTokens` ask "to what is this related?";

- `findRelationshipChains` and `findRelationshipTokenChains` ask "how is this
  related?", especially for transitive searches;

- `isLinked` asks "does a relationship like this exist?";

- `findRelationshipTokenSet` asks "what are the intransitive relationships
  that match my query?" and is particularly useful for low-level usage of the
  index data structures;

- `findRelationships` asks the same question, but returns an iterable of
  relationships rather than a set of tokens;

- `findValueTokenSet` asks "what are the value tokens for this particular
  indexed name and this relationship token?" and is useful for low-level
  usage of the index data structures such as transitive query factories; and

- the standard zope.index method `apply` essentially exposes the
  `findRelationshipTokenSet` and `findValueTokens` methods via a query object
  spelling.

`findRelationshipChains` and `findRelationshipTokenChains` are paired methods,
doing the same work but with and without resolving the resulting tokens; and
`findValues` and `findValueTokens` are also paired in the same way.

It is very important to note that all queries must use tokens, not actual
objects.  As introduced above, the index provides a method to ease that
requirement, in the form of a `tokenizeQuery` method that converts a dict with
objects to a dict with tokens.  You'll see below that we shorten our calls by
stashing `tokenizeQuery` away in the 'q' name.

    >>> q = ix.tokenizeQuery

We have indexed our first example relationship--"Fred has the role of project
manager in the zope.org redesign"--so we can search for it.  We'll first look
at `findValues` and `findValueTokens`.  Here, we ask 'who has the role of
project manager in the zope.org redesign?'.  We do it first with findValues
and then with findValueTokens [#findValue_errors]_.

.. [#findValue_errors] `findValueTokens` and `findValues` raise errors if
    you try to get a value that is not indexed.

    >>> list(ix.findValues(
    ...     'folks',
    ...     q({'reltype': 'has the role of',
    ...       'objects': roles['Project Manager'],
    ...       'context': projects['zope.org redesign']})))
    Traceback (most recent call last):
    ...
    ValueError: ('name not indexed', 'folks')

    >>> list(ix.findValueTokens(
    ...     'folks',
    ...     q({'reltype': 'has the role of',
    ...       'objects': roles['Project Manager'],
    ...       'context': projects['zope.org redesign']})))
    Traceback (most recent call last):
    ...
    ValueError: ('name not indexed', 'folks')

    >>> list(ix.findValues(
    ...     'subjects',
    ...     q({'reltype': 'has the role of',
    ...       'objects': roles['Project Manager'],
    ...       'context': projects['zope.org redesign']})))
    [<Person 'Fred'>]

    >>> [load(t, ix, {}) for t in ix.findValueTokens(
    ...     'subjects',
    ...     q({'reltype': 'has the role of',
    ...       'objects': roles['Project Manager'],
    ...       'context': projects['zope.org redesign']}))]
    [<Person 'Fred'>]

If you don't pass a query to these methods, you get all indexed values for the
given name in a BTree (don't modify this!  this is an internal data structure--
we pass it out directly because you can do efficient things with it with BTree
set operations).  In this case, we've only indexed a single relationship,
so its subjects are the subjects in this result.

    >>> res = ix.findValueTokens('subjects', maxDepth=1)
    >>> res # doctest: +ELLIPSIS
    <BTrees.IOBTree.IOBTree object at ...>
    >>> [load(t, ix, {}) for t in res]
    [<Person 'Fred'>]

If we want to find all the relationships for which Fred is a subject, we can
use `findRelationshipTokenSet`.  It, combined with `findValueTokenSet`, is
useful for querying the index data structures at a fairly low level, when you
want to use the data in a way that the other search methods don't support.

`findRelationshipTokenSet`, given a single dictionary of {indexName: token},
returns a set (based on the btree family for relationships in the index) of
relationship tokens that match it, intransitively.

    >>> res = ix.findRelationshipTokenSet(q({'subjects': people['Fred']}))
    >>> res # doctest: +ELLIPSIS
    <BTrees.IFBTree.IFTreeSet object at ...>
    >>> [intids.getObject(t) for t in res]
    [<(<Person 'Fred'>,) has the role of (<Role 'Project Manager'>,)>]

It is in fact equivalent to `findRelationshipTokens` called without
transitivity and without any filtering.

    >>> res2 = ix.findRelationshipTokens(
    ...     q({'subjects': people['Fred']}), maxDepth=1)
    >>> res2 is res
    True

The `findRelationshipTokenSet` method always returns a set, even if the
query does not have any results.

    >>> res = ix.findRelationshipTokenSet(q({'subjects': people['Ygritte']}))
    >>> res # doctest: +ELLIPSIS
    <BTrees.IFBTree.IFTreeSet object at ...>
    >>> list(res)
    []

An empty query returns all relationships in the index (this is true of other
search methods as well).

    >>> res = ix.findRelationshipTokenSet({})
    >>> res # doctest: +ELLIPSIS
    <BTrees.IFBTree.IFTreeSet object at ...>
    >>> len(res) == ix.documentCount()
    True
    >>> for r in ix.resolveRelationshipTokens(res):
    ...     if r not in ix:
    ...         print('oops')
    ...         break
    ... else:
    ...     print('correct')
    ...
    correct

`findRelationships` can do the same thing but with resolving the relationships.

    >>> list(ix.findRelationships(q({'subjects': people['Fred']})))
    [<(<Person 'Fred'>,) has the role of (<Role 'Project Manager'>,)>]

However, like `findRelationshipTokens` and unlike
`findRelationshipTokenSet`, `findRelationships` can be used
transitively, as shown in the introductory section of this document.

`findValueTokenSet`, given a relationship token and a value name, returns a
set (based on the btree family for the value) of value tokens for that
relationship.

    >>> src = ix.findRelationshipTokenSet(q({'subjects': people['Fred']}))

    >>> res = ix.findValueTokenSet(list(src)[0], 'subjects')
    >>> res # doctest: +ELLIPSIS
    <BTrees.IFBTree.IFTreeSet object at ...>
    >>> [load(t, ix, {}) for t in res]
    [<Person 'Fred'>]

Like `findRelationshipTokenSet` and `findRelationshipTokens`,
`findValueTokenSet` is equivalent to `findValueTokens` without a
transitive search or filtering.

    >>> res2 = ix.findValueTokenSet(list(src)[0], 'subjects')
    >>> res2 is res
    True

The apply method, part of the zope.index.interfaces.IIndexSearch interface,
can essentially only duplicate the `findValueTokens` and
`findRelationshipTokenSet` search calls.  The only additional functionality
is that the results always are IFBTree sets: if the tokens requested are not
in an IFBTree set (on the basis of the 'btree' key during instantiation, for
instance) then the index raises a ValueError.  A wrapper dict specifies the
type of search with the key, and the value should be the arguments for the
search.

Here, we ask for the current known roles on the zope.org redesign.

    >>> res = ix.apply({'values':
    ...     {'resultName': 'objects', 'query':
    ...         q({'reltype': 'has the role of',
    ...            'context': projects['zope.org redesign']})}})
    >>> res # doctest: +ELLIPSIS
    IFSet([...])
    >>> [load(t, ix, {}) for t in res]
    [<Role 'Project Manager'>]

Ideally, this would fail, because the tokens, while integers, are not actually
mergable with a intid-based catalog results.  However, the index only complains
if it can tell that the returning set is not an IFTreeSet or IFSet.

Here, we ask for the relationships that have the 'has the role of' type.

    >>> res = ix.apply({'relationships':
    ...     q({'reltype': 'has the role of'})})
    >>> res # doctest: +ELLIPSIS
    <BTrees.IFBTree.IFTreeSet object at ...>
    >>> [intids.getObject(t) for t in res]
    [<(<Person 'Fred'>,) has the role of (<Role 'Project Manager'>,)>]

Here, we ask for the known relationships types for the zope.org redesign.  It
will fail, because the result cannot be expressed as an IFBTree.IFTreeSet.

    >>> res = ix.apply({'values':
    ...     {'resultName': 'reltype', 'query':
    ...         q({'context': projects['zope.org redesign']})}})
    ... # doctest: +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
    ...
    ValueError: cannot fulfill `apply` interface because cannot return an
                (I|L)FBTree-based result

The same kind of error will be raised if you request relationships and the
relationships are not stored in IFBTree or LFBTree structures [#apply_errors]_.

.. [#apply_errors] Only one key may be in the dictionary.

    >>> res = ix.apply({'values':
    ...     {'resultName': 'objects', 'query':
    ...         q({'reltype': 'has the role of',
    ...            'context': projects['zope.org redesign']})},
    ...     'relationships': q({'reltype': 'has the role of'})})
    Traceback (most recent call last):
    ...
    ValueError: one key in the primary query dictionary

    The keys must be one of 'values' or 'relationships'.

    >>> res = ix.apply({'kumquats':
    ...     {'resultName': 'objects', 'query':
    ...         q({'reltype': 'has the role of',
    ...            'context': projects['zope.org redesign']})}})
    Traceback (most recent call last):
    ...
    ValueError: ('unknown query type', 'kumquats')

    If a relationship uses LFBTrees, searches are fine.

    >>> ix2 = index.Index( # explicit 64 bit
    ...     ({'element': IRelationship['subjects'], 'multiple': True},
    ...      IRelationship['relationshiptype'],
    ...      {'element': IRelationship['objects'], 'multiple': True},
    ...      IContextAwareRelationship['getContext']),
    ...     index.TransposingTransitiveQueriesFactory('subjects', 'objects'),
    ...     family=BTrees.family64)

    >>> list(ix2.apply({'values':
    ...     {'resultName': 'objects', 'query':
    ...         q({'subjects': people['Gary']})}}))
    []

    >>> list(ix2.apply({'relationships':
    ...     q({'subjects': people['Gary']})}))
    []

    But, as with shown in the main text for values, if you are using another
    BTree module for relationships, you'll get an error.

    >>> ix2 = index.Index( # explicit 64 bit
    ...     ({'element': IRelationship['subjects'], 'multiple': True},
    ...      IRelationship['relationshiptype'],
    ...      {'element': IRelationship['objects'], 'multiple': True},
    ...      IContextAwareRelationship['getContext']),
    ...     index.TransposingTransitiveQueriesFactory('subjects', 'objects'),
    ...     relFamily=BTrees.OIBTree)

    >>> list(ix2.apply({'relationships':
    ...     q({'subjects': people['Gary']})}))
    Traceback (most recent call last):
    ...
    ValueError: cannot fulfill `apply` interface because cannot return an (I|L)FBTree-based result

The last basic search methods, `isLinked`, `findRelationshipTokenChains`, and
`findRelationshipChains`, are most useful for transitive searches.  We
have not yet created any relationships that we can use transitively.  They
still will work with intransitive searches, so we will demonstrate them here
as an introduction, then discuss them more below when we introduce transitive
relationships.

`findRelationshipChains` and `findRelationshipTokenChains` let you find
transitive relationship paths. Right now a single relationship--a single
point--can't create much of a line. So first, here's a somewhat useless
example:

    >>> [[intids.getObject(t) for t in path] for path in
    ...  ix.findRelationshipTokenChains(
    ...     q({'reltype': 'has the role of'}))]
    ... # doctest: +NORMALIZE_WHITESPACE
    [[<(<Person 'Fred'>,) has the role of (<Role 'Project Manager'>,)>]]

That's useless, because there's no chance of it being a transitive search, and
so you might as well use findRelationshipTokenSet.  This will become more
interesting later on.

Here's the same example with findRelationshipChains, which resolves the
relationship tokens itself.

    >>> list(ix.findRelationshipChains(q({'reltype': 'has the role of'})))
    ... # doctest: +NORMALIZE_WHITESPACE
    [(<(<Person 'Fred'>,) has the role of (<Role 'Project Manager'>,)>,)]

`isLinked` returns a boolean if there is at least one path that matches the
search--in fact, the implementation is essentially ::

    try:
        iter(ix.findRelationshipTokenChains(...args...)).next()
    except StopIteration:
        return False
    else:
        return True

So, we can say

    >>> ix.isLinked(q({'subjects': people['Fred']}))
    True
    >>> ix.isLinked(q({'subjects': people['Gary']}))
    False
    >>> ix.isLinked(q({'subjects': people['Fred'],
    ...                'reltype': 'manages'}))
    False

This is reasonably useful as is, to test basic assertions.  It also works with
transitive searches, as we will see below.


An even simpler example
-----------------------

(This was added to test that searching for a simple relationship works
even when the transitive query factory is not set.)

Let's create a very simple relation type, using strings as the source
and target types:

  >>> class IStringRelation(interface.Interface):
  ...     name = interface.Attribute("The name of the value.")
  ...     value = interface.Attribute("The value associated with the name.")

  >>> @interface.implementer(IStringRelation)
  ... class StringRelation(persistent.Persistent, Contained):
  ...
  ...     def __init__(self, name, value):
  ...         self.name = name
  ...         self.value = value

  >>> app[u"string-relation-1"] = StringRelation("name1", "value1")
  >>> app[u"string-relation-2"] = StringRelation("name2", "value2")

  >>> transaction.commit()

We can now create an index that uses these:

  >>> from BTrees import OOBTree

  >>> sx = index.Index(
  ...     ({"element": IStringRelation["name"],
  ...       "load": None, "dump": None, "btree": OOBTree},
  ...      {"element": IStringRelation["value"],
  ...       "load": None, "dump": None, "btree": OOBTree},
  ...      ))

  >>> app["sx"] = sx
  >>> transaction.commit()

And we'll add the relations to the index:

  >>> app["sx"].index(app["string-relation-1"])
  >>> app["sx"].index(app["string-relation-2"])

Getting a relationship back out should be very simple.  Let's look for
all the values associates with "name1":

  >>> query = sx.tokenizeQuery({"name": "name1"})
  >>> list(sx.findValues("value", query))
  ['value1']



Searching for empty sets
------------------------

We've examined the most basic search capabilities.  One other feature of the
index and search is that one can search for relationships to an empty set, or,
for single-value relationships like 'reltype' and 'context' in our
examples, None.

Let's add a relationship with a 'manages' relationshiptype, and no context; and
a relationship with a 'commissioned' relationship type, and a company context.

Notice that there are two ways of adding indexes, by the way.  We have already
seen that the index has an 'index' method that takes a relationship.  Here we
use 'index_doc' which is a method defined in zope.index.interfaces.IInjection
that requires the token to already be generated.  Since we are using intids
to tokenize the relationships, we must add them to the ZODB app object to give
them the possibility of a connection.

    >>> app['abeAndBran'] = rel = Relationship(
    ...     (people['Abe'],), 'manages', (people['Bran'],))
    >>> ix.index_doc(intids.register(rel), rel)
    >>> app['abeAndVault'] = rel = SpecialRelationship(
    ...     (people['Abe'],), 'commissioned',
    ...     (projects['Vault design and implementation'],))
    >>> IContextAwareRelationship(rel).setContext(companies['Zookd'])
    >>> ix.index_doc(intids.register(rel), rel)

Now we can search for Abe's relationship that does not have a context.  The
None value is always used to match both an empty set and a single `None` value.
The index does not support any other "empty" values at this time.

    >>> sorted(
    ...     repr(load(t, ix, {})) for t in ix.findValueTokens(
    ...         'objects',
    ...         q({'subjects': people['Abe']})))
    ["<Person 'Bran'>", "<Project 'Vault design and implementation'>"]
    >>> [load(t, ix, {}) for t in ix.findValueTokens(
    ...     'objects', q({'subjects': people['Abe'], 'context': None}))]
    [<Person 'Bran'>]
    >>> sorted(
    ...     repr(v) for v in ix.findValues(
    ...         'objects',
    ...         q({'subjects': people['Abe']})))
    ["<Person 'Bran'>", "<Project 'Vault design and implementation'>"]
    >>> list(ix.findValues(
    ...     'objects', q({'subjects': people['Abe'], 'context': None})))
    [<Person 'Bran'>]

Note that the index does not currently support searching for relationships that
have any value, or one of a set of values.  This may be added at a later date;
the spelling for such queries are among the more troublesome parts.

Working with transitive searches
================================

It's possible to do transitive searches as well.  This can let you find all
transitive bosses, or transitive subordinates, in our 'manages' relationship
type.  Let's set up some example relationships.  Using letters to represent our
people, we'll create three hierarchies like this::

        A        JK           R
       / \      /  \
      B   C    LM   NOP     S T U
     / \  |     |          /| |  \
    D  E  F     Q         V W X   |
    |     |                    \--Y
    H     G                       |
    |                             Z
    I

This means that, for instance, person "A" ("Abe") manages "B" ("Bran") and "C"
("Cathy").

We already have a relationship from Abe to Bran, so we'll only be adding the
rest.

    >>> relmap = (
    ...     ('A', 'C'), ('B', 'D'), ('B', 'E'), ('C', 'F'),
    ...     ('F', 'G'), ('D', 'H'), ('H', 'I'), ('JK', 'LM'), ('JK', 'NOP'),
    ...     ('LM', 'Q'), ('R', 'STU'), ('S', 'VW'), ('T', 'X'), ('UX', 'Y'),
    ...     ('Y', 'Z'))
    >>> letters = dict((name[0], ob) for name, ob in people.items())
    >>> for subs, obs in relmap:
    ...     subs = tuple(letters[l] for l in subs)
    ...     obs = tuple(letters[l] for l in obs)
    ...     app['%sManages%s' % (''.join(o.name for o in subs),
    ...                          ''.join(o.name for o in obs))] = rel = (
    ...         Relationship(subs, 'manages', obs))
    ...     ix.index(rel)
    ...

Now we can do both transitive and intransitive searches.  Here are a few
examples.

    >>> [load(t, ix, {}) for t in ix.findValueTokens(
    ...     'subjects',
    ...     q({'objects': people['Ingrid'],
    ...        'reltype': 'manages'}))
    ...     ]
    [<Person 'Heather'>, <Person 'David'>, <Person 'Bran'>, <Person 'Abe'>]

Here's the same thing using findValues.

    >>> list(ix.findValues(
    ...     'subjects',
    ...     q({'objects': people['Ingrid'],
    ...        'reltype': 'manages'})))
    [<Person 'Heather'>, <Person 'David'>, <Person 'Bran'>, <Person 'Abe'>]

Notice that they are in order, walking away from the search start.  It also
is breadth-first--for instance, look at the list of superiors to Zane: Xen and
Uther come before Rob and Terry.

    >>> res = list(ix.findValues(
    ...     'subjects',
    ...     q({'objects': people['Zane'], 'reltype': 'manages'})))
    >>> res[0]
    <Person 'Ygritte'>
    >>> sorted(repr(p) for p in res[1:3])
    ["<Person 'Uther'>", "<Person 'Xen'>"]
    >>> sorted(repr(p) for p in res[3:])
    ["<Person 'Rob'>", "<Person 'Terry'>"]

Notice that all the elements of the search are maintained as it is walked--only
the transposed values are changed, and the rest remain statically.  For
instance, notice the difference between these two results.

    >>> [load(t, ix, {}) for t in ix.findValueTokens(
    ...     'objects',
    ...     q({'subjects': people['Cathy'], 'reltype': 'manages'}))]
    [<Person 'Fred'>, <Person 'Gary'>]
    >>> res = [load(t, ix, {}) for t in ix.findValueTokens(
    ...     'objects',
    ...     q({'subjects': people['Cathy']}))]
    >>> res[0]
    <Person 'Fred'>
    >>> sorted(repr(i) for i in res[1:])
    ["<Person 'Gary'>", "<Role 'Project Manager'>"]

The first search got what we expected for our management relationshiptype--
walking from Cathy, the relationshiptype was maintained, and we only got the
Gary subordinate.  The second search didn't specify the relationshiptype, so
the transitive search included the Role we added first (Fred has the role of
Project Manager for the zope.org redesign).

The `maxDepth` argument allows control over how far to search.  For instance,
if we only want to search for Bran's subordinates a maximum of two steps deep,
we can do so:

    >>> res = [load(t, ix, {}) for t in ix.findValueTokens(
    ...     'objects',
    ...     q({'subjects': people['Bran']}),
    ...     maxDepth=2)]
    >>> sorted(repr(i) for i in res)
    ["<Person 'David'>", "<Person 'Emily'>", "<Person 'Heather'>"]

The same is true for findValues.

    >>> res = list(ix.findValues(
    ...     'objects',
    ...     q({'subjects': people['Bran']}), maxDepth=2))
    >>> sorted(repr(i) for i in res)
    ["<Person 'David'>", "<Person 'Emily'>", "<Person 'Heather'>"]

A minimum depth--a number of relationships that must be traversed before
results are desired--can also be achieved trivially using the targetFilter
argument described soon below.  For now, we will continue in the order of the
arguments list, so `filter` is up next.

The `filter` argument takes an object (such as a function) that provides
interfaces.IFilter.  As the interface lists, it receives the current chain
of relationship tokens ("relchain"), the original query that started the search
("query"), the index object ("index"), and a dictionary that will be used
throughout the search and then discarded that can be used for optimizations
("cache").  It should return a boolean, which determines whether the given
relchain should be used at all--traversed or returned.  For instance, if
security dictates that the current user can only see certain relationships,
the filter could be used to make only the available relationships traversable.
Other uses are only getting relationships that were created after a given time,
or that have some annotation (available after resolving the token).

Let's look at an example of a filter that only allows relationships in a given
set, the way a security-based filter might work.  We'll then use it to model
a situation in which the current user can't see that Ygritte is managed by
Uther, in addition to Xen.

    >>> s = set(intids.getId(r) for r in app.values()
    ...         if IRelationship.providedBy(r))
    >>> relset = list(
    ...     ix.findRelationshipTokenSet(q({'subjects': people['Xen']})))
    >>> len(relset)
    1
    >>> s.remove(relset[0])
    >>> dump(people['Uther'], ix, {}) in list(
    ...     ix.findValueTokens('subjects', q({'objects': people['Ygritte']})))
    True
    >>> dump(people['Uther'], ix, {}) in list(ix.findValueTokens(
    ...     'subjects', q({'objects': people['Ygritte']}),
    ...     filter=lambda relchain, query, index, cache: relchain[-1] in s))
    False
    >>> people['Uther'] in list(
    ...     ix.findValues('subjects', q({'objects': people['Ygritte']})))
    True
    >>> people['Uther'] in list(ix.findValues(
    ...     'subjects', q({'objects': people['Ygritte']}),
    ...     filter=lambda relchain, query, index, cache: relchain[-1] in s))
    False

The next two search arguments are the targetQuery and the targetFilter.  They
both are filters on the output of the search methods, while not affecting the
traversal/search process.  The targetQuery takes a query identical to the main
query, and the targetFilter takes an IFilter identical to the one used by the
`filter` argument.  The targetFilter can do all of the work of the targetQuery,
but the targetQuery makes a common case--wanting to find the paths between two
objects, or if two objects are linked at all, for instance--convenient.

We'll skip over targetQuery for a moment (we'll return when we revisit
`findRelationshipChains` and `isLinked`), and look at targetFilter.
targetFilter can be used for many tasks, such as only returning values that
are in specially annotated relationships, or only returning values that have
traversed a certain hinge relationship in a two-part search, or other tasks.
A very simple one, though, is to effectively specify a minimum traversal depth.
Here, we find the people who are precisely two steps down from Bran, no more
and no less.  We do it twice, once with findValueTokens and once with
findValues.

    >>> [load(t, ix, {}) for t in ix.findValueTokens(
    ...     'objects', q({'subjects': people['Bran']}), maxDepth=2,
    ...     targetFilter=lambda relchain, q, i, c: len(relchain)>=2)]
    [<Person 'Heather'>]
    >>> list(ix.findValues(
    ...     'objects', q({'subjects': people['Bran']}), maxDepth=2,
    ...     targetFilter=lambda relchain, q, i, c: len(relchain)>=2))
    [<Person 'Heather'>]

Heather is the only person precisely two steps down from Bran.

Notice that we specified both maxDepth and targetFilter.  We could have
received the same output by specifying a targetFilter of `len(relchain)==2`
and no maxDepth, but there is an important difference in efficiency.  maxDepth
and filter can reduce the amount of work done by the index because they can
stop searching after reaching the maxDepth, or failing the filter; the
targetFilter and targetQuery arguments simply hide the results obtained, which
can reduce a bit of work in the case of getValues but generally don't reduce
any of the traversal work.

The last argument to the search methods is `transitiveQueriesFactory`.  It is
a powertool that replaces the index's default traversal factory for the
duration of the search.  This allows custom traversal for individual searches,
and can support a number of advanced use cases.  For instance, our index
assumes that you want to traverse objects and sources, and that the context
should be constant; that may not always be the desired traversal behavior.  If
we had a relationship of PERSON1 TAUGHT PERSON2 (the lessons of PERSON3) then
to find the teachers of any given person you might want to traverse PERSON1,
but sometimes you might want to traverse PERSON3 as well.  You can change the
behavior by providing a different factory.

To show this example we will need to add a few more relationships.  We will say
that Mary teaches Rob the lessons of Abe; Olaf teaches Zane the lessons of
Bran; Cathy teaches Bran the lessons of Lee; David teaches Abe the lessons of
Zane; and Emily teaches Mary the lessons of Ygritte.

In the diagram, left-hand lines indicate "taught" and right-hand lines indicate
"the lessons of", so ::

  E   Y
   \ /
    M

should be read as "Emily taught Mary the lessons of Ygritte".  Here's the full
diagram::

            C   L
             \ /
          O   B
           \ /
  E   Y D   Z
   \ /   \ /
    M     A
     \   /
      \ /
       R

You can see then that the transitive path of Rob's teachers is Mary and Emily,
but the transitive path of Rob's lessons is Abe, Zane, Bran, and Lee.

Transitive queries factories must do extra work when the transitive walk is
across token types.  We have used the TransposingTransitiveQueriesFactory to
build our transposers before, but now we need to write a custom one that
translates the tokens (ooh!  a
TokenTranslatingTransposingTransitiveQueriesFactory!  ...maybe we won't go that
far...).

We will add the relationships, build the custom transitive factory, and then
again do the search work twice, once with findValueTokens and once with
findValues.

    >>> for triple in ('EMY', 'MRA', 'DAZ', 'OZB', 'CBL'):
    ...     teacher, student, source = (letters[l] for l in triple)
    ...     rel = SpecialRelationship((teacher,), 'taught', (student,))
    ...     app['%sTaught%sTo%s' % (
    ...         teacher.name, source.name, student.name)] = rel
    ...     IContextAwareRelationship(rel).setContext(source)
    ...     ix.index_doc(intids.register(rel), rel)
    ...

    >>> def transitiveFactory(relchain, query, index, cache):
    ...     dynamic = cache.get('dynamic')
    ...     if dynamic is None:
    ...         intids = cache['intids'] = component.getUtility(
    ...             IIntIds, context=index)
    ...         static = cache['static'] = {}
    ...         dynamic = cache['dynamic'] = []
    ...         names = ['objects', 'context']
    ...         for nm, val in query.items():
    ...             try:
    ...                 ix = names.index(nm)
    ...             except ValueError:
    ...                 static[nm] = val
    ...             else:
    ...                 if dynamic:
    ...                     # both were specified: no transitive search known.
    ...                     del dynamic[:]
    ...                     cache['intids'] = False
    ...                     break
    ...                 else:
    ...                     dynamic.append(nm)
    ...                     dynamic.append(names[not ix])
    ...         else:
    ...             intids = component.getUtility(IIntIds, context=index)
    ...             if dynamic[0] == 'objects':
    ...                 def translate(t):
    ...                     return dump(intids.getObject(t), index, cache)
    ...             else:
    ...                 def translate(t):
    ...                     return intids.register(load(t, index, cache))
    ...             cache['translate'] = translate
    ...     else:
    ...         static = cache['static']
    ...         translate = cache['translate']
    ...     if dynamic:
    ...         for r in index.findValueTokenSet(relchain[-1], dynamic[1]):
    ...             res = {dynamic[0]: translate(r)}
    ...             res.update(static)
    ...             yield res

    >>> [load(t, ix, {}) for t in ix.findValueTokens(
    ...     'subjects',
    ...     q({'objects': people['Rob'], 'reltype': 'taught'}))]
    [<Person 'Mary'>, <Person 'Emily'>]
    >>> [intids.getObject(t) for t in ix.findValueTokens(
    ...     'context',
    ...     q({'objects': people['Rob'], 'reltype': 'taught'}),
    ...     transitiveQueriesFactory=transitiveFactory)]
    [<Person 'Abe'>, <Person 'Zane'>, <Person 'Bran'>, <Person 'Lee'>]

    >>> list(ix.findValues(
    ...     'subjects',
    ...     q({'objects': people['Rob'], 'reltype': 'taught'})))
    [<Person 'Mary'>, <Person 'Emily'>]
    >>> list(ix.findValues(
    ...     'context',
    ...     q({'objects': people['Rob'], 'reltype': 'taught'}),
    ...     transitiveQueriesFactory=transitiveFactory))
    [<Person 'Abe'>, <Person 'Zane'>, <Person 'Bran'>, <Person 'Lee'>]

transitiveQueryFactories can be very powerful, and we aren't finished talking
about them in this document: see "Transitively mapping multiple elements"
below.

We have now discussed, or at least mentioned, all of the available search
arguments.  The `apply` method's 'values' search has the same arguments and
features as `findValues`, so it can also do these transitive tricks.  Let's
get all of Karyn's subordinates.

    >>> res = ix.apply({'values':
    ...     {'resultName': 'objects', 'query':
    ...         q({'reltype': 'manages',
    ...           'subjects': people['Karyn']})}})
    >>> res # doctest: +ELLIPSIS
    IFSet([...])
    >>> sorted(repr(load(t, ix, {})) for t in res)
    ... # doctest: +NORMALIZE_WHITESPACE
    ["<Person 'Lee'>", "<Person 'Mary'>", "<Person 'Nancy'>",
     "<Person 'Olaf'>", "<Person 'Perry'>", "<Person 'Quince'>"]

As we return to `findRelationshipChains` and `findRelationshipTokenChains`, we
also return to the search argument we postponed above: targetQuery.

The `findRelationshipChains` and `findRelationshipTokenChains` can simply find
all paths:

    >>> res = [repr([intids.getObject(t) for t in path]) for path in
    ...  ix.findRelationshipTokenChains(
    ...     q({'reltype': 'manages', 'subjects': people['Jim']}
    ...     ))]
    >>> len(res)
    3
    >>> sorted(res[:2]) # doctest: +NORMALIZE_WHITESPACE
    ["[<(<Person 'Jim'>, <Person 'Karyn'>) manages
        (<Person 'Lee'>, <Person 'Mary'>)>]",
     "[<(<Person 'Jim'>, <Person 'Karyn'>) manages
        (<Person 'Nancy'>, <Person 'Olaf'>, <Person 'Perry'>)>]"]
    >>> res[2] # doctest: +NORMALIZE_WHITESPACE
    "[<(<Person 'Jim'>, <Person 'Karyn'>) manages
       (<Person 'Lee'>, <Person 'Mary'>)>,
      <(<Person 'Lee'>, <Person 'Mary'>) manages
       (<Person 'Quince'>,)>]"
    >>> res == [repr(list(p)) for p in
    ...  ix.findRelationshipChains(
    ...     q({'reltype': 'manages', 'subjects': people['Jim']}
    ...     ))]
    True

Like `findValues`, this is a breadth-first search.

If we use a targetQuery with `findRelationshipChains`, you can find all paths
between two searches. For instance, consider the paths between Rob and
Ygritte.  While a `findValues` search would only include Rob once if asked to
search for supervisors, there are two paths.  These can be found with the
targetQuery.

    >>> res = [repr([intids.getObject(t) for t in path]) for path in
    ...  ix.findRelationshipTokenChains(
    ...     q({'reltype': 'manages', 'subjects': people['Rob']}),
    ...     targetQuery=q({'objects': people['Ygritte']}))]
    >>> len(res)
    2
    >>> sorted(res[:2]) # doctest: +NORMALIZE_WHITESPACE
    ["[<(<Person 'Rob'>,) manages
        (<Person 'Sam'>, <Person 'Terry'>, <Person 'Uther'>)>,
       <(<Person 'Terry'>,) manages (<Person 'Xen'>,)>,
       <(<Person 'Uther'>, <Person 'Xen'>) manages (<Person 'Ygritte'>,)>]",
     "[<(<Person 'Rob'>,) manages
        (<Person 'Sam'>, <Person 'Terry'>, <Person 'Uther'>)>,
       <(<Person 'Uther'>, <Person 'Xen'>) manages (<Person 'Ygritte'>,)>]"]

Here's a query with no results:

    >>> len(list(ix.findRelationshipTokenChains(
    ...     q({'reltype': 'manages', 'subjects': people['Rob']}),
    ...     targetQuery=q({'objects': companies['Zookd']}))))
    0

You can combine targetQuery with targetFilter.  Here we arbitrarily say we
are looking for a path between Rob and Ygritte that is at least 3 links long.

    >>> res = [repr([intids.getObject(t) for t in path]) for path in
    ...  ix.findRelationshipTokenChains(
    ...     q({'reltype': 'manages', 'subjects': people['Rob']}),
    ...     targetQuery=q({'objects': people['Ygritte']}),
    ...     targetFilter=lambda relchain, q, i, c: len(relchain)>=3)]
    >>> len(res)
    1
    >>> res # doctest: +NORMALIZE_WHITESPACE
    ["[<(<Person 'Rob'>,) manages
        (<Person 'Sam'>, <Person 'Terry'>, <Person 'Uther'>)>,
       <(<Person 'Terry'>,) manages (<Person 'Xen'>,)>,
       <(<Person 'Uther'>, <Person 'Xen'>) manages (<Person 'Ygritte'>,)>]"]

`isLinked` takes the same arguments as all of the other transitive-aware
methods.  For instance, Rob and Ygritte are transitively linked, but Abe and
Zane are not.

    >>> ix.isLinked(
    ...     q({'reltype': 'manages', 'subjects': people['Rob']}),
    ...     targetQuery=q({'objects': people['Ygritte']}))
    True
    >>> ix.isLinked(
    ...     q({'reltype': 'manages', 'subjects': people['Abe']}),
    ...     targetQuery=q({'objects': people['Ygritte']}))
    False

Detecting cycles
----------------

Suppose we're modeling a 'king in disguise': someone high up in management also
works as a peon to see how his employees' lives are.  We could model this a
number of ways that might make more sense than what we'll do now, but to show
cycles at work we'll just add an additional relationship so that Abe works for
Gary.  That means that the very longest path from Ingrid up gets a lot longer--
in theory, it's infinitely long, because of the cycle.

The index keeps track of this and stops right when the cycle happens, and right
before the cycle duplicates any relationships.  It marks the chain that has
cycle as a special kind of tuple that implements ICircularRelationshipPath.
The tuple has a 'cycled' attribute that contains the one or more searches
that would be equivalent to following the cycle (given the same transitiveMap).

Let's actually look at the example we described.

    >>> res = list(ix.findRelationshipTokenChains(
    ...     q({'objects': people['Ingrid'], 'reltype': 'manages'})))
    >>> len(res)
    4
    >>> len(res[3])
    4
    >>> interfaces.ICircularRelationshipPath.providedBy(res[3])
    False
    >>> rel = Relationship(
    ...     (people['Gary'],), 'manages', (people['Abe'],))
    >>> app['GaryManagesAbe'] = rel
    >>> ix.index(rel)
    >>> res = list(ix.findRelationshipTokenChains(
    ...     q({'objects': people['Ingrid'], 'reltype': 'manages'})))
    >>> len(res)
    8
    >>> len(res[7])
    8
    >>> interfaces.ICircularRelationshipPath.providedBy(res[7])
    True
    >>> [sorted(ix.resolveQuery(search).items()) for search in res[7].cycled]
    [[('objects', <Person 'Abe'>), ('reltype', 'manages')]]
    >>> tuple(ix.resolveRelationshipTokens(res[7]))
    ... # doctest: +NORMALIZE_WHITESPACE
    (<(<Person 'Heather'>,) manages (<Person 'Ingrid'>,)>,
     <(<Person 'David'>,) manages (<Person 'Heather'>,)>,
     <(<Person 'Bran'>,) manages (<Person 'David'>,)>,
     <(<Person 'Abe'>,) manages (<Person 'Bran'>,)>,
     <(<Person 'Gary'>,) manages (<Person 'Abe'>,)>,
     <(<Person 'Fred'>,) manages (<Person 'Gary'>,)>,
     <(<Person 'Cathy'>,) manages (<Person 'Fred'>,)>,
     <(<Person 'Abe'>,) manages (<Person 'Cathy'>,)>)

The same kind of thing works for `findRelationshipChains`.  Notice that the
query in the .cycled attribute is not resolved: it is still the query that
would be needed to continue the cycle.

    >>> res = list(ix.findRelationshipChains(
    ...     q({'objects': people['Ingrid'], 'reltype': 'manages'})))
    >>> len(res)
    8
    >>> len(res[7])
    8
    >>> interfaces.ICircularRelationshipPath.providedBy(res[7])
    True
    >>> [sorted(ix.resolveQuery(search).items()) for search in res[7].cycled]
    [[('objects', <Person 'Abe'>), ('reltype', 'manages')]]
    >>> res[7] # doctest: +NORMALIZE_WHITESPACE
    cycle(<(<Person 'Heather'>,) manages (<Person 'Ingrid'>,)>,
          <(<Person 'David'>,) manages (<Person 'Heather'>,)>,
          <(<Person 'Bran'>,) manages (<Person 'David'>,)>,
          <(<Person 'Abe'>,) manages (<Person 'Bran'>,)>,
          <(<Person 'Gary'>,) manages (<Person 'Abe'>,)>,
          <(<Person 'Fred'>,) manages (<Person 'Gary'>,)>,
          <(<Person 'Cathy'>,) manages (<Person 'Fred'>,)>,
          <(<Person 'Abe'>,) manages (<Person 'Cathy'>,)>)

Notice that there is nothing special about the new relationship, by the way.
If we had started to look for Fred's supervisors, the cycle marker would have
been given for the relationship that points back to Fred as a supervisor to
himself.  There's no way for the computer to know which is the "cause" without
further help and policy.

Handling cycles can be tricky.  Now imagine that we have a cycle that involves
a relationship with two objects, only one of which causes the cycle.  The other
object should continue to be followed.

For instance, lets have Q manage L and Y.  The link to L will be a cycle, but
the link to Y is not, and should be followed.  This means that only the middle
relationship chain will be marked as a cycle.

    >>> rel = Relationship((people['Quince'],), 'manages',
    ...                    (people['Lee'], people['Ygritte']))
    >>> app['QuinceManagesLeeYgritte'] = rel
    >>> ix.index_doc(intids.register(rel), rel)
    >>> res = [p for p in ix.findRelationshipTokenChains(
    ...     q({'reltype': 'manages', 'subjects': people['Mary']}))]
    >>> [interfaces.ICircularRelationshipPath.providedBy(p) for p in res]
    [False, True, False]
    >>> [[intids.getObject(t) for t in p] for p in res]
    ... # doctest: +NORMALIZE_WHITESPACE
    [[<(<Person 'Lee'>, <Person 'Mary'>) manages (<Person 'Quince'>,)>],
     [<(<Person 'Lee'>, <Person 'Mary'>) manages (<Person 'Quince'>,)>,
      <(<Person 'Quince'>,) manages (<Person 'Lee'>, <Person 'Ygritte'>)>],
     [<(<Person 'Lee'>, <Person 'Mary'>) manages (<Person 'Quince'>,)>,
      <(<Person 'Quince'>,) manages (<Person 'Lee'>, <Person 'Ygritte'>)>,
      <(<Person 'Ygritte'>,) manages (<Person 'Zane'>,)>]]
    >>> [sorted(
    ...     (nm, nm == 'reltype' and t or load(t, ix, {}))
    ...     for nm, t in search.items()) for search in res[1].cycled]
    [[('reltype', 'manages'), ('subjects', <Person 'Lee'>)]]

Transitively mapping multiple elements
--------------------------------------

Transitive searches can do whatever searches the transitiveQueriesFactory
returns, which means that complex transitive behavior can be modeled.  For
instance, imagine genealogical relationships.  Let's say the basic
relationship is "MALE and FEMALE had CHILDREN".  Walking transitively to get
ancestors or descendants would need to distinguish between male children and
female children in order to correctly generate the transitive search.  This
could be accomplished by resolving each child token and examining the object
or, probably more efficiently, getting an indexed collection of males and
females (and cacheing it in the cache dictionary for further transitive steps)
and checking the gender by membership in the indexed collections.  Either of
these approaches could be performed by a transitiveQueriesFactory.  A full
example is left as an exercise to the reader.

Lies, damn lies, and statistics
===============================

The zope.index.interfaces.IStatistics methods are implemented to provide
minimal introspectability.  wordCount always returns 0, because words are
irrelevant to this kind of index.  documentCount returns the number of
relationships indexed.

    >>> ix.wordCount()
    0
    >>> ix.documentCount()
    25

Reindexing and removing relationships
=====================================

Using an index over an application's lifecycle usually requires changes to the
indexed objects.  As per the zope.index interfaces, `index_doc` can reindex
relationships, `unindex_doc` can remove them, and `clear` can clear the entire
index.

Here we change the zope.org project manager from Fred to Emily.

    >>> [load(t, ix, {}) for t in ix.findValueTokens(
    ...     'subjects',
    ...     q({'reltype': 'has the role of',
    ...       'objects': roles['Project Manager'],
    ...       'context': projects['zope.org redesign']}))]
    [<Person 'Fred'>]
    >>> rel = intids.getObject(list(ix.findRelationshipTokenSet(
    ...     q({'reltype': 'has the role of',
    ...       'objects': roles['Project Manager'],
    ...       'context': projects['zope.org redesign']})))[0])
    >>> rel.subjects = (people['Emily'],)
    >>> ix.index_doc(intids.register(rel), rel)
    >>> q = ix.tokenizeQuery
    >>> [load(t, ix, {}) for t in ix.findValueTokens(
    ...     'subjects',
    ...     q({'reltype': 'has the role of',
    ...       'objects': roles['Project Manager'],
    ...       'context': projects['zope.org redesign']}))]
    [<Person 'Emily'>]

Here we remove the relationship that made a cycle for Abe in the 'king in
disguise' scenario.

    >>> res = list(ix.findRelationshipTokenChains(
    ...     q({'objects': people['Ingrid'],
    ...        'reltype': 'manages'})))
    >>> len(res)
    8
    >>> len(res[7])
    8
    >>> interfaces.ICircularRelationshipPath.providedBy(res[7])
    True
    >>> rel = intids.getObject(list(ix.findRelationshipTokenSet(
    ...     q({'subjects': people['Gary'], 'reltype': 'manages',
    ...        'objects': people['Abe']})))[0])
    >>> ix.unindex(rel) # == ix.unindex_doc(intids.getId(rel))
    >>> ix.documentCount()
    24
    >>> res = list(ix.findRelationshipTokenChains(
    ...     q({'objects': people['Ingrid'], 'reltype': 'manages'})))
    >>> len(res)
    4
    >>> len(res[3])
    4
    >>> interfaces.ICircularRelationshipPath.providedBy(res[3])
    False

Finally we clear out the whole index.

    >>> ix.clear()
    >>> ix.documentCount()
    0
    >>> list(ix.findRelationshipTokenChains(
    ...     q({'objects': people['Ingrid'], 'reltype': 'manages'})))
    []
    >>> [load(t, ix, {}) for t in ix.findValueTokens(
    ...     'subjects',
    ...     q({'reltype': 'has the role of',
    ...       'objects': roles['Project Manager'],
    ...       'context': projects['zope.org redesign']}))]
    []

Optimizing relationship index use
=================================

There are three optimization opportunities built into the index.

- use the cache to load and dump tokens;

- don't load or dump tokens (the values themselves may be used as tokens); and

- have the returned value be of the same btree family as the result family.

For some operations, particularly with hundreds or thousands of members in a
single relationship value, some of these optimizations can speed up some
common-case reindexing work by around 100 times.

The easiest (and perhaps least useful) optimization is that all dump
calls and all load calls generated by a single operation share a cache
dictionary per call type (dump/load), per indexed relationship value.
Therefore, for instance, we could stash an intids utility, so that we
only had to do a utility lookup once, and thereafter it was only a
single dictionary lookup. This is what the default `generateToken` and
`resolveToken` functions in index.py do: look at them for an example.

A further optimization is to not load or dump tokens at all, but use values
that may be tokens.  This will be particularly useful if the tokens have
__cmp__ (or equivalent) in C, such as built-in types like ints.  To specify
this behavior, you create an index with the 'load' and 'dump' values for the
indexed attribute descriptions explicitly set to None.

    >>> ix = index.Index(
    ...     ({'element': IRelationship['subjects'], 'multiple': True,
    ...       'dump': None, 'load': None},
    ...      {'element': IRelationship['relationshiptype'],
    ...       'dump': relTypeDump, 'load': relTypeLoad, 'btree': OIBTree,
    ...       'name': 'reltype'},
    ...      {'element': IRelationship['objects'], 'multiple': True,
    ...       'dump': None, 'load': None},
    ...      {'element': IContextAwareRelationship['getContext'],
    ...       'name': 'context'}),
    ...     index.TransposingTransitiveQueriesFactory('subjects', 'objects'))
    ...
    >>> sm['rel_index_2'] = ix
    >>> app['ex_rel_1'] = rel = Relationship((1,), 'has the role of', (2,))
    >>> ix.index(rel)
    >>> list(ix.findValueTokens('objects', {'subjects': 1}))
    [2]

Finally, if you have single relationships that relate hundreds or thousands
of objects, it can be a huge win if the value is a 'multiple' of the same type
as the stored BTree for the given attribute.  The default BTree family for
attributes is IFBTree; IOBTree is also a good choice, and may be preferrable
for some applications.

    >>> ix = index.Index(
    ...     ({'element': IRelationship['subjects'], 'multiple': True,
    ...       'dump': None, 'load': None},
    ...      {'element': IRelationship['relationshiptype'],
    ...       'dump': relTypeDump, 'load': relTypeLoad, 'btree': OIBTree,
    ...       'name': 'reltype'},
    ...      {'element': IRelationship['objects'], 'multiple': True,
    ...       'dump': None, 'load': None},
    ...      {'element': IContextAwareRelationship['getContext'],
    ...       'name': 'context'}),
    ...     index.TransposingTransitiveQueriesFactory('subjects', 'objects'))
    ...
    >>> sm['rel_index_3'] = ix
    >>> from BTrees import IFBTree
    >>> app['ex_rel_2'] = rel = Relationship(
    ...     IFBTree.IFTreeSet((1,)), 'has the role of', IFBTree.IFTreeSet())
    >>> ix.index(rel)
    >>> list(ix.findValueTokens('objects', {'subjects': 1}))
    []
    >>> list(ix.findValueTokens('subjects', {'objects': None}))
    [1]

Reindexing is where some of the big improvements can happen.  The following
gyrations exercise the optimization code.

    >>> rel.objects.insert(2)
    1
    >>> ix.index(rel)
    >>> list(ix.findValueTokens('objects', {'subjects': 1}))
    [2]
    >>> rel.subjects = IFBTree.IFTreeSet((3,4,5))
    >>> ix.index(rel)
    >>> list(ix.findValueTokens('objects', {'subjects': 3}))
    [2]

    >>> rel.subjects.insert(6)
    1
    >>> ix.index(rel)
    >>> list(ix.findValueTokens('objects', {'subjects': 6}))
    [2]

    >>> rel.subjects.update(range(100, 200))
    100
    >>> ix.index(rel)
    >>> list(ix.findValueTokens('objects', {'subjects': 100}))
    [2]

    >>> rel.subjects = IFBTree.IFTreeSet((3,4,5,6))
    >>> ix.index(rel)
    >>> list(ix.findValueTokens('objects', {'subjects': 3}))
    [2]

    >>> rel.subjects = IFBTree.IFTreeSet(())
    >>> ix.index(rel)
    >>> list(ix.findValueTokens('objects', {'subjects': 3}))
    []

    >>> rel.subjects = IFBTree.IFTreeSet((3,4,5))
    >>> ix.index(rel)
    >>> list(ix.findValueTokens('objects', {'subjects': 3}))
    [2]

tokenizeValues and resolveValueTokens work correctly without loaders and
dumpers--that is, they do nothing.

    >>> ix.tokenizeValues((3,4,5), 'subjects')
    (3, 4, 5)
    >>> ix.resolveValueTokens((3,4,5), 'subjects')
    (3, 4, 5)

__contains__ and Unindexing
=============================

You can test whether a relationship is in an index with __contains__.  Note
that this uses the actual relationship, not the relationship token.

    >>> ix = index.Index(
    ...     ({'element': IRelationship['subjects'], 'multiple': True,
    ...       'dump': dump, 'load': load},
    ...      {'element': IRelationship['relationshiptype'],
    ...       'dump': relTypeDump, 'load': relTypeLoad, 'btree': OIBTree,
    ...       'name': 'reltype'},
    ...      {'element': IRelationship['objects'], 'multiple': True,
    ...       'dump': dump, 'load': load},
    ...      {'element': IContextAwareRelationship['getContext'],
    ...       'name': 'context'}),
    ...     index.TransposingTransitiveQueriesFactory('subjects', 'objects'))
    >>> ix.documentCount()
    0
    >>> app['fredisprojectmanager'].subjects = (people['Fred'],)
    >>> ix.index(app['fredisprojectmanager'])
    >>> ix.index(app['another_rel'])
    >>> ix.documentCount()
    2
    >>> app['fredisprojectmanager'] in ix
    True
    >>> list(ix.findValues(
    ...     'subjects',
    ...     q({'reltype': 'has the role of',
    ...       'objects': roles['Project Manager'],
    ...       'context': projects['zope.org redesign']})))
    [<Person 'Fred'>]

    >>> app['another_rel'] in ix
    True

    >>> app['abeAndBran'] in ix
    False

As noted, you can unindex using unindex(relationship) or
unindex_doc(relationship token).

    >>> ix.unindex_doc(ix.tokenizeRelationship(app['fredisprojectmanager']))
    >>> app['fredisprojectmanager'] in ix
    False
    >>> list(ix.findValues(
    ...     'subjects',
    ...     q({'reltype': 'has the role of',
    ...       'objects': roles['Project Manager'],
    ...       'context': projects['zope.org redesign']})))
    []

    >>> ix.unindex(app['another_rel'])
    >>> app['another_rel'] in ix
    False

As defined by zope.index.interfaces.IInjection, if the relationship is
not in the index then calling unindex_doc is a no-op; the same holds
true for unindex.

    >>> ix.unindex(app['abeAndBran'])
    >>> ix.unindex_doc(ix.tokenizeRelationship(app['abeAndBran']))

.. ......... ..
.. FOOTNOTES ..
.. ......... ..

.. [#apply] `apply` and the other zope.index-related methods are the obvious
    exceptions.


=====================
RelationshipContainer
=====================

The relationship container holds IRelationship objects. It includes an API to
search for relationships and the objects to which they link, transitively and
intransitively.  The relationships are objects in and of themselves, and they
can themselves be related as sources or targets in other relationships.

There are currently two implementations of the interface in this package.  One
uses intids, and the other uses key references.  They have different
advantages and disadvantages.

The intids makes it possible to get intid values directly.  This can make it
easier to merge the results with catalog searches and other intid-based
indexes.  Possibly more importantly, it does not create ghosted objects for
the relationships as they are searched unless absolutely necessary (for
instance, using a relationship filter), but uses the intids alone for
searches.  This can be very important if you are searching large databases of
relationships: the relationship objects and the associated keyref links in the
other implementation can flush the entire ZODB object cache, possibly leading
to unpleasant performance characteristics for your entire application.

On the other hand, there are a limited number of intids available: sys.maxint,
or 2147483647 on a 32 bit machine.  As the intid usage increases, the
efficiency of finding unique intids decreases.  This can be addressed by
increasing IOBTrees maximum integer to be 64 bit (9223372036854775807) or by
using the keyref implementation.  The keyref implementation also eliminates a
dependency--the intid utility itself--if that is desired.  This can be
important if you can't rely on having an intid utility, or if objects to be
related span intid utilities.  Finally, it's possible that the direct
attribute access that underlies the keyref implementation might be quicker
than the intid dereferencing, but this is unproven and may be false.

For our examples, we'll assume we've already imported a container and a
relationship from one of the available sources.  You can use a relationship
specific to your usage, or the generic one in shared, as long as it meets the
interface requirements.

It's also important to note that, while the relationship objects are an
important part of the design, they should not be abused.  If you want to store
other data on the relationship, it should be stored in another persistent
object, such as an attribute annotation's btree.  Typically relationship
objects will differ on the basis of interfaces, annotations, and possibly
small lightweight values on the objects themselves.

We'll assume that there is an application named `app` with 30 objects in it
(named 'ob0' through 'ob29') that we'll be relating.

Creating a relationship container is easy.  We'll use an abstract Container,
but it could be from the keyref or the intid modules.

    >>> from zc.relationship import interfaces
    >>> container = Container()
    >>> from zope.interface.verify import verifyObject
    >>> verifyObject(interfaces.IRelationshipContainer, container)
    True

The containers can be used as parts of other objects, or as standalone local
utilities.  Here's an example of adding one as a local utilty.

    >>> sm = app.getSiteManager()
    >>> sm['lineage_relationship'] = container
    >>> import zope.component.interfaces
    >>> registry = zope.component.interfaces.IComponentRegistry(sm)
    >>> registry.registerUtility(
    ...     container, interfaces.IRelationshipContainer, 'lineage')
    >>> import transaction
    >>> transaction.commit()

Adding relationships is also easy: instantiate and add.  The `add` method adds
objects and assigns them random alphanumeric keys.

    >>> rel = Relationship((app['ob0'],), (app['ob1'],))
    >>> verifyObject(interfaces.IRelationship, rel)
    True
    >>> container.add(rel)

Although the container does not have `__setitem__` and `__delitem__` (defining
`add` and `remove` instead), it does define the read-only elements of the basic
Python mapping interface.

    >>> container[rel.__name__] is rel
    True
    >>> len(container)
    1
    >>> list(container.keys()) == [rel.__name__]
    True
    >>> list(container) == [rel.__name__]
    True
    >>> list(container.values()) == [rel]
    True
    >>> container.get(rel.__name__) is rel
    True
    >>> container.get('17') is None
    True
    >>> rel.__name__ in container
    True
    >>> '17' in container
    False
    >>> list(container.items()) == [(rel.__name__, rel)]
    True

It also supports four searching methods: `findTargets`, `findSources`,
`findRelationships`, and `isLinked`.  Let's add a few more relationships and
examine some relatively simple cases.

    >>> container.add(Relationship((app['ob1'],), (app['ob2'],)))
    >>> container.add(Relationship((app['ob1'],), (app['ob3'],)))
    >>> container.add(Relationship((app['ob0'],), (app['ob3'],)))
    >>> container.add(Relationship((app['ob0'],), (app['ob4'],)))
    >>> container.add(Relationship((app['ob2'],), (app['ob5'],)))
    >>> transaction.commit() # this is indicative of a bug in ZODB; if you
    ... # do not do this then new objects will deactivate themselves into
    ... # nothingness when _p_deactivate is called

Now there are six direct relationships (all of the relationships point down
in the diagram)::

        ob0
        | |\
      ob1 | |
      | | | |
    ob2 ob3 ob4
      |
    ob5

The mapping methods still have kept up with the new additions.

    >>> len(container)
    6
    >>> len(container.keys())
    6
    >>> sorted(container.keys()) == sorted(
    ...     v.__name__ for v in container.values())
    True
    >>> sorted(container.items()) == sorted(
    ...     zip(container.keys(), container.values()))
    True
    >>> len([v for v in container.values() if container[v.__name__] is v])
    6
    >>> sorted(container.keys()) == sorted(container)
    True

More interestingly, lets examine some of the searching methods.  What are the
direct targets of ob0?

    >>> container.findTargets(app['ob0']) # doctest: +ELLIPSIS
    <generator object ...>

Ah-ha! It's a generator!  Let's try that again.

    >>> sorted(o.id for o in container.findTargets(app['ob0']))
    ['ob1', 'ob3', 'ob4']

OK, what about the ones no more than two relationships away?  We use the
`maxDepth` argument, which is the second placeful argument.

    >>> sorted(o.id for o in container.findTargets(app['ob0'], 2))
    ['ob1', 'ob2', 'ob3', 'ob4']

Notice that, even though ob3 is available both through one and two
relationships, it is returned only once.

Passing in None will get all related objects--the same here as passing in 3, or
any greater integer.

    >>> sorted(o.id for o in container.findTargets(app['ob0'], None))
    ['ob1', 'ob2', 'ob3', 'ob4', 'ob5']
    >>> sorted(o.id for o in container.findTargets(app['ob0'], 3))
    ['ob1', 'ob2', 'ob3', 'ob4', 'ob5']
    >>> sorted(o.id for o in container.findTargets(app['ob0'], 25))
    ['ob1', 'ob2', 'ob3', 'ob4', 'ob5']

This is true even if we put in a cycle.  We'll put in a cycle between ob5 and
ob1 and look at the results.

An important aspect of the algorithm used is that it returns closer
relationships first, which we can begin to see here.

    >>> container.add(Relationship((app['ob5'],), (app['ob1'],)))
    >>> transaction.commit()
    >>> sorted(o.id for o in container.findTargets(app['ob0'], None))
    ['ob1', 'ob2', 'ob3', 'ob4', 'ob5']
    >>> res = list(o.id for o in container.findTargets(app['ob0'], None))
    >>> sorted(res[:3]) # these are all one step away
    ['ob1', 'ob3', 'ob4']
    >>> res[3:] # ob 2 is two steps, and ob5 is three steps.
    ['ob2', 'ob5']

When you see the source in the targets, you know you are somewhere inside a
cycle.

    >>> sorted(o.id for o in container.findTargets(app['ob1'], None))
    ['ob1', 'ob2', 'ob3', 'ob5']
    >>> sorted(o.id for o in container.findTargets(app['ob2'], None))
    ['ob1', 'ob2', 'ob3', 'ob5']
    >>> sorted(o.id for o in container.findTargets(app['ob5'], None))
    ['ob1', 'ob2', 'ob3', 'ob5']

If you ask for objects of a distance that is not a positive integer, you'll get
a ValueError.

    >>> container.findTargets(app['ob0'], 0)
    Traceback (most recent call last):
    ...
    ValueError: maxDepth must be None or a positive integer
    >>> container.findTargets(app['ob0'], -1)
    Traceback (most recent call last):
    ...
    ValueError: maxDepth must be None or a positive integer
    >>> container.findTargets(app['ob0'], 'kumquat') # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: ...

The `findSources` method is the mirror of `findTargets`: given a target, it
finds all sources.  Using the same relationship tree built above, we'll search
for some sources.

    >>> container.findSources(app['ob0']) # doctest: +ELLIPSIS
    <generator object ...>
    >>> list(container.findSources(app['ob0']))
    []
    >>> list(o.id for o in container.findSources(app['ob4']))
    ['ob0']
    >>> list(o.id for o in container.findSources(app['ob4'], None))
    ['ob0']
    >>> sorted(o.id for o in container.findSources(app['ob1']))
    ['ob0', 'ob5']
    >>> sorted(o.id for o in container.findSources(app['ob1'], 2))
    ['ob0', 'ob2', 'ob5']
    >>> sorted(o.id for o in container.findSources(app['ob1'], 3))
    ['ob0', 'ob1', 'ob2', 'ob5']
    >>> sorted(o.id for o in container.findSources(app['ob1'], None))
    ['ob0', 'ob1', 'ob2', 'ob5']
    >>> sorted(o.id for o in container.findSources(app['ob3']))
    ['ob0', 'ob1']
    >>> sorted(o.id for o in container.findSources(app['ob3'], None))
    ['ob0', 'ob1', 'ob2', 'ob5']
    >>> list(o.id for o in container.findSources(app['ob5']))
    ['ob2']
    >>> list(o.id for o in container.findSources(app['ob5'], maxDepth=2))
    ['ob2', 'ob1']
    >>> sorted(o.id for o in container.findSources(app['ob5'], maxDepth=3))
    ['ob0', 'ob1', 'ob2', 'ob5']
    >>> container.findSources(app['ob0'], 0)
    Traceback (most recent call last):
    ...
    ValueError: maxDepth must be None or a positive integer
    >>> container.findSources(app['ob0'], -1)
    Traceback (most recent call last):
    ...
    ValueError: maxDepth must be None or a positive integer
    >>> container.findSources(app['ob0'], 'kumquat') # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: ...

The `findRelationships` method finds all relationships from, to, or between
two objects.  Because it supports transitive relationships, each member of the
resulting iterator is a tuple of one or more relationships.

All arguments to findRelationships are optional, but at least one of `source`
or `target` must be passed in.  A search depth defaults to one relationship
deep, like the other methods.

    >>> container.findRelationships(source=app['ob0']) # doctest: +ELLIPSIS
    <generator object ...>
    >>> sorted(
    ...     [repr(rel) for rel in path]
    ...     for path in container.findRelationships(source=app['ob0']))
    ...     # doctest: +NORMALIZE_WHITESPACE
    [['<Relationship from (<Demo ob0>,) to (<Demo ob1>,)>'],
     ['<Relationship from (<Demo ob0>,) to (<Demo ob3>,)>'],
     ['<Relationship from (<Demo ob0>,) to (<Demo ob4>,)>']]
    >>> list(container.findRelationships(target=app['ob0']))
    []
    >>> sorted(
    ...     [repr(rel) for rel in path]
    ...     for path in container.findRelationships(target=app['ob3']))
    ...     # doctest: +NORMALIZE_WHITESPACE
    [['<Relationship from (<Demo ob0>,) to (<Demo ob3>,)>'],
     ['<Relationship from (<Demo ob1>,) to (<Demo ob3>,)>']]
    >>> list(
    ...     [repr(rel) for rel in path]
    ...     for path in container.findRelationships(
    ...         source=app['ob1'], target=app['ob3']))
    ...     # doctest: +NORMALIZE_WHITESPACE
    [['<Relationship from (<Demo ob1>,) to (<Demo ob3>,)>']]
    >>> container.findRelationships()
    Traceback (most recent call last):
    ...
    ValueError: at least one of `source` and `target` must be provided

They may also be used as positional arguments, with the order `source` and
`target`.

    >>> sorted(
    ...     [repr(rel) for rel in path]
    ...     for path in container.findRelationships(app['ob1']))
    ...     # doctest: +NORMALIZE_WHITESPACE
    [['<Relationship from (<Demo ob1>,) to (<Demo ob2>,)>'],
     ['<Relationship from (<Demo ob1>,) to (<Demo ob3>,)>']]
    >>> sorted(
    ...     [repr(rel) for rel in path]
    ...     for path in container.findRelationships(app['ob5'], app['ob1']))
    ...     # doctest: +NORMALIZE_WHITESPACE
    [['<Relationship from (<Demo ob5>,) to (<Demo ob1>,)>']]

`maxDepth` is again available, but it is the third positional argument now, so
keyword usage will be more frequent than with the others.  Notice that the
second path has two members: from ob1 to ob2, then from ob2 to ob5.

    >>> sorted(
    ...     [repr(rel) for rel in path]
    ...     for path in container.findRelationships(app['ob1'], maxDepth=2))
    ...     # doctest: +NORMALIZE_WHITESPACE
    [['<Relationship from (<Demo ob1>,) to (<Demo ob2>,)>'],
     ['<Relationship from (<Demo ob1>,) to (<Demo ob2>,)>',
      '<Relationship from (<Demo ob2>,) to (<Demo ob5>,)>'],
     ['<Relationship from (<Demo ob1>,) to (<Demo ob3>,)>']]

Unique relationships are returned, rather than unique objects. Therefore,
while ob3 only has two transitive sources, ob1 and ob0, it has three transitive
paths.

    >>> sorted(
    ...     [repr(rel) for rel in path]
    ...     for path in container.findRelationships(
    ...         target=app['ob3'], maxDepth=2))
    ...     # doctest: +NORMALIZE_WHITESPACE
    [['<Relationship from (<Demo ob0>,) to (<Demo ob1>,)>',
      '<Relationship from (<Demo ob1>,) to (<Demo ob3>,)>'],
     ['<Relationship from (<Demo ob0>,) to (<Demo ob3>,)>'],
     ['<Relationship from (<Demo ob1>,) to (<Demo ob3>,)>'],
     ['<Relationship from (<Demo ob5>,) to (<Demo ob1>,)>',
      '<Relationship from (<Demo ob1>,) to (<Demo ob3>,)>']]

The same is true for the targets of ob0.

    >>> sorted(
    ...     [repr(rel) for rel in path]
    ...     for path in container.findRelationships(
    ...         source=app['ob0'], maxDepth=2))
    ...     # doctest: +NORMALIZE_WHITESPACE
    [['<Relationship from (<Demo ob0>,) to (<Demo ob1>,)>'],
     ['<Relationship from (<Demo ob0>,) to (<Demo ob1>,)>',
      '<Relationship from (<Demo ob1>,) to (<Demo ob2>,)>'],
     ['<Relationship from (<Demo ob0>,) to (<Demo ob1>,)>',
      '<Relationship from (<Demo ob1>,) to (<Demo ob3>,)>'],
     ['<Relationship from (<Demo ob0>,) to (<Demo ob3>,)>'],
     ['<Relationship from (<Demo ob0>,) to (<Demo ob4>,)>']]

Cyclic relationships are returned in a special tuple that implements
ICircularRelationshipPath.  For instance, consider all of the paths that lead
from ob0.  Notice first that all the paths are in order from shortest to
longest.

    >>> res = list(
    ...     [repr(rel) for rel in path]
    ...     for path in container.findRelationships(
    ...         app['ob0'], maxDepth=None))
    ...     # doctest: +NORMALIZE_WHITESPACE
    >>> sorted(res[:3]) # one step away # doctest: +NORMALIZE_WHITESPACE
    [['<Relationship from (<Demo ob0>,) to (<Demo ob1>,)>'],
     ['<Relationship from (<Demo ob0>,) to (<Demo ob3>,)>'],
     ['<Relationship from (<Demo ob0>,) to (<Demo ob4>,)>']]
    >>> sorted(res[3:5]) # two steps away # doctest: +NORMALIZE_WHITESPACE
    [['<Relationship from (<Demo ob0>,) to (<Demo ob1>,)>',
      '<Relationship from (<Demo ob1>,) to (<Demo ob2>,)>'],
     ['<Relationship from (<Demo ob0>,) to (<Demo ob1>,)>',
      '<Relationship from (<Demo ob1>,) to (<Demo ob3>,)>']]
    >>> res[5:] # three and four steps away # doctest: +NORMALIZE_WHITESPACE
    [['<Relationship from (<Demo ob0>,) to (<Demo ob1>,)>',
      '<Relationship from (<Demo ob1>,) to (<Demo ob2>,)>',
      '<Relationship from (<Demo ob2>,) to (<Demo ob5>,)>'],
     ['<Relationship from (<Demo ob0>,) to (<Demo ob1>,)>',
      '<Relationship from (<Demo ob1>,) to (<Demo ob2>,)>',
      '<Relationship from (<Demo ob2>,) to (<Demo ob5>,)>',
      '<Relationship from (<Demo ob5>,) to (<Demo ob1>,)>']]

The very last one is circular.

Now we'll change the expression to only include paths that implement
ICircularRelationshipPath.

    >>> list(
    ...     [repr(rel) for rel in path]
    ...     for path in container.findRelationships(
    ...         app['ob0'], maxDepth=None)
    ...         if interfaces.ICircularRelationshipPath.providedBy(path))
    ...     # doctest: +NORMALIZE_WHITESPACE
    [['<Relationship from (<Demo ob0>,) to (<Demo ob1>,)>',
      '<Relationship from (<Demo ob1>,) to (<Demo ob2>,)>',
      '<Relationship from (<Demo ob2>,) to (<Demo ob5>,)>',
      '<Relationship from (<Demo ob5>,) to (<Demo ob1>,)>']]

Note that, because relationships may have multiple targets, a relationship
that has a cycle may still be traversed for targets that do not generate a
cycle.  The further paths will not be marked as a cycle.

Cycle paths not only have a marker interface to identify them, but include a
`cycled` attribute that is a frozenset of the one or more searches that would
be equivalent to following the cycle(s).  If a source is provided, the searches
cycled searches would continue from the end of the path.

    >>> path = [path for path in container.findRelationships(
    ...     app['ob0'], maxDepth=None)
    ...     if interfaces.ICircularRelationshipPath.providedBy(path)][0]
    >>> path.cycled
    [{'source': <Demo ob1>}]
    >>> app['ob1'] in path[-1].targets
    True

If only a target is provided, the `cycled` search will continue from the
first relationship in the path.

    >>> path = [path for path in container.findRelationships(
    ...     target=app['ob5'], maxDepth=None)
    ...     if interfaces.ICircularRelationshipPath.providedBy(path)][0]
    >>> path # doctest: +NORMALIZE_WHITESPACE
    cycle(<Relationship from (<Demo ob5>,) to (<Demo ob1>,)>,
          <Relationship from (<Demo ob1>,) to (<Demo ob2>,)>,
          <Relationship from (<Demo ob2>,) to (<Demo ob5>,)>)
    >>> path.cycled
    [{'target': <Demo ob5>}]

maxDepth can also be used with the combination of source and target.

    >>> list(container.findRelationships(
    ...      app['ob0'], app['ob5'], maxDepth=None))
    ...     # doctest: +NORMALIZE_WHITESPACE
    [(<Relationship from (<Demo ob0>,) to (<Demo ob1>,)>,
      <Relationship from (<Demo ob1>,) to (<Demo ob2>,)>,
      <Relationship from (<Demo ob2>,) to (<Demo ob5>,)>)]

As usual, maxDepth must be a positive integer or None.

    >>> container.findRelationships(app['ob0'], maxDepth=0)
    Traceback (most recent call last):
    ...
    ValueError: maxDepth must be None or a positive integer
    >>> container.findRelationships(app['ob0'], maxDepth=-1)
    Traceback (most recent call last):
    ...
    ValueError: maxDepth must be None or a positive integer
    >>> container.findRelationships(app['ob0'], maxDepth='kumquat')
    ... # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: ...

The `isLinked` method is a convenient way to test if two objects are linked,
or if an object is a source or target in the graph. It defaults to a maxDepth
of 1.

    >>> container.isLinked(app['ob0'], app['ob1'])
    True
    >>> container.isLinked(app['ob0'], app['ob2'])
    False

Note that maxDepth is pointless when supplying only one of source or target.

    >>> container.isLinked(source=app['ob29'])
    False
    >>> container.isLinked(target=app['ob29'])
    False
    >>> container.isLinked(source=app['ob0'])
    True
    >>> container.isLinked(target=app['ob4'])
    True
    >>> container.isLinked(source=app['ob4'])
    False
    >>> container.isLinked(target=app['ob0'])
    False

Setting maxDepth works as usual when searching for a link between two objects,
though.

    >>> container.isLinked(app['ob0'], app['ob2'], maxDepth=2)
    True
    >>> container.isLinked(app['ob0'], app['ob5'], maxDepth=2)
    False
    >>> container.isLinked(app['ob0'], app['ob5'], maxDepth=3)
    True
    >>> container.isLinked(app['ob0'], app['ob5'], maxDepth=None)
    True

As usual, maxDepth must be a positive integer or None.

    >>> container.isLinked(app['ob0'], app['ob1'], maxDepth=0)
    Traceback (most recent call last):
    ...
    ValueError: maxDepth must be None or a positive integer
    >>> container.isLinked(app['ob0'], app['ob1'], maxDepth=-1)
    Traceback (most recent call last):
    ...
    ValueError: maxDepth must be None or a positive integer
    >>> container.isLinked(app['ob0'], app['ob1'], maxDepth='kumquat')
    ... # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: ...

The `remove` method is the next to last of the core interface: it allows you
to remove relationships from a container.  It takes a relationship object.

As an example, let's remove the relationship from ob5 to ob1 that we created
to make the cycle.

    >>> res = list(container.findTargets(app['ob2'], None)) # before removal
    >>> len(res)
    4
    >>> res[:2]
    [<Demo ob5>, <Demo ob1>]
    >>> sorted(repr(o) for o in res[2:])
    ['<Demo ob2>', '<Demo ob3>']
    >>> res = list(container.findSources(app['ob2'], None)) # before removal
    >>> res[0]
    <Demo ob1>
    >>> res[3]
    <Demo ob2>
    >>> sorted(repr(o) for o in res[1:3])
    ['<Demo ob0>', '<Demo ob5>']
    >>> rel = list(container.findRelationships(app['ob5'], app['ob1']))[0][0]
    >>> rel.sources
    (<Demo ob5>,)
    >>> rel.targets
    (<Demo ob1>,)
    >>> container.remove(rel)
    >>> list(container.findRelationships(app['ob5'], app['ob1']))
    []
    >>> list(container.findTargets(app['ob2'], None)) # after removal
    [<Demo ob5>]
    >>> list(container.findSources(app['ob2'], None)) # after removal
    [<Demo ob1>, <Demo ob0>]

Finally, the `reindex` method allows objects already in the container to be
reindexed.  The default implementation of the relationship objects calls this
automatically when sources and targets are changed.

To reiterate, the relationships looked like this before. ::

        ob0
        | |\
      ob1 | |
      | | | |
    ob2 ob3 ob4
      |
    ob5

We'll switch out ob3 and ob4, so the diagram looks like this. ::

        ob0
        | |\
      ob1 | |
      | | | |
    ob2 ob4 ob3
      |
    ob5

    >>> sorted(ob.id for ob in container.findTargets(app['ob1']))
    ['ob2', 'ob3']
    >>> sorted(ob.id for ob in container.findSources(app['ob3']))
    ['ob0', 'ob1']
    >>> sorted(ob.id for ob in container.findSources(app['ob4']))
    ['ob0']
    >>> rel = next(
    ...     iter(container.findRelationships(app['ob1'], app['ob3'])
    ... ))[0]
    >>> rel.targets
    (<Demo ob3>,)

    >>> rel.targets = [app['ob4']] # this calls reindex

    >>> rel.targets
    (<Demo ob4>,)

    >>> sorted(ob.id for ob in container.findTargets(app['ob1']))
    ['ob2', 'ob4']
    >>> sorted(ob.id for ob in container.findSources(app['ob3']))
    ['ob0']
    >>> sorted(ob.id for ob in container.findSources(app['ob4']))
    ['ob0', 'ob1']

The same sort of thing happens if we change sources.  We'll change the
diagram to look like this. ::

        ob0
        | |\
      ob1 | |
      |   | |
      ob2 | ob3
      | \ |
    ob5  ob4

    >>> rel.sources
    (<Demo ob1>,)
    >>> rel.sources = (app['ob2'],) # this calls reindex
    >>> rel.sources
    (<Demo ob2>,)

    >>> sorted(ob.id for ob in container.findTargets(app['ob1']))
    ['ob2']
    >>> sorted(ob.id for ob in container.findTargets(app['ob2']))
    ['ob4', 'ob5']
    >>> sorted(ob.id for ob in container.findTargets(app['ob0']))
    ['ob1', 'ob3', 'ob4']
    >>> sorted(ob.id for ob in container.findSources(app['ob4']))
    ['ob0', 'ob2']

Advanced Usage
==============

There are four other advanced tricks that the relationship container can do:
enable search filters; allow multiple sources and targets for a single
relationship; allow relating relationships; and exposing unresolved token
results.

Search Filters
--------------

Because relationships are objects themselves, a number of interesting usages
are possible.  They can implement additional interfaces, have annotations,
and have other attributes.  One use for this is to only find objects along
relationship paths with relationships that provide a given interface.  The
`filter` argument, allowed in `findSources`, `findTargets`,
`findRelationships`, and `isLinked`, supports this kind of use case.

For instance, imagine that we change the relationships to look like the diagram
below.  The `xxx` lines indicate a relationship that implements
ISpecialRelationship. ::

        ob0
        x |x
      ob1 | x
      x   | x
      ob2 | ob3
      | x |
    ob5  ob4

That is, the relationships from ob0 to ob1, ob0 to ob3, ob1 to ob2, and ob2 to
ob4 implement the special interface.  Let's make this happen first.

    >>> from zope import interface
    >>> class ISpecialInterface(interface.Interface):
    ...     """I'm special!  So special!"""
    ...
    >>> for src, tgt in (
    ...     (app['ob0'], app['ob1']),
    ...     (app['ob0'], app['ob3']),
    ...     (app['ob1'], app['ob2']),
    ...     (app['ob2'], app['ob4'])):
    ...     rel = list(container.findRelationships(src, tgt))[0][0]
    ...     interface.directlyProvides(rel, ISpecialInterface)
    ...

Now we can use `ISpecialInterface.providedBy` as a filter for all of the
methods mentioned above.

`findTargets`

    >>> sorted(ob.id for ob in container.findTargets(app['ob0']))
    ['ob1', 'ob3', 'ob4']
    >>> sorted(ob.id for ob in container.findTargets(
    ...     app['ob0'], filter=ISpecialInterface.providedBy))
    ['ob1', 'ob3']
    >>> sorted(ob.id for ob in container.findTargets(
    ...     app['ob0'], maxDepth=None))
    ['ob1', 'ob2', 'ob3', 'ob4', 'ob5']
    >>> sorted(ob.id for ob in container.findTargets(
    ...     app['ob0'], maxDepth=None, filter=ISpecialInterface.providedBy))
    ['ob1', 'ob2', 'ob3', 'ob4']

`findSources`

    >>> sorted(ob.id for ob in container.findSources(app['ob4']))
    ['ob0', 'ob2']
    >>> sorted(ob.id for ob in container.findSources(
    ...     app['ob4'], filter=ISpecialInterface.providedBy))
    ['ob2']
    >>> sorted(ob.id for ob in container.findSources(
    ...     app['ob4'], maxDepth=None))
    ['ob0', 'ob1', 'ob2']
    >>> sorted(ob.id for ob in container.findSources(
    ...     app['ob4'], maxDepth=None, filter=ISpecialInterface.providedBy))
    ['ob0', 'ob1', 'ob2']
    >>> sorted(ob.id for ob in container.findSources(
    ...     app['ob5'], maxDepth=None))
    ['ob0', 'ob1', 'ob2']
    >>> list(ob.id for ob in container.findSources(
    ...     app['ob5'], filter=ISpecialInterface.providedBy))
    []

`findRelationships`

    >>> len(list(container.findRelationships(
    ...     app['ob0'], app['ob4'], maxDepth=None)))
    2
    >>> len(list(container.findRelationships(
    ...     app['ob0'], app['ob4'], maxDepth=None,
    ...     filter=ISpecialInterface.providedBy)))
    1
    >>> len(list(container.findRelationships(app['ob0'])))
    3
    >>> len(list(container.findRelationships(
    ...     app['ob0'], filter=ISpecialInterface.providedBy)))
    2

`isLinked`

    >>> container.isLinked(app['ob0'], app['ob5'], maxDepth=None)
    True
    >>> container.isLinked(
    ...     app['ob0'], app['ob5'], maxDepth=None,
    ...     filter=ISpecialInterface.providedBy)
    False
    >>> container.isLinked(
    ...     app['ob0'], app['ob2'], maxDepth=None,
    ...     filter=ISpecialInterface.providedBy)
    True
    >>> container.isLinked(
    ...     app['ob0'], app['ob4'])
    True
    >>> container.isLinked(
    ...     app['ob0'], app['ob4'],
    ...     filter=ISpecialInterface.providedBy)
    False

Multiple Sources and/or Targets; Duplicate Relationships
--------------------------------------------------------

Relationships are not always between a single source and a single target.  Many
approaches to this are possible, but a simple one is to allow relationships to
have multiple sources and multiple targets.  This is an approach that the
relationship container supports.

    >>> container.add(Relationship(
    ...     (app['ob2'], app['ob4'], app['ob5'], app['ob6'], app['ob7']),
    ...     (app['ob1'], app['ob4'], app['ob8'], app['ob9'], app['ob10'])))
    >>> container.add(Relationship(
    ...     (app['ob10'], app['ob0']),
    ...     (app['ob7'], app['ob3'])))

Before we examine the results, look at those for a second.

Among the interesting items is that we have duplicated the ob2->ob4
relationship in the first example, and duplicated the ob0->ob3 relationship
in the second.  The relationship container does not limit duplicate
relationships: it simply adds and indexes them, and will include the additional
relationship path in findRelationships.

    >>> sorted(o.id for o in container.findTargets(app['ob4']))
    ['ob1', 'ob10', 'ob4', 'ob8', 'ob9']
    >>> sorted(o.id for o in container.findTargets(app['ob10']))
    ['ob3', 'ob7']
    >>> sorted(o.id for o in container.findTargets(app['ob4'], maxDepth=2))
    ['ob1', 'ob10', 'ob2', 'ob3', 'ob4', 'ob7', 'ob8', 'ob9']
    >>> sorted(
    ...     [repr(rel) for rel in path]
    ...     for path in container.findRelationships(
    ...         app['ob2'], app['ob4']))
    ...     # doctest: +NORMALIZE_WHITESPACE
    [['<Relationship from
       (<Demo ob2>, <Demo ob4>, <Demo ob5>, <Demo ob6>, <Demo ob7>)
       to
       (<Demo ob1>, <Demo ob4>, <Demo ob8>, <Demo ob9>, <Demo ob10>)>'],
     ['<Relationship from (<Demo ob2>,) to (<Demo ob4>,)>']]

There's also a reflexive relationship in there, with ob4 pointing to ob4.  It's
marked as a cycle.

    >>> list(container.findRelationships(app['ob4'], app['ob4']))
    ... # doctest: +NORMALIZE_WHITESPACE
    [cycle(<Relationship from
       (<Demo ob2>, <Demo ob4>, <Demo ob5>, <Demo ob6>, <Demo ob7>)
       to
       (<Demo ob1>, <Demo ob4>, <Demo ob8>, <Demo ob9>, <Demo ob10>)>,)]
    >>> list(container.findRelationships(app['ob4'], app['ob4']))[0].cycled
    [{'source': <Demo ob4>}]

Relating Relationships and Relationship Containers
--------------------------------------------------

Relationships are objects.  We've already shown and discussed how this means
that they can implement different interfaces and be annotated.  It also means
that relationships are first-class objects that can be related themselves.
This allows relationships that keep track of who created other relationships,
and other use cases.

Even the relationship containers themselves can be nodes in a relationship
container.

    >>> container1 = app['container1'] = Container()
    >>> container2 = app['container2'] = Container()
    >>> rel = Relationship((container1,), (container2,))
    >>> container.add(rel)
    >>> container.isLinked(container1, container2)
    True

Exposing Unresolved Tokens
--------------------------

For specialized use cases, usually optimizations, sometimes it is useful to
have access to raw results from a given implementation.  For instance, if a
relationship has many members, it might make sense to have an intid-based
relationship container return the actual intids.

The containers include three methods for these sorts of use cases:
`findTargetTokens`, `findSourceTokens`, and `findRelationshipTokens`.  They
take the same arguments as their similarly-named cousins.

Convenience classes
-------------------

Three convenience classes exist for relationships with a single source and/or a
single target only.

One-To-One Relationship
~~~~~~~~~~~~~~~~~~~~~~~

A `OneToOneRelationship` relates a single source to a single target.

    >>> from zc.relationship.shared import OneToOneRelationship
    >>> rel = OneToOneRelationship(app['ob20'], app['ob21'])

    >>> verifyObject(interfaces.IOneToOneRelationship, rel)
    True

All container methods work as for the general many-to-many relationship.  We
repeat some of the tests defined in the main section above (all relationships
defined there are actually one-to-one relationships).

    >>> container.add(rel)
    >>> container.add(OneToOneRelationship(app['ob21'], app['ob22']))
    >>> container.add(OneToOneRelationship(app['ob21'], app['ob23']))
    >>> container.add(OneToOneRelationship(app['ob20'], app['ob23']))
    >>> container.add(OneToOneRelationship(app['ob20'], app['ob24']))
    >>> container.add(OneToOneRelationship(app['ob22'], app['ob25']))
    >>> rel = OneToOneRelationship(app['ob25'], app['ob21'])
    >>> container.add(rel)

`findTargets`

    >>> sorted(o.id for o in container.findTargets(app['ob20'], 2))
    ['ob21', 'ob22', 'ob23', 'ob24']

`findSources`

    >>> sorted(o.id for o in container.findSources(app['ob21'], 2))
    ['ob20', 'ob22', 'ob25']

`findRelationships`

    >>> sorted(
    ...     [repr(rel) for rel in path]
    ...     for path in container.findRelationships(app['ob21'], maxDepth=2))
    ...     # doctest: +NORMALIZE_WHITESPACE
    [['<Relationship from (<Demo ob21>,) to (<Demo ob22>,)>'],
     ['<Relationship from (<Demo ob21>,) to (<Demo ob22>,)>',
      '<Relationship from (<Demo ob22>,) to (<Demo ob25>,)>'],
     ['<Relationship from (<Demo ob21>,) to (<Demo ob23>,)>']]

    >>> sorted(
    ...     [repr(rel) for rel in path]
    ...     for path in container.findRelationships(
    ...         target=app['ob23'], maxDepth=2))
    ...     # doctest: +NORMALIZE_WHITESPACE
    [['<Relationship from (<Demo ob20>,) to (<Demo ob21>,)>',
      '<Relationship from (<Demo ob21>,) to (<Demo ob23>,)>'],
     ['<Relationship from (<Demo ob20>,) to (<Demo ob23>,)>'],
     ['<Relationship from (<Demo ob21>,) to (<Demo ob23>,)>'],
     ['<Relationship from (<Demo ob25>,) to (<Demo ob21>,)>',
      '<Relationship from (<Demo ob21>,) to (<Demo ob23>,)>']]

    >>> list(container.findRelationships(
    ...      app['ob20'], app['ob25'], maxDepth=None))
    ...     # doctest: +NORMALIZE_WHITESPACE
    [(<Relationship from (<Demo ob20>,) to (<Demo ob21>,)>,
      <Relationship from (<Demo ob21>,) to (<Demo ob22>,)>,
      <Relationship from (<Demo ob22>,) to (<Demo ob25>,)>)]

    >>> list(
    ...     [repr(rel) for rel in path]
    ...     for path in container.findRelationships(
    ...         app['ob20'], maxDepth=None)
    ...         if interfaces.ICircularRelationshipPath.providedBy(path))
    ...     # doctest: +NORMALIZE_WHITESPACE
    [['<Relationship from (<Demo ob20>,) to (<Demo ob21>,)>',
      '<Relationship from (<Demo ob21>,) to (<Demo ob22>,)>',
      '<Relationship from (<Demo ob22>,) to (<Demo ob25>,)>',
      '<Relationship from (<Demo ob25>,) to (<Demo ob21>,)>']]

`isLinked`

    >>> container.isLinked(source=app['ob20'])
    True
    >>> container.isLinked(target=app['ob24'])
    True
    >>> container.isLinked(source=app['ob24'])
    False
    >>> container.isLinked(target=app['ob20'])
    False
    >>> container.isLinked(app['ob20'], app['ob22'], maxDepth=2)
    True
    >>> container.isLinked(app['ob20'], app['ob25'], maxDepth=2)
    False

`remove`

    >>> res = list(container.findTargets(app['ob22'], None)) # before removal
    >>> res[:2]
    [<Demo ob25>, <Demo ob21>]
    >>> container.remove(rel)
    >>> list(container.findTargets(app['ob22'], None)) # after removal
    [<Demo ob25>]

`reindex`

    >>> rel = next(
    ...     iter(container.findRelationships(app['ob21'], app['ob23']))
    ... )[0]

    >>> rel.target
    <Demo ob23>
    >>> rel.target = app['ob24'] # this calls reindex
    >>> rel.target
    <Demo ob24>

    >>> rel.source
    <Demo ob21>
    >>> rel.source = app['ob22'] # this calls reindex
    >>> rel.source
    <Demo ob22>

ManyToOneRelationship
~~~~~~~~~~~~~~~~~~~~~

A `ManyToOneRelationship` relates multiple sources to a single target.

    >>> from zc.relationship.shared import ManyToOneRelationship
    >>> rel = ManyToOneRelationship((app['ob22'], app['ob26']), app['ob24'])

    >>> verifyObject(interfaces.IManyToOneRelationship, rel)
    True

    >>> container.add(rel)
    >>> container.add(ManyToOneRelationship(
    ...     (app['ob26'], app['ob23']),
    ...     app['ob20']))

The relationship diagram now looks like this::

        ob20              (ob22, obj26)       (ob26, obj23)
        |   |\                  |                   |
      ob21  | |               obj24               obj20
      |     | |
    ob22    | ob23
      |  \  |
    ob25  ob24

We created a cycle for obj20 via obj23.

    >>> sorted(o.id for o in container.findSources(app['ob24'], None))
    ['ob20', 'ob21', 'ob22', 'ob23', 'ob26']

    >>> sorted(o.id for o in container.findSources(app['ob20'], None))
    ['ob20', 'ob23', 'ob26']

    >>> list(container.findRelationships(app['ob20'], app['ob20'], None))
    ... # doctest: +NORMALIZE_WHITESPACE
    [cycle(<Relationship from (<Demo ob20>,) to (<Demo ob23>,)>,
           <Relationship from (<Demo ob26>, <Demo ob23>) to (<Demo ob20>,)>)]
    >>> list(container.findRelationships(
    ...     app['ob20'], app['ob20'], 2))[0].cycled
    [{'source': <Demo ob20>}]

The `ManyToOneRelationship`'s `sources` attribute is mutable, while it's
`targets` attribute is immutable.

    >>> rel.sources
    (<Demo ob22>, <Demo ob26>)
    >>> rel.sources = [app['ob26'], app['ob24']]

    >>> rel.targets
    (<Demo ob24>,)
    >>> rel.targets = (app['ob22'],)
    Traceback (most recent call last):
    ...
    AttributeError: can't set attribute

But the relationship has an additional mutable `target` attribute.

    >>> rel.target
    <Demo ob24>
    >>> rel.target = app['ob22']

OneToManyRelationship
~~~~~~~~~~~~~~~~~~~~~

A `OneToManyRelationship` relates a single source to multiple targets.

    >>> from zc.relationship.shared import OneToManyRelationship
    >>> rel = OneToManyRelationship(app['ob22'], (app['ob20'], app['ob27']))

    >>> verifyObject(interfaces.IOneToManyRelationship, rel)
    True

    >>> container.add(rel)
    >>> container.add(OneToManyRelationship(
    ...     app['ob20'],
    ...     (app['ob23'], app['ob28'])))

The updated diagram looks like this::

        ob20              (ob26, obj24)       (ob26, obj23)
        |   |\                  |                   |
      ob21  | |               obj22               obj20
      |     | |                 |                   |
    ob22    | ob23        (ob20, obj27)       (ob23, obj28)
      |  \  |
    ob25  ob24

Alltogether there are now three cycles for ob22.

    >>> sorted(o.id for o in container.findTargets(app['ob22']))
    ['ob20', 'ob24', 'ob25', 'ob27']
    >>> sorted(o.id for o in container.findTargets(app['ob22'], None))
    ['ob20', 'ob21', 'ob22', 'ob23', 'ob24', 'ob25', 'ob27', 'ob28']

    >>> sorted(o.id for o in container.findTargets(app['ob20']))
    ['ob21', 'ob23', 'ob24', 'ob28']
    >>> sorted(o.id for o in container.findTargets(app['ob20'], None))
    ['ob20', 'ob21', 'ob22', 'ob23', 'ob24', 'ob25', 'ob27', 'ob28']

    >>> sorted(repr(c) for c in
    ...        container.findRelationships(app['ob22'], app['ob22'], None))
    ... # doctest: +NORMALIZE_WHITESPACE
    ['cycle(<Relationship from (<Demo ob22>,) to (<Demo ob20>, <Demo ob27>)>,
            <Relationship from (<Demo ob20>,) to (<Demo ob21>,)>,
            <Relationship from (<Demo ob21>,) to (<Demo ob22>,)>)',
     'cycle(<Relationship from (<Demo ob22>,) to (<Demo ob20>, <Demo ob27>)>,
            <Relationship from (<Demo ob20>,) to (<Demo ob24>,)>,
            <Relationship from (<Demo ob26>, <Demo ob24>) to (<Demo ob22>,)>)',
     'cycle(<Relationship from (<Demo ob22>,) to (<Demo ob24>,)>,
            <Relationship from (<Demo ob26>, <Demo ob24>) to (<Demo ob22>,)>)']

The `OneToManyRelationship`'s `targets` attribute is mutable, while it's
`sources` attribute is immutable.

    >>> rel.targets
    (<Demo ob20>, <Demo ob27>)
    >>> rel.targets = [app['ob28'], app['ob21']]

    >>> rel.sources
    (<Demo ob22>,)
    >>> rel.sources = (app['ob23'],)
    Traceback (most recent call last):
    ...
    AttributeError: can't set attribute

But the relationship has an additional mutable `source` attribute.

    >>> rel.source
    <Demo ob22>
    >>> rel.target = app['ob23']


=======
Changes
=======

2.0
===

The 2.x line is almost completely compatible with the 1.x line.
The one notable incompatibility does not affect the use of relationship
containers and is small enough that it will hopefully affect noone.

New Requirements
----------------

- zc.relation

Incompatibilities with 1.0
--------------------------

- `findRelationships` will now use the defaultTransitiveQueriesFactory if it
  is set.  Set ``maxDepth`` to 1 if you do not want this behavior.

- Some instantiation exceptions have different error messages.

Changes in 2.0
--------------

- the relationship index code has been moved out to zc.relation and
  significantly refactored there.  A fully backwards compatible subclass
  remains in zc.relationship.index

- support both 64-bit and 32-bit BTree families

- support specifying indexed values by passing callables rather than
2.0 (2018-06-19)

- in findValues and findValueTokens, `query` argument is now optional.  If
  the query evaluates to False in a boolean context, all values, or value
  tokens, are returned.  Value tokens are explicitly returned using the
  underlying BTree storage.  This can then be used directly for other BTree
  operations.

  In these and other cases, you should not ever mutate returned results!
  They may be internal data structures (and are intended to be so, so
  that they can be used for efficient set operations for other uses).
  The interfaces hopefully clarify what calls will return an internal
  data structure.

- README has a new beginning, which both demonstrates some of the new features
  and tries to be a bit simpler than the later sections.

- `findRelationships` and new method `findRelationshipTokens` can find
  relationships transitively and intransitively.  `findRelationshipTokens`
  when used intransitively repeats the behavior of `findRelationshipTokenSet`.
  (`findRelationshipTokenSet` remains in the API, not deprecated, a companion
  to `findValueTokenSet`.)

- 100% test coverage (per the usual misleading line analysis :-) of index
  module.  (Note that the significantly lower test coverage of the container
  code is unlikely to change without contributions: I use the index
  exclusively.  See plone.relations for a zc.relationship container with
  very good test coverage.)

- Tested with Python 2.7 and Python >= 3.5

- Added test extra to declare test dependency on ``zope.app.folder``.


1.1
===

(supports Zope 3.4/Zope 2.11/ZODB 3.8)

1.1.0
-----

- adjust to BTrees changes in ZODB 3.8 (thanks Juergen Kartnaller)

- converted buildout to rely exclusively on eggs

1.0
===

(supports Zope 3.3/Zope 2.10/ZODB 3.7)

1.0.2
-----

- Incorporated tests and bug fixes to relationship containers from
  Markus Kemmerling:

  * ManyToOneRelationship instantiation was broken

  * The `findRelationships` method misbehaved if both, `source` and `target`,
    are not None, but `bool(target)` evaluated to False.

  * ISourceRelationship and ITargetRelationship had errors.

1.0.1
-----

- Incorporated test and bug fix from Gabriel Shaar::

    if the target parameter is a container with no objects, then
    `shared.AbstractContainer.isLinked` resolves to False in a bool context and
    tokenization fails.  `target and tokenize({'target': target})` returns the
    target instead of the result of the tokenize function.

- Made README.rst tests pass on hopefully wider set of machines (this was a
  test improvement; the relationship index did not have the fragility).
  Reported by Gabriel Shaar.

1.0.0
-----

Initial release


