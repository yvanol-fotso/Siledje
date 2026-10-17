[Setup]
AppName=Siledje
AppVersion=1.0.0
AppPublisher=Siledje
DefaultDirName={autopf}\Siledje
DefaultGroupName=Siledje
OutputBaseFilename=Siledje_Setup_1.0.0
SetupIconFile=assets\images\siledje.ico
UninstallDisplayIcon={app}\Siledje.exe
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Files]
Source: "dist\Siledje\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{group}\Siledje"; Filename: "{app}\Siledje.exe"
Name: "{autodesktop}\Siledje"; Filename: "{app}\Siledje.exe"

[Run]
Filename: "{app}\Siledje.exe"; Description: "Lancer Siledje"; Flags: nowait postinstall