def add_checkboxes_and_button(input_html, output_html):
    from bs4 import BeautifulSoup

    # Load the input HTML file
    print(f"Loading input file: {input_html}")
    with open(input_html, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # Find the left columns container
    left_columns = soup.find('div', class_='left-columns')
    if not left_columns:
        print("Error: <div class='left-columns'> not found in the input HTML.")
        return

    print("Found <div class='left-columns'>. Processing items...")
    # Add checkboxes to each URL in the left columns
    for item in left_columns.find_all('div', class_='item'):
        if 'data-url' in item.attrs:
            print(f"Adding checkbox for URL: {item['data-url']}")
            checkbox = soup.new_tag('input', type='checkbox', attrs={'name': 'url', 'value': item['data-url']})
            item.insert(0, checkbox)
        else:
            print("Warning: <div class='item'> does not have 'data-url' attribute.")

    # Add a form around the left columns
    print("Wrapping <div class='left-columns'> in a form.")
    form = soup.new_tag('form', action='/save_selected', method='POST', id='urlForm')
    left_columns.wrap(form)

    # Add a submit button
    print("Adding submit button.")
    submit_button = soup.new_tag('button', type='button', id='submitBtn')
    submit_button.string = 'Transfer Selected'
    soup.body.append(submit_button)

    # Add a script to handle the selection and save to 'dich.html'
    print("Adding JavaScript for handling selection.")
    script = soup.new_tag('script')
    script.string = """
        document.getElementById('submitBtn').addEventListener('click', () => {
            const selectedUrls = Array.from(document.querySelectorAll('input[name="url"]:checked'))
                .map(checkbox => checkbox.value);

            console.log('Selected URLs:', selectedUrls);

            fetch('/save_selected', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ urls: selectedUrls })
            }).then(response => {
                if (response.ok) {
                    alert('Selected URLs transferred to dich.html successfully!');
                } else {
                    alert('Error transferring URLs.');
                }
            });
        });
    """
    soup.body.append(script)

    # Save the modified HTML to the output file
    print(f"Saving output to: {output_html}")
    with open(output_html, 'w', encoding='utf-8') as file:
        file.write(str(soup))

    print("Processing completed.")

# Usage
input_html = 'nhung3.html'
output_html = 'nhung3_with_checkboxes.html'
add_checkboxes_and_button(input_html, output_html)