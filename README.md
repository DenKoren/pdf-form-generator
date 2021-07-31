# pdf-form-generator
Here is the pack of two scripts:

1. Simple PDF form generator script that attaches form fields to existing PDF document
  * generates document with form fields
  * merges generated 'form' document with the original PDF
2. Simple PDF form filler script that fills form fields with values


## Quick start

### Get the scripts and init the environment
```shell script
# Clone this repository
git clone https://github.com/DenKoren/pdf-form-generator.git
cd pdf-form-generator

# Create virtual environment
python3 -m venv ./venv

# Activate it
source ./venv/bin/activate

# Upgrade the pip
pip install --upgrade pip

# Install the requirements
pip install -r ./requirements.txt
```

### Use the examples to generate first PDF form
```shell script
./attach-form.py ./examples/form-settings.yaml my_awesome_form ./examples/document.pdf ./examples/form.pdf
./fill-form.py ./examples/form.pdf ./examples/field-values.yaml ./examples/filled.pdf
```

## attach-form.py
This script generates PDF file with plain form (fields only, no visible text)
and merges it with the given original PDF file with text.

### Usage
```shell script
./attach-form.py '<form-settings.yaml>' '<form-name>' '<Document.pdf>' '<Result-with-fields.pdf>'
```

```shell script
./attach-form.py ./form-settings.yaml my_awesome_form ./original-document.pdf ./result-with-fields.pdf
```

### Form config
The form configuration is the regular yaml file.

Structure:
```yaml
# Script expects the full form configuration to be located inside 'form_settings' key
form_settings:
  # Custom field types. You can set here default values for fields.
  # They will be used when the field has no it's own value with the same key
  types:
    # Type 'default' has the special meaning. It is used as base type for all other types and fields when they have no
    # 'type' key set.
    # This means, all our fields will have maxlen=100, height=15, font_size=10, ... by default.
    default: { h: 15, maxlen: 100, font_size: 10, font_name: 'Helvetica', flags: ['doNotScroll'] }

    # Since the 'number' field has no 'type' set, script will use 'default' as parent type
    number: { w: 11, tooltip: "put a number here" }

  # Field groups are packs of fields that can be put at the given location all at once.
  # When group is placed on page, the 'x' and 'y' of the group are added to all fields inside the group
  # and the group name is prepended to each field's name of the group with the '-' delimiter:
  #   "{group_name}-{field_name}"
  groups:
    date:
      - { name: "day", x: 0, y: 0, w: 11, tooltip: "day", type: number }
      - { name: "month", x: 12.5, y: 0, w: 27, tooltip: "month", type: number }
      - { name: "year", x: 41, y: 0, w: 14, tooltip: "year", type: number }

    client_info:
      - { name: "surname", x: 16, y: 0, w: 58.5, tooltip: "Surname" }
      - { name: "name", x: 16, y: -5, w: 58.5, tooltip: "Name" }

        # You can use groups inside other groups.
        # Recursion is not allowed.
      - { name: "birth", x: 16, y: -10, group: date }

  # Forms keep final form field configurations. Each configuration has its name
  forms:
    my_awesome_form:
      # Each form has a list of pages and a list of fields on each page
      # Here are the page 1 fields:
      - - { name: "contract-number", x: 123.8, y: 265.7, w: 32, h: 18, tooltip: 'contract number', font_size: 16, type: number }

        # The group's 'x' and 'y' will be added to group's fields coordinates.
        # The group's name will be prepended to group's field names.
        # So we get here 3 fields: 'contract-date-day', 'contract-date-month' and 'contract-date-year'
        - { name: "contract-date", x: 131, y: 279.9, group: date }

      # Here are the page 2 fields
      - - { name: "contract-payment-digits", x: 27, y: 261.5, w: 24, tooltip: "amount in digits" }
        - { name: "contract-payment-text", x: 65.8, y: 261.5, w: 119, tooltip: "amount in text" }

      # Here are the page 3 fields
      - - { name: "additional_agreements", x: 20, y: 242.5, w: 168, h: 51, tooltip: "additional agreements", flags: ["multiline"] }
        - { name: "customer", x: 112, y: 211.5, group: client_info }
        - { name: "signature_date", x: 129, y: 186, group: date }

    my_another_form:
      - - { tooltip: "..." }
```

This script has no automation, it can't autodetect candidates for input fields,
it has no visual editor and so on. You have to adjust fields configuration
to original PDF document contents manually, but it is enough for some simple
tasks and it is free :).

I wrote it to make PDF modifications simpler: it is very annoying to redraw
the full PDF form in an online PDF editor tool after small changes in
original Mac OS X 'Pages' document or some other editor, that supports exporting to PDF,
but does not support AcroForms generation.

This script is published because it seems quite good example of the PDF form
generation task solution anyone can take and adopt to their own needs.

Feel free to use it and make PRs if you see how to make it better.

## fill-form.py

Fill form fields with values provided in map

### Usage

```shell script
./fill-form.py '<Form.pdf>' '[field-values.yaml]' '[Result-filled.pdf]'
```

* You can use `-` in place of any of parameters. It will mean `STDIN` or `STDOUT` depending on parameter.
* The defaults for `[field-values.yaml]` and `[Result-filled.pdf]` are `-`
* You can't use `-` for both `<Form.pdf>` and `[field-values.yaml]` because script will have no idea of place
  where the one ends and starts the another.

```shell script
# You can use it as regular file generator
./fill-form.py ./Document-with-form.pdf ./values-config.yaml ./Filled-document.pdf

# Get the field values from STDIN
cat ./values-config.yaml | ./fill-form.py ./Document-with-form.pdf - ./Filled-document.pdf

# Get the PDF from STDIN
cat ./Document-with-form.pdf | ./fill-form.py - ./values-config.yaml ./Filled-document.pdf

# Put filled document to STDOUT (these are equivalent)
./fill-form.py ./Document-with-form.pdf ./values-config.yaml - > ./Filled-document.pdf
./fill-form.py ./Document-with-form.pdf ./values-config.yaml > ./Filled-document.pdf

# Also possible to use the command as a filter (these are equivalent)
cat ./values-config.yaml | ./fill-form.py ./Document-with-form.pdf - - > ./Filled-document.pdf
cat ./values-config.yaml | ./fill-form.py ./Document-with-form.pdf > ./Filled-document.pdf
```

### Values config
The values configuration is the regular yaml file.

```yaml
# Script expects all form field values to be located inside `field_values` key
field_values:
    # The simple key->value, where 'key' is the name of the field and 'value' is its value:

    contract-number: c-130721-1

    # That's how our 'date' group from the example above expanded
    contract-date-day: 13
    contract-date-month: july
    contract-date-year: 2021

    contract-payment-digits: 0
    contract-payment-text:  zero dollars and 00 cents

    customer-surname: Lazy
    customer-name: John

    additional_agreements: |
        Some multiline text here
        To fit the lines in form, just adjust the font size of the field
        when you create it.

    # That's how our group inside group ('client_info' -> 'date') from the example above expanded
    customer-birth-day: 30
    customer-birth-month: January
    customer-birth-year: 2001

    signature_date-day: 10
    signature_date-month: February
    signature_date-year: 2021

```
