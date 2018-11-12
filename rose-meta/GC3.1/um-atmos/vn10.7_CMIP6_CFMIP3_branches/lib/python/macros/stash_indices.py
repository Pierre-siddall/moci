#!/usr/bin/env python
# -*- coding: utf-8 -*-
# *****************************COPYRIGHT******************************
# (C) Crown copyright Met Office. All rights reserved.
# For further details please refer to the file COPYRIGHT.txt
# which you should have received as part of this distribution.
# *****************************COPYRIGHT******************************
"""This module contains code to correct STASH namelist indices.

The TidyStashTransform and TidyStashValidate classes attempt to give
informative and unique indices (sort-keys) to STASH-related namelists.

For domain, time, and use profile namelists, the index looks like:
    PROFILENAME_CHECKSUM
e.g.
    namelist:umstash_domain(uns_0ddb75f0)

where PROFILENAME is the profile name and CHECKSUM is the first 8
characters of the SHA1 checksum of the dumped section text as found
in a rose config file, excluding the section header itself and the
profile name option (if relevant).

For streq namelists, the index looks like:
    STASHCODE_CHECKSUM
e.g.
    namelist:umstash_streq(09204_06770664)
where STASHCODE is the 5 digit section and item combination for that
request and CHECKSUM is as before.

For items namelists, the index looks like:
    CHECKSUM
e.g.
    namelist:items(0049721c)
where CHECKSUM is as before.

We have 16^8 possible checksum results for a given namelist name, and
the probability that at least two different namelist contents will have
the same checksum result (collide) follows the birthday problem,
assuming a good, nicely distributed checksum algorithm.

This gives a 50/50 probability of collision in a pool of about 80000
namelists, which a given application is unlikely to have access to.
There is a 1 in 100 chance of collision with about 10000 namelists.
There is a 1 in 24000 chance of collision with about 600. A collision
leads to a transform macro warning: 'Cannot rename: hash collision'.

On the command line (in Bash) creating a new checksum part of the index
can be done as follows (vary according to namelist type):
index=$(rose config --file=rose-app.conf 'namelist:umstash_time(83)' | \
        sed "/^tim_name/d" | sha1sum)
echo ${index:0:8}
You'll then need to prefix the profile name or STASH code for profile
and streq namelists respectively, followed by an underscore. items
namelists have no prefix and just have the checksum result as an index.

To run this macro standalone to test unit tests
export PYTHONPATH=$ROSE_HOME/lib/python/ 
first.

$ROSE_HOME should be replaced with the path to the root directory of your 
local Rose installation, which you can locate by running rose --version

"""


import StringIO
import ast
import hashlib
import unittest

import rose.config
import rose.macro


ERROR_ITEMS_OVERWRITE = (
    "Source/domain clash with namelist:items({0}) will cause UM abort")
SECTION_FORMAT = "{0}({1})"
STASH_SECTION_BASES = ["namelist:umstash_domain", "namelist:items",
                       "namelist:umstash_streq", "namelist:umstash_time",
                       "namelist:umstash_use"]
STASH_SECTION_BASES_NO_INCLUDE_OPTS_MAP = {"namelist:umstash_domain": ["dom_name"],
                                           "namelist:umstash_time": ["tim_name"],
                                           "namelist:umstash_use": ["use_name"],
                                           "namelist:items": ["ancilfilename"]}
STASH_SECTION_BASES_POINTER_OPT_MAP = {"namelist:umstash_domain": "dom_name",
                                       "namelist:umstash_time": "tim_name",
                                       "namelist:umstash_use": "use_name"}
STASH_SECTION_STREQ_PREFIX = "namelist:umstash_streq("
STASH_SECTION_BASES_CAN_HAVE_INDEX_PREFIXES = [
    "namelist:umstash_domain", "namelist:umstash_streq", "namelist:umstash_time", "namelist:umstash_use"]
STASH_SECTION_BASE_INDEX_PREFIX_RECIPES = {
    "namelist:umstash_streq": ["%02d%03d", ("isec", "item")]}


