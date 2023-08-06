LIGO Follow-up Advocate Tools
=============================

| **Build** | **Test** |
| :-: | :-: | :-: |
| [![build status](https://git.ligo.org/emfollow/ligo-followup-advocate/badges/master/build.svg)](https://git.ligo.org/emfollow/ligo-followup-advocate/pipelines) | [![coverage report](https://git.ligo.org/emfollow/ligo-followup-advocate/badges/master/coverage.svg)](https://emfollow.docs.ligo.org/ligo-followup-advocate/) |

To install
----------

The easiest way to install `ligo-followup-advocate`, is with `pip`:

    pip install --user ligo-followup-advocate

To upgrade
----------

Once you have installed the package, to check for and install updates, run the
following command:

    pip install --user --upgrade ligo-followup-advocate

Example
-------

`ligo-followup-advocate` provides a single command to draft a GCN Circular
skeleton. Pass it the authors and the GraceDB ID as follows:

    ligo-followup-advocate compose \
        'A. Einstein (IAS)' 'S. Hawking (Cambridge)' \
        'I. Newton (Cambridge)' 'Data (Starfleet)' \
        'G184098'

Optionally, you can have the program open the draft in your default mail client
by passing it the `--mailto` option.

For a list of other supported commands, run:

    ligo-followup-advocate --help

For further options for composing circulars, run:

    ligo-followup-advocate compose --help

You can also invoke most functions directly from a Python interpreter, like
this:

    >>> from ligo import followup_advocate
    >>> text = followup_advocate.compose('G184098')

To develop
----------

To participate in development, clone the git repository:

    git clone git@git.ligo.org:emfollow/ligo-followup-advocate.git

To release
----------

The project is set up so that releases are automatically uploaded to PyPI
whenever a tag is created. Use the following steps to issue a release. In the
example below, we are assuming that the current version is 0.0.5, and that we
are releasing version 0.0.6.

1.  Check the latest [pipeline status](https://git.ligo.org/emfollow/ligo-followup-advocate/pipelines)
    to make sure that the master branch builds without any errors.

2.  Make sure that all significant changes since the last release are
    documented in `CHANGES.md`.

3.  Update the heading for the current release in `CHANGES.md` from
    `0.0.6 (unreleased)` to `0.0.6 (YYYY-MM-DD)` where `YYYY-MM-DD` is today's
    date.

4.  Change the version number in `ligo/followup_advocate/version.py` from
    `0.0.6.dev0` to `0.0.6`.

5.  Commit those changes:

        git commit -m "Update changelog for version 0.0.6"

6.  Tag the release:

        git tag v0.0.6 -m "Version 0.0.6"

7.  Add a new section to `CHANGES.md` like this:

        ## 0.0.7 (unreleased)

        - No changes yet.

8.  Update the version in `ligo/followup_advocate/version.py` to `0.0.7.dev0`.

9.  Commit the changes:

        git commit -m "Back to development"

10. Push everything to GitLab:

        git push master --tags

    Within a few minutes, the new package will be built and uploaded to PyPI.

See also
--------

See also the [FollowupAdvocates page][1] in the EM Follow-up Wiki.



[1]: https://wiki.ligo.org/Bursts/EMFollow/FollowupAdvocates
