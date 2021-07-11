# pdf-form-generator
A simple PDF form generation script that uses hardcoded fields config to put
it over existing PDF file.

To customize form fields, just adjust 'pages_config' variable contents.

This script has no automation, it can't autodetect candidates for input fields,
it has no visual editor and so on. It just has hard-coded form shape that fits
only single PDF document, but sometimes it is enough for simple operations.

I wrote it to make PDF modifications simpler: it is very annoying to redraw
the full PDF form after small changes in original Mac OS X 'Pages' document
and exporting it into PDF file.

This script is published because it seems quite good example of the PDF form
generation task solution anyone can take and adopt to their own needs.

## Usage

python ./attach-form.py 'original-file.pdf' 'result-file.pdf' 
