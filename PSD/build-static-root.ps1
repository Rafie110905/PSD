$ErrorActionPreference = "Stop"

$root = $PSScriptRoot
$build = Join-Path $root "_build\html"
$utf8 = [System.Text.UTF8Encoding]::new($false)

Push-Location $root
try {
    & jupyter-book build . --all
    if ($LASTEXITCODE -ne 0) {
        throw "Jupyter Book build failed with exit code $LASTEXITCODE."
    }

    if (-not (Test-Path (Join-Path $build "intro.html"))) {
        throw "Build output was not found at $build."
    }

    foreach ($name in @("intro.html", "index.html", "genindex.html", "search.html", "searchindex.js")) {
        Copy-Item (Join-Path $build $name) -Destination $root -Force
    }
    Get-ChildItem $build -File -Filter "*.html" |
        Copy-Item -Destination $root -Force

    $pageNames = @(
        "Ekstraksi_Fitur_TSFEL_Data_Polutan_Udara_Kecamatan_Bangkalan",
        "K-Means Clustering pada Data Polutan Udara Implementasi Python dan KNIME",
        "klasifikasi_sawah_sentinel2_bangkalan",
        "K-Means_Clustering_Polynomial_Proyek_Sains_Data"
    )

    foreach ($pageName in $pageNames) {
        $sourcePage = Join-Path (Join-Path $build "_sources") "$pageName.html"
        if (-not (Test-Path $sourcePage)) {
            throw "Expected built page was not found: $sourcePage"
        }

        $nestedPages = Join-Path $root "_sources"
        if (-not (Test-Path $nestedPages)) {
            New-Item -ItemType Directory -Path $nestedPages | Out-Null
        }
        Copy-Item $sourcePage -Destination $nestedPages -Force

        $content = [System.IO.File]::ReadAllText($sourcePage, $utf8)
        $content = $content.Replace("../_static/", "_static/")
        $content = $content.Replace("../_images/", "_images/")
        $content = $content.Replace("../_sources/_sources/", "_sources/")
        $content = $content.Replace("../", "")
        $content = $content.Replace(
            "DOCUMENTATION_OPTIONS.pagename = '_sources/$pageName';",
            "DOCUMENTATION_OPTIONS.pagename = '$pageName';"
        )
        [System.IO.File]::WriteAllText((Join-Path $root "$pageName.html"), $content, $utf8)
    }

    foreach ($directory in @("_static", "_images")) {
        $sourceDirectory = Join-Path $build $directory
        $destinationDirectory = Join-Path $root $directory
        if (Test-Path $sourceDirectory) {
            Copy-Item (Join-Path $sourceDirectory "*") -Destination $destinationDirectory -Recurse -Force
        }
    }

    $darkThemeStyle = @"
<style>
html[data-theme="dark"] {
  --bs-body-bg: var(--pst-color-background);
  --bs-body-color: var(--pst-color-text-base);
}
html[data-theme="dark"] .bd-content table,
html[data-theme="dark"] .bd-content th,
html[data-theme="dark"] .bd-content td {
  color: var(--pst-color-text-base);
}
</style>
"@
    $rootPages = @(Get-ChildItem $build -File -Filter "*.html" | Select-Object -ExpandProperty Name) +
        ($pageNames | ForEach-Object { "$_.html" })
    foreach ($rootPage in $rootPages) {
        $pagePath = Join-Path $root $rootPage
        if (Test-Path $pagePath) {
            $content = [System.IO.File]::ReadAllText($pagePath, $utf8)
            foreach ($pageName in $pageNames) {
                $escapedPageName = [uri]::EscapeDataString($pageName)
                $rootLink = "href=`"$escapedPageName.html`""
                $content = $content.Replace("href=`"_sources/$pageName.html`"", $rootLink)
                $content = $content.Replace("href=`"_sources/$escapedPageName.html`"", $rootLink)
            }
            $content = $content.Replace("</head>", "$darkThemeStyle`n</head>")
            [System.IO.File]::WriteAllText($pagePath, $content, $utf8)
        }
    }
}
finally {
    Pop-Location
}
