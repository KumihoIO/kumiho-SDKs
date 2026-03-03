param(
    [string]$BuildDir = "build-vs2022",
    [ValidateSet("Debug", "Release", "RelWithDebInfo", "MinSizeRel")]
    [string]$Config = "Release",
    [string]$Generator = "Visual Studio 17 2022",
    [switch]$Integration,
    [switch]$IncludeLiveApiTests,
    [string]$VcpkgRoot = $env:VCPKG_ROOT
)

$ErrorActionPreference = "Stop"

function Resolve-VsCMakeBin {
    $vswhere = Join-Path ${env:ProgramFiles(x86)} "Microsoft Visual Studio\Installer\vswhere.exe"
    if (-not (Test-Path $vswhere)) {
        return $null
    }

    $installPath = & $vswhere -latest -products * -requires Microsoft.Component.MSBuild -property installationPath
    if ([string]::IsNullOrWhiteSpace($installPath)) {
        return $null
    }

    $cmakeBin = Join-Path $installPath "Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin"
    if (-not (Test-Path $cmakeBin)) {
        return $null
    }
    return $cmakeBin
}

function Resolve-CMake {
    $cmd = Get-Command cmake -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Path }

    $cmakeBin = Resolve-VsCMakeBin
    if ($cmakeBin) {
        $cmakeExe = Join-Path $cmakeBin "cmake.exe"
        if (Test-Path $cmakeExe) { return $cmakeExe }
    }
    throw "cmake not found. Install CMake or run from a VS Developer PowerShell."
}

function Resolve-CTest {
    $cmd = Get-Command ctest -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Path }

    $cmakeBin = Resolve-VsCMakeBin
    if ($cmakeBin) {
        $ctestExe = Join-Path $cmakeBin "ctest.exe"
        if (Test-Path $ctestExe) { return $ctestExe }
    }
    throw "ctest not found. Install CMake or run from a VS Developer PowerShell."
}

function Resolve-RepoRoot {
    $scriptDir = Split-Path -Parent $PSCommandPath
    return (Resolve-Path (Join-Path $scriptDir ".."))
}

$repoRoot = Resolve-RepoRoot
$buildPath = Join-Path $repoRoot $BuildDir

$cmakeExe = Resolve-CMake
$ctestExe = Resolve-CTest

if ([string]::IsNullOrWhiteSpace($VcpkgRoot)) {
    throw "VCPKG_ROOT is not set. Set `$env:VCPKG_ROOT to your vcpkg root (e.g. C:\\vcpkg) or pass -VcpkgRoot."
}

$toolchainFile = Join-Path $VcpkgRoot "scripts\buildsystems\vcpkg.cmake"
if (-not (Test-Path $toolchainFile)) {
    throw "vcpkg toolchain file not found at: $toolchainFile"
}

Write-Host "== Configure ==" -ForegroundColor Cyan
& $cmakeExe -S $repoRoot -B $buildPath -G $Generator -A x64 `
    -DCMAKE_TOOLCHAIN_FILE=$toolchainFile `
    -DKUMIHO_BUILD_TESTS=ON `
    -DKUMIHO_BUILD_INTEGRATION_TESTS=ON

Write-Host "== Build ($Config) ==" -ForegroundColor Cyan
& $cmakeExe --build $buildPath --config $Config

Write-Host "== Test ($Config) ==" -ForegroundColor Cyan

$ctestArgs = @(
    "--test-dir", $buildPath,
    "-C", $Config,
    "--output-on-failure"
)

if ($Integration) {
    # Integration tests are labeled "integration" and will self-skip unless KUMIHO_INTEGRATION_TEST=1.
    $env:KUMIHO_INTEGRATION_TEST = "1"
    $ctestArgs += @("-L", "integration")
} else {
    # Unit run: exclude integration-labeled tests.
    $ctestArgs += @("-LE", "integration")
}

& $ctestExe @ctestArgs
