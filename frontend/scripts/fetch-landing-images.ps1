# Curated Shee Aesthetics imagery — each file mapped to a verified Pexels beauty/spa shot.
# Run: powershell -ExecutionPolicy Bypass -File frontend/scripts/fetch-landing-images.ps1

$ErrorActionPreference = 'Continue'
$outDir = Join-Path $PSScriptRoot '..\public\images' | Resolve-Path
$headers = @{ 'User-Agent' = 'SheeAesthetics-ImageSync/2.0' }

$images = @{
  # Hero carousel: 1=spa room, 2=massage, 3=makeup application
  'hero-1.jpg'          = 'https://images.pexels.com/photos/3997999/pexels-photo-3997999.jpeg?auto=compress&cs=tinysrgb&w=1920'
  'hero-2.jpg'          = 'https://images.pexels.com/photos/3757942/pexels-photo-3757942.jpeg?auto=compress&cs=tinysrgb&w=1920'
  'hero-3.jpg'          = 'https://images.pexels.com/photos/2533266/pexels-photo-2533266.jpeg?auto=compress&cs=tinysrgb&w=1920'
  'welcome.jpg'         = 'https://images.pexels.com/photos/3997999/pexels-photo-3997999.jpeg?auto=compress&cs=tinysrgb&w=800'
  'more-bg.jpg'         = 'https://images.pexels.com/photos/3757952/pexels-photo-3757952.jpeg?auto=compress&cs=tinysrgb&w=1920'
  # Steps: consultation, treatment, glowing finish
  'step-meeting.jpg'    = 'https://images.pexels.com/photos/6476582/pexels-photo-6476582.jpeg?auto=compress&cs=tinysrgb&w=600'
  'step-treatment.jpg'  = 'https://images.pexels.com/photos/3757942/pexels-photo-3757942.jpeg?auto=compress&cs=tinysrgb&w=600'
  'step-finalizing.jpg' = 'https://images.pexels.com/photos/3018845/pexels-photo-3018845.jpeg?auto=compress&cs=tinysrgb&w=600'
  'service-facial.jpg'  = 'https://images.pexels.com/photos/3018845/pexels-photo-3018845.jpeg?auto=compress&cs=tinysrgb&w=800'
  'service-massage.jpg' = 'https://images.pexels.com/photos/3757942/pexels-photo-3757942.jpeg?auto=compress&cs=tinysrgb&w=800'
  'service-waxing.jpg'  = 'https://images.pexels.com/photos/3992209/pexels-photo-3992209.jpeg?auto=compress&cs=tinysrgb&w=800'
  'service-makeup.jpg'  = 'https://images.pexels.com/photos/2533266/pexels-photo-2533266.jpeg?auto=compress&cs=tinysrgb&w=800'
  'cta-bg.jpg'          = 'https://images.pexels.com/photos/3997999/pexels-photo-3997999.jpeg?auto=compress&cs=tinysrgb&w=1920'
  'gallery-1.jpg'       = 'https://images.pexels.com/photos/3997999/pexels-photo-3997999.jpeg?auto=compress&cs=tinysrgb&w=800'
  'gallery-2.jpg'       = 'https://images.pexels.com/photos/3757942/pexels-photo-3757942.jpeg?auto=compress&cs=tinysrgb&w=800'
  'gallery-3.jpg'       = 'https://images.pexels.com/photos/2533266/pexels-photo-2533266.jpeg?auto=compress&cs=tinysrgb&w=800'
  'gallery-4.jpg'       = 'https://images.pexels.com/photos/3757952/pexels-photo-3757952.jpeg?auto=compress&cs=tinysrgb&w=800'
  'gallery-5.jpg'       = 'https://images.pexels.com/photos/3018845/pexels-photo-3018845.jpeg?auto=compress&cs=tinysrgb&w=800'
  'gallery-6.jpg'       = 'https://images.pexels.com/photos/3992877/pexels-photo-3992877.jpeg?auto=compress&cs=tinysrgb&w=800'
}

$ok = 0
$fail = 0
foreach ($entry in $images.GetEnumerator()) {
  $dest = Join-Path $outDir $entry.Key
  Write-Host "Fetching $($entry.Key)..."
  try {
    Invoke-WebRequest -Uri $entry.Value -OutFile $dest -UseBasicParsing -Headers $headers -TimeoutSec 90
    $ok++
  } catch {
    Write-Warning "Failed $($entry.Key): $_"
    $fail++
  }
}

Write-Host "Done. $ok updated, $fail failed - $outDir"
