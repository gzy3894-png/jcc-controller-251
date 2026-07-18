# JCC Controller 固定签名（与 2.5.2 起一致）
#
# keystore: signing/jcc-controller.release.keystore
# storepass: android
# keypass:   android
# alias:     androiddebugkey
#
# 证书 SHA256（安装后可用 apksigner verify -v 核对）:
# 1E08A903AEF9C3A721510B64EC764D01D3D094EB954161B62544EA8F187B5953
#
# 从 2.5.2 起：用本 keystore 签名的版本可互相覆盖安装，无需卸载。
# 从原版 2.5.0 升到本系列：仍需先卸载（原作者签名不同）。