class TidyStashTransform(rose.macro.MacroBase):

    """Correct the index of STASH-related namelists."""

    ABORT_COLLISION = "Cannot rename: hash collision: {0}"
    ABORT_RENAME = "Cannot rename: {0} exists (identical)"
    CHANGE_DELETE = "Deleted - identical to {0}"
    CHANGE_POINTER = "{0} => {1} (identical)"
    CHANGE_RENAME_FROM = "Renamed from {0}"
    CHANGE_RENAME_TO = "Renamed to {0}"
    KEEP_DUPLICATED_NAMELISTS = True
    WARNING_RENAME = "Warning: {0} exists (identical)"

    def transform(self, config, meta_config=None):
        """Rename sections using a hash of their contents."""
        self._resolve_dupl_namelists(config)
        for data in get_section_new_indices(config):
            section_base, old_index, dest_index = data
            # section_base is the section minus index - e.g. namelist:umstash_domain.
            # old_index is the current index of that section.
            # dest_index is the new, correct index for that section.
            old_section = SECTION_FORMAT.format(section_base, old_index)
            dest_section = SECTION_FORMAT.format(section_base, dest_index)
            if config.get([dest_section]) is not None:
                # A section already exists in the config with this index.
                self._check_for_hash_collision(
                    config, section_base, (old_index, dest_index),
                )
                continue
            # Rename (and report renaming) the section and child variables.
            old_node = config.unset([old_section])
            self.add_report(old_section, None, None,
                            self.CHANGE_RENAME_TO.format(dest_section))
            old_id_opt_values = []
            for opt, node in old_node.value.items():
                old_id = rose.CONFIG_DELIMITER.join([old_section, opt])
                old_id_opt_values.append((old_id, opt, node.value))
            self.add_report(dest_section, None, None,
                            self.CHANGE_RENAME_FROM.format(old_section))
            for old_id, opt, value in old_id_opt_values:
                self.add_report(dest_section, opt, value,
                                self.CHANGE_RENAME_FROM.format(old_id))
            config.value.update({dest_section: old_node})
        self._report_dupl_items_namelists(config)
        return config, self.reports

    def _resolve_dupl_namelists(self, config):
        """Delete or report namelists with functionally identical contents.

        This loops through duplicate namelist resolution. We need to
        loop because namelist:umstash_streq sections can become duplicate
        if profile duplicates are resolved.

        """
        has_unresolved_duplicates = True
        while has_unresolved_duplicates:
            has_unresolved_duplicates = False
            dest_hash_indices = {}
            for data in get_section_new_indices(config):
                section_base, old_index, dest_index = data
                dest_section = SECTION_FORMAT.format(section_base, dest_index)

                # Use the hash to check duplication.
                # Index example: normal1-abcdef12. Hash example - abcdef12.
                dest_hash = dest_index.rsplit("_", 1)[-1]
                if dest_hash in dest_hash_indices:
                    # Another section wants to be renamed with this hash.
                    other_index, other_dest_index = (
                        dest_hash_indices[dest_hash])
                elif config.get([dest_section]) is not None:
                    # Another section already exists with this index.
                    other_index = dest_index
                    other_dest_index = dest_index
                else:
                    # No problem with this new hash (yet!) - continue.
                    dest_hash_indices[dest_hash] = (old_index, dest_index)
                    continue

                has_unresolved_duplicates = (
                    self._handle_dupl_namelists(
                        config, section_base,
                        (old_index, dest_index),
                        (other_index, other_dest_index),
                        dest_hash=dest_hash
                    ) or has_unresolved_duplicates
                )

    def _handle_dupl_namelists(self, config, section_base,
                               source_old_dest_indices,
                               other_old_dest_indices,
                               dest_hash=None):
        """Report or resolve a clash between two sections."""
        index, dest_index = source_old_dest_indices
        other_index, other_dest_index = other_old_dest_indices

        # Check for hash collision (different contents, same hash).
        if self._check_for_hash_collision(
                config, section_base, (index, other_index),
                dest_hash=dest_hash):
            # This is not a duplicate, but a hash collision (rare).
            return False

        # The contents of the sections must be the same.
        if self.KEEP_DUPLICATED_NAMELISTS:
            # This is a real duplicated namelist, but we must keep it/
            dest_section = SECTION_FORMAT.format(section_base, dest_index)
            if dest_index == other_dest_index:
                # They will have the same destination index.
                old_section = SECTION_FORMAT.format(section_base, index)
                self.add_report(
                    old_section, None, None,
                    self.ABORT_RENAME.format(dest_section),
                    is_warning=True
                )
            else:
                # They will have the same hash but not the same index.
                # The rename can proceed, but we should give a warning.
                other_dest_section = SECTION_FORMAT.format(
                    section_base, other_dest_index)
                self.add_report(
                    dest_section, None, None,
                    self.WARNING_RENAME.format(other_dest_section),
                    is_warning=True
                )
            return False

        # Must be a real duplicated namelist and we can remove it.
        self._remove_duplicate_namelist(
            config, section_base, index, other_index)
        return True

    def _remove_duplicate_namelist(self, config, section_base, index,
                                   other_index):
        """Remove a duplicate namelist and handle re-referencing."""
        old_section = SECTION_FORMAT.format(section_base, index)
        other_section = SECTION_FORMAT.format(section_base, other_index)
        pointer_opt = STASH_SECTION_BASES_POINTER_OPT_MAP.get(
            section_base)
        # pointer_opt is e.g. dom_name for namelist:umstash_domain sections.
        if pointer_opt is not None:
            old_pointer_value = config.get_value([old_section, pointer_opt])
            new_pointer_value = config.get_value([other_section, pointer_opt])
        config.unset([old_section])
        self.add_report(old_section, None, None,
                        self.CHANGE_DELETE.format(other_section))
        # Adjust any pointer names to use the other section.
        if pointer_opt is not None:
            keys_nodes = list(config.walk())
            keys_nodes.sort(lambda x, y:
                            rose.config.sort_settings(x[0][0],
                                                      y[0][0]))
            # Loop through to find namelist:umstash_streq sections using this profile.
            for keys, node in keys_nodes:
                if not keys[0].startswith(STASH_SECTION_STREQ_PREFIX):
                    continue
                if (len(keys) == 2 and keys[1] == pointer_opt and
                        node.value == old_pointer_value):
                    node.value = new_pointer_value
                    self.add_report(
                        keys[0], keys[1], node.value,
                        self.CHANGE_POINTER.format(
                            old_pointer_value,
                            new_pointer_value
                        )
                    )
        return True

    def _report_dupl_items_namelists(self, config):
        """Report errors for functionally duplicated ITEMS namelists."""
        for section, index in get_dupl_items_problems(config):
            self.add_report(section, None, None,
                            ERROR_ITEMS_OVERWRITE.format(index),
                            is_warning=True)

    def _check_for_hash_collision(self, config, section_base, indices,
                                  dest_hash=None):
        """Do the sections have different contents and want the same hash?"""
        no_include_opts = STASH_SECTION_BASES_NO_INCLUDE_OPTS_MAP.get(
            section_base, [])
        section1 = SECTION_FORMAT.format(section_base, indices[0])
        section2 = SECTION_FORMAT.format(section_base, indices[1])
        text1 = dump_section(config, section1,
                             no_include_opts=no_include_opts)
        text2 = dump_section(config, section2,
                             no_include_opts=no_include_opts)
        if text1 != text2:
            # The text is different but the desired hash or index is the same.
            if dest_hash is None:
                index = indices[1]
            else:
                index = dest_hash
            self.add_report(section1, None, None,
                            self.ABORT_COLLISION.format(index),
                            is_warning=True)
            return True
        return False


class TidyStashTransformPruneDuplicated(TidyStashTransform):

    """Correct the index of STASH-related namelists and prune duplicates."""

    KEEP_DUPLICATED_NAMELISTS = False


class TidyStashValidate(rose.macro.MacroBase):

    """Check if STASH-related namelists have the right index."""

    ERROR_INDEX = "Wrong index: {0} should be {1}"
    ERROR_INDEX_CLASH = "Identical sections: "
    ERROR_INDEX_HASH_OK = "Wrong index prefix (hash OK): {0} should be {1}"

    def validate(self, config, meta_config=None):
        """Validate indices."""
        for section_base in STASH_SECTION_BASES:
            no_include_opts = STASH_SECTION_BASES_NO_INCLUDE_OPTS_MAP.get(
                section_base, [])
            # Build a map of hashes vs indices. We can then check this map
            # to see which hashes share indices (= duplicate!).
            dest_hash_map = {}
            for index in list(get_all_indices(config, section_base)):
                this_hash = index.rsplit("_", 1)[-1]
                dest_hash_map.setdefault(index.rsplit("_", 1)[-1], [])
                dest_hash_map[this_hash].append(index)

            # Handle the incorrect indices, choosing how to report them.
            for old_index, dest_index in get_new_indices(config, section_base,
                                                         no_include_opts):
                # The section wants to be renamed from old_index to dest_index.
                old_hash = old_index.rsplit("_", 1)[-1]
                dest_hash = dest_index.rsplit("_", 1)[-1]

                # Remove old_index from the old hash list.
                if (old_hash in dest_hash_map and
                        old_index in dest_hash_map[old_hash]):
                    dest_hash_map[old_hash].remove(old_index)
                    if not dest_hash_map[old_hash]:
                        dest_hash_map.pop(old_hash)

                # Add dest_index to the destination hash list.
                dest_hash_map.setdefault(dest_hash, [])
                dest_hash_map[dest_hash].append(old_index)

                section = SECTION_FORMAT.format(section_base, old_index)
                dest_section = SECTION_FORMAT.format(section_base, dest_index)
                node = config.get([dest_section])
                if node is not None:
                    # Clash with existing section to be reported later.
                    continue
                if old_hash == dest_hash:
                    # The hash is OK, but the index prefix must be wrong.
                    self.add_report(section, None, None,
                                    self.ERROR_INDEX_HASH_OK.format(
                                        old_index, dest_index))
                else:
                    # The whole index is incorrect.
                    self.add_report(
                        section, None, None,
                        self.ERROR_INDEX.format(old_index, dest_index)
                    )

            # Handle index clashes.
            self._handle_namelist_clashes(section_base, dest_hash_map)

        # Validate items namelists with only-functionally-identical options.
        self._validate_dupl_items_namelists(config)
        return self.reports

    def _handle_namelist_clashes(self, section_base, dest_hash_map):
        """Handle namelists that have the same destination hash or index."""
        for same_content_indices in dest_hash_map.values():
            if len(same_content_indices) == 1:
                # Only one index has this hash.
                continue
            # Multiple sections (indices) want the same hash.
            # Report all the different sections.
            sections = []
            index = same_content_indices[0]
            rep_section = SECTION_FORMAT.format(section_base, index)
            sections.append(rep_section)
            for same_content_index in same_content_indices[1:]:
                if same_content_index == index:
                    continue
                sections.append(
                    SECTION_FORMAT.format(section_base,
                                          same_content_index)
                )
            text = self.ERROR_INDEX_CLASH + " == ".join(sections)
            self.add_report(rep_section, None, None, text)

    def _validate_dupl_items_namelists(self, config):
        """Report errors for functionally duplicated ITEMS namelists."""
        for section, index in get_dupl_items_problems(config):
            self.add_report(section, None, None,
                            ERROR_ITEMS_OVERWRITE.format(index))


