<!DOCTYPE html>
<html>
<head>
    <title>Chọn mẫu tin</title>
</head>
<body>
    <div id="url-list"></div>
    <button id="generateBtn">Tạo nhung3.html</button>
    <script>
        fetch('http://localhost:3000/get_urls') // Gọi API của Node.js
        .then(response => response.json())
        .then(urls => {
            const urlList = document.getElementById('url-list');
            urls.forEach(url => {
                const div = document.createElement('div');
                div.innerHTML = `<input type="checkbox" id="${url.id}" ${url.selected?'checked':''}/><label for="${url.id}"> ${url.title}</label><br>`
                urlList.appendChild(div);
            })
        })
        document.getElementById('generateBtn').addEventListener('click', () => {
            const selectedUrls = Array.from(document.querySelectorAll('input[type="checkbox"]:checked')).map(checkbox=>parseInt(checkbox.id))
            fetch('http://localhost:3000/update_urls',{
                method:'POST',
                headers:{
                    'Content-Type':'application/json'
                },
                body:JSON.stringify({selectedUrls:selectedUrls})
            }).then(response=>response.text()).then(text=>alert(text))
        })
    </script>
</body>
</html>