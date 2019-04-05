#!/usr/bin/bash
# vim:tw=0:ts=2:sw=2:et:
$(return 0 > /dev/null 2>&1) && echo "please run directly, not as a sourced script" && return 1

if [ "$EUID" -ne 0 ]
  then echo "Please run with root priviledges"
  exit 1
fi

echo "
Turtl Desktop -- Toggle whether line breaks are interpreted as 'soft' or 'hard'.

A soft break: When line breaks in a paragraph of text are ignored upon rendering
the final published content. The markdown interpreter will freely flow the
paragraph of text as needed to fit the dimensions of the document. Hard breaks
can still be forced with <br/> or a double-space at the end of a line.
Traditional markdown assumes 'soft breaking' behavior.

A hard break: When every line break in a paragraph of text is treated as a
carriage return in the final published content, regardless of the dimensions and
margin spacing of the output medium. Turtl has 'hard breaking' behavior set by
default.

This utility simply toggles between the two settings.
"

file="/usr/share/turtl-desktop/resources/app/build/app/main.js"
hard="breaks: true"
soft="breaks: false"

if [ -f "$file" ]; then
  grep -Fq "$soft" $file
  if  (( "$?" == 0 )) ; then
    sed -i.previous '{s/'"${soft}"'/'"${hard}"'/}' ${file}
    echo "## Markdown line break behavior set to 'hard'."
    echo "## Note: This change will not take effect until Turl Desktop is restarted."
  else
    grep -Fq "$hard" $file
    if (( "$?" == "0" )) ; then
      sed -i.previous '{s/'"${hard}"'/'"${soft}"'/}' ${file}
      echo "## Markdown line break behavior set to 'soft'."
      echo "## Note: This change will not take effect until Turl Desktop is restarted."
    else
      echo "ERROR: This should not happen. Could not find line break setting in $file"
      exit 1
    fi
  fi
else
  echo "ERROR: This should not happen. File not found: $file"
  exit 1
fi