def dump_section(config, section, no_include_opts=None):
    """Return some option=value multiline text used for checksums."""
    new_config = rose.config.ConfigNode()
    if no_include_opts is None:
        no_include_opts = []
    for keylist, opt_node in config.walk([section]):
        option = keylist[1]
        if option in no_include_opts:
            continue
        new_config.value[option] = opt_node
    config_string_file = StringIO.StringIO()
    rose.config.dump(new_config, config_string_file)
    config_string_file.seek(0)
    return config_string_file.read()


def get_all_indices(config, section_base):
    """Return all indices for a section_base in config.

    config should be a rose.config.ConfigNode instance.
    section_base should be the section name without an index - e.g.
    "namelist:foo".

    """
    for section in config.value.keys():
        if not section.startswith(section_base + "("):
            continue
        node = config.get([section])
        if not isinstance(node.value, dict):
            continue
        yield get_index_from_section(section)


def get_dupl_items_problems(config):
    """Report only-different-by-source-domain items sections."""
    items_str_pure_dict = {}
    items_str_dict = {}
    sections_nodes = list(config.walk())
    sections_nodes.sort(lambda x, y:
                        rose.config.sort_settings(x[0][0], y[0][0]))
    for keys, sect_node in sections_nodes:
        if not isinstance(sect_node.value, dict):
            continue
        if len(keys) != 1:
            continue
        section = keys[0]
        if section.startswith("namelist:items("):
            str_of_namelist = dump_section(
                config, section,
                no_include_opts=["domain", "source"]
            )
            pure_str_of_namelist = dump_section(config, section)
            this_index = get_index_from_section(section)
            items_str_dict.setdefault(str_of_namelist, [])
            items_str_dict[str_of_namelist].append(this_index)
            items_str_pure_dict.setdefault(pure_str_of_namelist, [])
            items_str_pure_dict[pure_str_of_namelist].append(this_index)
    pure_dupl_indices = []
    for indices in items_str_pure_dict.values():
        if len(indices) > 1:
            # These namelists are totally duplicated.
            pure_dupl_indices.extend(indices)
    for str_of_namelist, indices in items_str_dict.items():
        if len(indices) > 1:
            # These namelists are at least functionally duplicated.
            for index in indices[1:]:
                if index in pure_dupl_indices:
                    # It is actually a perfect copy of another items namelist.
                    # This will be reported in the normal duplicate checking.
                    pass
                else:
                    # It is just a functionally duplicated namelist.
                    section = get_section_from_index("namelist:items", index)
                    yield(section, indices[0])


def get_index_from_section(section):
    """Return the index string from an indexed section name."""
    return section.rsplit("(", 1)[1].rstrip(")")


def get_new_indices(config, section_base_name, no_include_opts=None):
    """Return a list of non-matching indices, if any."""
    if no_include_opts is None:
        no_include_opts = []
    keys = config.value.keys()
    keys.sort(rose.config.sort_settings)
    for section in keys:
        if not section.startswith(section_base_name + "("):
            continue
        text = dump_section(config, section, no_include_opts)
        old_index = get_index_from_section(section)
        dest_index_prefix = get_section_index_prefix(
            config, section, section_base_name)
        dest_index_suffix = hashlib.sha1(text).hexdigest()[:8]
        if dest_index_prefix:
            dest_index = dest_index_prefix + "_" + dest_index_suffix
        else:
            dest_index = dest_index_suffix
        if old_index != dest_index:
            yield (old_index, dest_index)


def get_section_index_prefix(config, section, section_base_name):
    """Prepend a user-friendly content-specific piece of info to the index."""
    if section_base_name not in STASH_SECTION_BASES_CAN_HAVE_INDEX_PREFIXES:
        return ""
    if section_base_name in STASH_SECTION_BASE_INDEX_PREFIX_RECIPES:
        recipe = STASH_SECTION_BASE_INDEX_PREFIX_RECIPES[section_base_name]
        format_string, options = recipe
        option_values = []
        for option in options:
            node = config.get([section, option])
            if node is None:
                return ""
            option_values.append(ast.literal_eval(node.value))
        option_values = tuple(option_values)
        return format_string % option_values
    info_opts = STASH_SECTION_BASES_NO_INCLUDE_OPTS_MAP.get(section_base_name)
    if info_opts is None:
        return ""
    info_opt = info_opts[0]
    node = config.get([section, info_opt])
    if node is None or any(_ in node.value for _ in "()[]="):
        return ""
    return node.value.strip("'\"").lower()


def get_section_from_index(section_base, index):
    """Return an indexed section name from a section base name and an index."""
    return section_base + "({0})".format(index)


def get_section_new_indices(config):
    """Get newly calculated indices for the config."""
    for section_base in STASH_SECTION_BASES:
        no_include_opts = STASH_SECTION_BASES_NO_INCLUDE_OPTS_MAP.get(
            section_base, [])
        for old_index, dest_index in get_new_indices(config, section_base,
                                                     no_include_opts):
            yield section_base, old_index, dest_index


