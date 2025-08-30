#!/bin/bash

# Output file
output_file="file-overview.txt"

# Create or clear the output file
> "$output_file"

{
    echo "### Monograph.tex Files ###"
    find . -type f -name "monograph.tex" -exec du -h {} + | while read size file; do
        mod_date=$(stat --format="%y" "$file")
        echo "$size $mod_date $file"
    done

    echo
    echo "### References.bib Files ###"
    find . -type f -name "references.bib" -exec du -h {} + | while read size file; do
        mod_date=$(stat --format="%y" "$file")
        echo "$size $mod_date $file"
    done
} > "$output_file"

echo "File overview has been saved to $output_file"
