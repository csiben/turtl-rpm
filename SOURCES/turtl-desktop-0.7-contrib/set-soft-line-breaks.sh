#!/usr/bin/bash
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi
echo "
Turtl Desktop: Set Turtl markdown renderer to treat all line breaks as 'soft'.

Traditional markdown renders a carriage return (line break) as a space with any
following text concatenated to the last, thus allowing the document margins to
dictate how a paragraph of text is word-wrapped. I.e, An application that
renders markdown into its more published form will, traditionally, treat a
paragraph of text very much the same way a browser will treat a paragraph of
text formated as HTML. We call this a 'soft' line break: A line break in the
editor, but ignored when rendered in the final document.

By default, a fresh install of Turtl Desktop is set to treat a line break as
'hard' and therefore break the text at that line break in the final rendering.

This command configures Turtl Desktop to honor the more traditional behavior
'soft' line break of markdown rendering."


default="/usr/share/turtl-desktop/resources/app/build/app/main.js"
file=$default
hard="breaks: true"
soft="breaks: false"
goingfrom=$hard
goingto=$soft

if [ "$#" -gt 0 ]; then
  file=$1
  echo
  echo "Overriding the default -- attempting to change the line break value in file:"
  echo "  $file"
fi

if [ -f "$file" ]; then
  grep -Fq "$goingto" $file
  if  [ "$?" -eq "0" ] ; then
    echo
    echo "Result: Line breaks already set to 'soft'."
  else
    grep -Fq "$goingfrom" $file
    if [ "$?" -ne "0" ] ; then
      echo
      echo "Result: Line break setting not found in the file listed below."
      echo "        This should not happen."
      echo "        File: $file"
    else
      echo
      read -r -p "About to set line breaks to 'soft'. Are you sure? [y/N] " response
      response=${response,,}    # tolower
      if [[ "$response" =~ ^(yes|y)$ ]]; then
        :
      else
        exit 1
      fi
      sed -i.previous '{s/'"${goingfrom}"'/'"${goingto}"'/}' ${file}
      # check that it has been set...
      grep -Fq "$goingto" $file
      if [ "$?" -ne "0" ] ; then
        echo "Result: Failed to set line break to 'soft'. This error shouldn't happen."
        exit 1
      fi
      echo
      echo "Result: Line breaks now treated as 'soft'."
      echo "        To have the change take effect, you must restart the application."
    fi
  fi
fi