class STASHIndexTestSuite(unittest.TestCase):

    """Class to test the macros."""

    TEST_CONFIG_STRING = """[namelist:domain_nml]
x=1
y=2

[namelist:foo]
a=1
b=2

# items(1)
[namelist:items(1)]
domain=1
item=302
section=0
source=4

# items(2), functionally equal to items(1)
[namelist:items(2)]
domain=1
item=302
section=0
source=2

# items(3), equal to items(1)
[namelist:items(3)]
domain=1
item=302
section=0
source=4

# domain(1) (=2)
[namelist:umstash_domain(1)]
dom_name='identical1'
imn=0

# domain(2) (=1)
[namelist:umstash_domain(2)]
dom_name='identical2'
imn=0

# domain(3)
[namelist:umstash_domain(3)]
dom_name='normal1'
imn=1
imsk=1

# domain(4)
[namelist:umstash_domain(4)]
dom_name='normal2'
imn=1
imsk=2

# streq(1) (if dup removed, =2)
[namelist:umstash_streq(1)]
dom_name='identical2'
isec=0
item=2
package='foo'
tim_name='normal1'
use_name='identical1'

# streq(2) (if dup removed, =1)
[namelist:umstash_streq(2)]
dom_name='identical1'
isec=0
item=2
package='foo'
tim_name='normal1'
use_name='identical2'

# streq(3) (=4)
[namelist:umstash_streq(3)]
dom_name='normal1'
isec=5
item=11
package='foo'
tim_name='normal1'
use_name='identical2'

# streq(4) (=3)
[namelist:umstash_streq(4)]
dom_name='normal1'
isec=5
item=11
package='foo'
tim_name='normal1'
use_name='identical2'

# streq(5)
[namelist:umstash_streq(5)]
dom_name='normal2'
isec=5
item=11
package='foo'
tim_name='normal2'
use_name='identical1'

# streq(d9ad6b73), old index format.
[namelist:umstash_streq(d9ad6b73)]
dom_name='normal2'
isec=50
item=999
package='bar'
tim_name='normal2'
use_name='identical1'

# time(1), user-ignored
[!namelist:umstash_time(1)]
tim_name='normal1'
iend=9

# time(2)
[namelist:umstash_time(2)]
tim_name='normal2'
iend=8

# use(1) (=2)
[namelist:umstash_use(1)]
use_name='identical1'
iunt=60

# use(2) (=1)
[namelist:umstash_use(2)]
use_name='identical2'
iunt=60

# use(3)
[namelist:umstash_use(3)]
use_name='normal1'
!iunt=60
"""

    TEST_TRANSFORM_KEEP_CONFIG_STRING = """[namelist:domain_nml]
x=1
y=2

[namelist:foo]
a=1
b=2

# items(3), equal to items(1)
[namelist:items(3)]
domain=1
item=302
section=0
source=4

# items(2), functionally equal to items(1)
[namelist:items(521d3f6c)]
domain=1
item=302
section=0
source=2

# items(1)
[namelist:items(97a136a1)]
domain=1
item=302
section=0
source=4

# domain(1) (=2)
[namelist:umstash_domain(identical1_ed6e1b5e)]
dom_name='identical1'
imn=0

# domain(2) (=1)
[namelist:umstash_domain(identical2_ed6e1b5e)]
dom_name='identical2'
imn=0

# domain(3)
[namelist:umstash_domain(normal1_4ccb4417)]
dom_name='normal1'
imn=1
imsk=1

# domain(4)
[namelist:umstash_domain(normal2_2af126ec)]
dom_name='normal2'
imn=1
imsk=2

# streq(4) (=3)
[namelist:umstash_streq(4)]
dom_name='normal1'
isec=5
item=11
package='foo'
tim_name='normal1'
use_name='identical2'

# streq(2) (if dup removed, =1)
[namelist:umstash_streq(00002_8f159890)]
dom_name='identical1'
isec=0
item=2
package='foo'
tim_name='normal1'
use_name='identical2'

# streq(1) (if dup removed, =2)
[namelist:umstash_streq(00002_94eb9a06)]
dom_name='identical2'
isec=0
item=2
package='foo'
tim_name='normal1'
use_name='identical1'

# streq(5)
[namelist:umstash_streq(05011_263d8bd0)]
dom_name='normal2'
isec=5
item=11
package='foo'
tim_name='normal2'
use_name='identical1'

# streq(3) (=4)
[namelist:umstash_streq(05011_f4c34d08)]
dom_name='normal1'
isec=5
item=11
package='foo'
tim_name='normal1'
use_name='identical2'

# streq(d9ad6b73), old index format.
[namelist:umstash_streq(50999_d9ad6b73)]
dom_name='normal2'
isec=50
item=999
package='bar'
tim_name='normal2'
use_name='identical1'

# time(1), user-ignored
[!namelist:umstash_time(normal1_16055de9)]
iend=9
tim_name='normal1'

# time(2)
[namelist:umstash_time(normal2_47fd949e)]
iend=8
tim_name='normal2'

# use(1) (=2)
[namelist:umstash_use(identical1_54db5261)]
iunt=60
use_name='identical1'

# use(2) (=1)
[namelist:umstash_use(identical2_54db5261)]
iunt=60
use_name='identical2'

# use(3)
[namelist:umstash_use(normal1_39bbfabd)]
!iunt=60
use_name='normal1'
"""

    TEST_TRANSFORM_KEEP_OUTPUT = (
        """stash_indices.TidyStashTransform: changes: 90
    namelist:umstash_domain(1)=None=None
        Renamed to namelist:umstash_domain(identical1_ed6e1b5e)
    namelist:umstash_domain(identical1_ed6e1b5e)=None=None
        Renamed from namelist:umstash_domain(1)
    namelist:umstash_domain(identical1_ed6e1b5e)=dom_name='identical1'
        Renamed from namelist:umstash_domain(1)=dom_name
    namelist:umstash_domain(identical1_ed6e1b5e)=imn=0
        Renamed from namelist:umstash_domain(1)=imn
    namelist:umstash_domain(2)=None=None
        Renamed to namelist:umstash_domain(identical2_ed6e1b5e)
    namelist:umstash_domain(identical2_ed6e1b5e)=None=None
        Renamed from namelist:umstash_domain(2)
    namelist:umstash_domain(identical2_ed6e1b5e)=dom_name='identical2'
        Renamed from namelist:umstash_domain(2)=dom_name
    namelist:umstash_domain(identical2_ed6e1b5e)=imn=0
        Renamed from namelist:umstash_domain(2)=imn
    namelist:umstash_domain(3)=None=None
        Renamed to namelist:umstash_domain(normal1_4ccb4417)
    namelist:umstash_domain(normal1_4ccb4417)=None=None
        Renamed from namelist:umstash_domain(3)
    namelist:umstash_domain(normal1_4ccb4417)=imsk=1
        Renamed from namelist:umstash_domain(3)=imsk
    namelist:umstash_domain(normal1_4ccb4417)=dom_name='normal1'
        Renamed from namelist:umstash_domain(3)=dom_name
    namelist:umstash_domain(normal1_4ccb4417)=imn=1
        Renamed from namelist:umstash_domain(3)=imn
    namelist:umstash_domain(4)=None=None
        Renamed to namelist:umstash_domain(normal2_2af126ec)
    namelist:umstash_domain(normal2_2af126ec)=None=None
        Renamed from namelist:umstash_domain(4)
    namelist:umstash_domain(normal2_2af126ec)=imsk=2
        Renamed from namelist:umstash_domain(4)=imsk
    namelist:umstash_domain(normal2_2af126ec)=dom_name='normal2'
        Renamed from namelist:umstash_domain(4)=dom_name
    namelist:umstash_domain(normal2_2af126ec)=imn=1
        Renamed from namelist:umstash_domain(4)=imn
    namelist:items(1)=None=None
        Renamed to namelist:items(97a136a1)
    namelist:items(97a136a1)=None=None
        Renamed from namelist:items(1)
    namelist:items(97a136a1)=item=302
        Renamed from namelist:items(1)=item
    namelist:items(97a136a1)=domain=1
        Renamed from namelist:items(1)=domain
    namelist:items(97a136a1)=section=0
        Renamed from namelist:items(1)=section
    namelist:items(97a136a1)=source=4
        Renamed from namelist:items(1)=source
    namelist:items(2)=None=None
        Renamed to namelist:items(521d3f6c)
    namelist:items(521d3f6c)=None=None
        Renamed from namelist:items(2)
    namelist:items(521d3f6c)=item=302
        Renamed from namelist:items(2)=item
    namelist:items(521d3f6c)=domain=1
        Renamed from namelist:items(2)=domain
    namelist:items(521d3f6c)=section=0
        Renamed from namelist:items(2)=section
    namelist:items(521d3f6c)=source=2
        Renamed from namelist:items(2)=source
    namelist:umstash_streq(1)=None=None
        Renamed to namelist:umstash_streq(00002_94eb9a06)
    namelist:umstash_streq(00002_94eb9a06)=None=None
        Renamed from namelist:umstash_streq(1)
    namelist:umstash_streq(00002_94eb9a06)=package='foo'
        Renamed from namelist:umstash_streq(1)=package
    namelist:umstash_streq(00002_94eb9a06)=tim_name='normal1'
        Renamed from namelist:umstash_streq(1)=tim_name
    namelist:umstash_streq(00002_94eb9a06)=use_name='identical1'
        Renamed from namelist:umstash_streq(1)=use_name
    namelist:umstash_streq(00002_94eb9a06)=dom_name='identical2'
        Renamed from namelist:umstash_streq(1)=dom_name
    namelist:umstash_streq(00002_94eb9a06)=isec=0
        Renamed from namelist:umstash_streq(1)=isec
    namelist:umstash_streq(00002_94eb9a06)=item=2
        Renamed from namelist:umstash_streq(1)=item
    namelist:umstash_streq(2)=None=None
        Renamed to namelist:umstash_streq(00002_8f159890)
    namelist:umstash_streq(00002_8f159890)=None=None
        Renamed from namelist:umstash_streq(2)
    namelist:umstash_streq(00002_8f159890)=package='foo'
        Renamed from namelist:umstash_streq(2)=package
    namelist:umstash_streq(00002_8f159890)=tim_name='normal1'
        Renamed from namelist:umstash_streq(2)=tim_name
    namelist:umstash_streq(00002_8f159890)=use_name='identical2'
        Renamed from namelist:umstash_streq(2)=use_name
    namelist:umstash_streq(00002_8f159890)=dom_name='identical1'
        Renamed from namelist:umstash_streq(2)=dom_name
    namelist:umstash_streq(00002_8f159890)=isec=0
        Renamed from namelist:umstash_streq(2)=isec
    namelist:umstash_streq(00002_8f159890)=item=2
        Renamed from namelist:umstash_streq(2)=item
    namelist:umstash_streq(3)=None=None
        Renamed to namelist:umstash_streq(05011_f4c34d08)
    namelist:umstash_streq(05011_f4c34d08)=None=None
        Renamed from namelist:umstash_streq(3)
    namelist:umstash_streq(05011_f4c34d08)=package='foo'
        Renamed from namelist:umstash_streq(3)=package
    namelist:umstash_streq(05011_f4c34d08)=tim_name='normal1'
        Renamed from namelist:umstash_streq(3)=tim_name
    namelist:umstash_streq(05011_f4c34d08)=use_name='identical2'
        Renamed from namelist:umstash_streq(3)=use_name
    namelist:umstash_streq(05011_f4c34d08)=dom_name='normal1'
        Renamed from namelist:umstash_streq(3)=dom_name
    namelist:umstash_streq(05011_f4c34d08)=isec=5
        Renamed from namelist:umstash_streq(3)=isec
    namelist:umstash_streq(05011_f4c34d08)=item=11
        Renamed from namelist:umstash_streq(3)=item
    namelist:umstash_streq(5)=None=None
        Renamed to namelist:umstash_streq(05011_263d8bd0)
    namelist:umstash_streq(05011_263d8bd0)=None=None
        Renamed from namelist:umstash_streq(5)
    namelist:umstash_streq(05011_263d8bd0)=package='foo'
        Renamed from namelist:umstash_streq(5)=package
    namelist:umstash_streq(05011_263d8bd0)=tim_name='normal2'
        Renamed from namelist:umstash_streq(5)=tim_name
    namelist:umstash_streq(05011_263d8bd0)=use_name='identical1'
        Renamed from namelist:umstash_streq(5)=use_name
    namelist:umstash_streq(05011_263d8bd0)=dom_name='normal2'
        Renamed from namelist:umstash_streq(5)=dom_name
    namelist:umstash_streq(05011_263d8bd0)=isec=5
        Renamed from namelist:umstash_streq(5)=isec
    namelist:umstash_streq(05011_263d8bd0)=item=11
        Renamed from namelist:umstash_streq(5)=item
    namelist:umstash_streq(d9ad6b73)=None=None
        Renamed to namelist:umstash_streq(50999_d9ad6b73)
    namelist:umstash_streq(50999_d9ad6b73)=None=None
        Renamed from namelist:umstash_streq(d9ad6b73)
    namelist:umstash_streq(50999_d9ad6b73)=package='bar'
        Renamed from namelist:umstash_streq(d9ad6b73)=package
    namelist:umstash_streq(50999_d9ad6b73)=tim_name='normal2'
        Renamed from namelist:umstash_streq(d9ad6b73)=tim_name
    namelist:umstash_streq(50999_d9ad6b73)=use_name='identical1'
        Renamed from namelist:umstash_streq(d9ad6b73)=use_name
    namelist:umstash_streq(50999_d9ad6b73)=dom_name='normal2'
        Renamed from namelist:umstash_streq(d9ad6b73)=dom_name
    namelist:umstash_streq(50999_d9ad6b73)=isec=50
        Renamed from namelist:umstash_streq(d9ad6b73)=isec
    namelist:umstash_streq(50999_d9ad6b73)=item=999
        Renamed from namelist:umstash_streq(d9ad6b73)=item
    namelist:umstash_time(1)=None=None
        Renamed to namelist:umstash_time(normal1_16055de9)
    namelist:umstash_time(normal1_16055de9)=None=None
        Renamed from namelist:umstash_time(1)
    namelist:umstash_time(normal1_16055de9)=tim_name='normal1'
        Renamed from namelist:umstash_time(1)=tim_name
    namelist:umstash_time(normal1_16055de9)=iend=9
        Renamed from namelist:umstash_time(1)=iend
    namelist:umstash_time(2)=None=None
        Renamed to namelist:umstash_time(normal2_47fd949e)
    namelist:umstash_time(normal2_47fd949e)=None=None
        Renamed from namelist:umstash_time(2)
    namelist:umstash_time(normal2_47fd949e)=tim_name='normal2'
        Renamed from namelist:umstash_time(2)=tim_name
    namelist:umstash_time(normal2_47fd949e)=iend=8
        Renamed from namelist:umstash_time(2)=iend
    namelist:umstash_use(1)=None=None
        Renamed to namelist:umstash_use(identical1_54db5261)
    namelist:umstash_use(identical1_54db5261)=None=None
        Renamed from namelist:umstash_use(1)
    namelist:umstash_use(identical1_54db5261)=iunt=60
        Renamed from namelist:umstash_use(1)=iunt
    namelist:umstash_use(identical1_54db5261)=use_name='identical1'
        Renamed from namelist:umstash_use(1)=use_name
    namelist:umstash_use(2)=None=None
        Renamed to namelist:umstash_use(identical2_54db5261)
    namelist:umstash_use(identical2_54db5261)=None=None
        Renamed from namelist:umstash_use(2)
    namelist:umstash_use(identical2_54db5261)=iunt=60
        Renamed from namelist:umstash_use(2)=iunt
    namelist:umstash_use(identical2_54db5261)=use_name='identical2'
        Renamed from namelist:umstash_use(2)=use_name
    namelist:umstash_use(3)=None=None
        Renamed to namelist:umstash_use(normal1_39bbfabd)
    namelist:umstash_use(normal1_39bbfabd)=None=None
        Renamed from namelist:umstash_use(3)
    namelist:umstash_use(normal1_39bbfabd)=iunt=60
        Renamed from namelist:umstash_use(3)=iunt
    namelist:umstash_use(normal1_39bbfabd)=use_name='normal1'
        Renamed from namelist:umstash_use(3)=use_name
stash_indices.TidyStashTransform: warnings: 5
    namelist:umstash_domain(identical2_ed6e1b5e)=None=None
        Warning: namelist:umstash_domain(identical1_ed6e1b5e) exists (identical)
    namelist:items(3)=None=None
        Cannot rename: namelist:items(97a136a1) exists (identical)
    namelist:umstash_streq(4)=None=None
        Cannot rename: namelist:umstash_streq(05011_f4c34d08) exists (identical)
    namelist:umstash_use(identical2_54db5261)=None=None
        Warning: namelist:umstash_use(identical1_54db5261) exists (identical)
    namelist:items(521d3f6c)=None=None
        Source/domain clash with namelist:items(3) will cause UM abort
""")

    TEST_TRANSFORM_CONFIG_STRING = """[namelist:domain_nml]
x=1
y=2

[namelist:foo]
a=1
b=2

# items(2), functionally equal to items(1)
[namelist:items(521d3f6c)]
domain=1
item=302
section=0
source=2

# items(1)
[namelist:items(97a136a1)]
domain=1
item=302
section=0
source=4

# domain(1) (=2)
[namelist:umstash_domain(identical1_ed6e1b5e)]
dom_name='identical1'
imn=0

# domain(3)
[namelist:umstash_domain(normal1_4ccb4417)]
dom_name='normal1'
imn=1
imsk=1

# domain(4)
[namelist:umstash_domain(normal2_2af126ec)]
dom_name='normal2'
imn=1
imsk=2

# streq(1) (if dup removed, =2)
[namelist:umstash_streq(00002_c2f44d54)]
dom_name='identical1'
isec=0
item=2
package='foo'
tim_name='normal1'
use_name='identical1'

# streq(3) (=4)
[namelist:umstash_streq(05011_1c83d5ad)]
dom_name='normal1'
isec=5
item=11
package='foo'
tim_name='normal1'
use_name='identical1'

# streq(5)
[namelist:umstash_streq(05011_263d8bd0)]
dom_name='normal2'
isec=5
item=11
package='foo'
tim_name='normal2'
use_name='identical1'

# streq(d9ad6b73), old index format.
[namelist:umstash_streq(50999_d9ad6b73)]
dom_name='normal2'
isec=50
item=999
package='bar'
tim_name='normal2'
use_name='identical1'

# time(1), user-ignored
[!namelist:umstash_time(normal1_16055de9)]
iend=9
tim_name='normal1'

# time(2)
[namelist:umstash_time(normal2_47fd949e)]
iend=8
tim_name='normal2'

# use(1) (=2)
[namelist:umstash_use(identical1_54db5261)]
iunt=60
use_name='identical1'

# use(3)
[namelist:umstash_use(normal1_39bbfabd)]
!iunt=60
use_name='normal1'
"""

    TEST_TRANSFORM_OUTPUT = """stash_indices.TidyStashTransformPruneDuplicated: changes: 82
    namelist:umstash_domain(2)=None=None
        Deleted - identical to namelist:umstash_domain(1)
    namelist:umstash_streq(1)=dom_name='identical1'
        'identical2' => 'identical1' (identical)
    namelist:items(3)=None=None
        Deleted - identical to namelist:items(1)
    namelist:umstash_streq(4)=None=None
        Deleted - identical to namelist:umstash_streq(3)
    namelist:umstash_use(2)=None=None
        Deleted - identical to namelist:umstash_use(1)
    namelist:umstash_streq(2)=use_name='identical1'
        'identical2' => 'identical1' (identical)
    namelist:umstash_streq(3)=use_name='identical1'
        'identical2' => 'identical1' (identical)
    namelist:umstash_streq(2)=None=None
        Deleted - identical to namelist:umstash_streq(1)
    namelist:umstash_domain(1)=None=None
        Renamed to namelist:umstash_domain(identical1_ed6e1b5e)
    namelist:umstash_domain(identical1_ed6e1b5e)=None=None
        Renamed from namelist:umstash_domain(1)
    namelist:umstash_domain(identical1_ed6e1b5e)=dom_name='identical1'
        Renamed from namelist:umstash_domain(1)=dom_name
    namelist:umstash_domain(identical1_ed6e1b5e)=imn=0
        Renamed from namelist:umstash_domain(1)=imn
    namelist:umstash_domain(3)=None=None
        Renamed to namelist:umstash_domain(normal1_4ccb4417)
    namelist:umstash_domain(normal1_4ccb4417)=None=None
        Renamed from namelist:umstash_domain(3)
    namelist:umstash_domain(normal1_4ccb4417)=imsk=1
        Renamed from namelist:umstash_domain(3)=imsk
    namelist:umstash_domain(normal1_4ccb4417)=dom_name='normal1'
        Renamed from namelist:umstash_domain(3)=dom_name
    namelist:umstash_domain(normal1_4ccb4417)=imn=1
        Renamed from namelist:umstash_domain(3)=imn
    namelist:umstash_domain(4)=None=None
        Renamed to namelist:umstash_domain(normal2_2af126ec)
    namelist:umstash_domain(normal2_2af126ec)=None=None
        Renamed from namelist:umstash_domain(4)
    namelist:umstash_domain(normal2_2af126ec)=imsk=2
        Renamed from namelist:umstash_domain(4)=imsk
    namelist:umstash_domain(normal2_2af126ec)=dom_name='normal2'
        Renamed from namelist:umstash_domain(4)=dom_name
    namelist:umstash_domain(normal2_2af126ec)=imn=1
        Renamed from namelist:umstash_domain(4)=imn
    namelist:items(1)=None=None
        Renamed to namelist:items(97a136a1)
    namelist:items(97a136a1)=None=None
        Renamed from namelist:items(1)
    namelist:items(97a136a1)=item=302
        Renamed from namelist:items(1)=item
    namelist:items(97a136a1)=domain=1
        Renamed from namelist:items(1)=domain
    namelist:items(97a136a1)=section=0
        Renamed from namelist:items(1)=section
    namelist:items(97a136a1)=source=4
        Renamed from namelist:items(1)=source
    namelist:items(2)=None=None
        Renamed to namelist:items(521d3f6c)
    namelist:items(521d3f6c)=None=None
        Renamed from namelist:items(2)
    namelist:items(521d3f6c)=item=302
        Renamed from namelist:items(2)=item
    namelist:items(521d3f6c)=domain=1
        Renamed from namelist:items(2)=domain
    namelist:items(521d3f6c)=section=0
        Renamed from namelist:items(2)=section
    namelist:items(521d3f6c)=source=2
        Renamed from namelist:items(2)=source
    namelist:umstash_streq(1)=None=None
        Renamed to namelist:umstash_streq(00002_c2f44d54)
    namelist:umstash_streq(00002_c2f44d54)=None=None
        Renamed from namelist:umstash_streq(1)
    namelist:umstash_streq(00002_c2f44d54)=package='foo'
        Renamed from namelist:umstash_streq(1)=package
    namelist:umstash_streq(00002_c2f44d54)=tim_name='normal1'
        Renamed from namelist:umstash_streq(1)=tim_name
    namelist:umstash_streq(00002_c2f44d54)=use_name='identical1'
        Renamed from namelist:umstash_streq(1)=use_name
    namelist:umstash_streq(00002_c2f44d54)=dom_name='identical1'
        Renamed from namelist:umstash_streq(1)=dom_name
    namelist:umstash_streq(00002_c2f44d54)=isec=0
        Renamed from namelist:umstash_streq(1)=isec
    namelist:umstash_streq(00002_c2f44d54)=item=2
        Renamed from namelist:umstash_streq(1)=item
    namelist:umstash_streq(3)=None=None
        Renamed to namelist:umstash_streq(05011_1c83d5ad)
    namelist:umstash_streq(05011_1c83d5ad)=None=None
        Renamed from namelist:umstash_streq(3)
    namelist:umstash_streq(05011_1c83d5ad)=package='foo'
        Renamed from namelist:umstash_streq(3)=package
    namelist:umstash_streq(05011_1c83d5ad)=tim_name='normal1'
        Renamed from namelist:umstash_streq(3)=tim_name
    namelist:umstash_streq(05011_1c83d5ad)=use_name='identical1'
        Renamed from namelist:umstash_streq(3)=use_name
    namelist:umstash_streq(05011_1c83d5ad)=dom_name='normal1'
        Renamed from namelist:umstash_streq(3)=dom_name
    namelist:umstash_streq(05011_1c83d5ad)=isec=5
        Renamed from namelist:umstash_streq(3)=isec
    namelist:umstash_streq(05011_1c83d5ad)=item=11
        Renamed from namelist:umstash_streq(3)=item
    namelist:umstash_streq(5)=None=None
        Renamed to namelist:umstash_streq(05011_263d8bd0)
    namelist:umstash_streq(05011_263d8bd0)=None=None
        Renamed from namelist:umstash_streq(5)
    namelist:umstash_streq(05011_263d8bd0)=package='foo'
        Renamed from namelist:umstash_streq(5)=package
    namelist:umstash_streq(05011_263d8bd0)=tim_name='normal2'
        Renamed from namelist:umstash_streq(5)=tim_name
    namelist:umstash_streq(05011_263d8bd0)=use_name='identical1'
        Renamed from namelist:umstash_streq(5)=use_name
    namelist:umstash_streq(05011_263d8bd0)=dom_name='normal2'
        Renamed from namelist:umstash_streq(5)=dom_name
    namelist:umstash_streq(05011_263d8bd0)=isec=5
        Renamed from namelist:umstash_streq(5)=isec
    namelist:umstash_streq(05011_263d8bd0)=item=11
        Renamed from namelist:umstash_streq(5)=item
    namelist:umstash_streq(d9ad6b73)=None=None
        Renamed to namelist:umstash_streq(50999_d9ad6b73)
    namelist:umstash_streq(50999_d9ad6b73)=None=None
        Renamed from namelist:umstash_streq(d9ad6b73)
    namelist:umstash_streq(50999_d9ad6b73)=package='bar'
        Renamed from namelist:umstash_streq(d9ad6b73)=package
    namelist:umstash_streq(50999_d9ad6b73)=tim_name='normal2'
        Renamed from namelist:umstash_streq(d9ad6b73)=tim_name
    namelist:umstash_streq(50999_d9ad6b73)=use_name='identical1'
        Renamed from namelist:umstash_streq(d9ad6b73)=use_name
    namelist:umstash_streq(50999_d9ad6b73)=dom_name='normal2'
        Renamed from namelist:umstash_streq(d9ad6b73)=dom_name
    namelist:umstash_streq(50999_d9ad6b73)=isec=50
        Renamed from namelist:umstash_streq(d9ad6b73)=isec
    namelist:umstash_streq(50999_d9ad6b73)=item=999
        Renamed from namelist:umstash_streq(d9ad6b73)=item
    namelist:umstash_time(1)=None=None
        Renamed to namelist:umstash_time(normal1_16055de9)
    namelist:umstash_time(normal1_16055de9)=None=None
        Renamed from namelist:umstash_time(1)
    namelist:umstash_time(normal1_16055de9)=tim_name='normal1'
        Renamed from namelist:umstash_time(1)=tim_name
    namelist:umstash_time(normal1_16055de9)=iend=9
        Renamed from namelist:umstash_time(1)=iend
    namelist:umstash_time(2)=None=None
        Renamed to namelist:umstash_time(normal2_47fd949e)
    namelist:umstash_time(normal2_47fd949e)=None=None
        Renamed from namelist:umstash_time(2)
    namelist:umstash_time(normal2_47fd949e)=tim_name='normal2'
        Renamed from namelist:umstash_time(2)=tim_name
    namelist:umstash_time(normal2_47fd949e)=iend=8
        Renamed from namelist:umstash_time(2)=iend
    namelist:umstash_use(1)=None=None
        Renamed to namelist:umstash_use(identical1_54db5261)
    namelist:umstash_use(identical1_54db5261)=None=None
        Renamed from namelist:umstash_use(1)
    namelist:umstash_use(identical1_54db5261)=iunt=60
        Renamed from namelist:umstash_use(1)=iunt
    namelist:umstash_use(identical1_54db5261)=use_name='identical1'
        Renamed from namelist:umstash_use(1)=use_name
    namelist:umstash_use(3)=None=None
        Renamed to namelist:umstash_use(normal1_39bbfabd)
    namelist:umstash_use(normal1_39bbfabd)=None=None
        Renamed from namelist:umstash_use(3)
    namelist:umstash_use(normal1_39bbfabd)=iunt=60
        Renamed from namelist:umstash_use(3)=iunt
    namelist:umstash_use(normal1_39bbfabd)=use_name='normal1'
        Renamed from namelist:umstash_use(3)=use_name
stash_indices.TidyStashTransformPruneDuplicated: warnings: 1
    namelist:items(97a136a1)=None=None
        Source/domain clash with namelist:items(521d3f6c) will cause UM abort
"""

    TEST_VALIDATE_OUTPUT = """stash_indices.TidyStashValidate: issues: 23
    namelist:umstash_domain(1)=None=None
        Wrong index: 1 should be identical1_ed6e1b5e
    namelist:umstash_domain(2)=None=None
        Wrong index: 2 should be identical2_ed6e1b5e
    namelist:umstash_domain(3)=None=None
        Wrong index: 3 should be normal1_4ccb4417
    namelist:umstash_domain(4)=None=None
        Wrong index: 4 should be normal2_2af126ec
    namelist:umstash_domain(1)=None=None
        Identical sections: namelist:umstash_domain(1) == namelist:umstash_domain(2)
    namelist:items(1)=None=None
        Wrong index: 1 should be 97a136a1
    namelist:items(2)=None=None
        Wrong index: 2 should be 521d3f6c
    namelist:items(3)=None=None
        Wrong index: 3 should be 97a136a1
    namelist:items(1)=None=None
        Identical sections: namelist:items(1) == namelist:items(3)
    namelist:umstash_streq(1)=None=None
        Wrong index: 1 should be 00002_94eb9a06
    namelist:umstash_streq(2)=None=None
        Wrong index: 2 should be 00002_8f159890
    namelist:umstash_streq(3)=None=None
        Wrong index: 3 should be 05011_f4c34d08
    namelist:umstash_streq(4)=None=None
        Wrong index: 4 should be 05011_f4c34d08
    namelist:umstash_streq(5)=None=None
        Wrong index: 5 should be 05011_263d8bd0
    namelist:umstash_streq(d9ad6b73)=None=None
        Wrong index prefix (hash OK): d9ad6b73 should be 50999_d9ad6b73
    namelist:umstash_streq(3)=None=None
        Identical sections: namelist:umstash_streq(3) == namelist:umstash_streq(4)
    namelist:umstash_time(1)=None=None
        Wrong index: 1 should be normal1_16055de9
    namelist:umstash_time(2)=None=None
        Wrong index: 2 should be normal2_47fd949e
    namelist:umstash_use(1)=None=None
        Wrong index: 1 should be identical1_54db5261
    namelist:umstash_use(2)=None=None
        Wrong index: 2 should be identical2_54db5261
    namelist:umstash_use(3)=None=None
        Wrong index: 3 should be normal1_39bbfabd
    namelist:umstash_use(1)=None=None
        Identical sections: namelist:umstash_use(1) == namelist:umstash_use(2)
    namelist:items(2)=None=None
        Source/domain clash with namelist:items(1) will cause UM abort
"""

    def setupTests(self):
        """Setup - we just need a dependence on rose.macro."""
        import rose.macro

    def test_transform_keep(self):
        """Test the Transform macro (keep duplicated namelists)."""
        setup_config = self._get_setup_config()
        new_config, reports = TidyStashTransform().transform(setup_config)
        ctrl_report_string = self.TEST_TRANSFORM_KEEP_OUTPUT
        my_report_string = rose.macro.get_reports_as_text(
            {None: reports},
            "stash_indices.TidyStashTransform",
            is_from_transform=True
        )
        self.assertEqual(my_report_string, ctrl_report_string)
        handle = StringIO.StringIO()
        rose.config.dump(new_config, handle)
        handle.seek(0)
        my_config_string = handle.read()
        ctrl_config_string = self.TEST_TRANSFORM_KEEP_CONFIG_STRING
        self.assertEqual(my_config_string, ctrl_config_string)

    def test_transform_no_keep(self):
        """Test the Transform macro (delete duplicated namelists)."""
        setup_config = self._get_setup_config()
        new_config, reports = (
            TidyStashTransformPruneDuplicated().transform(setup_config))
        ctrl_report_string = self.TEST_TRANSFORM_OUTPUT
        my_report_string = rose.macro.get_reports_as_text(
            {None: reports},
            "stash_indices.TidyStashTransformPruneDuplicated",
            is_from_transform=True
        )
        self.assertEqual(my_report_string, ctrl_report_string)
        handle = StringIO.StringIO()
        rose.config.dump(new_config, handle)
        handle.seek(0)
        my_config_string = handle.read()
        ctrl_config_string = self.TEST_TRANSFORM_CONFIG_STRING
        self.assertEqual(my_config_string, ctrl_config_string)

    def test_validate(self):
        """Test the Validator macro."""
        setup_config = self._get_setup_config()
        meta_config = rose.config.ConfigNode()
        reports = TidyStashValidate().validate(setup_config, meta_config)
        ctrl_report_string = self.TEST_VALIDATE_OUTPUT
        my_report_string = rose.macro.get_reports_as_text(
            {None: reports},
            "stash_indices.TidyStashValidate",
            is_from_transform=False
        )
        self.assertEqual(my_report_string, ctrl_report_string)

    def _get_setup_config(self):
        """Return a rose.config.ConfigNode from TEST_CONFIG_STRING."""
        handle = StringIO.StringIO(self.TEST_CONFIG_STRING)
        return rose.config.load(handle)

if __name__ == "__main__":
    import unittest
    unittest.main()
