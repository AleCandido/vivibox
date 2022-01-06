Start-BitsTransfer -Source 'https://api.github.com/repos/AleCandido/vivibox/releases' -Destination ./releases.json
$j = Get-Content .\releases.json | ConvertFrom-Json
rm .\releases.json
foreach ($rel in $j.GetEnumerator()) {
    if ( $rel.tag_name -like "case-extract-*" )
    {
        echo "Found $($rel.tag_name)"
        $assets_url = $rel.assets_url
        break
    }
}

echo $assets_url
Start-BitsTransfer -Source $assets_url -Destination ./assets.json
$assets = Get-Content .\assets.json | ConvertFrom-Json
rm .\assets.json
foreach ($a in $assets.GetEnumerator()) {
    if ( $a.name -eq "case-extract.zip" )
    {
	$download_url = $a.browser_download_url
    }
}

Start-BitsTransfer -Source $download_url
Expand-Archive .\case-extract.zip
rm .\case-extract.zip
pip install $(ls .\case-extract\case-extract\*.whl)
mv .\case-extract\case-extract\app.py .
rm -r .\case-extract, .\case-extract.zip
pip install pyinstaller
pyinstaller --noconsole --onefile .\app.py
mv .\dist\app.exe .\case-extract.exe
rm -r build, dist, app.spec