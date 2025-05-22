from lib.memory import PatternScanner

# pylint: disable=invalid-name

GWorld_pat = ("85 c0 75 ? ? 8b 05 ? ? ? ? c3", 7)
GNames_pat = ("8b 05 ? ? ? ? ff c0 c1 e9", 2)

scanner = PatternScanner("GameThread", "Win64-Shipping.exe")
GWorld = scanner.pattern_scan(GWorld_pat[0], GWorld_pat[1])
GNames = scanner.pattern_scan(GNames_pat[0], GNames_pat[1]) + 8
del scanner

# UWorld offsets
PersistentLevel = 0x30
OwningGameInstance = 0x1D8

# PersistentLevel offsets
ActorArray = 0xA0

# GameInstance offsets
LocalPlayers = 0x38

# LocalPlayer offsets
PlayerController = 0x30 #Temos o 28 e o 30

# PlayerController offsets
PlayerCameraManager = 0x358
AcknowledgedPawn = 0x340  #provavel ser o 340 mesmo

# PlayerCameraManager offsets
CameraCachePrivate = 0x13C8
CameraRotation = 0x13F0  # Offset para a rotação da câmera
CameraViewRotation = 0x1400  # Offset alternativo para a rotação da câmera
CameraRotation2 = 0x13A0  # Offset adicional para tentar (parece ter valores não-zero)
CameraRotation3 = 0x13A8  # Outro offset adicional para tentar

# Actor offsets
RootComponent = 0x1B8 # pravavel 1A0 ou 1B8 no format 3d
IsGhost = 0x688
CreatureName = 0xC80
Health = 0xCC0
MeshName = 0x2E8

# RootComponent offsets
RootPos = 0xF8 # ultimo estava F8 encontrado tb o E0 no fomart 3d
RootRot = 0x104 # Offset para a rotação do componente (quaternion)

# O nome dos players no offset fica no 0xC80
