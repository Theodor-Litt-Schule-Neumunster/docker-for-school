[Setup]
AppName=DockerLab
AppVersion=1.0.0
DefaultDirName={sd}\DockerLab
DefaultGroupName=DockerLab
OutputDir=.
OutputBaseFilename=DockerLab-Setup
Compression=lzma2
SolidCompression=yes
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
DisableDirPage=no
DisableProgramGroupPage=yes
UsePreviousAppDir=no
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\icon.ico

[Languages]
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[Files]
Source: "..\docker-compose.yml"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\homepage-data\*"; DestDir: "{app}\homepage-data"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\vscode-docker\*"; DestDir: "{app}\vscode-docker"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "start-DockerLab.ps1"; DestDir: "{app}"; Flags: ignoreversion
Source: "start-DockerLab.cmd"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Dirs]
Name: "{app}\vscode-data"; Flags: uninsalwaysuninstall
Name: "{app}\vscode-config"; Flags: uninsalwaysuninstall
Name: "{app}\windowsserver2022"; Flags: uninsalwaysuninstall
Name: "{app}\debian"; Flags: uninsalwaysuninstall

[Icons]
Name: "{group}\DockerLab starten"; Filename: "{app}\start-DockerLab.cmd"; WorkingDir: "{app}"; IconFilename: "{app}\icon.ico"
Name: "{commondesktop}\DockerLab"; Filename: "{app}\start-DockerLab.cmd"; WorkingDir: "{app}"; Tasks: desktopicon; IconFilename: "{app}\icon.ico"

[Tasks]
Name: "desktopicon"; Description: "Desktop-Verknüpfung erstellen"; Flags: unchecked

[Run]
Filename: "{app}\start-DockerLab.cmd"; WorkingDir: "{app}"; Description: "DockerLab starten"; Flags: nowait postinstall skipifsilent
