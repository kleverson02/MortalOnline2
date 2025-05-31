from lib.memory import PatternScanner

# pylint: disable=invalid-name

GWorld_pat = ("85 c0 75 ? ? 8b 05 ? ? ? ? c3", 7)
GNames_pat = ("8b 05 ? ? ? ? ff c0 c1 e9", 2)

scanner = PatternScanner("GameThread", "Win64-Shipping.exe")
GWorld = scanner.pattern_scan(GWorld_pat[0], GWorld_pat[1])
GNames = scanner.pattern_scan(GNames_pat[0], GNames_pat[1]) + 8
del scanner

PersistentLevel = 0x30
ActorArray = 0xA0 #0xB0

OwningGameInstance = 0x1D8
LocalPlayers = 0x38
PlayerController = 0x30
PlayerCameraManager = 0x350
CameraCachePrivate = 0x1448 #(PC 350) 1440,1448,1470, 
AcknowledgedPawn = 0x350 # usado 350

RootComponent = 0x1B8  # Atualizado de 0x1A0 para 0x1B8
RootPos = 0xF0   # 108, F8, F0

IsGhost = 0x658
CreatureName = 0xC80
Health = 0xCC0
GuildName = 0xCB0

MeshName = 0x2E8


# isGhost esses 3 offsets estao mudando 0x651 0x653 0x0658


# informação que nao deve ser alterada 
# Combinacoes PCM 0x300 |0x1310
# Combinacoes PC 0x350 |0x1368 | 1370, 1378 |0x1380|

# Fluxo 
# UWorld -> OwningGameInstance (0x1D8)
# GameInstance -> LocalPlayers (0x38)
# LocalPlayers[0] (primeiro elemento do array)
# LocalPlayer -> PlayerController (0x30)
# PlayerController -> AcknowledgedPawn (0x350)
# Pawn -> RootComponent (0x1B8)
# RootComponent -> RootPos (0x108)

