#!/bin/sh

export EDITOR="vim"

if test $# -ne 3 ; then
        echo >&2 "usage: `basename $0` MYFILE OLDFILE YOURFILE"
        exit 1
fi

# Keep a local copy of the filenames involved in the merge.
LOCAL="$1"
BASE="$2"
OTHER="$3"

cleanup() {
        if test -n "${TMPDIR}" && test -n "${WC}" ; then
                B=`dirname "${WC}"`
                TMPDIRPATH=`cd "${TMPDIR}"; pwd`
                WCPATH=`cd "${B}"; pwd`
                if test X"${B}" = X"${TMPDIR}" ; then
                        /bin/rm -f "${WC}"
                fi
        fi
}

success() {
        if test -z "${WC}" || test -z "${LOCAL}" ; then
                err 1 "internal merge script error."
        fi
        # The merge was successful.  Copy back the merged file on top of ${LOCAL}
        cp "${WC}" "${LOCAL}" && /bin/rm "${WC}"
        if test $? -ne 0 ; then
                err 1 "Failed to save merged file at ${LOCAL}"
        fi
}

err() {
        errcode=$1
        shift
        echo >&2 "`basename $0`: error: $*"
        cleanup
        exit $errcode
}

# Since this script depends on manual edits being performed to the files being
# merged, make sure that ${EDITOR} is truly set to something, even if this is
# just plain good ol' vi(1).
EDITOR="${EDITOR:-vi}"
export EDITOR

# First make sure $TMPDIR points to a meaningful directory.  We will be using
# this shell variable further down, so it's a good idea to make sure it isn't
# empty later on.
TMPDIR="${TMPDIR:-/var/tmp}"
export TMPDIR

# We will be using a temporary file with the diff3(1) output as the merge
# buffer, until either the merge removes all conflict markers from the working
# copy of the file or we fail somehow to complete the merge.
WC=`mktemp "${TMPDIR}/hgmerge-XXXXXX"`
if test $? -ne 0 ; then
        err 1 "Cannot create temporary file at ${TMPDIR}/hgmerge-XXXXXX"
fi

# We depend on diff3(1) being available to do the first pass of the merge,
# adding conflict markers around the areas that should be edited.
which diff3 >/dev/null 2>&1
if test $? -ne 0 ; then
        err 1 "No diff3(1) utility found in the current PATH."
fi

# First try to add conflict markers around the areas that need special
# attention in the ${LOCAL} file.  The output is not saved directly over the
# file that is currently in-conflict, but is saved in the ${WC} temporary file
# to allow editing of the conflict regions without
diff3 -m "${LOCAL}" "${BASE}" "${OTHER}" > "${WC}"
rc=$?
if test $rc -eq 0 ; then
        # No conflicts found.  Merge done.
        success
        exit 0
elif test $rc -gt 1 ; then
        err 1 "serious diff3 error, while trying to merhge ${LOCAL}"
fi

# In all other cases, diff3(1) has found conflicts, added the proper conflict
# markers to the ${WC} file and we should now edit this file.  Fire up an
# editor with the ${WC} file and let the user manually resolve the conflicts.
# When the editor exits successfully, there should be no conflict markers in
# the ${WC} file, otherwise we consider this merge failed.
${EDITOR} "${WC}"
if test $? -ne 0 ; then
        err 1 "merge error for ${LOCAL}"
fi
if grep '^<<<<<<<' "${WC}" >/dev/null 2>&1 ||
   grep '^|||||||' "${WC}" >/dev/null 2>&1 ||
   grep '^=======' "${WC}" >/dev/null 2>&1 ||
   grep '^>>>>>>>' "${WC}" >/dev/null 2>&1 ; then
        err 1 "conflict markers still found in the working-copy.  Merge aborted for ${LOCAL}"
fi

success
exit 0

