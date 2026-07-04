# Downloads curated Pexels spa/beauty images for Shee Aesthetics landing.
# Run: powershell -ExecutionPolicy Bypass -File frontend/scripts/fetch-landing-images.ps1

$ErrorActionPreference = 'Continue'
$outDir = Join-Path $PSScriptRoot '..\public\images' | Resolve-Path
$headers = @{ 'User-Agent' = 'SheeAesthetics-ImageSync/1.0' }

$images = @{
  'hero-1.jpg'         = 'https://images.pexels.com/photos/5069437/pexels-photo-5069437.jpeg?auto=compress&cs=tinysrgb&w=1920'
  'hero-2.jpg'         = 'https://images.pexels.com/photos/7750099/pexels-photo-7750099.jpeg?auto=compress&cs=tinysrgb&w=1920'
  'hero-3.jpg'         = 'https://images.pexels.com/photos/3757376/pexels-photo-3757376.jpeg?auto=compress&cs=tinysrgb&w=1920'
  'welcome.jpg'        = 'https://images.pexels.com/photos/5069437/pexels-photo-5069437.jpeg?auto=compress&cs=tinysrgb&w=1200'
  'service-facial.jpg' = 'https://images.pexels.com/photos/5069620/pexels-photo-5069620.jpeg?auto=compress&cs=tinysrgb&w=800'
  'service-massage.jpg'= 'https://images.pexels.com/photos/3757942/pexels-photo-3757942.jpeg?auto=compress&cs=tinysrgb&w=800'
  'service-waxing.jpg' = 'https://images.pexels.com/photos/3992878/pexels-photo-3992878.jpeg?auto=compress&cs=tinysrgb&w=800'
  'service-makeup.jpg' = 'https://images.pexels.com/photos/4467682/pexels-photo-4467682.jpeg?auto=compress&cs=tinysrgb&w=800'
  'cta-bg.jpg'         = 'https://images.pexels.com/photos/3993449/pexels-photo-3993449.jpeg?auto=compress&cs=tinysrgb&w=1920'
  'gallery-1.jpg'      = 'https://images.pexels.com/photos/5069437/pexels-photo-5069437.jpeg?auto=compress&cs=tinysrgb&w=800'
  'gallery-2.jpg'      = 'https://images.pexels.com/photos/7750099/pexels-photo-7750099.jpeg?auto=compress&cs=tinysrgb&w=800'
  'gallery-3.jpg'      = 'https://images.pexels.com/photos/3757376/pexels-photo-3757376.jpeg?auto=compress&cs=tinysrgb&w=800'
  'gallery-4.jpg'      = 'https://images.pexels.com/photos/5069620/pexels-photo-5069620.jpeg?auto=compress&cs=tinysrgb&w=800'
  'gallery-5.jpg'      = 'https://images.pexels.com/photos/4467682/pexels-photo-4467682.jpeg?auto=compress&cs=tinysrgb&w=800'
  'gallery-6.jpg'      = 'https://images.pexels.com/photos/3992878/pexels-photo-3992878.jpeg?auto=compress&cs=tinysrgb&w=800'
  'blog-1.jpg'         = 'https://images.pexels.com/photos/5069620/pexels-photo-5069620.jpeg?auto=compress&cs=tinysrgb&w=900'
  'blog-2.jpg'         = 'https://images.pexels.com/photos/4467682/pexels-photo-4467682.jpeg?auto=compress&cs=tinysrgb&w=900'
  'blog-3.jpg'         = 'https://images.pexels.com/photos/5069437/pexels-photo-5069437.jpeg?auto=compress&cs=tinysrgb&w=900'
  'testimonial-1.jpg'  = 'https://images.pexels.com/photos/774909/pexels-photo-774909.jpeg?auto=compress&cs=tinysrgb&w=400'
  'testimonial-2.jpg'  = 'https://images.pexels.com/photos/1181519/pexels-photo-1181519.jpeg?auto=compress&cs=tinysrgb&w=400'
  'testimonial-3.jpg'  = 'https://images.pexels.com/photos/1181690/pexels-photo-1181690.jpeg?auto=compress&cs=tinysrgb&w=400'
}

$ok = 0
$fail = 0
foreach ($entry in $images.GetEnumerator()) {
  $dest = Join-Path $outDir $entry.Key
  Write-Host "Fetching $($entry.Key)..."
  try {
    Invoke-WebRequest -Uri $entry.Value -OutFile $dest -UseBasicParsing -Headers $headers
    $ok++
  } catch {
    Write-Warning "Failed $($entry.Key): $_"
    $fail++
  }
}

Write-Host "Done. $ok updated, $fail failed - $outDir"
