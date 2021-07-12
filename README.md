# pdf-form-generator
A simple PDF form generator script that generates document with form fields 
using hardcoded fields configuration (see `pages_config` variable) and
merges its pages with pages from original PDF document.

To customize form fields, just adjust `pages_config` variable contents in 
`attach-form.py`.

This script has no automation, it can't autodetect candidates for input fields,
it has no visual editor and so on. You have to adjust fields configuration
to original PDF document contents manually, but it is enough for some simple 
tasks and it is free :).

I wrote it to make PDF modifications simpler: it is very annoying to redraw
the full PDF form in an online PDF editor tool after small changes in 
original Mac OS X 'Pages' document.

This script is published because it seems quite good example of the PDF form
generation task solution anyone can take and adopt to their own needs.

## Usage

python ./attach-form.py 'original-file.pdf' 'result-file.pdf' 
