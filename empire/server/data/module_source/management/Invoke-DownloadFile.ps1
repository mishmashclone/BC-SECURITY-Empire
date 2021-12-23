function Invoke-DownloadFile {
<#PSScriptInfo

.VERSION 19.05.24

.GUID d1de0de3-d0f2-4094-a2f2-f75cd8d0fab3

.AUTHOR Tim Small

.COMPANYNAME

.COPYRIGHT 2019

.TAGS web download webclient

.LICENSEURI

.PROJECTURI https://github.com/Smalls1652/Get-RandomPowerShellScripts/blob/master/Actions/Networking/Invoke-DownloadFile.ps1

.ICONURI

.EXTERNALMODULEDEPENDENCIES 

.REQUIREDSCRIPTS

.EXTERNALSCRIPTDEPENDENCIES

.RELEASENOTES
Fixed current dir paths

.PRIVATEDATA

#> 





<# 

.DESCRIPTION 
 Download files from the internet through PowerShell. 

#>

[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory = $true)][string]$Url,
    [string]$Path
)

function convertFileSize {
    param(
        $bytes
    )

    if ($bytes -lt 1MB) {
        return "$([Math]::Round($bytes / 1KB, 2)) KB"
    }
    elseif ($bytes -lt 1GB) {
        return "$([Math]::Round($bytes / 1MB, 2)) MB"
    }
    elseif ($bytes -lt 1TB) {
        return "$([Math]::Round($bytes / 1GB, 2)) GB"
    }
}

Write-Host "URL set to ""$($Url)""."

switch ($Path) {
    { ([regex]::Match($PSItem, "(?:(?:.+[\/\\]){2,}(?:(?'fileName'.+)|)|.+)").Groups | Where-Object -Property "Name" -eq "fileName" | Select-Object -ExpandProperty "Success") -eq $false } {
        "[*] Path parameter set, but no filename. Parsing Url for filename."
        if (!([regex]::Match($Path, "^.+[\/\\]$") | Select-Object -ExpandProperty "Success")) {
            if ($Path.ToCharArray() -contains "/") {
                $Path = "$($Path)/"
            }
            elseif ($Path.ToCharArray() -contains "\") {
                $Path = "$($Path)\"
            }
        }
        $URLParser = $Url | Select-String -Pattern ".*\:\/\/.*\/(.*\.{1}\w*).*" -List

        $Path = "$($Path)$($URLParser.Matches.Groups[1].Value)"
    }
    Default {
        "[*] Path parameter not set, parsing Url for filename."
        $URLParser = $Url | Select-String -Pattern ".*\:\/\/.*\/(.*\.{1}\w*).*" -List

        $Path = "./$($URLParser.Matches.Groups[1].Value)"
    }
}

"[*] Path set to ""$($Path)""."

#Load in the WebClient object.
"[*] Loading in WebClient object."
try {
    $Downloader = New-Object -TypeName System.Net.WebClient
}
catch [Exception] {
    Write-Error $_ -ErrorAction Stop
}

#Creating a temporary file.
$TmpFile = New-TemporaryFile
"[*] TmpFile set to ""$($TmpFile)""."

try {

    #Start the download by using WebClient.DownloadFileTaskAsync, since this lets us show progress on screen.
    "[+] Starting download..."
    $Downloader.Headers.Add("User-Agent: Other");
    $FileDownload = $Downloader.DownloadFileTaskAsync($Url, $TmpFile)

    #Register the event from WebClient.DownloadProgressChanged to monitor download progress.
    "[*] Registering the ""DownloadProgressChanged"" event handle from the WebClient object."
    Register-ObjectEvent -InputObject $Downloader -EventName DownloadProgressChanged -SourceIdentifier WebClient.DownloadProgressChanged | Out-Null

    #Wait two seconds for the registration to fully complete
    Start-Sleep -Seconds 3

    if ($FileDownload.IsFaulted) {
        "[!] An error occurred. Generating error."
        Write-Error $FileDownload.GetAwaiter().GetResult()
        break
    }

    #While the download is showing as not complete, we keep looping to get event data.
    while (!($FileDownload.IsCompleted)) {

        if ($FileDownload.IsFaulted) {
            "[!] An error occurred. Generating error."
            Write-Error $FileDownload.GetAwaiter().GetResult()
            break
        }

        $EventData = Get-Event -SourceIdentifier WebClient.DownloadProgressChanged | Select-Object -ExpandProperty "SourceEventArgs" -Last 1

        $ReceivedData = ($EventData | Select-Object -ExpandProperty "BytesReceived")
        $TotalToReceive = ($EventData | Select-Object -ExpandProperty "TotalBytesToReceive")
        $TotalPercent = $EventData | Select-Object -ExpandProperty "ProgressPercentage"

        Write-Progress -Activity "Downloading File" -Status "Percent Complete: $($TotalPercent)%" -CurrentOperation "Downloaded $(convertFileSize -bytes $ReceivedData) / $(convertFileSize -bytes $TotalToReceive)" -PercentComplete $TotalPercent
    }
}
catch [Exception] {
    $ErrorDetails = $_

    switch ($ErrorDetails.FullyQualifiedErrorId) {
        "ArgumentNullException" { 
            Write-Error -Exception "ArgumentNullException" -ErrorId "ArgumentNullException" -Message "Either the Url or Path is null." -Category InvalidArgument -TargetObject $Downloader -ErrorAction Stop
        }
        "WebException" {
            Write-Error -Exception "WebException" -ErrorId "WebException" -Message "An error occurred while downloading the resource." -Category OperationTimeout -TargetObject $Downloader -ErrorAction Stop
        }
        "InvalidOperationException" {
            Write-Error -Exception "InvalidOperationException" -ErrorId "InvalidOperationException" -Message "The file at ""$($Path)"" is in use by another process." -Category WriteError -TargetObject $Path -ErrorAction Stop
        }
        Default {
            Write-Error $ErrorDetails -ErrorAction Stop
        }
    }
}
finally {
    #Cleanup tasks
    "[*] Cleaning up..."
    Write-Progress -Activity "Downloading File" -Completed
    Unregister-Event -SourceIdentifier WebClient.DownloadProgressChanged

    if (($FileDownload.IsCompleted) -and !($FileDownload.IsFaulted)) {
        #If the download was finished without termination, then we move the file.
        "[*] Moved the downloaded file to ""$($Path)""."
        Move-Item -Path $TmpFile -Destination $Path -Force
    }
    else {
        #If the download was terminated, we remove the file.
        "[*] Cancelling the download and removing the tmp file."
        $Downloader.CancelAsync()
        Remove-Item -Path $TmpFile -Force
    }

    $Downloader.Dispose()
  }
}
