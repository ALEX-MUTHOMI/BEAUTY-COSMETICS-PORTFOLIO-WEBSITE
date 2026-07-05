# Mellis-style spa imagery — rooms, products, and treatment details only (no stock portraits).
# Run: powershell -ExecutionPolicy Bypass -File frontend/scripts/fetch-landing-images.ps1

$ErrorActionPreference = 'Continue'
$outDir = Join-Path $PSScriptRoot '..\public\images' | Resolve-Path
$headers = @{ 'User-Agent' = 'SheeAesthetics-ImageSync/1.0' }

$images = @{
  # Hero — spa atmosphere (interiors, candles, towels — no faces)
  'hero-1.jpg'          = 'https://images.pexels.com/photos/3993449/pexels-photo-3993449.jpeg?auto=compress&cs=tinysrgb&w=1920'
  'hero-2.jpg'          = 'https://images.pexels.com/photos/3757376/pexels-photo-3757376.jpeg?auto=compress&cs=tinysrgb&w=1920'
  'hero-3.jpg'          = 'https://images.pexels.com/photos/2500790/pexels-photo-2500790.jpeg?auto=compress&cs=tinysrgb&w=1920'
  'welcome.jpg'         = 'https://images.pexels.com/photos/3685530/pexels-photo-3685530.jpeg?auto=compress&cs=tinysrgb&w=1200'
  # Flow steps — booking desk mood, massage detail, checkout products
  'step-meeting.jpg'    = 'https://images.pexels.com/photos/3847656/pexels-photo-3847656.jpeg?auto=compress&cs=tinysrgb&w=600'
  'step-treatment.jpg'  = 'https://images.pexels.com/photos/3757942/pexels-photo-3757942.jpeg?auto=compress&cs=tinysrgb&w=600'
  'step-finalizing.jpg' = 'https://images.pexels.com/photos/3997999/pexels-photo-3997999.jpeg?auto=compress&cs=tinysrgb&w=600'
  # Service circles — treatment close-ups, no identifiable faces
  'service-facial.jpg'  = 'https://images.pexels.com/photos/3018845/pexels-photo-3018845.jpeg?auto=compress&cs=tinysrgb&w=800'
  'service-massage.jpg'   = 'https://images.pexels.com/photos/3757942/pexels-photo-3757942.jpeg?auto=compress&cs=tinysrgb&w=800'
  'service-waxing.jpg'    = 'https://images.pexels.com/photos/3992209/pexels-photo-3992209.jpeg?auto=compress&cs=tinysrgb&w=800'
  'service-makeup.jpg'    = 'https://images.pexels.com/photos/4467687/pexels-photo-4467687.jpeg?auto=compress&cs=tinysrgb&w=800'
  'cta-bg.jpg'            = 'https://images.pexels.com/photos/3993449/pexels-photo-3993449.jpeg?auto=compress&cs=tinysrgb&w=1920'
  # Gallery — studio mood board (rooms, products, tools)
  'gallery-1.jpg'         = 'https://images.pexels.com/photos/3993449/pexels-photo-3993449.jpeg?auto=compress&cs=tinysrgb&w=800'
  'gallery-2.jpg'         = 'https://images.pexels.com/photos/3757952/pexels-photo-3757952.jpeg?auto=compress&cs=tinysrgb&w=800'
  'gallery-3.jpg'         = 'https://images.pexels.com/photos/3685530/pexels-photo-3685530.jpeg?auto=compress&cs=tinysrgb&w=800'
  'gallery-4.jpg'         = 'https://images.pexels.com/photos/3757942/pexels-photo-3757942.jpeg?auto=compress&cs=tinysrgb&w=800'
  'gallery-5.jpg'         = 'https://images.pexels.com/photos/4467687/pexels-photo-4467687.jpeg?auto=compress&cs=tinysrgb&w=800'
  'gallery-6.jpg'         = 'https://images.pexels.com/photos/3997999/pexels-photo-3997999.jpeg?auto=compress&cs=tinysrgb&w=800'
  'blog-1.jpg'            = 'https://images.pexels.com/photos/3018845/pexels-photo-3018845.jpeg?auto=compress&cs=tinysrgb&w=900'
  'blog-2.jpg'            = 'https://images.pexels.com/photos/4467687/pexels-photo-4467687.jpeg?auto=compress&cs=tinysrgb&w=900'
  'blog-3.jpg'            = 'https://images.pexels.com/photos/3757376/pexels-photo-3757376.jpeg?auto=compress&cs=tinysrgb&w=900'
}

$ok = 0
$fail = 0
foreach ($entry in $images.GetEnumerator()) {
  $dest = Join-Path $outDir $entry.Key
  Write-Host "Fetching $($entry.Key)..."
  try {
    Invoke-WebRequest -Uri $entry.Value -OutFile $dest -UseBasicParsing -Headers $headers -TimeoutSec 60
    $ok++
  } catch {
    Write-Warning "Failed $($entry.Key): $_"
    $fail++
  }
}

Write-Host "Done. $ok updated, $fail failed - $outDir"
