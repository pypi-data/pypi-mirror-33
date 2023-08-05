.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

==========================
collective.immediatecreate
==========================

.. image:: https://img.shields.io/pypi/v/collective.immediatecreate.svg
    :target: https://pypi.org/project/collective.immediatecreate/
    :alt: Latest PyPI version

.. image:: https://travis-ci.org/collective/collective.immediatecreate.svg?branch=master
    :target: https://travis-ci.org/collective/collective.immediatecreate

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/ambv/black

Folderish types are designed to be able to contain content.
However when you use ``collective.folderishtypes`` (or custom folderish types) in Plone and you simply add a folderish item and edit it immediately after adding you will see that all the assets you upload through the editor will be stored as siblings of the item you just created. This is due to the fact that the new item does not "exist" yet, that is, before it has been saved once.

This addon creates the object immediately, so items can be stored inside.

Features
--------

ID/ Shortname
    A valid (and intermediate) ID will be generated after "add <Type>..." has been clicked, so the item can be persisted.
    However, the ID changes when the user saves the content for the first time so the Plone's default behavior is retained.
    However, this feature might not be wanted by some users and is configureable.

Verification
    Additionally the drop-in-feature covers the usecase when an added type has mandatory fields or custom verification.
    All verification tasks are performed as usual when the user saves an item.

Cancel becomes Delete
    When the user interacts with the item after it has been automatically created the "cancel" button is turned into a "delete" button.
    If the cancel button is clicked, the item will be discarded.

Cleanup
    In order to get rid of initially created but never saved nor deleted items,
    a cleanup script is provided.


Installation
------------

Install collective.immediatecreate by adding it to your buildout::

    [buildout]

    ...

    eggs =
        collective.immediatecreate


and then running ``bin/buildout``

Restart Plone and install it in control panel under addons.


Activation
----------

After installation nothing changed.
The feature must be activated for a type first.
To make a type available for immediate add two chnaged need to be done:

1. Add the behavior `collective.immediatecreate` to the type in the control panel under `Dexterity Content Types`

2. Modify the Factory Type Information using the ZMI under `portal_types`.
   Change the value of  `Add view URL (Expression)` to `++add-immediate++TYPENAME`.

Configuration using GenericSetup
--------------------------------

In a policy profile in filesystem the a Type Information under `profiles/default/types/TYPENAME.xml` can be edited to make a type aware of immediate create::

    <?xml version="1.0"?>
    <object
        i18n:domain="plone"
        meta_type="Dexterity FTI"
        name="MyFolderishType"
        xmlns:i18n="http://xml.zope.org/namespaces/i18n">

        <!-- ... SNIP ... -->

        <property name="add_view_expr">string:${folder_url}/++addimmediate++MyFolderishType</property>

        <!-- ... SNIP ... -->

        <!-- Enabled behaviors -->
        <property name="behaviors" purge="False">
          <element value="collective.immediatecreate" />
        </property>

        <!-- ... SNIP ... -->
    </object>


Source Code
-----------

The sources are in a GIT DVCS with its main branches at `github <http://github.com/collective/collective.immediatecreate>`_.
There you can report issue too.

We'd be happy to see many forks and pull-requests to make this addon even better.

This package uses the `black coding style <https://github.com/ambv/black/>`_ with 79 chars line length.


Support
-------

Maintainers are `Jens Klein <mailto:jk@kleinundpartner.at>`_, `Georg Bernhard <mailto:G.Bernhard@akbild.ac.at>`_ and the BlueDynamics Alliance developer team.
We appreciate any contribution and if a release is needed to be done on pypi, please just contact one of us.
We also offer commercial support if any training, coaching, integration or adaptions are needed.

If you are having issues, please let us know.


License
-------

The project is licensed under the GPLv2.
