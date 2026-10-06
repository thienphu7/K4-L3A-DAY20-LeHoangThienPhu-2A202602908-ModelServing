param([ValidateSet('ON','OFF')][string]$Native = 'ON')
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$toolsRoot = 'C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools'
$devCmd = Join-Path $toolsRoot 'Common7\Tools\VsDevCmd.bat'
if (-not (Test-Path -LiteralPath $devCmd)) { throw "Missing toolchain: $devCmd" }
$envLines = & cmd.exe /d /c "call `"$devCmd`" -arch=x64 -host_arch=x64 >nul && set"
if ($LASTEXITCODE -ne 0) { throw 'Developer environment failed' }
foreach ($line in $envLines) {
    if ($line -match '^([^=]+)=(.*)$') {
        [Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
    }
}
$cmake = Join-Path $toolsRoot 'Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe'
$ninja = Join-Path $toolsRoot 'Common7\IDE\CommonExtensions\Microsoft\CMake\Ninja\ninja.exe'
$buildDir = if ($Native -eq 'ON') { 'bonus/llama.cpp/build' } else { 'bonus/llama.cpp/build-zbaseline' }
& $cmake -S bonus/llama.cpp -B $buildDir -G Ninja "-DCMAKE_MAKE_PROGRAM=$ninja" -DCMAKE_BUILD_TYPE=Release "-DGGML_NATIVE=$Native" -DGGML_CUDA=OFF -DGGML_VULKAN=OFF -DLLAMA_BUILD_TESTS=OFF -DLLAMA_CURL=OFF
if ($LASTEXITCODE -ne 0) { throw 'CMake configure failed' }
& $cmake --build $buildDir --target llama-bench --parallel 4
if ($LASTEXITCODE -ne 0) { throw 'Compilation failed' }
Write-Host "Release CPU build complete: GGML_NATIVE=$Native, $buildDir"
