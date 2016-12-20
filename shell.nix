with import <nixpkgs> {}; stdenv.mkDerivation {
  name = "env";
  buildInputs = [
    python3
    python3Packages.mutagen
    python3Packages.flask
  ];
  shellHook = "export PYTHONPATH=.:$PYTHONPATH";
}
