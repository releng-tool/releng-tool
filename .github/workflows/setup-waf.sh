#!/usr/bin/env bash
#
# Script to install `waf` into the platform.

# setup an interim directory
temp_dir=$(mktemp -d); pushd "$temp_dir" >/dev/null || exit 1

###############################################################################
# Version to install.

waf_version="2.1.9"

cat <<EOF >waf-"$waf_version".tar.bz2.asc
-----BEGIN PGP SIGNATURE-----

iQIzBAABCgAdFiEEjH6y+TsMRfVzL+XRG6xXHc13IpUFAmkVHS0ACgkQG6xXHc13
IpWyqQ//cC4kju+ibnjb6hFsoV1mbHzt6Oweg2IavWyVWq0zcBosEwEoMWxqG7ou
o7GjFDx8paN/vb+RYKzvN5kj6wT0BXBICq6MDOS26kNS2/fvtKTfIRI1T6H3PBlg
qMKN9H2DBaV3zR4/E05qjjYbNyNeUjBjIJixHPot/RNjrT5kj8+1EoH6RYiEXvcX
pZwSf1tPJINjd4O7mcoWPV+SqyzzBZl/8mgRWn1vy4UsH/haxDRwixZkS0bQ12Xc
kSVBhoLZdG3JATwUDILs9BsKpCQ1cLiX53WRnEB/TsrVW2E0wR5r+N1YgqAEnQ0w
NpKNRbztPP3z92yb5aUyqdIUUnuUvDtkln1enD4eRqWRYla7yTYp3+BZtLrg9ZHX
6LLWzNwRKDdZ9EU5hFhcmr4Zv1BndByJKIHfuRC+ZeJkZ8NUop2hIjgOiRZtKphl
bGbf2j/BMt51krhJ2qyL6SAZ/B9GStETJtzLJqqckdpO3tTN6Pfc/NnSrluU6sNy
TLOQgl303LvFZdM6ucOX+Npk/4K3h++lhA4iXx/xTnO+1m0RC1ZMVq95ZuVpru8w
IZP/MQtghRWLp11yhrIYQouZJIWysZM9hLRQjusP/jCuv5+7t/ip9lo7e3DBh+Aq
2WmpwrzhvNFFqHmbD86KM9IEaAL4hjYAmCKLorgmslhCrHEZDQU=
=Wmjt
-----END PGP SIGNATURE-----
EOF

###############################################################################

# waf's project public key
gpg --import <<EOF
-----BEGIN PGP PUBLIC KEY BLOCK-----

mQINBGTWwoEBEADYhx0mRt8fzJ0i9bGJctQSh4gyCXC9vHkclmtw8j/3ixFid045
dajTcrjfUyGkErN4YPWiS94Fffv/1ATC+CH9AfYJuS5htQAx3j/0vbdSI2tstzxr
yemtBUCrmMKCGUA1rln3eo4e2/v/qJLxEZ0/PkXCmsFZkucU4BFH20i3lGswGZZn
yoppZsFAsGeZ0JZQnKeJuqvASPuzTPvvfEd1tErvNOtRJ9ObJDSSgKaWZaBSU4x5
ARIjdzETSzstOYL+SgW2wiVoV0h9pAVaXCeL6e4Llr6fp6ptgqxcdlznLaIZhmuA
kmtGT2Cb8MxbgAqr2LWhgSN9VxvAe0yToMoRzj95RuAn054Kgcr2e9/CDDRvK45z
tuaP+579j+cUM0lNGyUxN/ZzMYdMs+xB816zokyV07WrNXbx0u16kzeLl5nP3cdB
H9b/14DCiq85hsAeDyZFAbWT7Cn26WYpHZj8mkFyFmba/jOCisTZW6iFekADarvE
ybctOUUMdrdtsqo53leYCrypWlJta4ixhNaGCMIw0p8/fZCcx5ECj3q5NXt+ZKiZ
5/f70LhsxvlcfNo9m2P06eit+IMV7STSx0CTKZUPyga5KeqGi4EtJZ0KGZWfBXhF
ODQAYpdnIMV+/9fMF0EE9iB0sgL0Me8hUL2KkhTWJ2OwnmE0VAZ5W+JmywARAQAB
tBxXYWYgUHJvamVjdCA8bm9yZXBseUB3YWYuaW8+iQJMBBMBCgA2FiEEjH6y+TsM
RfVzL+XRG6xXHc13IpUFAmTWwoECGwMFCRLMAwADCwkIBRUKCQgLAh4BAheAAAoJ
EBusVx3NdyKVSLsP/00nputckP0s1aC7ZSK+wiHn6umA4/kX4i+i+mQvStajsTZr
sSOs8UxL7kxRMDrKGdNekjxs0JU/MZ5+xL8+1odFxr/GSF343/9qXze301SKnmeS
ev3P/EJ9jkv8q+7LVjwlIkJ09OajvlEdC8Gkm6RuOaUcmO1G7secqCs15GXh+f8n
wS3nM0TGitzpomqE09C7OywUe3HhB+lSKCcOf6/8SFIeuxh5dp9Pcj3gUlpwXevH
IT/V+pMR/YlocpWQFyuMIRMIUCuYaWnHxndoB87ctwsepidQWj5DnbAG7gYGemGa
hhFG0VVHoLrR3tZAJcNxtr37E/9Efb152Ki9Eip+Pm5ov0miTGES1wCuFCmZXGaZ
aJcLBHng/iQme2XkRZ1t1MkywFK6eMvv3IBn3tICw54h5x6A7W2qTNeNvu3NQ7Oe
LRleMUmMFfceAXoCCqzcsdK44yetUutRSrEBf1hO13v34R5/DWagk1MU8y7SLBHA
oeIM1JwI0NEQx4kn1PLXBQbqllVllBakuPdIrk8zmflHd6/mSWcH2M2kDRzucuJN
ro912aDcD1Fp4WUM+CRfsP6tgkaDK1mXL/whtkHomMOUeA0OhGO8hp68PEb7toNR
h95ZBcAyRl7K/77Un80HxPT6rHBHyZOsX745UdivHbcdv/yjRNUywC/82RkiuQIN
BGTWwoEBEADEMA0ny4v9n7fjZPS9m8dypPXKgLUtlJKg9W1X8Wu5DiC+j24dhvoP
1IBVdEsRIRgDEu7VCI6t2OdlX7+4EYP3ltFlZ/tIgd8yhq2Kaim6hnQLPBehq/0K
7EXqvhZ5wxLi9jaW4ltlcmMPpEm/MBv0nv19TwEocQfevioFZwX/sohaRpqS8R26
YVSBNsdmC1arJEXaFtmrXGPXMcCDflbkJ+Sk4okpkBANWHeNftT0LSV/5fov/gbA
nlwm7+UCU+D81JlCH1S1mHGHgHVsQatDSuN1GLdg0Uk85t/qrqpXcjz8SYMfqP1E
TPeq3DaArOtUxKdHR8dDtwZ4zRthhoOcqB9PvVXYq65f9+ad9fmASgYdrHMNccqg
V7VGu761MCD90iB2R7z4Ga3BWfxs+ywDV+wTzgMINRV1HlbNYpCF/vzUlvpBBx9f
ryclk6HhF6qtV3vWb5+r6gXUFunP9VBXqCOeJtbxBxRGImfYuuFen9qdq0aWtxl0
59oO4Sj1vRxMnw6T5di13WgtGSKvI6SKgXf37o+u5+YepQVTOEg84mciS4GKq8KI
CTcMlO0LItU2Y1BD6T+RO6YdGVGU3CLUnq3WsTQ0mBtFNkeIwMNfU5yNynDO6Y2d
O4R9nB7uhrlSudheIj8VIIsMlPgBfIvkErjOAfGXsEWSmsRWRja2YQARAQABiQI8
BBgBCgAmFiEEjH6y+TsMRfVzL+XRG6xXHc13IpUFAmTWwoECGwwFCRLMAwAACgkQ
G6xXHc13IpU58A/+KBmBO5vQ1sWiGczB5i887/v+fvbcbS6fHkLIaxApimVGXklV
Qjp7MGq1K1vnzPc0ovu9aFbxfdNSq6iwhAvB1Q9JFv1b7zhyWiaOIeCM6mYliBZW
GnWEe56GMiYW503vlglUEoYJ/4N/I6r1i5mNMj8D6xqtZfbAOk3bnt9ws7yBOpKe
LfZXWz9q23fXg1PRKmU0E9OFC87tfw/5Wltp7GVFzFdLWchhITTYcO+sjF3O2yNv
3STUQpmdx9NEZSEWKIEd7msnf7BA5FnNPjWZx59FULZWzuWOcJ/foPbktpvKXF34
yT5SV9UIlXjCteZrMd5fxK5u6Tacae5n6fw8eFbS4l/6BOxSGROb+H3ilpqebzvJ
gv8ryQkFh076BevWndJMeq5kxuKv49jVON4SzbtEReLRkcFXFD6mGK+2d02ksW+f
NiGMBQYTXCfY97LROieyQ32hvhAIqacnE7L7F0U6Yz98gVkq57ThHBLNfOu4gqYj
PhpOr/iddN1mVNxzZagx+serw7xQUg8WhoFA9QkWmx7Bn3PGQnrtGEslbL6Lo+pI
VOzahFM1mHIcv3bfbGlN54fgKUoFOElnlSBNZrFS6E74MoNRq2CLzRmku7uNDcVR
IYlK05zLaeHsRNnBKgN7YOW05M4p+0K5OecuXm66Yajezi/+vyMf13tulIU=
=zzf7
-----END PGP PUBLIC KEY BLOCK-----
EOF

# download package
wget https://waf.io/waf-"$waf_version".tar.bz2
gpg --verify waf-"$waf_version".tar.bz2.asc

# extract package
tar -xf waf-"$waf_version".tar.bz2 --strip-components=1

# build package
./waf-light configure build

# install waf
cp waf /usr/bin/waf

# cleanup
rm -rf "$temp_dir"

# run waf once to setup cache
popd >/dev/null
waf --version
